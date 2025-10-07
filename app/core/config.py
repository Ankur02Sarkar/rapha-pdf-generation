"""
Application Configuration Module

This module contains all configuration settings for the FastAPI application.
It uses Pydantic for settings validation and environment variable management.
Optimized for both local development and AWS Lambda deployment.

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
    Includes AWS Lambda-specific configurations.
    """
    
    # Application settings
    PROJECT_NAME: str = "RaphaCure PDF Generation API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # Default to False for production
    
    # Environment detection
    ENVIRONMENT: str = "development"  # development, staging, production
    IS_LAMBDA: bool = bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    
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
    
    # AWS Lambda specific settings
    LAMBDA_TIMEOUT: int = 30  # seconds
    LAMBDA_MEMORY: int = 1024  # MB
    
    # PDF generation settings
    PDF_MAX_SIZE_MB: int = 10
    PDF_TIMEOUT_SECONDS: int = 30
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Create settings instance
settings = Settings()