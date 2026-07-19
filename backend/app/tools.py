import os
from sqlalchemy.orm import Session
from app.models import Customer, Order, Subscription, KnowledgeBase, KBChunk
from app.utils.embeddings import get_embedding, cosine_similarity
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

def search_knowledge_base(db: Session, query: str, limit: int = 3, similarity_threshold: float = 0.35):
    """
    Searches the Knowledge Base chunks using semantic vector embeddings and cosine similarity.
    Falls back to text keyword matching if no semantic matches exceed the threshold (especially useful in sandbox mode).
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    query_vector = get_embedding(query, api_key=api_key)
    
    # Retrieve all chunks
    all_chunks = db.query(KBChunk).all()
    
    # Calculate similarity score for each chunk
    scored_chunks = []
    for chunk in all_chunks:
        if chunk.embedding:
            score = cosine_similarity(query_vector, chunk.embedding)
            if score >= similarity_threshold:
                scored_chunks.append((score, chunk))
                
    # Sort by similarity score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:limit]
    
    # Fallback to keyword matching if no semantic matches found (e.g. in sandbox mode or no matches exceed threshold)
    if not top_chunks:
        # Search by individual keywords
        keywords = [word for word in query.lower().split() if len(word) > 3]
        if not keywords:
            keywords = [query.strip().lower()]
            
        fallback_scored_chunks = []
        all_db_chunks = db.query(KBChunk).all()
        for chunk in all_db_chunks:
            score = 0.0
            title_lower = chunk.kb_article.title.lower()
            content_lower = chunk.content.lower()
            category_lower = chunk.kb_article.category.lower()
            
            for kw in keywords:
                if kw in title_lower:
                    score += 2.0
                if kw in category_lower:
                    score += 1.5
                if kw in content_lower:
                    score += 1.0
                    
            if score > 0:
                # Map score to a pseudo-similarity score in the range [0.5, 0.99]
                sim_score = 0.5 + min(0.49, score / 10.0)
                fallback_scored_chunks.append((sim_score, chunk))
                
        fallback_scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = fallback_scored_chunks[:limit]
        
    return [
        {
            "id": r[1].kb_article.id,
            "category": r[1].kb_article.category,
            "title": r[1].kb_article.title,
            "content": r[1].content,
            "similarity_score": r[0]
        } for r in top_chunks
    ]
