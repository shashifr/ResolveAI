import os
import re
import uuid
import datetime
import time
from collections import defaultdict
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db, SessionLocal
from app.models import Ticket, Message, AuditLog, Customer, Order, Subscription
from app.graph import run_support_flow, create_audit_entry, ACTION_THRESHOLDS
from app.tools import issue_refund, cancel_subscription
from app.utils.logging_config import setup_structured_logging, correlation_id_ctx

# Initialize structured JSON logging
setup_structured_logging()

app = FastAPI(title="AI Customer Support Backend API")

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread-safe in-memory rate limiting map
request_history = defaultdict(list)

# Rate limiting middleware (100 requests per minute per IP)
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        now = time.time()
        minute_ago = now - 60
        request_history[client_ip] = [t for t in request_history[client_ip] if t > minute_ago]
        if len(request_history[client_ip]) >= 100:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Maximum 100 requests per minute allowed."}
            )
        request_history[client_ip].append(now)
        return await call_next(request)

# Correlation ID Middleware to trace logs across HTTP requests
class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(correlation_id)
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)

app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RateLimitMiddleware)

# API Security Gating Dependency
security_scheme = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if not credentials or credentials.credentials != settings.API_BEARER_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Authorization Bearer Token"
        )

# Startup hook to initialize db
@app.on_event("startup")
def startup_event():
    # Database initialization
    init_db()

# Pydantic Schemas for API Requests
class EmailSimulationRequest(BaseModel):
    sender_email: str
    sender_name: Optional[str] = "Customer"
    subject: str
    body: str

class ChatSimulationRequest(BaseModel):
    ticket_id: Optional[str] = None
    customer_email: str
    message: str

class VoiceSimulationRequest(BaseModel):
    customer_email: str
    transcript: str

class ActionApprovalRequest(BaseModel):
    action: str # approve, reject, edit
    edited_reply: Optional[str] = None

# 1. Channels Simulation Endpoints
@app.post("/api/simulate/email", dependencies=[Depends(verify_token)])
def simulate_email(req: EmailSimulationRequest, db: Session = Depends(get_db)):
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    # Save the ticket metadata
    ticket = Ticket(
        id=ticket_id,
        customer_email=req.sender_email.strip(),
        customer_name=req.sender_name,
        channel="email",
        status="Open",
        subject=req.subject
    )
    db.add(ticket)
    db.commit()
    
    # Run through the LangGraph flow
    result = run_support_flow(
        ticket_id=ticket_id,
        message_text=req.body,
        customer_email=req.sender_email,
        channel="email"
    )
    
    # Refresh ticket from DB to get updated fields
    db.refresh(ticket)
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": ticket.status,
        "confidence_score": ticket.confidence_score,
        "is_auto_resolved": result["is_auto_resolved"],
        "reply": result["final_reply"]
    }

@app.post("/api/simulate/chat", dependencies=[Depends(verify_token)])
def simulate_chat(req: ChatSimulationRequest, db: Session = Depends(get_db)):
    is_new = False
    ticket_id = req.ticket_id
    
    if not ticket_id:
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        is_new = True
        ticket = Ticket(
            id=ticket_id,
            customer_email=req.customer_email.strip(),
            customer_name="Chat Customer",
            channel="chat",
            status="Open",
            subject="Live Chat Session"
        )
        db.add(ticket)
        db.commit()
    else:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
            
    # Run through the LangGraph flow
    result = run_support_flow(
        ticket_id=ticket_id,
        message_text=req.message,
        customer_email=req.customer_email,
        channel="chat"
    )
    
    db.refresh(ticket)
    
    # Get latest agent reply
    latest_msg = db.query(Message).filter(Message.ticket_id == ticket_id, Message.sender == "agent").order_by(Message.id.desc()).first()
    reply_content = latest_msg.content if latest_msg else ""
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": ticket.status,
        "confidence_score": ticket.confidence_score,
        "is_auto_resolved": result["is_auto_resolved"],
        "reply": reply_content if result["is_auto_resolved"] else result["resolution"]["reply"],
        "explanation": "" if result["is_auto_resolved"] else result["resolution"]["explanation"]
    }

