"""
PDF Generation Service

This module provides comprehensive PDF generation functionality using ReportLab
for prescription and invoice documents.
"""

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from app.schemas.prescription import PrescriptionRequest, PDFResponse as PrescriptionPDFResponse
from app.schemas.invoice import InvoiceRequest, PDFResponse as InvoicePDFResponse


class PDFGenerationService:
    """
    Service class for generating PDF documents using ReportLab.
    
    This service handles the conversion of structured data into professional
    PDF documents using ReportLab library.
    """
    
    def __init__(self):
        """
        Initialize the PDF generation service.
        
        Sets up ReportLab styles and configurations for optimal PDF rendering.
        """
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for different document elements."""
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        # Bold info style
        self.styles.add(ParagraphStyle(
            name='BoldInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
    
    def _generate_pdf_bytes(self, story_elements: list) -> bytes:
        """
        Generate PDF bytes from story elements using ReportLab.
        
        Args:
            story_elements: List of ReportLab flowable elements
            
        Returns:
            PDF content as bytes
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            doc.build(story_elements)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
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
            prescription_data: Prescription information and medications
            
        Returns:
            PrescriptionPDFResponse with PDF data and metadata
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            story = []
            
            # Header
            story.append(Paragraph("MEDICAL PRESCRIPTION", self.styles['CustomHeader']))
            story.append(Spacer(1, 20))
            
            # Doctor Information
            story.append(Paragraph("Doctor Information", self.styles['CustomSubHeader']))
            doctor_info = [
                f"<b>Dr. {prescription_data.doctor.name}</b>",
                f"Qualifications: {prescription_data.doctor.qualifications}",
                f"Specialization: {prescription_data.doctor.specialization}",
                f"Registration No: {prescription_data.doctor.registration_number}",
                f"Clinic: {prescription_data.doctor.clinic_name}",
                f"Address: {prescription_data.doctor.clinic_address}",
                f"Phone: {prescription_data.doctor.phone}"
            ]
            for info in doctor_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            story.append(Spacer(1, 15))
            
            # Patient Information
            story.append(Paragraph("Patient Information", self.styles['CustomSubHeader']))
            patient_info = [
                f"<b>Name:</b> {prescription_data.patient.name}",
                f"<b>Age:</b> {prescription_data.patient.age} years",
                f"<b>Gender:</b> {prescription_data.patient.gender}",
                f"<b>Patient ID:</b> {prescription_data.patient.patient_id or 'N/A'}",
                f"<b>Phone:</b> {prescription_data.patient.phone or 'N/A'}"
            ]
            for info in patient_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            story.append(Spacer(1, 15))
            
            # Prescription Details
            story.append(Paragraph("Prescription Details", self.styles['CustomSubHeader']))
            story.append(Paragraph(f"<b>Date:</b> {prescription_data.prescription_date}", self.styles['InfoStyle']))
            story.append(Paragraph(f"<b>Symptoms:</b> {prescription_data.symptoms or 'N/A'}", self.styles['InfoStyle']))
            story.append(Spacer(1, 15))
            
            # Medications Table
            story.append(Paragraph("Medications", self.styles['CustomSubHeader']))
            med_data = [['Medication', 'Dosage', 'Timing', 'Duration', 'Notes']]
            for med in prescription_data.medications:
                med_data.append([
                    med.name,
                    med.dosage,
                    med.timing,
                    med.duration,
                    med.note or ''
                ])
            
            med_table = Table(med_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
            med_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(med_table)
            story.append(Spacer(1, 15))
            
            # Advice
            if prescription_data.advice:
                story.append(Paragraph("Medical Advice", self.styles['CustomSubHeader']))
                story.append(Paragraph(prescription_data.advice, self.styles['InfoStyle']))
                story.append(Spacer(1, 15))
            
            # Next Follow-up
            if prescription_data.next_followup:
                story.append(Paragraph(f"<b>Next Follow-up:</b> {prescription_data.next_followup}", self.styles['BoldInfo']))
            
            # Generate PDF
            pdf_bytes = self._generate_pdf_bytes(story)
            
            # Create filename
            patient_name = prescription_data.patient.name.replace(" ", "_")
            filename = f"prescription_{patient_name}_{prescription_data.prescription_date}.pdf"
            
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
                pdf_data=None,
                filename=None
            )
    
    def generate_invoice_pdf(self, invoice_data: InvoiceRequest) -> InvoicePDFResponse:
        """
        Generate an invoice PDF from invoice data.
        
        Args:
            invoice_data: Invoice information including items and customer details
            
        Returns:
            InvoicePDFResponse with PDF data and metadata
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            story = []
            
            # Header
            story.append(Paragraph("INVOICE", self.styles['CustomHeader']))
            story.append(Spacer(1, 20))
            
            # Invoice Info
            invoice_info = [
                f"<b>Invoice Number:</b> {invoice_data.invoice_number}",
                f"<b>Invoice Date:</b> {invoice_data.invoice_date}",
                f"<b>Currency:</b> {invoice_data.currency}"
            ]
            for info in invoice_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            story.append(Spacer(1, 15))
            
            # Business Information
            story.append(Paragraph("From:", self.styles['CustomSubHeader']))
            business_info = [
                f"<b>{invoice_data.business.name}</b>",
                invoice_data.business.address,
                f"Phone: {invoice_data.business.phone}",
                f"Email: {invoice_data.business.email}"
            ]
            if invoice_data.business.website:
                business_info.append(f"Website: {invoice_data.business.website}")
            if invoice_data.business.tax_id:
                business_info.append(f"Tax ID: {invoice_data.business.tax_id}")
            
            for info in business_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            story.append(Spacer(1, 15))
            
            # Customer Information
            story.append(Paragraph("Bill To:", self.styles['CustomSubHeader']))
            customer_info = [
                f"<b>{invoice_data.customer.name}</b>",
                invoice_data.customer.address
            ]
            if invoice_data.customer.phone:
                customer_info.append(f"Phone: {invoice_data.customer.phone}")
            if invoice_data.customer.email:
                customer_info.append(f"Email: {invoice_data.customer.email}")
            if invoice_data.customer.customer_id:
                customer_info.append(f"Customer ID: {invoice_data.customer.customer_id}")
            
            for info in customer_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            story.append(Spacer(1, 20))
            
            # Items Table
            story.append(Paragraph("Items", self.styles['CustomSubHeader']))
            item_data = [['Description', 'Qty', 'Unit Price', 'Discount %', 'Tax %', 'Total']]
            
            for item in invoice_data.items:
                item_data.append([
                    item.description,
                    str(item.quantity),
                    f"{invoice_data.currency} {item.unit_price:.2f}",
                    f"{item.discount_percent:.1f}%",
                    f"{item.tax_percent:.1f}%",
                    f"{invoice_data.currency} {item.total:.2f}"
                ])
            
            item_table = Table(item_data, colWidths=[2.5*inch, 0.7*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(item_table)
            story.append(Spacer(1, 15))
            
            # Totals
            totals_data = [
                ['Subtotal:', f"{invoice_data.currency} {invoice_data.subtotal:.2f}"],
                ['Total Discount:', f"{invoice_data.currency} {invoice_data.total_discount:.2f}"],
                ['Total Tax:', f"{invoice_data.currency} {invoice_data.total_tax:.2f}"],
                ['<b>Total Amount:</b>', f"<b>{invoice_data.currency} {invoice_data.total_amount:.2f}</b>"]
            ]
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(totals_table)
            story.append(Spacer(1, 20))
            
            # Payment Information
            story.append(Paragraph("Payment Information", self.styles['CustomSubHeader']))
            payment_info = [
                f"<b>Payment Terms:</b> {invoice_data.payment_info.payment_terms}",
                f"<b>Due Date:</b> {invoice_data.payment_info.due_date}"
            ]
            if invoice_data.payment_info.payment_method:
                payment_info.append(f"<b>Payment Method:</b> {invoice_data.payment_info.payment_method}")
            if invoice_data.payment_info.bank_details:
                payment_info.append(f"<b>Bank Details:</b> {invoice_data.payment_info.bank_details}")
            
            for info in payment_info:
                story.append(Paragraph(info, self.styles['InfoStyle']))
            
            # Notes
            if invoice_data.notes:
                story.append(Spacer(1, 15))
                story.append(Paragraph("Notes", self.styles['CustomSubHeader']))
                story.append(Paragraph(invoice_data.notes, self.styles['InfoStyle']))
            
            # Generate PDF
            pdf_bytes = self._generate_pdf_bytes(story)
            
            # Create filename
            customer_name = invoice_data.customer.name.replace(" ", "_")
            filename = f"invoice_{invoice_data.invoice_number}_{customer_name}.pdf"
            
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
                pdf_data=None,
                filename=None
            )
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about available PDF templates.
        
        Returns:
            Dictionary containing template information
        """
        return {
            "available_templates": ["prescription", "invoice"],
            "pdf_engine": "ReportLab",
            "supported_formats": ["PDF"],
            "features": [
                "Professional formatting",
                "Table layouts",
                "Custom styling",
                "Lambda compatible"
            ]
        }


# Global service instance
pdf_service = PDFGenerationService()