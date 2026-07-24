import uuid
import hashlib
import asyncio
import io
import re
import boto3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker

# OCR Libraries
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# NLP / PII Masking Library
import spacy

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: 'en_core_web_sm' model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

# ======================================================
# FastAPI App
# ======================================================

app = FastAPI(title="Vista Ingestion & Pipeline Service")

# ======================================================
# MinIO Configuration
# ======================================================

s3_client = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

BUCKET_NAME = "raw-report"

try:
    existing_buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
    if BUCKET_NAME not in existing_buckets:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    print(f"MinIO Warning: {e}")

# ======================================================
# Database Configuration (SQLite with WAL & Timeout Fix)
# ======================================================

DATABASE_URL = "sqlite:///./pipeline.db"

# Added timeout=30 to allow SQLite to wait for locks to clear
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# ======================================================
# Enable WAL Mode on Startup (Prevents Database Locks)
# ======================================================

@app.on_event("startup")
def startup_db():
    with engine.connect() as connection:
        connection.execute(text("PRAGMA journal_mode=WAL;"))

# ======================================================
# Database Model
# ======================================================

class ReportTracker(Base):
    __tablename__ = "pipeline_tracking"

    upload_id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    file_hash = Column(String, index=True, nullable=False)
    status = Column(String, default="PROCESSING")
    current_step = Column(String, default="Ingestion")
    progress_pct = Column(Integer, default=10)
    extracted_text = Column(Text, nullable=True)  # Raw OCR Output
    masked_text = Column(Text, nullable=True)     # Anonymized Text
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ======================================================
# Helper Functions
# ======================================================

def calculate_sha256(file_bytes: bytes) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

def perform_ocr(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    text_content = ""

    try:
        if ext in ['png', 'jpg', 'jpeg', 'bmp', 'tiff']:
            image = Image.open(io.BytesIO(file_bytes))
            text_content = pytesseract.image_to_string(image)
        elif ext == 'pdf':
            images = convert_from_bytes(file_bytes)
            pages_text = [pytesseract.image_to_string(img) for img in images]
            text_content = "\n--- PAGE BREAK ---\n".join(pages_text)
        else:
            text_content = file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        text_content = f"[OCR Extraction Error: {str(e)}]"

    return text_content.strip()

def mask_pii(text: str) -> str:
    """Anonymizes text using Regex rules and spaCy NER."""
    if not text:
        return ""

    sanitized = text

    # 1. Regex Masking (Structured Data)
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\b(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'

    sanitized = re.sub(email_pattern, '[EMAIL_REDACTED]', sanitized)
    sanitized = re.sub(phone_pattern, '[PHONE_REDACTED]', sanitized)
    sanitized = re.sub(date_pattern, '[DATE_REDACTED]', sanitized)

    # 2. spaCy NER Masking (Names, Organizations, Locations)
    if nlp:
        doc = nlp(sanitized)
        entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
        for ent in entities:
            if ent.label_ == "PERSON":
                sanitized = sanitized[:ent.start_char] + "[NAME_REDACTED]" + sanitized[ent.end_char:]
            elif ent.label_ == "ORG":
                sanitized = sanitized[:ent.start_char] + "[ORG_REDACTED]" + sanitized[ent.end_char:]
            elif ent.label_ in ["GPE", "LOC"]:
                sanitized = sanitized[:ent.start_char] + "[LOCATION_REDACTED]" + sanitized[ent.end_char:]

    return sanitized

def update_tracker(upload_id: str, **kwargs):
    """Safely updates a tracking record using short-lived DB sessions."""
    with SessionLocal() as db:
        record = db.query(ReportTracker).filter(ReportTracker.upload_id == upload_id).first()
        if record:
            for key, value in kwargs.items():
                setattr(record, key, value)
            db.commit()

# ======================================================
# Upload Endpoint with Non-Blocking Atomic DB Sessions
# ======================================================

@app.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    upload_id = str(uuid.uuid4())
    
    try:
        # STEP 1: Ingestion
        file_bytes = await file.read()
        file_hash = calculate_sha256(file_bytes)
        
        extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
        stored_filename = f"{upload_id}.{extension}"

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=stored_filename,
            Body=file_bytes,
            ContentType=file.content_type or "application/octet-stream"
        )

        with SessionLocal() as db:
            record = ReportTracker(
                upload_id=upload_id,
                file_name=file.filename,
                file_hash=file_hash,
                status="PROCESSING",
                current_step="Ingestion",
                progress_pct=10
            )
            db.add(record)
            db.commit()

        # STEP 2: SHA256 Duplicate Check
        await asyncio.sleep(1)
        with SessionLocal() as db:
            existing_report = db.query(ReportTracker).filter(
                ReportTracker.file_hash == file_hash, 
                ReportTracker.upload_id != upload_id
            ).first()

        if existing_report:
            update_tracker(
                upload_id, 
                status="SKIPPED_DUPLICATE", 
                current_step="SHA256 Check", 
                progress_pct=100
            )
            return {
                "status": "SKIPPED_DUPLICATE",
                "message": "Duplicate report detected via SHA256 hash.",
                "upload_id": upload_id
            }

        update_tracker(upload_id, current_step="SHA256 Check", progress_pct=30)

        # STEP 3: OCR Engine Execution
        update_tracker(upload_id, current_step="OCR Engine", progress_pct=50)
        extracted_text = perform_ocr(file_bytes, file.filename)
        update_tracker(upload_id, extracted_text=extracted_text)

        # STEP 4: PII Masking Execution
        update_tracker(upload_id, current_step="PII Masking", progress_pct=70)
        masked_text = mask_pii(extracted_text)
        update_tracker(upload_id, masked_text=masked_text)

        # STEP 5 & 6: Pipeline Completion
        await asyncio.sleep(1)
        update_tracker(
            upload_id, 
            current_step="Embeddings", 
            status="COMPLETED", 
            progress_pct=100
        )

        return {
            "status": "SUCCESS",
            "upload_id": upload_id,
            "original_name": file.filename,
            "raw_text_snippet": extracted_text[:150],
            "masked_text_snippet": masked_text[:150]
        }

    except Exception as e:
        update_tracker(upload_id, status="FAILED")
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================
# Status & Inspection API
# ======================================================

@app.get("/api/pipeline-status")
def get_pipeline_status():
    with SessionLocal() as db:
        records = (
            db.query(ReportTracker)
            .order_by(ReportTracker.created_at.desc())
            .all()
        )
        return [
            {
                "upload_id": r.upload_id,
                "file_name": r.file_name,
                "status": r.status or "UNKNOWN",
                "current_step": r.current_step or "Ingestion",
                "progress_pct": r.progress_pct or 0,
                "created_at": r.created_at.strftime("%H:%M:%S") if r.created_at else datetime.utcnow().strftime("%H:%M:%S"),
                "raw_snippet": (r.extracted_text[:80] + "...") if r.extracted_text else "Awaiting extraction...",
                "masked_snippet": (r.masked_text[:80] + "...") if r.masked_text else "Awaiting redaction..."
            }
            for r in records
        ]

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>dashboard.html not found</h1>"

@app.get("/")
def root():
    return {"service": "Vista Ingestion Service", "status": "Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
