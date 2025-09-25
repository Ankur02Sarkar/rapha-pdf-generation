"""
PDF Generation API Endpoints

This module defines FastAPI endpoints for generating PDF documents
from prescription and invoice data using WeasyPrint.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.schemas.prescription import PrescriptionRequest, PDFResponse as PrescriptionPDFResponse
from app.schemas.invoice import InvoiceRequest, PDFResponse as InvoicePDFResponse
from app.services.pdf_service import pdf_service
from app.utils.responses import success_response, error_response

# Create router instance
router = APIRouter(prefix="/pdf", tags=["PDF Generation"])


@router.post(
    "/prescription",
    response_model=PrescriptionPDFResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Prescription PDF",
    description="Generate a professional prescription PDF document from patient, doctor, and medication data."
)
async def generate_prescription_pdf(
    prescription_data: PrescriptionRequest
) -> PrescriptionPDFResponse:
    """
    Generate a prescription PDF document.
    
    This endpoint accepts prescription data including patient information,
    doctor details, medications, and generates a professional PDF document
    suitable for medical use.
    
    Args:
        prescription_data: Complete prescription information including:
            - Patient details (name, age, gender, contact info)
            - Doctor information (name, license, clinic details)
            - Medications list with dosage, frequency, duration
            - Diagnosis and additional notes
    
    Returns:
        PrescriptionPDFResponse: Contains success status, message, and base64-encoded PDF data
        
    Raises:
        HTTPException: If PDF generation fails or validation errors occur
        
    Example:
        ```json
        {
            "patient": {
                "name": "John Doe",
                "age": 35,
                "gender": "M",
                "phone": "+1234567890"
            },
            "doctor": {
                "name": "Dr. Jane Smith",
                "specialization": "General Medicine",
                "license_number": "MD12345",
                "clinic_name": "City Medical Center",
                "clinic_address": "456 Health Ave",
                "phone": "+1987654321"
            },
            "medications": [
                {
                    "name": "Amoxicillin",
                    "dosage": "500mg",
                    "frequency": "Three times daily",
                    "duration": "7 days"
                }
            ]
        }
        ```
    """
    try:
        # Generate PDF using the service
        pdf_response = pdf_service.generate_prescription_pdf(prescription_data)
        
        if not pdf_response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=pdf_response.message
            )
        
        return pdf_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during prescription PDF generation: {str(e)}"
        )


@router.post(
    "/invoice",
    response_model=InvoicePDFResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Invoice PDF",
    description="Generate a professional invoice PDF document from business, customer, and billing data."
)
async def generate_invoice_pdf(
    invoice_data: InvoiceRequest
) -> InvoicePDFResponse:
    """
    Generate an invoice PDF document.
    
    This endpoint accepts invoice data including business information,
    customer details, line items, and generates a professional PDF invoice
    suitable for business use.
    
    Args:
        invoice_data: Complete invoice information including:
            - Business details (name, address, contact info, tax ID)
            - Customer information (name, address, customer ID)
            - Invoice items with quantities, prices, taxes, discounts
            - Payment terms and due dates
    
    Returns:
        InvoicePDFResponse: Contains success status, message, and base64-encoded PDF data
        
    Raises:
        HTTPException: If PDF generation fails or validation errors occur
        
    Example:
        ```json
        {
            "business": {
                "name": "Tech Solutions Inc.",
                "address": "123 Business Ave",
                "phone": "+1-555-0123",
                "email": "billing@techsolutions.com"
            },
            "customer": {
                "name": "ABC Corporation",
                "address": "456 Client St",
                "email": "accounts@abccorp.com"
            },
            "items": [
                {
                    "description": "Web Development Services",
                    "quantity": "40",
                    "unit_price": "75.00",
                    "tax_percent": "8.5"
                }
            ],
            "payment_info": {
                "payment_terms": "Net 30",
                "due_date": "2024-02-15"
            },
            "invoice_number": "INV-2024-001"
        }
        ```
    """
    try:
        # Generate PDF using the service
        pdf_response = pdf_service.generate_invoice_pdf(invoice_data)
        
        if not pdf_response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=pdf_response.message
            )
        
        return pdf_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during invoice PDF generation: {str(e)}"
        )


@router.get(
    "/templates/info",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Template Information",
    description="Retrieve information about available PDF templates."
)
async def get_template_info() -> Dict[str, Any]:
    """
    Get information about available PDF templates.
    
    This endpoint provides metadata about the available HTML templates
    used for PDF generation, including file sizes and modification dates.
    
    Returns:
        Dict containing template information and metadata
        
    Raises:
        HTTPException: If template information retrieval fails
    """
    try:
        template_info = pdf_service.get_template_info()
        
        return success_response(
            data=template_info,
            message="Template information retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template information: {str(e)}"
        )


@router.get(
    "/health",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="PDF Service Health Check",
    description="Check the health and status of the PDF generation service."
)
async def pdf_service_health() -> Dict[str, Any]:
    """
    Check the health of the PDF generation service.
    
    This endpoint verifies that the PDF generation service is operational
    and all required dependencies are available.
    
    Returns:
        Dict containing service health status and version information
    """
    try:
        import weasyprint
        import jinja2
        
        health_data = {
            "service": "PDF Generation Service",
            "status": "healthy",
            "dependencies": {
                "weasyprint": weasyprint.__version__,
                "jinja2": jinja2.__version__
            },
            "templates": pdf_service.get_template_info()
        }
        
        return success_response(
            data=health_data,
            message="PDF service is healthy and operational"
        )
        
    except Exception as e:
        return error_response(
            message=f"PDF service health check failed: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )