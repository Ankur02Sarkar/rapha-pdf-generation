"""
Prescription PDF Generation Schemas

This module defines Pydantic models for prescription PDF generation,
including patient information, doctor details, medications, and response models.
"""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PatientInfo(BaseModel):
    """
    Patient information schema for prescription generation.
    
    Attributes:
        name: Full name of the patient
        age: Patient's age in years
        gender: Patient's gender (M/F/Other)
        phone: Contact phone number
        address: Patient's address
        patient_id: Unique patient identifier
    """
    name: str = Field(..., min_length=1, max_length=100, description="Patient's full name")
    age: int = Field(..., ge=0, le=150, description="Patient's age")
    gender: str = Field(..., pattern="^(M|F|Other)$", description="Patient's gender")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=200, description="Patient's address")
    patient_id: Optional[str] = Field(None, max_length=50, description="Unique patient ID")


class DoctorInfo(BaseModel):
    """
    Doctor information schema for prescription generation.
    
    Attributes:
        name: Doctor's full name
        specialization: Medical specialization
        license_number: Medical license number
        clinic_name: Name of the clinic/hospital
        clinic_address: Clinic address
        phone: Doctor's contact number
        email: Doctor's email address
    """
    name: str = Field(..., min_length=1, max_length=100, description="Doctor's full name")
    specialization: str = Field(..., min_length=1, max_length=100, description="Medical specialization")
    license_number: str = Field(..., min_length=1, max_length=50, description="Medical license number")
    clinic_name: str = Field(..., min_length=1, max_length=100, description="Clinic/Hospital name")
    clinic_address: str = Field(..., min_length=1, max_length=200, description="Clinic address")
    phone: str = Field(..., max_length=20, description="Doctor's phone number")
    email: Optional[str] = Field(None, max_length=100, description="Doctor's email")


class Medication(BaseModel):
    """
    Medication schema for prescription items.
    
    Attributes:
        name: Medication name
        dosage: Dosage information
        frequency: How often to take the medication
        duration: Duration of treatment
        instructions: Special instructions for the medication
        quantity: Quantity to be dispensed
    """
    name: str = Field(..., min_length=1, max_length=100, description="Medication name")
    dosage: str = Field(..., min_length=1, max_length=50, description="Dosage (e.g., 500mg)")
    frequency: str = Field(..., min_length=1, max_length=50, description="Frequency (e.g., twice daily)")
    duration: str = Field(..., min_length=1, max_length=50, description="Duration (e.g., 7 days)")
    instructions: Optional[str] = Field(None, max_length=200, description="Special instructions")
    quantity: Optional[str] = Field(None, max_length=20, description="Quantity to dispense")


class PrescriptionRequest(BaseModel):
    """
    Complete prescription generation request schema.
    
    Attributes:
        patient: Patient information
        doctor: Doctor information
        medications: List of prescribed medications
        diagnosis: Medical diagnosis
        prescription_date: Date of prescription
        notes: Additional notes or instructions
        prescription_id: Unique prescription identifier
    """
    patient: PatientInfo
    doctor: DoctorInfo
    medications: List[Medication] = Field(..., min_items=1, description="List of medications")
    diagnosis: Optional[str] = Field(None, max_length=200, description="Medical diagnosis")
    prescription_date: date = Field(default_factory=date.today, description="Prescription date")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    prescription_id: Optional[str] = Field(None, max_length=50, description="Unique prescription ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient": {
                    "name": "John Doe",
                    "age": 35,
                    "gender": "M",
                    "phone": "+1234567890",
                    "address": "123 Main St, City, State",
                    "patient_id": "P001"
                },
                "doctor": {
                    "name": "Dr. Jane Smith",
                    "specialization": "General Medicine",
                    "license_number": "MD12345",
                    "clinic_name": "City Medical Center",
                    "clinic_address": "456 Health Ave, City, State",
                    "phone": "+1987654321",
                    "email": "dr.smith@clinic.com"
                },
                "medications": [
                    {
                        "name": "Amoxicillin",
                        "dosage": "500mg",
                        "frequency": "Three times daily",
                        "duration": "7 days",
                        "instructions": "Take with food",
                        "quantity": "21 tablets"
                    }
                ],
                "diagnosis": "Upper respiratory tract infection",
                "notes": "Follow up in 1 week if symptoms persist"
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