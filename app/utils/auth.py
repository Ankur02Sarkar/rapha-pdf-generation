"""
Authentication Utilities

This module contains utility functions for JWT token handling,
user authentication, and security-related operations.

Author: Principal Backend Architect
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.schemas.user import TokenData, UserInDB
from app.services.user_service import UserService

# Security scheme for JWT token extraction
security = HTTPBearer()


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        TokenData: The decoded token data
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    return token_data


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials
        
    Returns:
        UserInDB: The current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = UserService.get_user_by_email(email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Get the current authenticated and active user.
    
    Args:
        current_user (UserInDB): The current user from token
        
    Returns:
        UserInDB: The current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user