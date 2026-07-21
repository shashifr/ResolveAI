import unittest
import unittest.mock
import os
import sys
import hashlib
import uuid

# Add the current folder to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal, engine
from app.models import Base, Customer, Order, Subscription, KnowledgeBase, KBChunk, Ticket, Message, AuditLog
from app.llm import ModelRouter, classify_intent_simulated, generate_resolution_simulated
from app.tools import get_customer_by_email, get_order_status, issue_refund, cancel_subscription
from app.graph import run_support_flow, ACTION_THRESHOLDS

class TestAISupportAgent(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize test database tables
        init_db()
        
    def setUp(self):
        # Create a new session for each test
        self.db = SessionLocal()
        # Clean up database tables for isolation
        self.db.query(AuditLog).delete()
        self.db.query(Message).delete()
        self.db.query(Ticket).delete()
        self.db.query(Order).delete()
        self.db.query(Subscription).delete()
        self.db.query(KBChunk).delete()
        self.db.query(KnowledgeBase).delete()
        self.db.query(Customer).delete()
        self.db.commit()
        
        # Setup mock customer, order, and subscription
        self.customer = Customer(name="John Doe", email="john.doe@example.com", phone="+1-555-0100")
        self.db.add(self.customer)
        self.db.commit()
        
        self.order = Order(
            id="ORD-9999",
            customer_id=self.customer.id,
            total_amount=80.00,
            status="Delivered",
            items=[{"name": "USB-C Hub", "price": 80.0, "qty": 1}],
            tracking_number="TRK-999999",
            shipping_address="100 Main St, New York, NY 10001"
        )
        
        self.subscription = Subscription(
            id="SUB-9999",
            customer_id=self.customer.id,
            plan_name="Cloud Storage Basic",
            status="Active",
            price=9.99
        )
        
        # Seed FAQ / Knowledge Base
        self.faq = KnowledgeBase(
            category="Shipping",
            title="How long does shipping take?",
            content="Standard shipping takes 3-5 business days."
        )
        
        self.db.add_all([self.order, self.subscription, self.faq])
        self.db.commit()

        self.faq_chunk = KBChunk(
            kb_id=self.faq.id,
            chunk_index=0,
            content="Standard shipping takes 3-5 business days.",
            embedding=[0.1] * 768
        )
        self.db.add(self.faq_chunk)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_customer_retrieval(self):
        cust = get_customer_by_email(self.db, "john.doe@example.com")
        self.assertIsNotNone(cust)
        self.assertEqual(cust.name, "John Doe")

    def test_order_status_tool(self):
        status_info = get_order_status(self.db, "ORD-9999")
        self.assertIn("status", status_info)
        self.assertEqual(status_info["status"], "Delivered")
        self.assertFalse(status_info["is_delayed"])

    def test_issue_refund_tool(self):
        # Test partial refund
        refund_res = issue_refund(self.db, "ORD-9999", 40.0, "Customer dissatisfaction")
        self.assertTrue(refund_res["success"])
        self.assertEqual(refund_res["new_status"], "Refunded ($40.0)")
        
        # Test full refund
        refund_res_full = issue_refund(self.db, "ORD-9999", 80.0, "Return request")
        self.assertTrue(refund_res_full["success"])
        self.assertEqual(refund_res_full["new_status"], "Refunded")

    def test_cancel_subscription_tool(self):
        cancel_res = cancel_subscription(self.db, "SUB-9999", "Too expensive")
        self.assertTrue(cancel_res["success"])
        self.assertEqual(cancel_res["new_status"], "Cancelled")

    def test_intent_classification(self):
        # Test refund intent classification
        res = classify_intent_simulated("I want a refund for ORD-9999 of $120")
        self.assertEqual(res["intent"], "refund_request")
        self.assertEqual(res["extracted_entities"]["order_id"], "ORD-9999")
        self.assertEqual(res["extracted_entities"]["refund_amount"], 120.0)
        self.assertIn("high_refund_value", res["risk_flags"]) # Since refund > $100 ($120)

        # Test angry language detection
        res_angry = classify_intent_simulated("This is unacceptable service, I want my money back!")
        self.assertIn("angry_language", res_angry["risk_flags"])

    def test_resolution_drafting(self):
        context = {
            "customer": {"name": "John Doe", "email": "john.doe@example.com"},
            "orders": [{"id": "ORD-9999", "status": "Delivered", "total_amount": 80.0, "items": [{"qty": 1, "name": "USB-C Hub"}]}],
            "subscriptions": [],
            "kb_articles": []
        }
        res = generate_resolution_simulated(
            message_text="I want a refund for ORD-9999 of $80",
            intent="refund_request",
            entities={"order_id": "ORD-9999", "refund_amount": 80.0},
            risk_flags=["high_refund_value"],
            context=context
        )
        self.assertIn("refund of $80.0", res["reply"].lower())
        self.assertLess(res["confidence"], 0.85) # High value refund should lower confidence to escalate
        self.assertEqual(len(res["proposed_actions"]), 1)
        self.assertEqual(res["proposed_actions"][0]["action"], "issue_refund")

    def test_cryptographic_audit_ledger(self):
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        ticket = Ticket(
            id=ticket_id,
            customer_email="john.doe@example.com",
            channel="email",
            status="Open"
        )
        self.db.add(ticket)
        self.db.commit()

        # Create block 1
        log1 = AuditLog(
            ticket_id=ticket_id,
            node="intake",
            input_summary="Inbound query logged",
            model_used="System",
            tokens=0,
            cost=0.0,
            confidence=1.0,
            action_taken="Registered thread",
            prev_hash="0" * 64,
            hash=hashlib.sha256(b"block1").hexdigest()
        )
        self.db.add(log1)
        self.db.commit()

        # Create block 2 chained to block 1
        log2 = AuditLog(
            ticket_id=ticket_id,
            node="classifier",
            input_summary="Classification step",
            model_used="Gemini",
            tokens=100,
            cost=0.00015,
            confidence=0.95,
            action_taken="Classified refund",
            prev_hash=log1.hash,
            hash=hashlib.sha256(f"{log1.hash}|classifier".encode()).hexdigest()
        )
        self.db.add(log2)
        self.db.commit()

        # Validate chain links
        logs = self.db.query(AuditLog).filter(AuditLog.ticket_id == ticket_id).order_by(AuditLog.id.asc()).all()
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[1].prev_hash, logs[0].hash)

    def test_full_support_flow_faq(self):
        ticket_id = f"TKT-FAQ-{uuid.uuid4().hex[:4].upper()}"
        result = run_support_flow(
            ticket_id=ticket_id,
            message_text="How long does shipping take?",
            customer_email="john.doe@example.com",
            channel="email"
        )
        self.assertTrue(result["is_auto_resolved"])
        self.assertIn("Standard shipping takes 3-5 business days.", result["final_reply"])

    def test_full_support_flow_refund_escalated(self):
        ticket_id = f"TKT-REFUND-{uuid.uuid4().hex[:4].upper()}"
        result = run_support_flow(
            ticket_id=ticket_id,
            message_text="I want a refund for my order ORD-9999 of $120.00",
            customer_email="john.doe@example.com",
            channel="email"
        )
        self.assertFalse(result["is_auto_resolved"])

    @unittest.mock.patch('requests.post')
    def test_real_llm_api_call(self, mock_post):
        # Mock successful Gemini API response for intent classification
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"intent": "order_status", "confidence": 0.95, "extracted_entities": {"order_id": "ORD-9999"}, "risk_flags": []}'
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Enable real LLM execution for this test
        router = ModelRouter()
        router.api_key = "MOCK_KEY"
        router.use_real_llm = True

        res = router.classify_intent("Where is my order ORD-9999?")
        self.assertEqual(res["result"].intent, "order_status")
        self.assertEqual(res["result"].confidence, 0.95)

if __name__ == "__main__":
    unittest.main()
