import os
import re
import json
import hashlib
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.config import settings

# Model pricing configurations (Cost per 1,000 tokens)
MODEL_PRICING = {
    "tier_0": {"name": "Haiku-class (Cheap)", "input": 0.00025, "output": 0.00125},
    "tier_1": {"name": "Sonnet-class (Standard)", "input": 0.003, "output": 0.015},
    "tier_2": {"name": "Opus-class (Frontier)", "input": 0.015, "output": 0.075}
}

class ExtractedEntities(BaseModel):
    order_id: Optional[str] = None
    subscription_id: Optional[str] = None
    refund_amount: Optional[float] = None

class ClassificationResult(BaseModel):
    intent: str
    confidence: float
    extracted_entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    risk_flags: List[str] = []

class ProposedAction(BaseModel):
    action: str
    args: Dict[str, Any] = Field(default_factory=dict)

class ResolutionResult(BaseModel):
    reply: str
    confidence: float
    proposed_actions: List[ProposedAction] = []
    explanation: str

def classify_intent_simulated(message_text: str) -> Dict[str, Any]:
    """
    Highly realistic simulation of Tier 0 model classifying support tickets.
    """
    text = message_text.lower()
    
    # Defaults
    intent = "general_faq"
    confidence = 0.95
    entities = {}
    risk_flags = []
    
    # Order Status / Tracking
    if any(k in text for k in ["order status", "where is my order", "track", "tracking", "status of my order", "when will my order arrive", "has my order shipped"]):
        intent = "order_status"
        confidence = 0.92
    
    # Refund request
    elif any(k in text for k in ["refund", "money back", "return", "chargeback", "get my money"]) and "policy" not in text:
        intent = "refund_request"
        confidence = 0.94
        
    # Shipping Delay
    elif any(k in text for k in ["delay", "late", "still not here", "lost in transit", "package not delivered", "where is it"]):
        intent = "shipping_delay"
        confidence = 0.88
        
    # Subscription Cancellation
    elif any(k in text for k in ["cancel subscription", "cancel membership", "stop charging", "unsubscribe"]):
        intent = "subscription_cancel"
        confidence = 0.96
        
    # Account access
    elif any(k in text for k in ["login", "sign in", "password", "reset password", "account locked", "cannot access account"]):
        intent = "account_access"
        confidence = 0.90
        
    # Extract ORD-XXXX or SUB-XXXX
    order_match = re.search(r'ord-\d+', text)
    if order_match:
        entities["order_id"] = order_match.group(0).upper()
        
    sub_match = re.search(r'sub-\d+', text)
    if sub_match:
        entities["subscription_id"] = sub_match.group(0).upper()
        
    # Extract refund amount if any
    price_match = re.search(r'\$\s*(\d+(\.\d{2})?)', text)
    if price_match:
        entities["refund_amount"] = float(price_match.group(1))
        
    # Risk flag analysis
    # High value refund
    if intent == "refund_request":
        amt = entities.get("refund_amount", 0.0)
        # Check order total if not specified, default to $100 if we cannot find it
        if amt > 100.0 or not amt:
            risk_flags.append("high_refund_value")
            
    # Legal threat
    if any(k in text for k in ["sue", "lawyer", "legal", "attorney", "court", "better business bureau", "bbb", "police"]):
        risk_flags.append("legal_threat")
        confidence -= 0.15 # Classification certainty drops
        
    # Angry customer
    if any(k in text for k in ["unacceptable", "terrible", "worst", "hate", "pissed", "furious", "garbage", "scam", "shitty", "awful", "horrible"]):
        risk_flags.append("angry_language")
        confidence -= 0.10
        
    # Confidence bounds
    confidence = max(0.4, min(1.0, confidence))
    
    return {
        "intent": intent,
        "confidence": confidence,
        "extracted_entities": entities,
        "risk_flags": risk_flags
    }

