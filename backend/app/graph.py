import datetime
import json
import hashlib
from typing import Dict, Any, List, TypedDict, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from app.database import SessionLocal
from app.models import Ticket, Message, AuditLog, Customer
from app.llm import ModelRouter, ClassificationResult, ResolutionResult
from app.tools import get_customer_by_email, get_order_status, issue_refund, cancel_subscription, search_knowledge_base

# Thresholds for different actions
ACTION_THRESHOLDS = {
    "order_status": 0.80,
    "refund_request": 0.85,
    "shipping_delay": 0.80,
    "subscription_cancel": 0.90, # retention escalation policy
    "account_access": 0.80,
    "general_faq": 0.80
}

class AgentState(TypedDict):
    ticket_id: str
    message_text: str
    channel: str
    customer_email: str
    
    # Processing states
    classification: Optional[Dict[str, Any]]
    selected_tier: str
    model_name: str
    context: Dict[str, Any]
    resolution: Optional[Dict[str, Any]]
    confidence_score: float
    is_auto_resolved: bool
    final_reply: str
    node_logs: List[Dict[str, Any]] # Log entries collected to be written to DB

def create_audit_entry(db: Session, ticket_id: str, node: str, input_summary: str, model_used: str, tokens: int, cost: float, confidence: float, action_taken: str) -> AuditLog:
    """
    Computes a cryptographic-style SHA-256 hash chained to the last log entry for this ticket.
    """
    # Find last hash
    last_log = db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.id.desc()).first()
    prev_hash = last_log.hash if last_log else "0" * 64
    
    # Calculate current hash
    data_to_hash = f"{prev_hash}|{ticket_id}|{node}|{input_summary}|{model_used}|{tokens}|{cost}|{confidence}|{action_taken}"
    current_hash = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
    
    log_entry = AuditLog(
        ticket_id=ticket_id,
        node=node,
        input_summary=input_summary,
        model_used=model_used,
        tokens=tokens,
        cost=cost,
        confidence=confidence,
        action_taken=action_taken,
        prev_hash=prev_hash,
        hash=current_hash
    )
    return log_entry

# Node 1: Intake & Normalize
def intake_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    ticket_id = state["ticket_id"]
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        # Create a new ticket if not exists (for chat widget creation)
        ticket = Ticket(
            id=ticket_id,
            customer_email=state["customer_email"],
            channel=state["channel"],
            status="Open",
            confidence_score=0.0,
            token_cost=0.0
        )
        db.add(ticket)
        db.commit()
    
    # Save the incoming customer message in DB
    customer_msg = Message(
        ticket_id=ticket_id,
        sender="customer",
        content=state["message_text"]
    )
    db.add(customer_msg)
    db.commit()
    
    # Log intake node
    log = create_audit_entry(
        db=db,
        ticket_id=ticket_id,
        node="intake",
        input_summary=f"Normalized {state['channel']} message: {state['message_text'][:100]}...",
        model_used="System Routing",
        tokens=0,
        cost=0.0,
        confidence=1.0,
        action_taken="Message registered, thread active"
    )
    db.add(log)
    db.commit()
    db.close()
    
    return {"node_logs": [log]}

# Node 2: Classify Intent & Risk
def classify_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    router = ModelRouter()
    
    result = router.classify_intent(state["message_text"])
    classification = result["result"]
    
    # Log classification node
    log = create_audit_entry(
        db=db,
        ticket_id=state["ticket_id"],
        node="classifier",
        input_summary=f"Input: {state['message_text'][:100]}...",
        model_used=result["model"],
        tokens=result["tokens"],
        cost=result["cost"],
        confidence=classification.confidence,
        action_taken=f"Intent: {classification.intent}, Risk flags: {classification.risk_flags}"
    )
    
    # Accumulate token costs
    ticket = db.query(Ticket).filter(Ticket.id == state["ticket_id"]).first()
    if ticket:
        ticket.token_cost += result["cost"]
        db.commit()
        
    db.add(log)
    db.commit()
    db.close()
    
    return {
        "classification": classification.dict(),
        "node_logs": [log]
    }

