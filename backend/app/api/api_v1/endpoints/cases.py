# backend/app/api/api_v1/endpoints/cases.py
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ksp_models import CaseMaster, Employee, ArrestSurrender, ChargesheetDetails, Section, ActSectionAssociation
from app.schemas.case import CaseMasterResponse, CaseMasterDetailResponse, CaseTimelineEvent

router = APIRouter()

@router.get("/search", response_model=List[CaseMasterResponse])
def search_cases(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search facts or case numbers"),
    district_id: Optional[int] = Query(None),
    station_id: Optional[int] = Query(None),
    status_id: Optional[int] = Query(None),
    major_head_id: Optional[int] = Query(None),
    minor_head_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search KSP cases using relational filters, registered date ranges, and keyword matches.
    """
    filters = []
    
    # Text Search matches fact narrative or case number
    if query:
        filters.append(or_(
            CaseMaster.BriefFacts.ilike(f"%{query}%"),
            CaseMaster.CrimeNo.ilike(f"%{query}%"),
            CaseMaster.CaseNo.ilike(f"%{query}%")
        ))
        
    if district_id:
        # Resolve station district mapping
        filters.append(CaseMaster.station.has(DistrictID=district_id))
    if station_id:
        filters.append(CaseMaster.PoliceStationID == station_id)
    if status_id:
        filters.append(CaseMaster.CaseStatusID == status_id)
    if major_head_id:
        filters.append(CaseMaster.CrimeMajorHeadID == major_head_id)
    if minor_head_id:
        filters.append(CaseMaster.CrimeMinorHeadID == minor_head_id)
    if start_date:
        filters.append(CaseMaster.CrimeRegisteredDate >= start_date)
    if end_date:
        filters.append(CaseMaster.CrimeRegisteredDate <= end_date)
        
    # Execute query
    results = db.query(CaseMaster)\
                .filter(and_(*filters))\
                .order_by(CaseMaster.CrimeRegisteredDate.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
                
    return results

@router.get("/{case_id}", response_model=CaseMasterDetailResponse)
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full details of a specific case including complainants, victims, accused, and acts/sections.
    """
    case = db.query(CaseMaster).filter(CaseMaster.CaseMasterID == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case file not found.")
    return case

@router.get("/{case_id}/timeline", response_model=List[CaseTimelineEvent])
def get_case_timeline(case_id: int, db: Session = Depends(get_db)):
    """
    Build a chronological timeline of events for a case file (Registration -> Arrests -> Chargesheets).
    """
    case = db.query(CaseMaster).filter(CaseMaster.CaseMasterID == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case file not found.")
        
    timeline = []
    
    # 1. Registration Event
    officer_name = None
    if case.PolicePersonID:
        officer = db.query(Employee).filter(Employee.EmployeeID == case.PolicePersonID).first()
        if officer:
            officer_name = f"{officer.FirstName} (KGID: {officer.KGID})"
            
    timeline.append(CaseTimelineEvent(
        event_name="FIR Registered",
        event_date=case.CrimeRegisteredDate,
        description=f"FIR registered under Category {case.CaseCategoryID} at station ID {case.PoliceStationID}.",
        icon_type="registration",
        officer_name=officer_name
    ))
    
    # 2. Arrest Events
    arrests = db.query(ArrestSurrender).filter(ArrestSurrender.CaseMasterID == case_id).all()
    for arrest in arrests:
        io_name = None
        if arrest.IOID:
            io = db.query(Employee).filter(Employee.EmployeeID == arrest.IOID).first()
            if io:
                io_name = f"{io.FirstName} (KGID: {io.KGID})"
                
        accused_name = "Suspect"
        if arrest.accused:
            accused_name = arrest.accused.AccusedName
            
        timeline.append(CaseTimelineEvent(
            event_name="Accused Arrested / Surrendered",
            event_date=arrest.ArrestSurrenderDate,
            description=f"Suspect {accused_name} apprehended (Type ID: {arrest.ArrestSurrenderTypeID}). Produced before Court ID {arrest.CourtID}.",
            icon_type="arrest",
            officer_name=io_name
        ))
        
    # 3. Chargesheet Event
    chargesheets = db.query(ChargesheetDetails).filter(ChargesheetDetails.CaseMasterID == case_id).all()
    for cs in chargesheets:
        cs_officer = None
        if cs.PolicePersonID:
            cso = db.query(Employee).filter(Employee.EmployeeID == cs.PolicePersonID).first()
            if cso:
                cs_officer = f"{cso.FirstName} (KGID: {cso.KGID})"
                
        type_desc = {"A": "Chargesheet Submitted", "B": "False Case Filed", "C": "Undetected Case Closed"}.get(cs.cstype, "Report Filed")
        
        timeline.append(CaseTimelineEvent(
            event_name="Final Report Submitted",
            event_date=cs.csdate.date(),
            description=f"Final investigation report submitted to court (Type: {cs.cstype} - {type_desc}).",
            icon_type="chargesheet",
            officer_name=cs_officer
        ))
        
    # Sort events by date ascending
    timeline.sort(key=lambda x: x.event_date)
    return timeline

@router.get("/{case_id}/similar", response_model=List[CaseMasterResponse])
def get_similar_cases(case_id: int, db: Session = Depends(get_db), limit: int = 5):
    """
    Find solved/similar cases based on overlapping legal sections and major/minor crime heads.
    """
    case = db.query(CaseMaster).filter(CaseMaster.CaseMasterID == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case file not found.")
        
    # Find sections associated with current case
    section_queries = db.query(ActSectionAssociation.ActID, ActSectionAssociation.SectionID)\
                        .filter(ActSectionAssociation.CaseMasterID == case_id)\
                        .all()
                        
    similar_case_ids = set()
    
    # Match by sections
    if section_queries:
        for act_id, sec_id in section_queries:
            matches = db.query(ActSectionAssociation.CaseMasterID)\
                        .filter(
                            and_(
                                ActSectionAssociation.ActID == act_id,
                                ActSectionAssociation.SectionID == sec_id,
                                ActSectionAssociation.CaseMasterID != case_id
                            )
                        )\
                        .limit(limit * 2)\
                        .all()
            for m in matches:
                similar_case_ids.add(m[0])
                
    # If not enough matches, fallback to matching minor/major head
    if len(similar_case_ids) < limit:
        matches = db.query(CaseMaster.CaseMasterID)\
                    .filter(
                        and_(
                            CaseMaster.CrimeMinorHeadID == case.CrimeMinorHeadID,
                            CaseMaster.CaseMasterID != case_id
                        )
                    )\
                    .limit(limit * 2)\
                    .all()
        for m in matches:
            similar_case_ids.add(m[0])
            
    if not similar_case_ids:
        return []
        
    # Fetch case records
    similar_cases = db.query(CaseMaster)\
                      .filter(CaseMaster.CaseMasterID.in_(list(similar_case_ids)))\
                      .limit(limit)\
                      .all()
                      
    return similar_cases
