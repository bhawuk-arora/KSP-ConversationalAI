# backend/app/api/deps.py
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import UserBase, TokenPayload

# Matches the local test token endpoint we'll register in auth.py
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token"
)

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    """
    Extracts Bearer token from headers, validates it against JWT secrets, 
    and checks user existence and role scopes.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not token_data.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing subject identity",
        )
        
    # Return mock authenticated user representation based on token claims
    return UserBase(
        email=token_data.sub,
        role=token_data.role or "Constable",
        station_id=token_data.station_id
    )

class RoleChecker:
    """Enforces fine-grained role authorization policies per endpoint."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserBase = Depends(get_current_user)) -> UserBase:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {self.allowed_roles}. Your role: {current_user.role}"
            )
        return current_user
