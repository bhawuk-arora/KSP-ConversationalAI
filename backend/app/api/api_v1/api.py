# backend/app/api/api_v1/api.py
from fastapi import APIRouter

from app.api.api_v1.endpoints import cases, accused, auth

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(accused.router, prefix="/accused", tags=["accused"])
