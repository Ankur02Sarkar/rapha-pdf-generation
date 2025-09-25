"""
Invoice PDF Generation Schemas

This module defines Pydantic models for invoice PDF generation,
including business information, customer details, line items, and response models.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class BusinessInfo(BaseModel):
    """
    Business information schema for invoice generation.
    
    Attributes:
        name: Business name
        address: Business address
        phone: Business phone number
        email: Business email
        website: Business website
        tax_id: Tax identification number
        logo_url: URL to business logo (optional)
    """
    name: str = Field(..., min_length=1, max_length=100, description="Business name")
    address: str = Field(..., min_length=1, max_length=200, description="Business address")
    phone: str = Field(..., max_length=20, description="Business phone number")
    email: str = Field(..., max_length=100, description="Business email")
    website: Optional[str] = Field(None, max_length=100, description="Business website")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID number")
    logo_url: Optional[str] = Field(None, max_length=200, description="Logo URL")


class CustomerInfo(BaseModel):
    """
    Customer information schema for invoice generation.
    
    Attributes:
        name: Customer name (individual or company)
        address: Customer address
        phone: Customer phone number
        email: Customer email
        customer_id: Unique customer identifier
        tax_id: Customer tax ID (for businesses)
    """
    name: str = Field(..., min_length=1, max_length=100, description="Customer name")
    address: str = Field(..., min_length=1, max_length=200, description="Customer address")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    email: Optional[str] = Field(None, max_length=100, description="Customer email")
    customer_id: Optional[str] = Field(None, max_length=50, description="Customer ID")
    tax_id: Optional[str] = Field(None, max_length=50, description="Customer tax ID")


class InvoiceItem(BaseModel):
    """
    Invoice line item schema.
    
    Attributes:
        description: Item description
        quantity: Quantity of items
        unit_price: Price per unit
        discount_percent: Discount percentage (0-100)
        tax_percent: Tax percentage (0-100)
        total: Total amount for this line item
    """
    description: str = Field(..., min_length=1, max_length=200, description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    discount_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Discount %")
    tax_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100, description="Tax %")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal before discount and tax."""
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        return self.subtotal * (self.discount_percent / 100)
    
    @property
    def taxable_amount(self) -> Decimal:
        """Calculate amount after discount, before tax."""
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.taxable_amount * (self.tax_percent / 100)
    
    @property
    def total(self) -> Decimal:
        """Calculate total amount including tax."""
        return self.taxable_amount + self.tax_amount


class PaymentInfo(BaseModel):
    """
    Payment information schema.
    
    Attributes:
        payment_terms: Payment terms (e.g., "Net 30")
        due_date: Payment due date
        payment_method: Preferred payment method
        bank_details: Bank account details for payment
        notes: Additional payment notes
    """
    payment_terms: str = Field(default="Net 30", max_length=50, description="Payment terms")
    due_date: date = Field(..., description="Payment due date")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method")
    bank_details: Optional[str] = Field(None, max_length=200, description="Bank details")
    notes: Optional[str] = Field(None, max_length=300, description="Payment notes")


class InvoiceRequest(BaseModel):
    """
    Complete invoice generation request schema.
    
    Attributes:
        business: Business information
        customer: Customer information
        items: List of invoice items
        payment_info: Payment information
        invoice_number: Invoice number
        invoice_date: Invoice date
        currency: Currency code (e.g., USD, EUR)
        notes: Additional notes
        discount_percent: Overall invoice discount
        tax_percent: Overall invoice tax
    """
    business: BusinessInfo
    customer: CustomerInfo
    items: List[InvoiceItem] = Field(..., min_items=1, description="Invoice items")
    payment_info: PaymentInfo
    invoice_number: str = Field(..., min_length=1, max_length=50, description="Invoice number")
    invoice_date: date = Field(default_factory=date.today, description="Invoice date")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate total before tax."""
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_discount(self) -> Decimal:
        """Calculate total discount amount."""
        return sum(item.discount_amount for item in self.items)
    
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(item.tax_amount for item in self.items)
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate final total amount."""
        return sum(item.total for item in self.items)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business": {
                    "name": "Tech Solutions Inc.",
                    "address": "123 Business Ave, Tech City, TC 12345",
                    "phone": "+1-555-0123",
                    "email": "billing@techsolutions.com",
                    "website": "www.techsolutions.com",
                    "tax_id": "TAX123456789"
                },
                "customer": {
                    "name": "ABC Corporation",
                    "address": "456 Client St, Business City, BC 67890",
                    "phone": "+1-555-0456",
                    "email": "accounts@abccorp.com",
                    "customer_id": "CUST001"
                },
                "items": [
                    {
                        "description": "Web Development Services",
                        "quantity": "40",
                        "unit_price": "75.00",
                        "tax_percent": "8.5"
                    },
                    {
                        "description": "Domain Registration",
                        "quantity": "1",
                        "unit_price": "15.00",
                        "tax_percent": "8.5"
                    }
                ],
                "payment_info": {
                    "payment_terms": "Net 30",
                    "due_date": "2024-02-15",
                    "payment_method": "Bank Transfer",
                    "bank_details": "Account: 1234567890, Routing: 987654321"
                },
                "invoice_number": "INV-2024-001",
                "currency": "USD",
                "notes": "Thank you for your business!"
            }
        }
    )


class PDFResponse(BaseModel):
    """
    PDF generation response schema.
    
    Attributes:
        success: Whether PDF generation was successful
        message: Response message
        pdf_data: Base64 encoded PDF data
        filename: Suggested filename for the PDF
        content_type: MIME type of the response
        size_bytes: Size of the generated PDF in bytes
    """
    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    pdf_data: Optional[str] = Field(None, description="Base64 encoded PDF data")
    filename: Optional[str] = Field(None, description="Suggested filename")
    content_type: str = Field(default="application/pdf", description="MIME type")
    size_bytes: Optional[int] = Field(None, description="PDF size in bytes")

    model_config = ConfigDict(from_attributes=True)