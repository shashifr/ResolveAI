import urllib.request
import json
import time

API_BASE = "http://localhost:8000/api"

def send_post(endpoint, data):
    req = urllib.request.Request(
        f"{API_BASE}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer resolveai-demo-token"
        },
        method="POST"
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def send_get(endpoint):
    req = urllib.request.Request(
        f"{API_BASE}{endpoint}",
        headers={"Authorization": "Bearer resolveai-demo-token"}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode("utf-8"))

def run_tests():
    print("=== AI Customer Support API Integration Verification ===")
    
    # 1. Test FAQ (Should Auto-Resolve)
    print("\n[Test 1] Simulating Inbound FAQ Email...")
    faq_payload = {
        "sender_email": "alice.vance@gmail.com",
        "sender_name": "Alice Vance",
        "subject": "Return Policy Inquiry",
        "body": "Hi, can you tell me what your return policy is? How long do I have to return my items?"
    }
    faq_res = send_post("/simulate/email", faq_payload)
    print(f"Result: Ticket {faq_res['ticket_id']} created.")
    print(f"  Confidence Score: {faq_res['confidence_score']:.2f}")
    print(f"  Is Auto-Resolved: {faq_res['is_auto_resolved']}")
    print(f"  Status: {faq_res['status']}")
    print(f"  Reply Sent: {faq_res['reply'][:100]}...")
    assert faq_res["is_auto_resolved"] is True
    assert faq_res["status"] == "Resolved"
    
    # 2. Test High-Value Refund (Should Escalate)
    print("\n[Test 2] Simulating Inbound High-Value Refund Email...")
    refund_payload = {
        "sender_email": "alice.vance@gmail.com",
        "sender_name": "Alice Vance",
        "subject": "Refund Request for Order #1001",
        "body": "Hi, I received my headphones ORD-1001 but they are broken. I would like a full refund of $120."
    }
    refund_res = send_post("/simulate/email", refund_payload)
    tkt_id = refund_res["ticket_id"]
    print(f"Result: Ticket {tkt_id} created.")
    print(f"  Confidence Score: {refund_res['confidence_score']:.2f}")
    print(f"  Is Auto-Resolved: {refund_res['is_auto_resolved']}")
    print(f"  Status: {refund_res['status']}")
    assert refund_res["is_auto_resolved"] is False
    assert refund_res["status"] == "Escalated"
    
    # Check details of escalated ticket
    print(f"\n[Test 2.1] Fetching ticket details for {tkt_id}...")
    details = send_get(f"/tickets/{tkt_id}")
    print(f"  Proposed Actions: {details['drafted_actions']}")
    print(f"  Explanation: {details['explanation']}")
    print(f"  Audit Nodes Chained: {[log['node'] for log in details['audit_logs']]}")
    
    # Check cryptographic chain validation
    print("\n[Test 2.2] Checking Cryptographic Hash Chain integrity...")
    logs = details["audit_logs"]
    for i in range(1, len(logs)):
        assert logs[i]["prev_hash"] == logs[i-1]["hash"]
        print(f"  Block {i} linked: {logs[i-1]['hash'][:10]}... -> {logs[i]['hash'][:10]}... (VERIFIED)")
    print("  Cryptographic trace ledger is intact and valid!")
    
    # 3. Test Human Console Approval
    print(f"\n[Test 3] Simulating Human Console approval of ticket {tkt_id}...")
    action_payload = {
        "action": "approve"
    }
    action_res = send_post(f"/tickets/{tkt_id}/action", action_payload)
    print(f"Result: {action_res['success']}")
    print(f"  New Status: {action_res['new_status']}")
    print(f"  Action Taken: {action_res['action_taken']}")
    
    # Verify ticket is now resolved and contains final messages
    details_after = send_get(f"/tickets/{tkt_id}")
    print(f"  Details after action status: {details_after['status']}")
    print(f"  Latest Audit Node: {details_after['audit_logs'][-1]['node']}")
    print(f"  Latest Hash: {details_after['audit_logs'][-1]['hash'][:16]}...")
    assert details_after["status"] == "Resolved"
    assert details_after["audit_logs"][-1]["node"] == "human_console"
    
    # 4. Test Dashboard Metrics
    print("\n[Test 4] Fetching global dashboard metrics...")
    metrics = send_get("/metrics")
    print(f"Metrics:")
    print(f"  Total Tickets: {metrics['total_tickets']}")
    print(f"  Resolved Count: {metrics['resolved_count']}")
    print(f"  Autonomous Count: {metrics['autonomous_count']}")
    print(f"  Autonomy Rate: {metrics['autonomy_rate']}%")
    print(f"  Total Actual Cost: ${metrics['total_actual_cost']:.5f}")
    print(f"  Baseline Opus Cost: ${metrics['baseline_cost']:.5f}")
    print(f"  Total Cost Saved: ${metrics['savings']:.5f}")
    
    print("\n=== All Tests Passed Successfully! ===")

if __name__ == "__main__":
    run_tests()