@app.post("/api/simulate/voice", dependencies=[Depends(verify_token)])
def simulate_voice(req: VoiceSimulationRequest, db: Session = Depends(get_db)):
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    
    # Save ticket metadata
    ticket = Ticket(
        id=ticket_id,
        customer_email=req.customer_email.strip(),
        customer_name="Voice Caller",
        channel="voice",
        status="Open",
        subject="Voice Call Session"
    )
    db.add(ticket)
    db.commit()
    
    # Run through the LangGraph flow
    result = run_support_flow(
        ticket_id=ticket_id,
        message_text=req.transcript,
        customer_email=req.customer_email,
        channel="voice"
    )
    
    db.refresh(ticket)
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": ticket.status,
        "confidence_score": ticket.confidence_score,
        "is_auto_resolved": result["is_auto_resolved"],
        "reply": result["final_reply"]
    }

# 2. Human Console API
@app.get("/api/tickets", dependencies=[Depends(verify_token)])
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.updated_at.desc()).all()
    
    response = []
    for t in tickets:
        # Get latest message
        latest_msg = db.query(Message).filter(Message.ticket_id == t.id).order_by(Message.timestamp.desc()).first()
        latest_content = latest_msg.content if latest_msg else "No messages"
        
        response.append({
            "id": t.id,
            "customer_email": t.customer_email,
            "customer_name": t.customer_name,
            "channel": t.channel,
            "status": t.status,
            "subject": t.subject,
            "confidence_score": t.confidence_score,
            "token_cost": round(t.token_cost, 4),
            "updated_at": t.updated_at.isoformat(),
            "latest_message": latest_content
        })
    return response

@app.get("/api/tickets/{ticket_id}", dependencies=[Depends(verify_token)])
def get_ticket_details(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    messages = db.query(Message).filter(Message.ticket_id == ticket_id).order_by(Message.timestamp.asc()).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.timestamp.asc()).all()
    
    # Check if there is a pending drafted action (resolution node audit log contains it)
    resolution_log = db.query(AuditLog).filter(
        AuditLog.ticket_id == ticket_id,
        AuditLog.node == "resolution_agent"
    ).order_by(AuditLog.id.desc()).first()
    
    drafted_actions = []
    drafted_reply = ""
    explanation = ""
    
    if resolution_log and ticket.status == "Escalated":
        # Extract action taken, which contains proposed actions
        # We can parse the resolution state
        # Let's extract proposed actions
        # To do this safely, we can fetch from the audit log action_taken string or query details
        # Let's parse the action taken string or check details
        # Actually, let's extract the action_taken string, or parse state
        # Better yet, let's find the last audit log for resolution_agent and pull actions
        # Let's write a parser or save it in the DB.
        # Since we logged action_taken = f"Proposed reply: ..., Actions: {proposed_actions}"
        # We can parse it, or we can just reconstruct the simulated actions based on the ticket type
        # Let's rebuild the draft details dynamically based on intent to keep it robust and simple!
        intent_match = db.query(AuditLog).filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.node == "classifier"
        ).order_by(AuditLog.id.desc()).first()
        
        intent = "general_faq"
        risk_flags = []
        if intent_match:
            # Parse "Intent: X, Risk flags: Y"
            match_txt = intent_match.action_taken
            if "Intent:" in match_txt:
                intent = match_txt.split("Intent:")[1].split(",")[0].strip()
            if "Risk flags:" in match_txt:
                risk_flags_str = match_txt.split("Risk flags:")[1].strip()
                if risk_flags_str != "[]":
                    risk_flags = [f.strip("[]'\" ") for f in risk_flags_str.split(",")]
                    
        # Let's fetch orders for customer
        cust = db.query(Customer).filter(Customer.email == ticket.customer_email).first()
        orders = cust.orders if cust else []
        subs = cust.subscriptions if cust else []
        
        # Call simulated resolution again to retrieve exact draft proposed
        # Or look up the latest customer message
        cust_msg = db.query(Message).filter(Message.ticket_id == ticket_id, Message.sender == "customer").order_by(Message.id.desc()).first()
        msg_text = cust_msg.content if cust_msg else ""
        
        context_data = {
            "customer": {"name": cust.name if cust else "Customer", "email": ticket.customer_email},
            "orders": [{"id": o.id, "status": o.status, "total_amount": o.total_amount, "items": o.items} for o in orders],
            "subscriptions": [{"id": s.id, "plan_name": s.plan_name, "status": s.status, "price": s.price} for s in subs],
            "kb_articles": []
        }
        
        from app.llm import generate_resolution_simulated
        sim_res = generate_resolution_simulated(msg_text, intent, {"order_id": orders[0].id if orders else None, "subscription_id": subs[0].id if subs else None}, risk_flags, context_data)
        drafted_reply = sim_res["reply"]
        drafted_actions = sim_res["proposed_actions"]
        explanation = sim_res["explanation"]
        
    return {
        "id": ticket.id,
        "customer_email": ticket.customer_email,
        "customer_name": ticket.customer_name,
        "channel": ticket.channel,
        "status": ticket.status,
        "subject": ticket.subject,
        "confidence_score": ticket.confidence_score,
        "token_cost": round(ticket.token_cost, 4),
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
        "messages": [
            {
                "sender": m.sender,
                "content": m.content,
                "timestamp": m.timestamp.isoformat()
            } for m in messages
        ],
        "audit_logs": [
            {
                "node": a.node,
                "input_summary": a.input_summary,
                "model_used": a.model_used,
                "tokens": a.tokens,
                "cost": round(a.cost, 5),
                "confidence": a.confidence,
                "action_taken": a.action_taken,
                "prev_hash": a.prev_hash,
                "hash": a.hash,
                "timestamp": a.timestamp.isoformat()
            } for a in audit_logs
        ],
        "drafted_actions": drafted_actions,
        "drafted_reply": drafted_reply,
        "explanation": explanation
    }

