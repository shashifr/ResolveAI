import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base
from app.config import settings

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Helper for authentication
headers = {"Authorization": f"Bearer {settings.API_BEARER_TOKEN}"}

def test_get_metrics_empty():
    response = client.get("/api/metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] == 0
    assert data["resolved_count"] == 0

def test_unauthorized_access():
    response = client.get("/api/metrics")
    assert response.status_code == 401

@patch("app.main.run_support_flow")
def test_simulate_email(mock_run_support_flow):
    mock_run_support_flow.return_value = {
        "is_auto_resolved": True,
        "final_reply": "This is a simulated reply",
    }
    
    payload = {
        "sender_email": "test@example.com",
        "sender_name": "Test User",
        "subject": "Help me",
        "body": "I need help with my order."
    }
    
    response = client.post("/api/simulate/email", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ticket_id" in data
    assert data["is_auto_resolved"] is True
    assert data["reply"] == "This is a simulated reply"

@patch("app.main.run_support_flow")
def test_simulate_chat(mock_run_support_flow):
    mock_run_support_flow.return_value = {
        "is_auto_resolved": False,
        "resolution": {
            "reply": "Draft reply",
            "explanation": "Needs human review"
        }
    }
    
    payload = {
        "customer_email": "test2@example.com",
        "message": "Hello chat"
    }
    
    response = client.post("/api/simulate/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ticket_id" in data
    assert data["reply"] == "Draft reply"
