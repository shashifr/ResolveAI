from sqlalchemy.orm import Session
from app.models import Customer, Order, Subscription, KnowledgeBase
import datetime

def get_customer_by_email(db: Session, email: str):
    return db.query(Customer).filter(Customer.email.ilike(email.strip())).first()

def get_order_status(db: Session, order_id: str):
    order = db.query(Order).filter(Order.id == order_id.strip().upper()).first()
    if not order:
        return {"error": f"Order {order_id} not found."}
    
    # Check if order is delayed (e.g. status Shipped, but ordered 5 days ago)
    # Standard shipping takes 3-5 days. If status is Shipped and ordered > 4 days ago, might be delayed.
    is_delayed = False
    if order.status == "Shipped" and (datetime.datetime.utcnow() - order.order_date).days > 4:
        is_delayed = True
        
    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "order_date": order.order_date.isoformat(),
        "total_amount": order.total_amount,
        "status": "Shipped (Delayed)" if is_delayed else order.status,
        "items": order.items,
        "tracking_number": order.tracking_number,
        "shipping_address": order.shipping_address,
        "is_delayed": is_delayed
    }

def issue_refund(db: Session, order_id: str, amount: float, reason: str):
    order = db.query(Order).filter(Order.id == order_id.strip().upper()).first()
    if not order:
        return {"success": False, "error": f"Order {order_id} not found."}
    
    if amount <= 0 or amount > order.total_amount:
        return {"success": False, "error": f"Invalid refund amount: ${amount}. Max refund is ${order.total_amount}."}
    
    # Update order status to refunded / partially refunded
    if amount == order.total_amount:
        order.status = "Refunded"
    else:
        order.status = f"Refunded (${amount})"
        
    db.commit()
    return {
        "success": True,
        "order_id": order.id,
        "refund_amount": amount,
        "new_status": order.status,
        "message": f"Successfully refunded ${amount} to customer's original payment method. Reason: {reason}."
    }

def cancel_subscription(db: Session, subscription_id: str, reason: str):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id.strip().upper()).first()
    if not sub:
        return {"success": False, "error": f"Subscription {subscription_id} not found."}
    
    if sub.status == "Cancelled":
        return {"success": False, "error": f"Subscription {subscription_id} is already cancelled."}
        
    sub.status = "Cancelled"
    sub.next_billing_date = None # No next billing
    db.commit()
    
    return {
        "success": True,
        "subscription_id": sub.id,
        "plan_name": sub.plan_name,
        "new_status": "Cancelled",
        "message": f"Successfully cancelled subscription {sub.plan_name}. Reason: {reason}."
    }

def search_knowledge_base(db: Session, query: str):
    query_str = f"%{query.strip()}%"
    results = db.query(KnowledgeBase).filter(
        (KnowledgeBase.title.ilike(query_str)) |
        (KnowledgeBase.content.ilike(query_str)) |
        (KnowledgeBase.category.ilike(query_str))
    ).all()
    
    if not results:
        return []
        
    return [
        {
            "id": r.id,
            "category": r.category,
            "title": r.title,
            "content": r.content
        } for r in results
    ]
