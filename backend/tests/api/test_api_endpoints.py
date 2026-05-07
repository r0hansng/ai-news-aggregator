import pytest
from fastapi.testclient import TestClient
from backend.cmd.api import app
from backend.infra.database.connection import get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the AI News Aggregator API"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_onboard_user_validation_error():
    # Test onboarding with missing fields to verify Pydantic validation
    response = client.post("/api/v1/users/onboard", json={"name": "Test"})
    assert response.status_code == 422 # Unprocessable Entity
