from pydantic import BaseModel
from typing import Optional


class Patient(BaseModel):
    patientid: int
    firstname: str
    lastname: Optional[str] = None
    age: int
    gender: str


class Document(BaseModel):
    filename: str
    file_type: str
    extracted_text: Optional[str] = None


class MedicalRecord(BaseModel):
    patient: Patient
    document: Document
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None