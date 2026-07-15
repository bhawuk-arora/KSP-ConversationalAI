# backend/app/api/api_v1/endpoints/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.schemas.user import Token

router = APIRouter()

# Mock user credentials catalog for testing different KSP clearances
MOCK_USERS = {
    "dgp@ksp.gov.in": {"role": "Supervisor", "station_id": 1, "password": "password123"},
    "io@ksp.gov.in": {"role": "Investigator", "station_id": 1002, "password": "password123"},
    "constable@ksp.gov.in": {"role": "Constable", "station_id": 1002, "password": "password123"},
    "analyst@ksp.gov.in": {"role": "Analyst", "station_id": 2, "password": "password123"}
}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login. Validates credentials and returns a JWT access token.
    For local testing, use one of these logins:
    - dgp@ksp.gov.in | password123
    - io@ksp.gov.in | password123
    - constable@ksp.gov.in | password123
    - analyst@ksp.gov.in | password123
    """
    email = form_data.username.lower().strip()
    password = form_data.password
    
    if email not in MOCK_USERS or MOCK_USERS[email]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_info = MOCK_USERS[email]
    access_token = create_access_token(
        subject=email,
        role=user_info["role"],
        station_id=user_info["station_id"]
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