# Node 3: Context Retrieval
def context_retriever_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    email = state["customer_email"]
    classification = state["classification"]
    intent = classification["intent"]
    entities = classification["extracted_entities"]
    
    # 1. Fetch customer details
    cust = get_customer_by_email(db, email)
    cust_data = {}
    orders_data = []
    subs_data = []
    
    if cust:
        cust_data = {"id": cust.id, "name": cust.name, "email": cust.email, "phone": cust.phone}
        # Fetch orders
        for o in cust.orders:
            orders_data.append({
                "id": o.id,
                "status": o.status,
                "total_amount": o.total_amount,
                "order_date": o.order_date.isoformat(),
                "items": o.items,
                "tracking_number": o.tracking_number,
                "shipping_address": o.shipping_address
            })
        # Fetch subscriptions
        for s in cust.subscriptions:
            subs_data.append({
                "id": s.id,
                "plan_name": s.plan_name,
                "status": s.status,
                "price": s.price,
                "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else None
            })
            
    # 2. Fetch Knowledge Base articles based on intent & text
    search_query = intent.replace("_", " ")
    kb_results = search_knowledge_base(db, search_query)
    if not kb_results:
        text = state["message_text"].lower()
        if "policy" in text or "return" in text:
            kb_results = search_knowledge_base(db, "return policy")
        elif "shipping" in text or "delivery" in text or "delay" in text:
            kb_results = search_knowledge_base(db, "shipping")
        elif "cancel" in text or "subscription" in text:
            kb_results = search_knowledge_base(db, "cancel")
        elif "password" in text or "reset" in text or "login" in text:
            kb_results = search_knowledge_base(db, "password")
        else:
            for word in text.split():
                if len(word) > 4:
                    kb_results = search_knowledge_base(db, word)
                    if kb_results:
                        break
        
    context = {
        "customer": cust_data,
        "orders": orders_data,
        "subscriptions": subs_data,
        "kb_articles": kb_results
    }
    
    # Log context node
    log = create_audit_entry(
        db=db,
        ticket_id=state["ticket_id"],
        node="context_retriever",
        input_summary=f"Retrieve CRM & KB data for email: {email}",
        model_used="System Retrieval",
        tokens=0,
        cost=0.0,
        confidence=1.0,
        action_taken=f"Fetched Customer ID: {cust_data.get('id', 'None')}, Orders: {len(orders_data)}, KB Articles: {len(kb_results)}"
    )
    db.add(log)
    db.commit()
    db.close()
    
    return {
        "context": context,
        "node_logs": [log]
    }

# Node 4: MoE Resolution Agent
def resolve_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    router = ModelRouter()
    
    # Reconstruct ClassificationResult object
    class_obj = ClassificationResult(**state["classification"])
    
    # Route and execute LLM call
    res = router.route_and_resolve(state["message_text"], class_obj, state["context"])
    resolution = res["result"]
    tier = res["tier"]
    model = res["model"]
    
    # Log resolution node
    log = create_audit_entry(
        db=db,
        ticket_id=state["ticket_id"],
        node="resolution_agent",
        input_summary=f"CRM & KB Context passed to {model}",
        model_used=model,
        tokens=res["tokens"],
        cost=res["cost"],
        confidence=resolution.confidence,
        action_taken=f"Proposed reply: {resolution.reply[:100]}..., Actions: {resolution.proposed_actions}"
    )
    
    # Update cost
    ticket = db.query(Ticket).filter(Ticket.id == state["ticket_id"]).first()
    if ticket:
        ticket.token_cost += res["cost"]
        db.commit()
        
    db.add(log)
    db.commit()
    db.close()
    
    return {
        "resolution": resolution.dict(),
        "selected_tier": tier,
        "model_name": model,
        "confidence_score": resolution.confidence,
        "node_logs": [log]
    }

# Node 5: Confidence Gating
def gate_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    intent = state["classification"]["intent"]
    confidence = state["confidence_score"]
    
    # Get threshold for intent
    threshold = ACTION_THRESHOLDS.get(intent, 0.80)
    
    # Check if we should auto-resolve
    is_auto = confidence >= threshold
    
    # Log gating node
    log = create_audit_entry(
        db=db,
        ticket_id=state["ticket_id"],
        node="confidence_gate",
        input_summary=f"Confidence: {confidence:.2f} vs Threshold: {threshold:.2f} for intent '{intent}'",
        model_used="System Gate",
        tokens=0,
        cost=0.0,
        confidence=1.0,
        action_taken="GATED: Auto-execute" if is_auto else "GATED: Escalate to human queue"
    )
    db.add(log)
    db.commit()
    db.close()
    
    return {
        "is_auto_resolved": is_auto,
        "node_logs": [log]
    }

