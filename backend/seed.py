import sys
import os
import datetime

# Add current folder to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal
from app.models import Customer, Order, Subscription, KnowledgeBase

def seed_data():
    print("Initializing Database tables...")
    init_db()
    
    db = SessionLocal()
    
    # Check if database has already been seeded
    if db.query(Customer).first() is not None:
        print("Database already contains data. Skipping seeding.")
        db.close()
        return

    print("Seeding database...")

    # 1. Customers
    alice = Customer(name="Alice Vance", email="alice.vance@gmail.com", phone="+1-555-0199")
    bob = Customer(name="Bob Miller", email="bob.miller@outlook.com", phone="+1-555-0142")
    charlie = Customer(name="Charlie Green", email="charlie.green@yahoo.com", phone="+1-555-0188")
    
    db.add_all([alice, bob, charlie])
    db.commit() # Commit to generate IDs
    
    # 2. Orders
    now = datetime.datetime.utcnow()
    orders = [
        Order(
            id="ORD-1001",
            customer_id=alice.id,
            order_date=now - datetime.timedelta(days=2),
            total_amount=120.00,
            status="Delivered",
            items=[{"name": "Wireless Noise-Cancelling Headphones", "price": 120.0, "qty": 1}],
            tracking_number="TRK-987654321",
            shipping_address="123 Maple St, Seattle, WA 98101"
        ),
        Order(
            id="ORD-1002",
            customer_id=bob.id,
            order_date=now - datetime.timedelta(days=5),
            total_amount=45.00,
            status="Shipped", # Delayed shipping!
            items=[{"name": "Ergonomic Desk Mouse", "price": 45.0, "qty": 1}],
            tracking_number="TRK-112233445",
            shipping_address="456 Pine Ave, Chicago, IL 60601"
        ),
        Order(
            id="ORD-1003",
            customer_id=bob.id,
            order_date=now - datetime.timedelta(days=30),
            total_amount=299.00,
            status="Delivered",
            items=[
                {"name": "Mechanical Keyboard Pro", "price": 150.0, "qty": 1},
                {"name": "Dual Monitor Stand", "price": 149.0, "qty": 1}
            ],
            tracking_number="TRK-556677889",
            shipping_address="456 Pine Ave, Chicago, IL 60601"
        ),
        Order(
            id="ORD-1004",
            customer_id=charlie.id,
            order_date=now - datetime.timedelta(days=1),
            total_amount=850.00,
            status="Processing",
            items=[{"name": "Smart Office Desk (Height Adjustable)", "price": 850.0, "qty": 1}],
            tracking_number=None,
            shipping_address="789 Oak Rd, Austin, TX 78701"
        )
    ]
    
    db.add_all(orders)
    
    # 3. Subscriptions
    subs = [
        Subscription(
            id="SUB-2001",
            customer_id=alice.id,
            plan_name="Sentinel Cloud Pro (Monthly)",
            status="Active",
            price=29.99,
            next_billing_date=now + datetime.timedelta(days=20)
        ),
        Subscription(
            id="SUB-2002",
            customer_id=charlie.id,
            plan_name="Sentinel Developer Suite (Annual)",
            status="Active",
            price=199.00,
            next_billing_date=now + datetime.timedelta(days=120)
        )
    ]
    db.add_all(subs)
    
    # 4. FAQs / Knowledge Base
    faqs = [
        KnowledgeBase(
            category="Shipping",
            title="How long does shipping take?",
            content="Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days. International shipping varies by destination but typically takes 7-14 business days."
        ),
        KnowledgeBase(
            category="Shipping",
            title="Where is my tracking number?",
            content="Once your order ships, we send a shipping confirmation email containing a tracking number and a link to trace the package. You can also view this in your dashboard under order details."
        ),
        KnowledgeBase(
            category="Refund",
            title="What is your return policy?",
            content="We offer a 30-day return policy for all unused products in their original packaging. Refunds are processed back to the original payment method within 5-7 business days of receiving the returned item. Shipping fees are non-refundable."
        ),
        KnowledgeBase(
            category="Refund",
            title="Can I get a refund on software or subscriptions?",
            content="Subscriptions can be cancelled at any time and will remain active until the end of the billing period. We do not offer partial refunds for unused time. Digital software products are non-refundable once activated."
        ),
        KnowledgeBase(
            category="Account",
            title="How do I cancel my subscription?",
            content="To cancel your subscription, navigate to Billing Settings in your Account Console, click 'Cancel Subscription' next to the active plan, and confirm. Your subscription will remain active until the current billing cycle ends."
        ),
        KnowledgeBase(
            category="Account",
            title="How do I reset my password?",
            content="Click on the 'Forgot Password' link on the login page. Enter your registered email address and we will send you a secure link to reset your password. The link is valid for 24 hours."
        )
    ]
    db.add_all(faqs)
    
    db.commit()
    print("Database successfully seeded!")
    db.close()

if __name__ == "__main__":
    seed_data()
