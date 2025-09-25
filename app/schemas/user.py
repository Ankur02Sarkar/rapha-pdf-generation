"""
User Pydantic Schemas

This module contains Pydantic models for user data validation,
serialization, and API request/response handling.

Author: Principal Backend Architect
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    
    This schema contains fields that are shared across
    different user-related operations.
    """
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(True, description="Whether the user account is active")


class UserCreate(UserBase):
    """
    Schema for user creation requests.
    
    This schema is used when creating a new user account
    and includes the password field for registration.
    """
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")


class UserUpdate(BaseModel):
    """
    Schema for user update requests.
    
    This schema allows partial updates to user information.
    All fields are optional to support PATCH operations.
    """
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, description="Updated full name")
    is_active: Optional[bool] = Field(None, description="Updated active status")
    password: Optional[str] = Field(None, min_length=8, description="Updated password")


class UserInDB(UserBase):
    """
    Schema representing a user as stored in the database.
    
    This schema includes all fields that are stored in the database,
    including the hashed password and metadata.
    """
    id: int = Field(..., description="Unique user identifier")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """
    Schema for user responses (public view).
    
    This schema is used for API responses and excludes
    sensitive information like passwords.
    """
    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login requests.
    
    This schema validates login credentials submitted
    through the authentication endpoint.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class Token(BaseModel):
    """
    Schema for JWT token responses.
    
    This schema is used when returning authentication
    tokens to the client.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class TokenData(BaseModel):
    """
    Schema for token payload data.
    
    This schema represents the data contained within
    a JWT token for validation purposes.
    """
    email: Optional[str] = Field(None, description="User email from token")