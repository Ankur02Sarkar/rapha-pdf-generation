"""
PDF Generation Service

This module provides comprehensive PDF generation functionality using WeasyPrint
and Jinja2 templates for prescription and invoice documents.
"""

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from io import BytesIO

from jinja2 import Environment, FileSystemLoader, Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.schemas.prescription import PrescriptionRequest, PDFResponse as PrescriptionPDFResponse
from app.schemas.invoice import InvoiceRequest, PDFResponse as InvoicePDFResponse


class PDFGenerationService:
    """
    Service class for generating PDF documents from HTML templates.
    
    This service handles the conversion of structured data into professional
    PDF documents using WeasyPrint and Jinja2 templating engine.
    """
    
    def __init__(self):
        """
        Initialize the PDF generation service.
        
        Sets up the Jinja2 environment and WeasyPrint font configuration
        for optimal PDF rendering.
        """
        # Get the templates directory path
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Initialize WeasyPrint font configuration
        self.font_config = FontConfiguration()
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the provided context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary containing template variables
            
        Returns:
            Rendered HTML string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If template rendering fails
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise Exception(f"Template rendering failed: {str(e)}")
    
    def _generate_pdf_bytes(self, html_content: str, css_content: Optional[str] = None) -> bytes:
        """
        Generate PDF bytes from HTML content using WeasyPrint.
        
        Args:
            html_content: HTML content to convert
            css_content: Optional additional CSS content
            
        Returns:
            PDF content as bytes
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Create HTML object
            html_doc = HTML(string=html_content)
            
            # Generate PDF with font configuration
            pdf_bytes = html_doc.write_pdf(font_config=self.font_config)
            
            return pdf_bytes
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _create_pdf_response(
        self, 
        pdf_bytes: bytes, 
        filename: str, 
        success_message: str
    ) -> Dict[str, Any]:
        """
        Create a standardized PDF response dictionary.
        
        Args:
            pdf_bytes: PDF content as bytes
            filename: Suggested filename for the PDF
            success_message: Success message for the response
            
        Returns:
            Dictionary containing PDF response data
        """
        # Encode PDF to base64 for JSON response
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            "success": True,
            "message": success_message,
            "pdf_data": pdf_base64,
            "filename": filename,
            "content_type": "application/pdf",
            "size_bytes": len(pdf_bytes)
        }
    
    def generate_prescription_pdf(self, prescription_data: PrescriptionRequest) -> PrescriptionPDFResponse:
        """
        Generate a prescription PDF from prescription data.
        
        Args:
            prescription_data: Prescription request containing patient, doctor, and medication info
            
        Returns:
            PrescriptionPDFResponse containing the generated PDF data
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Prepare template context
            context = {
                "patient": prescription_data.patient,
                "doctor": prescription_data.doctor,
                "medications": prescription_data.medications,
                "symptoms": prescription_data.symptoms,
                "tests_suggested": prescription_data.tests_suggested,
                "hyperlinks": prescription_data.hyperlinks,
                "reports": prescription_data.reports,
                "advice": prescription_data.advice,
                "next_followup": prescription_data.next_followup,
                "prescription_date": prescription_data.prescription_date,
                "consult_type": prescription_data.consult_type,
                "prescription_id": prescription_data.prescription_id,
                "generated_at": datetime.now()
            }
            
            # Render HTML template
            html_content = self._render_template("prescription.html", context)
            
            # Generate PDF
            pdf_bytes = self._generate_pdf_bytes(html_content)
            
            # Create filename
            patient_name = prescription_data.patient.name.replace(" ", "_")
            # Handle date string format (e.g., "2024-01-15" or "15-01-2024")
            date_str = prescription_data.prescription_date.replace("-", "")
            filename = f"prescription_{patient_name}_{date_str}.pdf"
            
            # Create response
            response_data = self._create_pdf_response(
                pdf_bytes, 
                filename, 
                "Prescription PDF generated successfully"
            )
            
            return PrescriptionPDFResponse(**response_data)
            
        except Exception as e:
            return PrescriptionPDFResponse(
                success=False,
                message=f"Failed to generate prescription PDF: {str(e)}",
                content_type="application/json"
            )
    
    def generate_invoice_pdf(self, invoice_data: InvoiceRequest) -> InvoicePDFResponse:
        """
        Generate an invoice PDF from invoice data.
        
        Args:
            invoice_data: Invoice request containing business, customer, and item info
            
        Returns:
            InvoicePDFResponse containing the generated PDF data
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Prepare template context with calculated totals
            context = {
                "business": invoice_data.business,
                "customer": invoice_data.customer,
                "items": invoice_data.items,
                "payment_info": invoice_data.payment_info,
                "invoice_number": invoice_data.invoice_number,
                "invoice_date": invoice_data.invoice_date,
                "currency": invoice_data.currency,
                "notes": invoice_data.notes,
                "subtotal": invoice_data.subtotal,
                "total_discount": invoice_data.total_discount,
                "total_tax": invoice_data.total_tax,
                "total_amount": invoice_data.total_amount,
                "generated_at": datetime.now()
            }
            
            # Render HTML template
            html_content = self._render_template("invoice.html", context)
            
            # Generate PDF
            pdf_bytes = self._generate_pdf_bytes(html_content)
            
            # Create filename
            invoice_number = invoice_data.invoice_number.replace("/", "_").replace(" ", "_")
            date_str = invoice_data.invoice_date.strftime("%Y%m%d")
            filename = f"invoice_{invoice_number}_{date_str}.pdf"
            
            # Create response
            response_data = self._create_pdf_response(
                pdf_bytes, 
                filename, 
                "Invoice PDF generated successfully"
            )
            
            return InvoicePDFResponse(**response_data)
            
        except Exception as e:
            return InvoicePDFResponse(
                success=False,
                message=f"Failed to generate invoice PDF: {str(e)}",
                content_type="application/json"
            )
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about available templates.
        
        Returns:
            Dictionary containing template information
        """
        templates_info = {
            "available_templates": [],
            "templates_directory": str(self.templates_dir)
        }
        
        try:
            if self.templates_dir.exists():
                for template_file in self.templates_dir.glob("*.html"):
                    templates_info["available_templates"].append({
                        "name": template_file.name,
                        "path": str(template_file),
                        "size_bytes": template_file.stat().st_size,
                        "modified": datetime.fromtimestamp(template_file.stat().st_mtime).isoformat()
                    })
        except Exception as e:
            templates_info["error"] = f"Failed to read templates directory: {str(e)}"
        
        return templates_info


# Global service instance
pdf_service = PDFGenerationService()