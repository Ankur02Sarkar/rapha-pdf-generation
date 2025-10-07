"""
AWS Lambda Handler for FastAPI Application

This module provides the Lambda handler function that wraps the FastAPI
application using Mangum for serverless deployment on AWS Lambda.

Author: Principal Backend Architect
"""

import sys
import os

# Add the parent directory to the Python path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from mangum import Mangum

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    This function serves as the entry point for AWS Lambda and uses Mangum
    to adapt the FastAPI application for the Lambda runtime environment.
    
    Args:
        event (dict): The Lambda event object containing request data
        context (LambdaContext): The Lambda context object containing runtime information
        
    Returns:
        dict: The response object formatted for API Gateway
    """
    # Create Mangum handler with optimized settings for Lambda
    handler = Mangum(
        app, 
        lifespan="off",  # Disable lifespan events for Lambda
        api_gateway_base_path=None,  # Let API Gateway handle base path
        text_mime_types=[
            "application/json",
            "application/javascript",
            "application/xml",
            "application/vnd.api+json",
        ]
    )
    
    return handler(event, context)

# Alternative handler for direct import
handler = Mangum(app, lifespan="off")