# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: str
    role: str  # Constable, Investigator, Analyst, Supervisor, Admin
    station_id: Optional[int] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None  # user email
    role: Optional[str] = None
    station_id: Optional[int] = None
