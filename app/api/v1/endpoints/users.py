"""
User API Endpoints

This module contains all user-related API endpoints including
authentication, user management, and CRUD operations.

Author: Principal Backend Architect
"""

from typing import List
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import User, UserCreate, UserUpdate, UserLogin, Token
from app.services.user_service import UserService
from app.utils.auth import get_current_active_user
from app.utils.responses import success_response, error_response
from app.core.config import settings

router = APIRouter()


@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """
    Register a new user account.
    
    This endpoint creates a new user account with the provided information.
    The password is automatically hashed before storage.
    
    Args:
        user_create (UserCreate): User registration data
        
    Returns:
        dict: Success response with created user data
        
    Raises:
        HTTPException: If email is already registered
    """
    try:
        user = UserService.create_user(user_create)
        return success_response(
            data=user.dict(),
            message="User registered successfully",
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/auth/login", response_model=dict)
async def login_user(user_login: UserLogin):
    """
    Authenticate user and return access token.
    
    This endpoint validates user credentials and returns a JWT token
    for authenticated access to protected endpoints.
    
    Args:
        user_login (UserLogin): User login credentials
        
    Returns:
        dict: Success response with access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = UserService.authenticate_user(user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = UserService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    token_data = Token(access_token=access_token, token_type="bearer")
    
    return success_response(
        data=token_data.dict(),
        message="Login successful"
    )


@router.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token endpoint.
    
    This endpoint provides OAuth2 password flow compatibility
    for authentication using form data.
    
    Args:
        form_data (OAuth2PasswordRequestForm): OAuth2 form data
        
    Returns:
        Token: JWT access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = UserService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = UserService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    This endpoint returns the profile information of the currently
    authenticated user based on the provided JWT token.
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response with user data
    """
    return success_response(
        data=current_user.dict(),
        message="User profile retrieved successfully"
    )


@router.get("/users", response_model=dict)
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    """
    Get all users (protected endpoint).
    
    This endpoint returns a list of all users in the system.
    Requires authentication to access.
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response with list of users
    """
    users = UserService.get_all_users()
    return success_response(
        data=[user.dict() for user in users],
        message=f"Retrieved {len(users)} users successfully"
    )


@router.get("/users/{user_id}", response_model=dict)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by ID.
    
    This endpoint retrieves detailed information about a specific user
    identified by their unique ID.
    
    Args:
        user_id (int): The ID of the user to retrieve
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response with user data
        
    Raises:
        HTTPException: If user is not found
    """
    user = UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return success_response(
        data=user.dict(),
        message="User retrieved successfully"
    )


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a specific user by ID.
    
    This endpoint allows updating user information. Users can only
    update their own profile unless they have admin privileges.
    
    Args:
        user_id (int): The ID of the user to update
        user_update (UserUpdate): Updated user data
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response with updated user data
        
    Raises:
        HTTPException: If user is not found or access is denied
    """
    # Check if user is updating their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    updated_user = UserService.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return success_response(
        data=updated_user.dict(),
        message="User updated successfully"
    )


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific user by ID.
    
    This endpoint allows deleting a user account. Users can only
    delete their own account unless they have admin privileges.
    
    Args:
        user_id (int): The ID of the user to delete
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response confirming deletion
        
    Raises:
        HTTPException: If user is not found or access is denied
    """
    # Check if user is deleting their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    deleted = UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return success_response(
        data={"deleted_user_id": user_id},
        message="User deleted successfully"
    )