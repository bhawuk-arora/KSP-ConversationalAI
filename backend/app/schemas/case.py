# backend/app/schemas/case.py
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional

# Helper schemas for nested detailed representations
class ComplainantSchema(BaseModel):
    ComplainantID: int
    ComplainantName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class VictimSchema(BaseModel):
    VictimMasterID: int
    VictimName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[int] = None
    VictimPolice: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AccusedSchema(BaseModel):
    AccusedMasterID: int
    AccusedName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[str] = None
    PersonID: str
    model_config = ConfigDict(from_attributes=True)

class ActSectionSchema(BaseModel):
    ActID: str
    SectionID: str
    ActOrderID: Optional[int] = None
    SectionOrderID: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

# Main CaseMaster schemas
class CaseMasterBase(BaseModel):
    CaseMasterID: int
    CrimeNo: str
    CaseNo: str
    CrimeRegisteredDate: date
    PolicePersonID: Optional[int] = None
    PoliceStationID: Optional[int] = None
    CaseCategoryID: Optional[int] = None
    GravityOffenceID: Optional[int] = None
    CrimeMajorHeadID: Optional[int] = None
    CrimeMinorHeadID: Optional[int] = None
    CaseStatusID: Optional[int] = None
    CourtID: Optional[int] = None
    IncidentFromDate: Optional[datetime] = None
    IncidentToDate: Optional[datetime] = None
    InfoReceivedPSDate: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    BriefFacts: Optional[str] = None

class CaseMasterCreate(CaseMasterBase):
    pass

class CaseMasterResponse(BaseModel):
    CaseMasterID: int
    CrimeNo: str
    CaseNo: str
    CrimeRegisteredDate: date
    PoliceStationID: Optional[int] = None
    CaseStatusID: Optional[int] = None
    CrimeMajorHeadID: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    BriefFacts: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class CaseMasterDetailResponse(CaseMasterBase):
    complainants: List[ComplainantSchema] = []
    victims: List[VictimSchema] = []
    accused_persons: List[AccusedSchema] = []
    act_section_assocs: List[ActSectionSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

class CaseTimelineEvent(BaseModel):
    event_name: str
    event_date: date
    description: str
    icon_type: str  # e.g., 'registration', 'arrest', 'chargesheet'
    officer_name: Optional[str] = None
