# backend/app/schemas/victim.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class VictimBase(BaseModel):
    VictimMasterID: int
    CaseMasterID: int
    VictimName: str
    AgeYear: Optional[int] = None
    GenderID: Optional[int] = None
    VictimPolice: Optional[str] = None

class VictimCreate(VictimBase):
    pass

class VictimResponse(VictimBase):
    model_config = ConfigDict(from_attributes=True)
