# backend/app/schemas/accused.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class AccusedBase(BaseModel):
    AccusedMasterID: int
    CaseMasterID: int
    AccusedName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[str] = None
    PersonID: str

class AccusedCreate(AccusedBase):
    pass

class AccusedResponse(AccusedBase):
    model_config = ConfigDict(from_attributes=True)

class AccusedDetailResponse(AccusedBase):
    crime_no: Optional[str] = None
    crime_major_head: Optional[str] = None
    registered_date: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
