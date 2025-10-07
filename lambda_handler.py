"""
AWS Lambda Handler for FastAPI Application

This module provides the Lambda handler function that adapts the FastAPI
application for AWS Lambda execution using Mangum.

Author: Principal Backend Architect
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from mangum import Mangum
from main import app

# Configure Lambda-specific settings
os.environ.setdefault("AWS_LAMBDA_FUNCTION_NAME", "rapha-pdf-generation")

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    This function serves as the entry point for AWS Lambda execution.
    It uses Mangum to adapt the FastAPI application for Lambda.
    
    Args:
        event: AWS Lambda event object containing request data
        context: AWS Lambda context object containing runtime information
        
    Returns:
        dict: HTTP response formatted for API Gateway
    """
    # Initialize Mangum handler with optimized settings for Lambda
    asgi_handler = Mangum(
        app,
        lifespan="off",  # Disable lifespan for Lambda
        api_gateway_base_path="/",  # Set base path for API Gateway
        text_mime_types=[
            "application/json",
            "application/javascript",
            "application/xml",
            "application/vnd.api+json",
        ]
    )
    
    return asgi_handler(event, context)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)