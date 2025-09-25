"""
API Response Utilities

This module provides standardized response formatting utilities
for consistent API responses across the application.

Author: Principal Backend Architect
"""

from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Create a standardized success response.
    
    Args:
        data (Any): The response data
        message (str): Success message
        status_code (int): HTTP status code
        meta (Optional[Dict[str, Any]]): Additional metadata
        
    Returns:
        JSONResponse: Standardized success response
    """
    response_content = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if meta:
        response_content["meta"] = meta
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


def error_response(
    message: str = "An error occurred",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        errors (Optional[Dict[str, Any]]): Detailed error information
        error_code (Optional[str]): Application-specific error code
        
    Returns:
        JSONResponse: Standardized error response
    """
    response_content = {
        "success": False,
        "message": message,
        "error": True
    }
    
    if errors:
        response_content["errors"] = errors
    
    if error_code:
        response_content["error_code"] = error_code
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


def paginated_response(
    data: Any,
    total: int,
    page: int = 1,
    per_page: int = 10,
    message: str = "Success"
) -> JSONResponse:
    """
    Create a standardized paginated response.
    
    Args:
        data (Any): The paginated data
        total (int): Total number of items
        page (int): Current page number
        per_page (int): Items per page
        message (str): Success message
        
    Returns:
        JSONResponse: Standardized paginated response
    """
    total_pages = (total + per_page - 1) // per_page
    
    meta = {
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return success_response(
        data=data,
        message=message,
        meta=meta
    )