# Node 6: Executor / Escalation Packager
def execute_node(state: AgentState) -> Dict[str, Any]:
    db = SessionLocal()
    ticket_id = state["ticket_id"]
    is_auto = state["is_auto_resolved"]
    resolution = state["resolution"]
    proposed_actions = resolution["proposed_actions"]
    reply = resolution["reply"]
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    action_notes = []
    
    if is_auto:
        # Auto-execute proposed actions
        for act in proposed_actions:
            name = act["action"]
            args = act["args"]
            
            if name == "issue_refund":
                res = issue_refund(db, args["order_id"], args["amount"], args.get("reason", "Auto-refund"))
                action_notes.append(f"Auto-executed refund: {res}")
            elif name == "cancel_subscription":
                res = cancel_subscription(db, args["subscription_id"], args.get("reason", "Auto-cancel"))
                action_notes.append(f"Auto-executed cancel: {res}")
                
        # Send auto-reply to customer
        agent_msg = Message(
            ticket_id=ticket_id,
            sender="agent",
            content=reply
        )
        db.add(agent_msg)
        
        # Update ticket status
        if ticket:
            ticket.status = "Resolved"
            ticket.confidence_score = state["confidence_score"]
            ticket.subject = state["classification"]["intent"].replace("_", " ").title()
            
        action_taken_str = "Auto-resolved. Actions executed: " + (", ".join(action_notes) if action_notes else "None (FAQ answer)")
    else:
        # Escalate ticket: Don't execute proposed actions, save draft message & action details to DB
        # The frontend will display the ticket as "Escalated" with draft actions and draft reply
        if ticket:
            ticket.status = "Escalated"
            ticket.confidence_score = state["confidence_score"]
            ticket.subject = state["classification"]["intent"].replace("_", " ").title()
            
        action_taken_str = f"Escalated. Reason: {resolution.get('explanation', 'Low confidence')}. Drafted reply & actions packed."
        
    db.commit()
    
    # Log executor node
    log = create_audit_entry(
        db=db,
        ticket_id=ticket_id,
        node="executor_gate",
        input_summary=f"Execution block running. Autonomy status: {is_auto}",
        model_used="System Executor",
        tokens=0,
        cost=0.0,
        confidence=1.0,
        action_taken=action_taken_str
    )
    db.add(log)
    db.commit()
    
    # Add a final message notifying about escalation if escalated
    if not is_auto:
        system_msg = Message(
            ticket_id=ticket_id,
            sender="system",
            content=f"Ticket escalated to queue. Reason: {resolution.get('explanation', 'Low confidence score')}."
        )
        db.add(system_msg)
        db.commit()
        
    db.close()
    
    return {
        "final_reply": reply if is_auto else "",
        "node_logs": [log]
    }

# Create LangGraph workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("intake", intake_node)
workflow.add_node("classifier", classify_node)
workflow.add_node("context_retriever", context_retriever_node)
workflow.add_node("resolution_agent", resolve_node)
workflow.add_node("confidence_gate", gate_node)
workflow.add_node("executor", execute_node)

# Set entry point
workflow.set_entry_point("intake")

# Connect nodes
workflow.add_edge("intake", "classifier")
workflow.add_edge("classifier", "context_retriever")
workflow.add_edge("context_retriever", "resolution_agent")
workflow.add_edge("resolution_agent", "confidence_gate")
workflow.add_edge("confidence_gate", "executor")
workflow.add_edge("executor", END)

# Compile graph
compiled_graph = workflow.compile()

def run_support_flow(ticket_id: str, message_text: str, customer_email: str, channel: str = "email") -> Dict[str, Any]:
    """
    Executes the support agent LangGraph pipeline.
    """
    initial_state = {
        "ticket_id": ticket_id,
        "message_text": message_text,
        "channel": channel,
        "customer_email": customer_email,
        "classification": None,
        "selected_tier": "",
        "model_name": "",
        "context": {},
        "resolution": None,
        "confidence_score": 0.0,
        "is_auto_resolved": False,
        "final_reply": "",
        "node_logs": []
    }
    
    return compiled_graph.invoke(initial_state)
