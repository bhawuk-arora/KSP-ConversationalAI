# backend/app/core/config.py
from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KSP Crime Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "ksp_db"
    
    # JWT & Auth Settings (for later phases)
    JWT_SECRET_KEY: str = "ksp_jwt_secret_key_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
