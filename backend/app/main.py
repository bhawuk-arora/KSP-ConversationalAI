# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade Crime Intelligence APIs for Karnataka State Police.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS for Next.js frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to Zoho Catalyst domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["system"])
def health_check():
    """Simple connection health indicator for Catalyst routing checks."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
