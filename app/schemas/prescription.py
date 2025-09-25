"""
Prescription PDF Generation Schemas

This module defines Pydantic models for prescription PDF generation,
including patient information, doctor details, medications, vitals, tests, and response models.
"""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class VitalSigns(BaseModel):
    """
    Patient vital signs schema.
    
    Attributes:
        blood_pressure: Blood pressure reading (e.g., "140/90 mmHg")
        pulse: Pulse rate (e.g., "78 bpm")
        weight: Patient weight (e.g., "75 kg")
        temperature: Body temperature (e.g., "98.6°F")
        spo2: Oxygen saturation (e.g., "98%")
        height: Patient height (e.g., "170 cm")
    """
    blood_pressure: Optional[str] = Field(None, max_length=20, description="Blood pressure reading")
    pulse: Optional[str] = Field(None, max_length=20, description="Pulse rate")
    weight: Optional[str] = Field(None, max_length=20, description="Patient weight")
    temperature: Optional[str] = Field(None, max_length=20, description="Body temperature")
    spo2: Optional[str] = Field(None, max_length=20, description="Oxygen saturation")
    height: Optional[str] = Field(None, max_length=20, description="Patient height")


class PatientInfo(BaseModel):
    """
    Patient information schema for prescription generation.
    
    Attributes:
        name: Full name of the patient
        age: Patient's age in years
        gender: Patient's gender (Male/Female/Other)
        phone: Contact phone number
        address: Patient's address
        patient_id: Unique patient identifier
        vitals: Patient vital signs
    """
    name: str = Field(..., min_length=1, max_length=100, description="Patient's full name")
    age: int = Field(..., ge=0, le=150, description="Patient's age")
    gender: str = Field(..., description="Patient's gender")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=200, description="Patient's address")
    patient_id: Optional[str] = Field(None, max_length=50, description="Unique patient ID")
    vitals: Optional[VitalSigns] = Field(None, description="Patient vital signs")


class DoctorInfo(BaseModel):
    """
    Doctor information schema for prescription generation.
    
    Attributes:
        name: Doctor's full name
        qualifications: Medical qualifications (e.g., "MBBS, MD (Internal Medicine)")
        specialization: Medical specialization
        registration_number: Medical registration number
        clinic_name: Name of the clinic/hospital
        clinic_address: Clinic address
        phone: Doctor's contact number
        email: Doctor's email address
        website: Clinic website
        signature_url: URL to doctor's digital signature image
    """
    name: str = Field(..., min_length=1, max_length=100, description="Doctor's full name")
    qualifications: str = Field(..., min_length=1, max_length=200, description="Medical qualifications")
    specialization: str = Field(..., min_length=1, max_length=100, description="Medical specialization")
    registration_number: str = Field(..., min_length=1, max_length=50, description="Medical registration number")
    clinic_name: str = Field(..., min_length=1, max_length=100, description="Clinic/Hospital name")
    clinic_address: str = Field(..., min_length=1, max_length=300, description="Clinic address")
    phone: str = Field(..., max_length=20, description="Doctor's phone number")
    email: Optional[str] = Field(None, max_length=100, description="Doctor's email")
    website: Optional[str] = Field(None, max_length=100, description="Clinic website")
    signature_url: Optional[str] = Field(None, max_length=200, description="Digital signature image URL")


class Medication(BaseModel):
    """
    Medication schema for prescription items.
    
    Attributes:
        name: Medication name with strength (e.g., "Amlodipine 5mg")
        dosage: Dosage pattern (e.g., "1-0-0" for morning-afternoon-evening)
        timing: When to take (e.g., "Before Food", "After Food")
        duration: Duration of treatment (e.g., "30 days")
        start_date: When to start the medication
        note: Purpose or special instructions (e.g., "For BP control")
    """
    name: str = Field(..., min_length=1, max_length=100, description="Medication name with strength")
    dosage: str = Field(..., min_length=1, max_length=50, description="Dosage pattern (e.g., 1-0-0)")
    timing: str = Field(..., min_length=1, max_length=50, description="When to take medication")
    duration: str = Field(..., min_length=1, max_length=50, description="Duration of treatment")
    start_date: str = Field(..., min_length=1, max_length=20, description="Start date for medication")
    note: Optional[str] = Field(None, max_length=100, description="Purpose or special instructions")


class TestSuggested(BaseModel):
    """
    Medical test suggestion schema.
    
    Attributes:
        test_type: Type of medical test (e.g., "ECG (Electrocardiogram)")
    """
    test_type: str = Field(..., min_length=1, max_length=100, description="Type of medical test")


class Hyperlink(BaseModel):
    """
    Educational hyperlink schema.
    
    Attributes:
        title: Link title/description
        url: URL to the resource
    """
    title: str = Field(..., min_length=1, max_length=100, description="Link title")
    url: str = Field(..., min_length=1, max_length=200, description="URL to resource")