def generate_resolution_simulated(
    message_text: str,
    intent: str,
    entities: Dict[str, Any],
    risk_flags: List[str],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulation of Tier 1/Tier 2 models generating drafts and executing actions.
    """
    customer_name = context.get("customer", {}).get("name", "Customer")
    orders = context.get("orders", [])
    subscriptions = context.get("subscriptions", [])
    kb_articles = context.get("kb_articles", [])
    
    reply = ""
    proposed_actions = []
    explanation = ""
    confidence = 0.95
    
    # Lower confidence based on risk flags
    if "angry_language" in risk_flags:
        confidence -= 0.15
    if "legal_threat" in risk_flags:
        confidence -= 0.35
        explanation = "Ticket contains legal threats. Handing off to human agent for safety."
    
    # 1. Order Status Intent
    if intent == "order_status":
        order_id = entities.get("order_id")
        
        # Find order in context
        target_order = None
        if order_id:
            target_order = next((o for o in orders if o["id"] == order_id), None)
        elif orders:
            target_order = orders[0] # Take latest
            
        if target_order:
            status = target_order["status"]
            tracking = target_order["tracking_number"]
            items_str = ", ".join([f"{i['qty']}x {i['name']}" for i in target_order["items"]])
            
            if status == "Delivered":
                reply = f"Hi {customer_name},\n\nYour order {target_order['id']} ({items_str}) was delivered to {target_order['shipping_address']}. Tracking details can be viewed here: {tracking}."
                explanation = "Order is successfully delivered. Safe to auto-resolve."
            elif status == "Shipped":
                reply = f"Hi {customer_name},\n\nYour order {target_order['id']} ({items_str}) is currently in transit. The tracking number is {tracking}."
                explanation = "Order is shipped and in transit. Safe to auto-resolve."
            elif status == "Shipped (Delayed)":
                reply = f"Hi {customer_name},\n\nI see order {target_order['id']} is currently delayed. The package is with the courier (Tracking: {tracking}). Let me escalate this to our support team to look into the delay."
                confidence = 0.65
                explanation = "Order is shipped but delayed. Customer may need compensation or high-touch update."
            else:
                reply = f"Hi {customer_name},\n\nYour order {target_order['id']} ({items_str}) is currently {status.lower()}. We are preparing it for shipment."
                explanation = "Order is processing. Safe to auto-resolve."
        else:
            reply = f"Hi {customer_name},\n\nI couldn't find any recent orders associated with your account. Could you please provide your order ID?"
            confidence = 0.70
            explanation = "No order found in customer history. Need customer clarification."

    # 2. Refund Request Intent
    elif intent == "refund_request":
        order_id = entities.get("order_id")
        target_order = None
        if order_id:
            target_order = next((o for o in orders if o["id"] == order_id), None)
        elif orders:
            target_order = orders[0]
            
        refund_amount = entities.get("refund_amount")
        
        if target_order:
            max_refund = target_order["total_amount"]
            amt = refund_amount if refund_amount else max_refund
            
            if amt > max_refund:
                reply = f"Hi {customer_name},\n\nI see you're requesting a refund of ${amt} for order {target_order['id']}. However, the total order amount was only ${max_refund}. I am transferring this to a supervisor to review."
                confidence = 0.50
                explanation = f"Requested refund amount (${amt}) exceeds order total (${max_refund})."
            elif amt > 50.0:
                # High-value refunds require human review
                reply = f"Hi {customer_name},\n\nI have drafted a refund of ${amt} for your order {target_order['id']}. Since this is above our automatic refund threshold of $50, I've requested a support agent to approve this refund immediately."
                confidence = 0.60
                proposed_actions = [{"action": "issue_refund", "args": {"order_id": target_order["id"], "amount": amt, "reason": "Customer request (high-value)"}}]
                explanation = f"Refund amount ${amt} is above the automated $50 threshold. Requires human confirmation."
            else:
                # Low value refunds auto-resolved!
                reply = f"Hi {customer_name},\n\nI have successfully processed a refund of ${amt} for your order {target_order['id']} back to your original payment method. You should see it in 5-7 business days."
                proposed_actions = [{"action": "issue_refund", "args": {"order_id": target_order["id"], "amount": amt, "reason": "Customer request (low-value)"}}]
                explanation = f"Refund of ${amt} is within $50 threshold. Auto-executed."
        else:
            reply = f"Hi {customer_name},\n\nI would be happy to help with your return/refund request, but I couldn't locate your order. Could you please provide your order ID?"
            confidence = 0.70
            explanation = "No order found in history to refund. Escalated for clarification."

    # 3. Shipping Delay Intent
    elif intent == "shipping_delay":
        order_id = entities.get("order_id")
        target_order = next((o for o in orders if o["id"] == order_id), None) if order_id else (orders[0] if orders else None)
        
        if target_order:
            status = target_order["status"]
            tracking = target_order["tracking_number"]
            
            if status == "Shipped" or "Delayed" in status:
                reply = f"Hi {customer_name},\n\nI sincerely apologize for the delay with order {target_order['id']}. The tracking number is {tracking}. I am flagging this order with our logistics team to expedite delivery."
                proposed_actions = []
                confidence = 0.75
                explanation = "Delayed shipping complaint. Auto-drafted apologize email but escalated to monitor courier."
            elif status == "Delivered":
                reply = f"Hi {customer_name},\n\nI see order {target_order['id']} is marked as delivered to {target_order['shipping_address']} (Tracking: {tracking}). If you cannot find the package, please check around your property or with neighbors."
                explanation = "Order is delivered, shipping complaint resolved with info."
            else:
                reply = f"Hi {customer_name},\n\nYour order {target_order['id']} is still in processing. I will escalate this to shipping to speed up dispatch."
                confidence = 0.70
                explanation = "Order stuck in processing. Needs shipping coordinator escalation."
        else:
            reply = f"Hi {customer_name},\n\nI couldn't locate your order. Please reply with the order ID so I can investigate the delivery delay."
            confidence = 0.70
            explanation = "Missing order ID for shipping complaint."

    # 4. Subscription Cancel Intent
    elif intent == "subscription_cancel":
        sub_id = entities.get("subscription_id")
        target_sub = next((s for s in subscriptions if s["id"] == sub_id), None) if sub_id else (subscriptions[0] if subscriptions else None)
        
        if target_sub:
            if target_sub["status"] == "Cancelled":
                reply = f"Hi {customer_name},\n\nYour subscription for {target_sub['plan_name']} has already been cancelled. You will not be charged again."
                explanation = "Subscription already cancelled."
            else:
                # Subscription cancellations are high risk and always escalated in our business logic for retention!
                reply = f"Hi {customer_name},\n\nI've prepared a cancellation for your {target_sub['plan_name']} subscription. A human agent is reviewing this right now to finalize the cancellation and check if we can offer a discount."
                confidence = 0.55
                proposed_actions = [{"action": "cancel_subscription", "args": {"subscription_id": target_sub["id"], "reason": "Customer cancellation request"}}]
                explanation = "Subscription cancellation request. Escalated to retention queue."
        else:
            reply = f"Hi {customer_name},\n\nI couldn't find an active subscription under your account. If you believe this is an error, please provide your subscription or billing ID."
            confidence = 0.75
            explanation = "Customer requested cancellation, but no subscription found."

    # 5. Account Access Intent
    elif intent == "account_access":
        reply = f"Hi {customer_name},\n\nI understand you're having trouble accessing your account. I have triggered a password reset link to your email ({context.get('customer', {}).get('email', '')}). Please check your spam folder if you do not receive it in 5 minutes."
        explanation = "Triggered password reset. Safe to auto-resolve."
        # No database write action needed, but we simulate reset
        
    # 6. General FAQ Intent
    else:
        # Search KB in context
        if kb_articles:
            best_article = kb_articles[0]
            reply = f"Hi {customer_name},\n\nHere is what I found regarding your question:\n\n{best_article['content']}"
            explanation = f"Resolved via Knowledge Base article: '{best_article['title']}'."
        else:
            reply = f"Hi {customer_name},\n\nThank you for contacting customer support. I'm routing your query to an agent who can help you right away."
            confidence = 0.50
            explanation = "No matching KB article found. Escalating query to agent."

    confidence = max(0.1, min(1.0, confidence))
    
    return {
        "reply": reply,
        "confidence": confidence,
        "proposed_actions": proposed_actions,
        "explanation": explanation
    }

class ModelRouter:
    """
    MoE Router that determines model tier, executes calls (mocked or real),
    tracks tokens and calculates costs.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.use_real_llm = bool(self.api_key)
        if self.use_real_llm:
            print("[ModelRouter] Found Gemini API key. Real LLM execution enabled.")
        else:
            print("[ModelRouter] No Gemini API key found. Sandbox simulation enabled.")
        
    def call_gemini_api(self, prompt: str, schema: Any, model: str = "gemini-1.5-flash") -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Extract JSON schema from Pydantic
        schema_dict = schema.model_json_schema() if hasattr(schema, "model_json_schema") else schema.schema()
        
        # Clean schema for Gemini compatibility (remove titles, description, definitions etc)
        def clean_schema(s):
            if not isinstance(s, dict):
                return s
            cleaned = {}
            for k, v in s.items():
                if k in ["title", "description", "additionalProperties", "$defs", "definitions"]:
                    continue
                if k == "properties":
                    cleaned[k] = {pk: clean_schema(pv) for pk, pv in v.items()}
                elif k == "items":
                    cleaned[k] = clean_schema(v)
                else:
                    cleaned[k] = v
            return cleaned
            
        cleaned_schema = clean_schema(schema_dict)
        
        # Convert type strings to uppercase (e.g. "OBJECT", "STRING")
        def convert_types_to_upper(s):
            if not isinstance(s, dict):
                return s
            converted = {}
            for k, v in s.items():
                if k == "type" and isinstance(v, str):
                    converted[k] = v.upper()
                elif isinstance(v, dict):
                    converted[k] = convert_types_to_upper(v)
                elif isinstance(v, list):
                    converted[k] = [convert_types_to_upper(item) if isinstance(item, dict) else item for item in v]
                else:
                    converted[k] = v
            return converted
            
        final_schema = convert_types_to_upper(cleaned_schema)

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": final_schema
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
            else:
                print(f"Gemini API returned status code {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None

    def classify_intent(self, message_text: str) -> Dict[str, Any]:
        """
        Classifies incoming query. Uses Tier 0.
        Returns: {result: ClassificationResult, model: str, tokens: int, cost: float}
        """
        model_tier = "tier_0"
        model_name = MODEL_PRICING[model_tier]["name"]
        res = None
        
        if self.use_real_llm:
            prompt = (
                "You are an incoming customer support ticket intent classifier.\n"
                f"Classify the following customer query:\n\"{message_text}\"\n\n"
                "Allowed intents:\n"
                "- \"order_status\" (inquiring about status, tracking, or delivery of an order)\n"
                "- \"refund_request\" (asking for a return, refund, chargeback, or money back)\n"
                "- \"shipping_delay\" (complaining about delayed shipment or transit delays)\n"
                "- \"subscription_cancel\" (requesting cancellation of subscription or membership)\n"
                "- \"account_access\" (locked out, password reset, login problems)\n"
                "- \"general_faq\" (general return policy questions, or other standard company policy questions)\n\n"
                "Extract entities if present:\n"
                "- \"order_id\" (format ORD-XXXX, e.g. ORD-1001)\n"
                "- \"subscription_id\" (format SUB-XXXX, e.g. SUB-2001)\n"
                "- \"refund_amount\" (exact refund dollar value as a float, e.g. 120.00)\n\n"
                "Identify risk flags (list of strings):\n"
                "- \"high_refund_value\" (if intent is refund_request and the requested amount is over $100, or if no amount is mentioned but you suspect it's a high-value purchase refund request)\n"
                "- \"legal_threat\" (if customer mentions lawyers, suing, BBB, court, or legal actions)\n"
                "- \"angry_language\" (if customer uses profanity, insults, angry capitalization, or extreme frustration)\n\n"
                "Provide a confidence score between 0.0 and 1.0 (float) for the intent classification."
            )
            api_res = self.call_gemini_api(prompt, ClassificationResult, "gemini-1.5-flash")
            if api_res:
                res = api_res
                print(f"[Gemini Classifier] Successfully classified intent: {res.get('intent')} (Conf: {res.get('confidence')})")
            else:
                print("[Gemini Classifier] Warning: API call failed or timed out. Falling back to simulation.")
                
        if not res:
            res = classify_intent_simulated(message_text)
            
        # Calculate tokens based on simple length heuristics
        prompt_tokens = len(message_text.split()) + 150
        comp_tokens = 80
        cost = (prompt_tokens * MODEL_PRICING["tier_0"]["input"] + comp_tokens * MODEL_PRICING["tier_0"]["output"]) / 1000
        
        return {
            "result": ClassificationResult(**res),
            "model": model_name,
            "tokens": prompt_tokens + comp_tokens,
            "cost": round(cost, 6)
        }
        
    def route_and_resolve(
        self,
        message_text: str,
        classification: ClassificationResult,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Routes to standard or frontier tier and generates resolution.
        """
        # Determine tier
        if (
            "legal_threat" in classification.risk_flags or
            "high_refund_value" in classification.risk_flags or
            classification.confidence < 0.75 or
            "angry_language" in classification.risk_flags
        ):
            tier = "tier_2"
            model_id = "gemini-1.5-pro"
        elif classification.intent in ["order_status", "refund_request", "shipping_delay", "subscription_cancel"]:
            tier = "tier_1"
            model_id = "gemini-1.5-flash"
        else:
            tier = "tier_0"
            model_id = "gemini-1.5-flash"
            
        pricing = MODEL_PRICING[tier]
        res = None
        
        if self.use_real_llm:
            # Prepare entities as dictionary
            entities_data = classification.extracted_entities
            entities_dict = entities_data.dict() if hasattr(entities_data, 'dict') else entities_data
            
            prompt = (
                "You are an AI customer support resolution expert. Your job is to draft a helpful, professional reply to the customer and propose any system actions (like refunds or cancellations) if applicable.\n\n"
                f"Customer Message:\n\"{message_text}\"\n\n"
                f"Classification Intent: {classification.intent}\n"
                f"Extracted Entities: {entities_dict}\n"
                f"Risk Flags: {classification.risk_flags}\n\n"
                f"Context (CRM Profile, Order History, Active Subscriptions, Knowledge Base articles):\n{json.dumps(context, indent=2)}\n\n"
                "Guidelines:\n"
                "1. Formulate a polite, helpful customer support email response (under 'reply').\n"
                "2. If the user's issue can be resolved with a refund or cancellation:\n"
                "   - For refunds: Look at their order history in the context. If they specify an order or if there is a clear latest order to refund, and the amount is valid (<= order total), propose an action to refund. Note: If the refund is over $50, still propose it but set a low confidence score (e.g. 0.60) so it escalates to human review, explaining in the explanation that it exceeds the auto threshold.\n"
                "   - For cancellations: Propose cancellation of the subscription. Note: In our business rules, all subscription cancellations should be escalated to human agents for retention (confidence score should be set to 0.55).\n"
                "   - If no order is found or if details are missing, politely ask the user for clarification in your reply and do not propose any actions. Set confidence score lower (e.g., 0.70) to escalate.\n"
                "3. If it's a general FAQ, use the Knowledge Base article in the context to draft the reply. Set confidence high (0.95) if a good match is found, or low (0.50) if no matching article is in context.\n"
                "4. Set the \"confidence\" score between 0.0 and 1.0 based on how confident you are that this resolution is fully correct and safe to execute automatically.\n"
                "5. Set the \"explanation\" field to explain your reasoning (especially why you set a low confidence score or why you proposed a particular action).\n\n"
                "Propose actions inside the 'proposed_actions' array as objects with 'action' and 'args' fields:\n"
                "- Example refund: {\"action\": \"issue_refund\", \"args\": {\"order_id\": \"ORD-1001\", \"amount\": 120.0, \"reason\": \"Reason details\"}}\n"
                "- Example cancel: {\"action\": \"cancel_subscription\", \"args\": {\"subscription_id\": \"SUB-2001\", \"reason\": \"Reason details\"}}"
            )
            api_res = self.call_gemini_api(prompt, ResolutionResult, model_id)
            if api_res:
                res = api_res
                print(f"[Gemini Resolver] Successfully generated resolution via {model_id} (Conf: {res.get('confidence')})")
            else:
                print(f"[Gemini Resolver] Warning: API call failed or timed out. Falling back to simulation.")
                
        if not res:
            entities_dict = classification.extracted_entities.dict() if hasattr(classification.extracted_entities, "dict") else classification.extracted_entities
            res = generate_resolution_simulated(
                message_text,
                classification.intent,
                entities_dict,
                classification.risk_flags,
                context
            )
            
        # Token metrics
        prompt_tokens = len(message_text.split()) + len(str(context).split()) + 300
        comp_tokens = len(res["reply"].split()) + 100
        cost = (prompt_tokens * pricing["input"] + comp_tokens * pricing["output"]) / 1000
        
        return {
            "result": ResolutionResult(**res),
            "tier": tier,
            "model": pricing["name"],
            "tokens": prompt_tokens + comp_tokens,
            "cost": round(cost, 6)
        }
