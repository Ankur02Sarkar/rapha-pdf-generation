"""
User Service Module

This module contains business logic for user operations including
authentication, user management, and data validation.

Author: Principal Backend Architect
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.schemas.user import UserCreate, UserUpdate, UserInDB, User
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user storage (replace with database in production)
fake_users_db: Dict[str, Dict[str, Any]] = {}
user_id_counter = 1


class UserService:
    """
    Service class for user-related operations.
    
    This class encapsulates all business logic related to user management,
    authentication, and data operations following the Repository pattern.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password (str): The plain text password to verify
            hashed_password (str): The hashed password to compare against
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Generate a hash for the given password.
        
        Args:
            password (str): The plain text password to hash
            
        Returns:
            str: The hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[UserInDB]:
        """
        Retrieve a user by their email address.
        
        Args:
            email (str): The email address to search for
            
        Returns:
            Optional[UserInDB]: The user if found, None otherwise
        """
        user_data = fake_users_db.get(email)
        if user_data:
            return UserInDB(**user_data)
        return None

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user with email and password.
        
        Args:
            email (str): The user's email address
            password (str): The user's plain text password
            
        Returns:
            Optional[UserInDB]: The authenticated user if credentials are valid, None otherwise
        """
        user = UserService.get_user_by_email(email)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data (dict): The data to encode in the token
            expires_delta (Optional[timedelta]): Custom expiration time
            
        Returns:
            str: The encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_user(user_create: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            user_create (UserCreate): The user creation data
            
        Returns:
            User: The created user (without sensitive data)
            
        Raises:
            HTTPException: If user already exists
        """
        global user_id_counter
        
        # Check if user already exists
        if UserService.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user data
        hashed_password = UserService.get_password_hash(user_create.password)
        now = datetime.utcnow()
        
        user_data = {
            "id": user_id_counter,
            "email": user_create.email,
            "full_name": user_create.full_name,
            "is_active": user_create.is_active,
            "hashed_password": hashed_password,
            "created_at": now,
            "updated_at": now
        }
        
        # Store user (in production, this would be a database operation)
        fake_users_db[user_create.email] = user_data
        user_id_counter += 1
        
        # Return user without sensitive data
        return User(**user_data)

    @staticmethod
    def get_all_users() -> List[User]:
        """
        Retrieve all users from the system.
        
        Returns:
            List[User]: List of all users (without sensitive data)
        """
        users = []
        for user_data in fake_users_db.values():
            users.append(User(**user_data))
        return users

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id (int): The user ID to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        for user_data in fake_users_db.values():
            if user_data["id"] == user_id:
                return User(**user_data)
        return None

    @staticmethod
    def update_user(user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id (int): The ID of the user to update
            user_update (UserUpdate): The update data
            
        Returns:
            Optional[User]: The updated user if found, None otherwise
        """
        # Find user by ID
        user_email = None
        for email, user_data in fake_users_db.items():
            if user_data["id"] == user_id:
                user_email = email
                break
        
        if not user_email:
            return None
        
        # Update user data
        user_data = fake_users_db[user_email]
        update_data = user_update.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = UserService.get_password_hash(update_data.pop("password"))
        
        update_data["updated_at"] = datetime.utcnow()
        user_data.update(update_data)
        
        return User(**user_data)

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id (int): The ID of the user to delete
            
        Returns:
            bool: True if user was deleted, False if not found
        """
        # Find and delete user by ID
        for email, user_data in list(fake_users_db.items()):
            if user_data["id"] == user_id:
                del fake_users_db[email]
                return True
        return False