@app.post("/api/tickets/{ticket_id}/action", dependencies=[Depends(verify_token)])
def approve_escalated_action(ticket_id: str, req: ActionApprovalRequest, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if ticket.status != "Escalated":
        raise HTTPException(status_code=400, detail="Only escalated tickets can have human actions applied")
        
    if req.action == "approve" or req.action == "edit":
        # 1. Resolve draft actions. Let's find customer details and run actions
        cust = db.query(Customer).filter(Customer.email == ticket.customer_email).first()
        orders = cust.orders if cust else []
        subs = cust.subscriptions if cust else []
        
        # Pull latest customer message to find intent
        cust_msg = db.query(Message).filter(Message.ticket_id == ticket_id, Message.sender == "customer").order_by(Message.id.desc()).first()
        msg_text = cust_msg.content if cust_msg else ""
        
        intent_match = db.query(AuditLog).filter(
            AuditLog.ticket_id == ticket_id,
            AuditLog.node == "classifier"
        ).order_by(AuditLog.id.desc()).first()
        
        intent = "general_faq"
        if intent_match and "Intent:" in intent_match.action_taken:
            intent = intent_match.action_taken.split("Intent:")[1].split(",")[0].strip()
            
        context_data = {
            "customer": {"name": cust.name if cust else "Customer", "email": ticket.customer_email},
            "orders": [{"id": o.id, "status": o.status, "total_amount": o.total_amount, "items": o.items} for o in orders],
            "subscriptions": [{"id": s.id, "plan_name": s.plan_name, "status": s.status, "price": s.price} for s in subs],
            "kb_articles": []
        }
        
        from app.llm import generate_resolution_simulated
        # Reconstruct refund details
        entities = {}
        order_match = re_match = None
        # Try to parse order id
        order_id_match = re.search(r'ORD-\d+', msg_text.upper())
        if order_id_match:
            entities["order_id"] = order_id_match.group(0)
        else:
            entities["order_id"] = orders[0].id if orders else None
            
        sub_id_match = re.search(r'SUB-\d+', msg_text.upper())
        if sub_id_match:
            entities["subscription_id"] = sub_id_match.group(0)
        else:
            entities["subscription_id"] = subs[0].id if subs else None
            
        price_match = re.search(r'\$\s*(\d+(\.\d{2})?)', msg_text)
        if price_match:
            entities["refund_amount"] = float(price_match.group(1))
            
        sim_res = generate_resolution_simulated(msg_text, intent, entities, [], context_data)
        actions = sim_res["proposed_actions"]
        
        action_notes = []
        for act in actions:
            name = act["action"]
            args = act["args"]
            if name == "issue_refund":
                res = issue_refund(db, args["order_id"], args["amount"], args.get("reason", "Human Approved Refund"))
                action_notes.append(f"Refund of ${args['amount']} for order {args['order_id']}")
            elif name == "cancel_subscription":
                res = cancel_subscription(db, args["subscription_id"], args.get("reason", "Human Approved Cancellation"))
                action_notes.append(f"Cancelled subscription {args['subscription_id']}")
                
        # 2. Append reply message to client
        final_reply = req.edited_reply if req.action == "edit" and req.edited_reply else sim_res["reply"]
        
        agent_msg = Message(
            ticket_id=ticket_id,
            sender="agent",
            content=final_reply
        )
        db.add(agent_msg)
        
        ticket.status = "Resolved"
        ticket.confidence_score = 1.0 # Human approved is absolute confidence
        
        action_note_str = ", ".join(action_notes) if action_notes else "Reply sent"
        action_audit = f"Human Approved Action ({req.action.upper()}). Actions executed: {action_note_str}"
        
    elif req.action == "reject":
        agent_msg = Message(
            ticket_id=ticket_id,
            sender="agent",
            content="Hi, we've reviewed your request but unfortunately cannot approve it at this time. Let us know if you need help with anything else."
        )
        db.add(agent_msg)
        ticket.status = "Resolved"
        action_audit = "Human Rejected Action. Sent rejection message to customer."
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    # Log human decision to audit chain
    log = create_audit_entry(
        db=db,
        ticket_id=ticket_id,
        node="human_console",
        input_summary=f"Human Console review submitted for ticket {ticket_id}",
        model_used="Human Intervention",
        tokens=0,
        cost=0.0,
        confidence=1.0,
        action_taken=action_audit
    )
    db.add(log)
    db.commit()
    db.close()
    
    return {"success": True, "new_status": "Resolved", "action_taken": action_audit}

@app.get("/api/metrics", dependencies=[Depends(verify_token)])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    # 1. Total tickets
    total_tickets = db.query(Ticket).count()
    
    # 2. Resolved tickets count
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "Resolved").all()
    resolved_count = len(resolved_tickets)
    
    # 3. Autonomous tickets: Resolved tickets that NEVER had a 'human_console' node log
    # Let's count them by querying tickets where 'human_console' is not in their audit logs
    autonomous_count = 0
    total_tokens = 0
    total_actual_cost = 0.0
    
    for t in resolved_tickets:
        has_human = db.query(AuditLog).filter(
            AuditLog.ticket_id == t.id,
            AuditLog.node == "human_console"
        ).first() is not None
        
        if not has_human:
            autonomous_count += 1
            
        # Accumulate tokens & cost
        t_tokens = db.query(AuditLog).filter(AuditLog.ticket_id == t.id).all()
        for tok in t_tokens:
            total_tokens += tok.tokens
            total_actual_cost += tok.cost
            
    # Trust Autonomy Rate: % of resolved tickets resolved autonomously
    autonomy_rate = round((autonomous_count / resolved_count * 100), 1) if resolved_count > 0 else 0.0
    
    # 4. Baseline Cost: Baseline cost if we routed everything through Tier 2 (Opus-class Frontier Model)
    # Opus price: Input $0.015/1K, Output $0.075/1K -> Avg $0.045/1K tokens
    # Baseline Cost = total_tokens * 0.045 / 1000
    baseline_cost = round((total_tokens * 0.045) / 1000, 4)
    savings = round(max(0.0, baseline_cost - total_actual_cost), 4)
    
    # 5. Average response time simulation
    # Autonomous: 1-3 seconds. Escalated: 10-20 mins.
    # We can compute a simulated average response time
    # If all resolved: average is (autonomous_count * 2s + (resolved_count - autonomous_count) * 900s) / resolved_count
    avg_resp_time_sec = 0
    if resolved_count > 0:
        avg_resp_time_sec = int((autonomous_count * 2 + (resolved_count - autonomous_count) * 900) / resolved_count)
        
    return {
        "total_tickets": total_tickets,
        "resolved_count": resolved_count,
        "autonomous_count": autonomous_count,
        "autonomy_rate": autonomy_rate,
        "total_actual_cost": round(total_actual_cost, 4),
        "baseline_cost": baseline_cost,
        "savings": savings,
        "avg_resp_time_sec": avg_resp_time_sec
    }
