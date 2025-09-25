"""
Application Configuration Module

This module contains all configuration settings for the FastAPI application.
It uses Pydantic for settings validation and environment variable management.

Author: Principal Backend Architect
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Application settings configuration class.
    
    This class defines all configuration parameters for the application,
    with support for environment variable overrides and validation.
    """
    
    # Application settings
    PROJECT_NAME: str = "RaphaCure PDF Generation API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database settings (for future use)
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Create settings instance
settings = Settings()