class Report(BaseModel):
    """
    Medical report schema.
    
    Attributes:
        filename: Report filename
        description: Brief description of the report
        url: URL to access the report
    """
    filename: str = Field(..., min_length=1, max_length=100, description="Report filename")
    description: Optional[str] = Field(None, max_length=200, description="Report description")
    url: Optional[str] = Field(None, max_length=200, description="URL to access report")


class PrescriptionRequest(BaseModel):
    """
    Complete prescription generation request schema.
    
    Attributes:
        patient: Patient information including vitals
        doctor: Doctor information with qualifications
        medications: List of prescribed medications
        symptoms: Patient symptoms
        tests_suggested: List of suggested medical tests
        hyperlinks: Educational links for patient
        reports: Medical reports and documents
        advice: Medical advice and instructions
        next_followup: Next appointment date
        prescription_date: Date of prescription
        consult_type: Type of consultation (In-Person, Online, etc.)
        prescription_id: Unique prescription identifier
    """
    patient: PatientInfo
    doctor: DoctorInfo
    medications: List[Medication] = Field(..., min_items=1, description="List of medications")
    symptoms: Optional[str] = Field(None, max_length=300, description="Patient symptoms")
    tests_suggested: Optional[List[TestSuggested]] = Field(None, description="Suggested medical tests")
    hyperlinks: Optional[List[Hyperlink]] = Field(None, description="Educational links")
    reports: Optional[List[Report]] = Field(None, description="Medical reports")
    advice: Optional[str] = Field(None, max_length=1000, description="Medical advice and instructions")
    next_followup: Optional[str] = Field(None, max_length=50, description="Next appointment date")
    prescription_date: str = Field(..., description="Prescription date")
    consult_type: Optional[str] = Field("In-Person", max_length=20, description="Type of consultation")
    prescription_id: Optional[str] = Field(None, max_length=50, description="Unique prescription ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient": {
                    "name": "Rajesh Kumar Patel",
                    "age": 45,
                    "gender": "Male",
                    "phone": "+91 98765 43210",
                    "patient_id": "P001",
                    "vitals": {
                        "blood_pressure": "140/90 mmHg",
                        "pulse": "78 bpm",
                        "weight": "75 kg",
                        "temperature": "98.6°F",
                        "spo2": "98%",
                        "height": "170 cm"
                    }
                },
                "doctor": {
                    "name": "Dr. Priya Sharma",
                    "qualifications": "MBBS, MD (Internal Medicine)",
                    "specialization": "Consultant Physician, Diabetologist",
                    "registration_number": "MH-12345-2018",
                    "clinic_name": "RaphaCure Medical Center",
                    "clinic_address": "VIBGYOR High school, 38/3, 6th cross, road, opp. Thomas Square, HSR Extension, Reliable Tranquil Layout, Bengaluru, Karnataka 560102",
                    "phone": "+91 95551 66000",
                    "email": "wellness@raphacure.com",
                    "website": "www.raphacure.com"
                },
                "medications": [
                    {
                        "name": "Amlodipine 5mg",
                        "dosage": "1-0-0",
                        "timing": "Before Food",
                        "duration": "30 days",
                        "start_date": "15-01-2024",
                        "note": "For BP control"
                    },
                    {
                        "name": "Metformin 500mg",
                        "dosage": "1-0-1",
                        "timing": "After Food",
                        "duration": "30 days",
                        "start_date": "15-01-2024",
                        "note": "For diabetes"
                    }
                ],
                "symptoms": "Chest pain, Shortness of breath, Fatigue, Dizziness",
                "tests_suggested": [
                    {"test_type": "ECG (Electrocardiogram)"},
                    {"test_type": "Lipid Profile"},
                    {"test_type": "HbA1c (Glycated Hemoglobin)"},
                    {"test_type": "Chest X-Ray"}
                ],
                "hyperlinks": [
                    {
                        "title": "Diabetes Care Guidelines",
                        "url": "https://www.raphacure.com/diabetes-care"
                    },
                    {
                        "title": "Heart Health Tips",
                        "url": "https://www.raphacure.com/heart-health"
                    }
                ],
                "reports": [
                    {
                        "filename": "Blood Test Report - 10-01-2024.pdf",
                        "description": "Complete blood count and metabolic panel results"
                    },
                    {
                        "filename": "ECG Report - 12-01-2024.pdf",
                        "description": "Electrocardiogram showing normal sinus rhythm"
                    }
                ],
                "advice": "1. Take medications as prescribed at the same time daily\\n2. Monitor blood pressure and blood sugar levels regularly\\n3. Follow a low-sodium, diabetic-friendly diet\\n4. Engage in moderate exercise for 30 minutes daily\\n5. Avoid smoking and limit alcohol consumption\\n6. Get adequate sleep (7-8 hours per night)\\n7. Manage stress through relaxation techniques\\n8. Return immediately if chest pain worsens or new symptoms develop",
                "next_followup": "15-02-2024 (Thursday)",
                "prescription_date": "15-01-2024",
                "consult_type": "In-Person",
                "prescription_id": "RX001"
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