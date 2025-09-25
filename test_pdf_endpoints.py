#!/usr/bin/env python3
"""
Test script for PDF generation endpoints.

This script tests the prescription and invoice PDF generation endpoints
to ensure they work correctly and return valid base64-encoded PDF data.
"""

import requests
import json
import base64
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_prescription_endpoint():
    """Test the prescription PDF generation endpoint."""
    print("🧪 Testing Prescription PDF Generation...")
    
    # Sample prescription data
    prescription_data = {
        "patient": {
            "name": "John Doe",
            "age": 35,
            "gender": "M",
            "phone": "+1234567890",
            "address": "123 Main St, City, State 12345",
            "patient_id": "P001"
        },
        "doctor": {
            "name": "Dr. Jane Smith",
            "specialization": "General Medicine",
            "license_number": "MD12345",
            "clinic_name": "City Medical Center",
            "clinic_address": "456 Health Ave, Medical District",
            "phone": "+1987654321",
            "email": "dr.smith@citymedical.com"
        },
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "Three times daily",
                "duration": "7 days",
                "instructions": "Take with food"
            },
            {
                "name": "Ibuprofen",
                "dosage": "200mg",
                "frequency": "As needed",
                "duration": "5 days",
                "instructions": "For pain relief"
            }
        ],
        "diagnosis": "Upper respiratory tract infection",
        "notes": "Follow up in 1 week if symptoms persist",
        "date": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/pdf/prescription",
            json=prescription_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prescription PDF generated successfully!")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   PDF Data Length: {len(result.get('pdf_data', ''))} characters")
            
            # Verify it's valid base64
            try:
                pdf_bytes = base64.b64decode(result.get('pdf_data', ''))
                print(f"   Decoded PDF Size: {len(pdf_bytes)} bytes")
                print(f"   PDF Header: {pdf_bytes[:10]}")  # Should start with %PDF
                return True
            except Exception as e:
                print(f"❌ Invalid base64 data: {e}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_invoice_endpoint():
    """Test the invoice PDF generation endpoint."""
    print("\n🧪 Testing Invoice PDF Generation...")
    
    # Sample invoice data
    invoice_data = {
        "business": {
            "name": "Tech Solutions Inc.",
            "address": "123 Business Ave, Tech District, CA 90210",
            "phone": "+1-555-0123",
            "email": "billing@techsolutions.com",
            "website": "www.techsolutions.com",
            "tax_id": "TAX123456789"
        },
        "customer": {
            "name": "ABC Corporation",
            "address": "456 Client St, Business Park, NY 10001",
            "email": "accounts@abccorp.com",
            "phone": "+1-555-0456",
            "customer_id": "CUST001"
        },
        "items": [
            {
                "description": "Web Development Services",
                "quantity": "40",
                "unit_price": "75.00",
                "tax_percent": "8.5",
                "discount_percent": "0"
            },
            {
                "description": "Database Setup & Configuration",
                "quantity": "8",
                "unit_price": "120.00",
                "tax_percent": "8.5",
                "discount_percent": "5.0"
            },
            {
                "description": "API Integration",
                "quantity": "16",
                "unit_price": "90.00",
                "tax_percent": "8.5",
                "discount_percent": "0"
            }
        ],
        "payment_info": {
            "payment_terms": "Net 30",
            "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "payment_method": "Bank Transfer",
            "notes": "Thank you for your business!"
        },
        "invoice_number": "INV-2024-001",
        "invoice_date": datetime.now().strftime("%Y-%m-%d"),
        "currency": "USD"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/pdf/invoice",
            json=invoice_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Invoice PDF generated successfully!")
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   PDF Data Length: {len(result.get('pdf_data', ''))} characters")
            
            # Verify it's valid base64
            try:
                pdf_bytes = base64.b64decode(result.get('pdf_data', ''))
                print(f"   Decoded PDF Size: {len(pdf_bytes)} bytes")
                print(f"   PDF Header: {pdf_bytes[:10]}")  # Should start with %PDF
                return True
            except Exception as e:
                print(f"❌ Invalid base64 data: {e}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_health_endpoint():
    """Test the PDF service health endpoint."""
    print("\n🧪 Testing PDF Service Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/pdf/health")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF service health check passed!")
            print(f"   Status: {result.get('data', {}).get('status')}")
            print(f"   Dependencies: {result.get('data', {}).get('dependencies')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting PDF Generation API Tests...\n")
    
    tests = [
        test_health_endpoint,
        test_prescription_endpoint,
        test_invoice_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PDF generation API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()