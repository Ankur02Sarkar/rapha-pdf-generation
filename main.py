"""
FastAPI Application Entry Point

This module serves as the main entry point for the FastAPI application.
It configures global middleware, CORS settings, and imports all API routers.

Author: Principal Backend Architect
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.core.config import settings
from app.api.v1.endpoints import pdf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A production-grade FastAPI application with modular architecture",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """
        Add processing time header to all responses.
        
        Args:
            request (Request): The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The response with added timing header
        """
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Global HTTP exception handler.
        
        Args:
            request (Request): The request that caused the exception
            exc (HTTPException): The HTTP exception that was raised
            
        Returns:
            JSONResponse: Standardized error response
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url)
            }
        )

    # Include API routers
    app.include_router(
        pdf.router,
        prefix="/api/v1"
    )

    # Health check endpoint
    # @app.get("/health")
    # async def health_check():
    #     """
    #     Health check endpoint for monitoring and load balancers.
        
    #     Returns:
    #         dict: Health status information
    #     """
    #     return {
    #         "status": "healthy",
    #         "service": settings.PROJECT_NAME,
    #         "version": settings.VERSION
    #     }

    return app

# Create the FastAPI application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
