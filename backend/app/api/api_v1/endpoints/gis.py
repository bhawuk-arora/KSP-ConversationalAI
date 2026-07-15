# backend/app/api/api_v1/endpoints/gis.py
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.user import UserBase
from app.models.ksp_models import CaseMaster

router = APIRouter()

@router.get("/hotspots", response_model=List[Dict[str, Any]])
def get_gis_hotspots(
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user)
):
    """
    Retrieves case coordinates (lat, long) and crime metadata for GIS map rendering.
    Filters out records with missing coordinates.
    """
    results = db.query(
        CaseMaster.CaseMasterID,
        CaseMaster.CrimeNo,
        CaseMaster.latitude,
        CaseMaster.longitude,
        CaseMaster.CrimeRegisteredDate,
        CaseMaster.CrimeMajorHeadID
    ).filter(
        CaseMaster.latitude.isnot(None),
        CaseMaster.longitude.isnot(None)
    ).limit(500).all()
    
    hotspots = []
    for row in results:
        hotspots.append({
            "id": row.CaseMasterID,
            "crime_no": row.CrimeNo,
            "latitude": float(row.latitude),
            "longitude": float(row.longitude),
            "date": str(row.CrimeRegisteredDate),
            "major_head_id": row.CrimeMajorHeadID or 0
        })
        
    return hotspots
