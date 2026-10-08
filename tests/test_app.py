import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.database.models import EmailAnalysis

from sqlalchemy.pool import StaticPool

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Email Assistant" in response.content

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_email_validation():
    # Empty subject
    response = client.post("/api/analyze", json={"subject": "", "content": "Test body"})
    assert response.status_code == 400
    
    # Very long input
    response = client.post("/api/analyze", json={"subject": "Test", "content": "A" * 15000})
    assert response.status_code == 400

def test_classification_demo_mode():
    # Because API key is empty, this should use demo mode
    response = client.post("/api/analyze", json={"subject": "Urgent meeting", "content": "Please join the meeting ASAP."})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Important"
    assert data["is_demo"] == True
    assert "id" in data

def test_history_retrieval_and_deletion():
    # Retrieve
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    
    record_id = data[0]["id"]
    
    # Delete
    del_res = client.delete(f"/api/history/{record_id}")
    assert del_res.status_code == 200
    
    # Verify deletion
    response2 = client.get("/api/history")
    data2 = response2.json()
    assert len(data2) == len(data) - 1

def test_history_delete_not_found():
    res = client.delete("/api/history/999999")
    assert res.status_code == 404
