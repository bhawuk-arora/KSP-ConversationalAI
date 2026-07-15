# backend/tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify that the health check endpoint returns 200 and correct status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "project" in response.json()

def test_openapi_docs_exist():
    """Verify that the OpenAPI JSON schema loads successfully."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "info" in response.json()
    assert response.json()["info"]["title"] == "KSP Crime Intelligence Platform"
