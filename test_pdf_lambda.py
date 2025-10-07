#!/usr/bin/env python3
"""
Test script for PDF generation endpoints on AWS Lambda
"""

import json
import boto3
import base64
from datetime import datetime

# Configuration
AWS_REGION = "ap-south-1"
LAMBDA_FUNCTION_NAME = "rapha-pdf-generation-lambda"

def create_api_gateway_event(method, path, body=None):
    """Create a proper API Gateway v2.0 event for testing"""
    event = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
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
                "method": method,
                "path": path,
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
    
    if body:
        event["body"] = json.dumps(body)
        event["headers"]["content-length"] = str(len(event["body"]))
    
    return event

def test_prescription_pdf():
    """Test prescription PDF generation"""
    print("🧪 Testing prescription PDF generation...")
    
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        # Sample prescription data matching the schema
        prescription_data = {
            "patient": {
                "name": "John Doe",
                "age": 35,
                "gender": "Male",
                "phone": "+1-555-0123",
                "patient_id": "P001"
            },
            "doctor": {
                "name": "Dr. Smith",
                "qualifications": "MBBS, MD",
                "specialization": "General Medicine",
                "registration_number": "MED-12345",
                "clinic_name": "RaphaCure Clinic",
                "clinic_address": "123 Health Street, Medical City, MC 12345",
                "phone": "+1-555-0456",
                "email": "dr.smith@raphacure.com"
            },
            "medications": [
                {
                    "name": "Amoxicillin 500mg",
                    "dosage": "1-0-1",
                    "timing": "After Food",
                    "duration": "7 days",
                    "start_date": "2025-10-07",
                    "note": "For infection"
                },
                {
                    "name": "Ibuprofen 200mg",
                    "dosage": "1-1-1",
                    "timing": "After Food",
                    "duration": "5 days",
                    "start_date": "2025-10-07",
                    "note": "For pain relief"
                }
            ],
            "prescription_date": "2025-10-07",
            "symptoms": "Fever, body ache",
            "advice": "Take rest and drink plenty of fluids"
        }
        
        event = create_api_gateway_event("POST", "/api/v1/pdf/prescription", prescription_data)
        
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Payload=json.dumps(event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if 'errorMessage' in payload:
            print(f"❌ Lambda error: {payload['errorMessage']}")
            return False
        
        if payload.get('statusCode') == 200:
            print("✅ Prescription PDF generated successfully")
            body = json.loads(payload['body'])
            if 'pdf_data' in body:
                print(f"✅ PDF data received (length: {len(body['pdf_data'])} characters)")
            return True
        else:
            print(f"❌ Unexpected status code: {payload.get('statusCode')}")
            print(f"Response: {payload}")
            return False
            
    except Exception as e:
        print(f"❌ Prescription PDF test failed: {str(e)}")
        return False

def test_invoice_pdf():
    """Test invoice PDF generation"""
    print("🧪 Testing invoice PDF generation...")
    
    try:
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        
        # Sample invoice data matching the schema
        invoice_data = {
            "business": {
                "name": "RaphaCure Clinic",
                "address": "123 Health Street, Medical City, MC 12345",
                "phone": "+1-555-0123",
                "email": "billing@raphacure.com",
                "website": "www.raphacure.com",
                "tax_id": "TAX123456789"
            },
            "customer": {
                "name": "Jane Smith",
                "address": "456 Patient Ave, City, ST 67890",
                "phone": "+1-555-0456",
                "email": "jane.smith@email.com",
                "customer_id": "PAT001"
            },
            "items": [
                {
                    "description": "Medical Consultation",
                    "quantity": 1,
                    "unit_price": 100.00,
                    "tax_percent": 10.0
                },
                {
                    "description": "Blood Test",
                    "quantity": 1,
                    "unit_price": 50.00,
                    "tax_percent": 10.0
                }
            ],
            "payment_info": {
                "payment_terms": "Net 30",
                "due_date": "2025-11-07",
                "payment_method": "Bank Transfer",
                "bank_details": "Account: 1234567890, Routing: 987654321"
            },
            "invoice_number": "INV-2025-001",
            "currency": "USD",
            "notes": "Thank you for choosing RaphaCure!"
        }
        
        event = create_api_gateway_event("POST", "/api/v1/pdf/invoice", invoice_data)
        
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Payload=json.dumps(event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if 'errorMessage' in payload:
            print(f"❌ Lambda error: {payload['errorMessage']}")
            return False
        
        if payload.get('statusCode') == 200:
            print("✅ Invoice PDF generated successfully")
            body = json.loads(payload['body'])
            if 'pdf_data' in body:
                print(f"✅ PDF data received (length: {len(body['pdf_data'])} characters)")
            return True
        else:
            print(f"❌ Unexpected status code: {payload.get('statusCode')}")
            print(f"Response: {payload}")
            return False
            
    except Exception as e:
        print(f"❌ Invoice PDF test failed: {str(e)}")
        return False

def main():
    """Run all PDF generation tests"""
    print("🚀 Starting PDF generation tests on AWS Lambda...")
    print("=" * 60)
    
    results = []
    
    # Test prescription PDF
    results.append(("Prescription PDF", test_prescription_pdf()))
    
    print()
    
    # Test invoice PDF
    results.append(("Invoice PDF", test_invoice_pdf()))
    
    print()
    print("=" * 60)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All PDF generation tests passed!")
        print("Your FastAPI Lambda function is ready for production!")
    else:
        print("❌ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()