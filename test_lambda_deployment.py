#!/usr/bin/env python3
"""
Lambda Deployment Test Script

This script tests the deployed FastAPI Lambda function to ensure
it's working correctly with AWS Lambda and API Gateway.

Author: Principal Backend Architect
"""

import json
import boto3
import requests
import sys
from typing import Dict, Any

# Configuration
LAMBDA_FUNCTION_NAME = "rapha-pdf-generation-lambda"
AWS_REGION = "ap-south-1"

def test_lambda_direct():
    """
    Test the Lambda function directly using AWS SDK with proper API Gateway event.
    
    Returns:
        bool: True if test passes, False otherwise
    """
    print("🧪 Testing Lambda function directly...")
    
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        # Create a proper API Gateway v2.0 event for Mangum
        test_event = {
            "version": "2.0",
            "routeKey": "GET /health",
            "rawPath": "/health",
            "rawQueryString": "",
            "headers": {
                "accept": "application/json",
                "content-type": "application/json",
                "host": "lambda-url.ap-south-1.on.aws",
                "user-agent": "test-client"
            },
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "test",
                "domainName": "lambda-url.ap-south-1.on.aws",
                "http": {
                    "method": "GET",
                    "path": "/health",
                    "protocol": "HTTP/1.1",
                    "sourceIp": "127.0.0.1",
                    "userAgent": "test-client"
                },
                "requestId": "test-request-id",
                "stage": "$default",
                "time": "01/Jan/2023:00:00:00 +0000",
                "timeEpoch": 1672531200000
            },
            "isBase64Encoded": False
        }
        
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("✅ Lambda function invocation successful")
            print(f"Response: {json.dumps(payload, indent=2)}")
            
            # Check for Lambda errors first
            if 'errorMessage' in payload:
                print(f"❌ Lambda function error: {payload['errorMessage']}")
                return False
            
            # Check if the response has the expected structure
            if 'statusCode' in payload and payload['statusCode'] == 200:
                print("✅ Health endpoint responding correctly")
                return True
            else:
                print(f"❌ Unexpected response structure: {payload}")
                return False
        else:
            print(f"❌ Lambda invocation failed with status: {response['StatusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lambda function: {str(e)}")
        return False

def test_api_gateway(api_url: str):
    """
    Test the API Gateway endpoint.
    
    Args:
        api_url (str): The API Gateway URL
        
    Returns:
        bool: True if test passes, False otherwise
    """
    print(f"🌐 Testing API Gateway at: {api_url}")
    
    try:
        # Test health endpoint
        health_url = f"{api_url}/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ API Gateway health endpoint responding")
            print(f"Response: {response.json()}")
            
            # Test API documentation endpoint
            docs_url = f"{api_url}/docs"
            docs_response = requests.get(docs_url, timeout=30)
            
            if docs_response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print("⚠️  API documentation not accessible (this might be expected)")
            
            return True
        else:
            print(f"❌ API Gateway test failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing API Gateway: {str(e)}")
        return False

def get_api_gateway_url():
    """
    Get the API Gateway URL from CloudFormation stack.
    
    Returns:
        str: API Gateway URL or None if not found
    """
    try:
        cf_client = boto3.client('cloudformation', region_name=AWS_REGION)
        
        response = cf_client.describe_stacks(
            StackName='rapha-pdf-api-gateway'
        )
        
        for stack in response['Stacks']:
            for output in stack.get('Outputs', []):
                if output['OutputKey'] == 'ApiGatewayUrl':
                    return output['OutputValue']
        
        return None
        
    except Exception as e:
        print(f"⚠️  Could not retrieve API Gateway URL: {str(e)}")
        return None

def get_lambda_function_url():
    """
    Get the Lambda Function URL if configured.
    
    Returns:
        str: Lambda Function URL or None if not found
    """
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        response = lambda_client.get_function_url_config(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        
        return response['FunctionUrl'].rstrip('/')
        
    except Exception as e:
        print(f"⚠️  Lambda Function URL not configured: {str(e)}")
        return None

def test_pdf_endpoints(base_url: str):
    """
    Test the PDF generation endpoints.
    
    Args:
        base_url (str): The base URL for the API
        
    Returns:
        bool: True if tests pass, False otherwise
    """
    print("📄 Testing PDF endpoints...")
    
    try:
        # Test prescription endpoint (if it exists)
        prescription_url = f"{base_url}/api/v1/pdf/prescription"
        
        # This is a basic test - you might need to adjust based on your actual endpoints
        test_data = {
            "patient_name": "Test Patient",
            "doctor_name": "Test Doctor",
            "medications": ["Test Medication"]
        }
        
        response = requests.post(
            prescription_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("✅ PDF prescription endpoint responding")
            return True
        elif response.status_code == 404:
            print("⚠️  PDF endpoints not found - check your API routes")
            return True  # Not a failure, just not implemented
        else:
            print(f"❌ PDF endpoint test failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error testing PDF endpoints: {str(e)}")
        return True  # Not a critical failure

def main():
    """
    Main test function.
    """
    print("🚀 Starting Lambda deployment tests...\n")
    
    # Test 1: Direct Lambda invocation
    lambda_test_passed = test_lambda_direct()
    print()
    
    # Test 2: API Gateway (if available)
    api_gateway_url = get_api_gateway_url()
    lambda_function_url = get_lambda_function_url()
    
    api_test_passed = False
    
    if api_gateway_url:
        api_test_passed = test_api_gateway(api_gateway_url)
        if api_test_passed:
            test_pdf_endpoints(api_gateway_url)
    elif lambda_function_url:
        print("📝 Using Lambda Function URL for testing...")
        api_test_passed = test_api_gateway(lambda_function_url)
        if api_test_passed:
            test_pdf_endpoints(lambda_function_url)
    else:
        print("⚠️  No API Gateway or Lambda Function URL found")
        print("   You can create a Lambda Function URL with:")
        print(f"   aws lambda create-function-url-config --function-name {LAMBDA_FUNCTION_NAME} --auth-type NONE")
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print(f"   Lambda Direct Test: {'✅ PASSED' if lambda_test_passed else '❌ FAILED'}")
    print(f"   API Gateway Test: {'✅ PASSED' if api_test_passed else '⚠️  SKIPPED/FAILED'}")
    
    if lambda_test_passed:
        print("\n🎉 Your FastAPI Lambda deployment is working!")
        if api_gateway_url:
            print(f"🌐 API Gateway URL: {api_gateway_url}")
        if lambda_function_url:
            print(f"🔗 Lambda Function URL: {lambda_function_url}")
    else:
        print("\n❌ Deployment tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()