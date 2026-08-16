from models.schema import Patient, Document, MedicalRecord


patient = Patient(
    patientid=1,
    firstname="Aditi",
    lastname="Sharma",
    age=20,
    gender="F"
)


document = Document(
    filename="sample.pdf",
    file_type="digital_pdf",
    extracted_text="Patient report"
)


record = MedicalRecord(
    patient=patient,
    document=document,
    diagnosis="Normal"
)


print(record)