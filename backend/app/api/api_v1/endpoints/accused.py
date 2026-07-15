# backend/app/api/api_v1/endpoints/accused.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ksp_models import Accused, CaseMaster, ArrestSurrender
from app.schemas.accused import AccusedResponse, AccusedDetailResponse

router = APIRouter()

@router.get("/search", response_model=List[AccusedResponse])
def search_accused(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Search accused by name"),
    gender: Optional[str] = Query(None, description="M, F, T"),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search and filter suspect profiles in KSP records.
    """
    filters = []
    if name:
        filters.append(Accused.AccusedName.ilike(f"%{name}%"))
    if gender:
        filters.append(Accused.GenderID == gender)
    if min_age:
        filters.append(Accused.AgeYear >= min_age)
    if max_age:
        filters.append(Accused.AgeYear <= max_age)
        
    results = db.query(Accused)\
                .filter(and_(*filters))\
                .offset(offset)\
                .limit(limit)\
                .all()
    return results

@router.get("/{accused_id}/history", response_model=List[AccusedDetailResponse])
def get_accused_history(accused_id: int, db: Session = Depends(get_db)):
    """
    Fetch historical cases and arrests associated with a specific accused suspect (supporting repeat offender identification).
    """
    # Find matching suspect record
    base_record = db.query(Accused).filter(Accused.AccusedMasterID == accused_id).first()
    if not base_record:
        raise HTTPException(status_code=404, detail="Accused record not found.")
        
    # Search all occurrences of this name (or same ID if mapped) to display criminal history
    history = db.query(Accused)\
                .filter(Accused.AccusedName.ilike(base_record.AccusedName))\
                .all()
                
    response_data = []
    for record in history:
        # Join case details
        case = db.query(CaseMaster).filter(CaseMaster.CaseMasterID == record.CaseMasterID).first()
        crime_no = None
        registered_date = None
        crime_major_head = None
        
        if case:
            crime_no = case.CrimeNo
            registered_date = str(case.CrimeRegisteredDate)
            if case.major_head:
                crime_major_head = case.major_head.CrimeGroupName
                
        response_data.append(AccusedDetailResponse(
            AccusedMasterID=record.AccusedMasterID,
            CaseMasterID=record.CaseMasterID,
            AccusedName=record.AccusedName,
            AgeYear=record.AgeYear,
            GenderID=record.GenderID,
            PersonID=record.PersonID,
            crime_no=crime_no,
            crime_major_head=crime_major_head,
            registered_date=registered_date
        ))
        
    return response_data
