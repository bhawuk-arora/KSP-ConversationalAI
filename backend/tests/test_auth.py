# backend/tests/test_auth.py
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db

client = TestClient(app)

# Create a mock database session to isolate tests from running PostgreSQL instances
mock_db = MagicMock()
# Mock the query chain: db.query().filter().first() returns None (triggering a 404 instead of connection failure)
mock_db.query.return_value.filter.return_value.first.return_value = None

def override_get_db():
    try:
        yield mock_db
    finally:
        pass

# Override get_db dependency globally for tests
app.dependency_overrides[get_db] = override_get_db

def test_login_success():
    """Verify that a valid user can successfully obtain a JWT token."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "io@ksp.gov.in", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_incorrect_password():
    """Verify that login fails with incorrect credentials."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "io@ksp.gov.in", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_unauthenticated_access_denied():
    """Verify that access is blocked without a JWT token."""
    response = client.get("/api/v1/cases/search")
    assert response.status_code == 401

def test_rbac_constable_denied_case_detail():
    """Verify that a Constable token is blocked from accessing case details (requires Investigator+)."""
    # 1. Login as constable
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "constable@ksp.gov.in", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    # 2. Try to access case detail
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/cases/101", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_rbac_investigator_allowed_case_detail():
    """Verify that an Investigator token is permitted to access case details (receiving a mocked 404)."""
    # 1. Login as investigator
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "io@ksp.gov.in", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    # 2. Access case detail (should bypass RoleChecker and return 404 from our mock_db)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/cases/101", headers=headers)
    assert response.status_code == 404
