from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    orders = relationship("Order", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True) # e.g. ORD-1001
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(String, nullable=False) # Shipped, Pending, Processing, Delivered, Returned
    items = Column(JSON, nullable=False) # list of dicts: [{"name": "...", "price": 10.0, "qty": 1}]
    tracking_number = Column(String, nullable=True)
    shipping_address = Column(String, nullable=False)
    
    customer = relationship("Customer", back_populates="orders")

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(String, primary_key=True) # e.g. SUB-2001
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    plan_name = Column(String, nullable=False)
    status = Column(String, nullable=False) # Active, Cancelled
    price = Column(Float, nullable=False)
    next_billing_date = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="subscriptions")

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False) # Refund, Shipping, FAQ
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(String, primary_key=True) # e.g. TKT-3001
    customer_email = Column(String, nullable=False, index=True)
    customer_name = Column(String, nullable=True)
    channel = Column(String, nullable=False) # email, chat, voice
    status = Column(String, default="Open") # Open, Escalated, Resolved
    subject = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.0)
    token_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    messages = relationship("Message", back_populates="ticket", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="ticket", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey('tickets.id'), nullable=False)
    sender = Column(String, nullable=False) # customer, agent, system (for status changes)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="messages")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey('tickets.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    node = Column(String, nullable=False) # LangGraph node name
    input_summary = Column(Text, nullable=False)
    model_used = Column(String, nullable=True)
    tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    confidence = Column(Float, nullable=True)
    action_taken = Column(Text, nullable=True) # e.g. Refund issued / Escalated
    prev_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    
    ticket = relationship("Ticket", back_populates="audit_logs")
