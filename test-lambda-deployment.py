#!/usr/bin/env python3
"""
AWS Lambda Deployment Testing Script

This script tests the deployed Lambda function to ensure all endpoints
are working correctly and PDF generation is functioning properly.

Author: Principal Backend Architect
"""

import json
import requests
import base64
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Test configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://your-api-id.execute-api.ap-south-1.amazonaws.com/prod")
TIMEOUT = 30

# ANSI color codes for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log_info(message: str) -> None:
    """Log info message with color."""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {message}")

def log_success(message: str) -> None:
    """Log success message with color."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}")

def log_warning(message: str) -> None:
    """Log warning message with color."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {message}")

def log_error(message: str) -> None:
    """Log error message with color."""
    print(f"{Colors.RED}[ERROR]{Colors.END} {message}")

def make_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make HTTP request to the API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        data: Request payload for POST requests
        
    Returns:
        Dict containing response data and metadata
    """
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        log_info(f"Making {method} request to {endpoint}")
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.json() if response.content else {},
            "success": 200 <= response.status_code < 300,
            "response_time": response.elapsed.total_seconds()
        }
        
    except requests.exceptions.Timeout:
        log_error(f"Request timeout after {TIMEOUT} seconds")
        return {"status_code": 408, "success": False, "error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        log_error(f"Request failed: {str(e)}")
        return {"status_code": 500, "success": False, "error": str(e)}
    except json.JSONDecodeError:
        log_error("Invalid JSON response")
        return {"status_code": 500, "success": False, "error": "Invalid JSON response"}

def test_health_endpoint() -> bool:
    """Test the main health endpoint."""
    log_info("Testing main health endpoint...")
    
    result = make_request("GET", "/api/v1/health")
    
    if result["success"]:
        log_success(f"Health endpoint working (Response time: {result['response_time']:.2f}s)")
        return True
    else:
        log_error(f"Health endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def test_pdf_health_endpoint() -> bool:
    """Test the PDF service health endpoint."""
    log_info("Testing PDF service health endpoint...")
    
    result = make_request("GET", "/api/v1/pdf/health")
    
    if result["success"]:
        data = result["data"]
        log_success(f"PDF health endpoint working (Response time: {result['response_time']:.2f}s)")
        log_info(f"WeasyPrint version: {data.get('weasyprint_version', 'Unknown')}")
        log_info(f"Jinja2 version: {data.get('jinja2_version', 'Unknown')}")
        return True
    else:
        log_error(f"PDF health endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def test_template_info_endpoint() -> bool:
    """Test the template info endpoint."""
    log_info("Testing template info endpoint...")
    
    result = make_request("GET", "/api/v1/pdf/templates/info")
    
    if result["success"]:
        data = result["data"]
        log_success(f"Template info endpoint working (Response time: {result['response_time']:.2f}s)")
        log_info(f"Available templates: {len(data.get('templates', []))}")
        return True
    else:
        log_error(f"Template info endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def test_prescription_pdf_generation() -> bool:
    """Test prescription PDF generation."""
    log_info("Testing prescription PDF generation...")
    
    # Sample prescription data
    prescription_data = {
        "patient": {
            "name": "John Doe",
            "age": 35,
            "gender": "Male",
            "phone": "+1-555-0123",
            "email": "john.doe@example.com",
            "address": "123 Main St, Anytown, ST 12345"
        },
        "doctor": {
            "name": "Dr. Jane Smith",
            "license_number": "MD123456",
            "clinic_name": "RaphaCure Medical Center",
            "clinic_address": "456 Health Ave, Medical City, ST 67890",
            "phone": "+1-555-0456",
            "email": "dr.smith@raphacure.com"
        },
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "3 times daily",
                "duration": "7 days",
                "instructions": "Take with food"
            },
            {
                "name": "Ibuprofen",
                "dosage": "200mg",
                "frequency": "As needed",
                "duration": "5 days",
                "instructions": "Take with food, maximum 4 times daily"
            }
        ],
        "diagnosis": "Upper respiratory tract infection",
        "notes": "Follow up in 1 week if symptoms persist",
        "date": datetime.now().isoformat()
    }
    
    result = make_request("POST", "/api/v1/pdf/prescription", prescription_data)
    
    if result["success"]:
        data = result["data"]
        log_success(f"Prescription PDF generated (Response time: {result['response_time']:.2f}s)")
        
        # Validate PDF data
        pdf_data = data.get("pdf_data")
        if pdf_data:
            try:
                # Decode base64 to verify it's valid
                pdf_bytes = base64.b64decode(pdf_data)
                if pdf_bytes.startswith(b'%PDF'):
                    log_success(f"Valid PDF generated (Size: {len(pdf_bytes)} bytes)")
                    
                    # Optionally save PDF for manual inspection
                    with open("test_prescription.pdf", "wb") as f:
                        f.write(pdf_bytes)
                    log_info("PDF saved as test_prescription.pdf for inspection")
                    
                    return True
                else:
                    log_error("Generated data is not a valid PDF")
                    return False
            except Exception as e:
                log_error(f"Failed to decode PDF data: {str(e)}")
                return False
        else:
            log_error("No PDF data in response")
            return False
    else:
        log_error(f"Prescription PDF generation failed: {result.get('error', 'Unknown error')}")
        return False

def test_invoice_pdf_generation() -> bool:
    """Test invoice PDF generation."""
    log_info("Testing invoice PDF generation...")
    
    # Sample invoice data
    invoice_data = {
        "business": {
            "name": "RaphaCure Medical Services",
            "address": "456 Health Ave, Medical City, ST 67890",
            "phone": "+1-555-0456",
            "email": "billing@raphacure.com",
            "tax_id": "12-3456789"
        },
        "customer": {
            "name": "John Doe",
            "address": "123 Main St, Anytown, ST 12345",
            "phone": "+1-555-0123",
            "email": "john.doe@example.com"
        },
        "invoice_details": {
            "invoice_number": "INV-2024-001",
            "date": datetime.now().isoformat(),
            "due_date": "2024-02-15",
            "payment_terms": "Net 30"
        },
        "items": [
            {
                "description": "Medical Consultation",
                "quantity": 1,
                "unit_price": 150.00,
                "total": 150.00
            },
            {
                "description": "Prescription Medication",
                "quantity": 2,
                "unit_price": 25.00,
                "total": 50.00
            }
        ],
        "totals": {
            "subtotal": 200.00,
            "tax_rate": 0.08,
            "tax_amount": 16.00,
            "total": 216.00
        },
        "notes": "Thank you for choosing RaphaCure Medical Services"
    }
    
    result = make_request("POST", "/api/v1/pdf/invoice", invoice_data)
    
    if result["success"]:
        data = result["data"]
        log_success(f"Invoice PDF generated (Response time: {result['response_time']:.2f}s)")
        
        # Validate PDF data
        pdf_data = data.get("pdf_data")
        if pdf_data:
            try:
                # Decode base64 to verify it's valid
                pdf_bytes = base64.b64decode(pdf_data)
                if pdf_bytes.startswith(b'%PDF'):
                    log_success(f"Valid PDF generated (Size: {len(pdf_bytes)} bytes)")
                    
                    # Optionally save PDF for manual inspection
                    with open("test_invoice.pdf", "wb") as f:
                        f.write(pdf_bytes)
                    log_info("PDF saved as test_invoice.pdf for inspection")
                    
                    return True
                else:
                    log_error("Generated data is not a valid PDF")
                    return False
            except Exception as e:
                log_error(f"Failed to decode PDF data: {str(e)}")
                return False
        else:
            log_error("No PDF data in response")
            return False
    else:
        log_error(f"Invoice PDF generation failed: {result.get('error', 'Unknown error')}")
        return False

def run_all_tests() -> None:
    """Run all tests and provide summary."""
    log_info(f"Starting Lambda deployment tests for: {API_BASE_URL}")
    log_info("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("PDF Health Endpoint", test_pdf_health_endpoint),
        ("Template Info Endpoint", test_template_info_endpoint),
        ("Prescription PDF Generation", test_prescription_pdf_generation),
        ("Invoice PDF Generation", test_invoice_pdf_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        log_info(f"\n{Colors.BOLD}Running: {test_name}{Colors.END}")
        log_info("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            log_error(f"Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    log_info("\n" + "=" * 60)
    log_info(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    log_info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if success else f"{Colors.RED}FAIL{Colors.END}"
        log_info(f"{test_name}: {status}")
    
    log_info("-" * 60)
    if passed == total:
        log_success(f"All tests passed! ({passed}/{total})")
        log_success("Your Lambda deployment is working correctly!")
    else:
        log_error(f"Some tests failed. ({passed}/{total} passed)")
        log_error("Please check the deployment and try again.")
    
    return passed == total

if __name__ == "__main__":
    # Check if API URL is provided
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    if "your-api-id" in API_BASE_URL:
        log_warning("Please update the API_BASE_URL with your actual API Gateway URL")
        log_info("Usage: python test-lambda-deployment.py <API_GATEWAY_URL>")
        log_info("Example: python test-lambda-deployment.py https://abc123.execute-api.ap-south-1.amazonaws.com/prod")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)