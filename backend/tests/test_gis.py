# backend/tests/test_gis.py
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.pop(get_db, None)

def test_get_gis_hotspots_unauthenticated(mock_db):
    """Verify that fetching GIS hotspot data requires Bearer JWT authentication."""
    response = client.get("/api/v1/gis/hotspots")
    assert response.status_code == 401

def test_get_gis_hotspots_success(mock_db):
    """Verify that fetching GIS hotspot data succeeds and returns float coordinates list."""
    # Mock database query results
    mock_case_row = MagicMock()
    mock_case_row.CaseMasterID = 1
    mock_case_row.CrimeNo = "KSP/2026/00102"
    mock_case_row.latitude = 12.9631
    mock_case_row.longitude = 77.5724
    mock_case_row.CrimeRegisteredDate = "2026-05-20"
    mock_case_row.CrimeMajorHeadID = 2
    
    # Configure query chain mockup
    mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [mock_case_row]

    # 1. Get login token
    login_resp = client.post(
        "/api/v1/auth/token",
        data={"username": "io@ksp.gov.in", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Query hotspots
    response = client.get("/api/v1/gis/hotspots", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["crime_no"] == "KSP/2026/00102"
    assert data[0]["latitude"] == 12.9631
    assert data[0]["longitude"] == 77.5724
