# backend/app/core/database.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# Create engine with connection pooling enabled
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,       # Verifies connections before executing queries
    pool_size=10,             # Keep up to 10 active connections in pool
    max_overflow=20           # Allow temporary overflow up to 20 connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """Dependency injection helper supplying local database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
