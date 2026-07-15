# backend/tests/test_network.py
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.ksp_models import Accused, CaseMaster

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.pop(get_db, None)

def test_trace_suspect_network_unauthenticated(mock_db):
    """Verify that tracing suspect relationship networks requires JWT auth."""
    response = client.get("/api/v1/network/suspect/1001")
    assert response.status_code == 401

def test_trace_suspect_network_success(mock_db):
    """Verify that tracing suspect relationship networks succeeds and returns nodes and edges list structure."""
    # 1. Mock DB returns a target Accused and a CaseMaster link
    # Using correct SQLAlchemy properties (AccusedMasterID, AccusedName)
    mock_accused = Accused(AccusedMasterID=1001, AccusedName="Ravi alias Kariya", CaseMasterID=505)
    mock_case = CaseMaster(CaseMasterID=505, CrimeNo="123", CrimeMajorHeadID=2)
    
    # Configure mock query chain response
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_accused, None]
    mock_db.query.return_value.join.return_value.filter.return_value.limit.return_value.all.return_value = [mock_case]
    mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

    # 2. Get login token
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "io@ksp.gov.in", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Call endpoint
    response = client.get("/api/v1/network/suspect/1001", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    
    # Should have target suspect node and case node
    nodes = data["nodes"]
    assert len(nodes) > 0
    assert any(n["type"] == "accused" for n in nodes)
