import uuid
import hashlib
import asyncio
import boto3
from config import *
from cleaning.validate import validate_dataframe
from cleaning.normalize import normalize_dataframe
from cleaning.standardize import standardize_dataframe
from cleaning.duplicate import remove_duplicates
from preprocessing.image_reader import extract_from_image
from preprocessing.pdf_reader import extract_from_pdf
from preprocessing.scanned_pdf import extract_from_scanned_pdf
from preprocessing.csv_reader import read_csv
from preprocessing.json_reader import read_json
from preprocessing.dataset_detector import detect_dataset
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from storage.minio_storage import upload_dataframe_to_bucket

# Import our masking module
from cleaning.masking import mask_pii

# ======================================================
# FastAPI App
# ======================================================

app = FastAPI(title="Vista Ingestion & Pipeline Service")

# ======================================================
# MinIO Configuration
# ======================================================

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

BUCKET_NAME = BRONZE_BUCKET
try:
    existing_buckets = [
        bucket["Name"]
        for bucket in s3_client.list_buckets().get("Buckets", [])
    ]

    required_buckets = [
        BRONZE_BUCKET,
        SILVER_BUCKET,
        REJECTED_BUCKET
    ]

    for bucket in required_buckets:
        if bucket not in existing_buckets:
            s3_client.create_bucket(Bucket=bucket)

except Exception as e:
    print(f"MinIO Warning: {e}")

# ======================================================
# Database Configuration (SQLite with WAL & Timeout Fix)
# ======================================================



# Added timeout=30 to allow SQLite to wait for locks to clear
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
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

        extension = file.filename.lower().split(".")[-1]

        if extension == "csv":
            dataframe = read_csv(file_bytes)

            # Automatically detect dataset type from CSV columns
            dataset_type = detect_dataset(dataframe)

            if dataset_type is None:

                raise HTTPException(
                    status_code=400,
                    detail="Unknown dataset type"
                )

            errors = validate_dataframe(
                dataframe,
                dataset_type
            )

            if errors:

                # Store invalid file in Rejected bucket
                s3_client.put_object(
                    Bucket=REJECTED_BUCKET,
                    Key=stored_filename,
                    Body=file_bytes,
                    ContentType=file.content_type or "application/octet-stream"
                )

                update_tracker(
                    upload_id,
                    status="REJECTED",
                    current_step="Validation Failed",
                    progress_pct=100
                )

                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": "Validation failed",
                        "errors": errors
                    }
                )

            dataframe = normalize_dataframe(dataframe)
            dataframe = standardize_dataframe(dataframe)
            dataframe, removed = remove_duplicates(dataframe)

            upload_dataframe_to_bucket(
                dataframe,
                SILVER_BUCKET,
                stored_filename
            )

            extracted_text = dataframe.to_string(index=False)

        elif extension == "json":
            json_data = read_json(file_bytes)
            extracted_text = str(json_data)

        elif extension == "pdf":
            extracted_text = extract_from_pdf(file_bytes)

            if not extracted_text.strip():
                extracted_text = extract_from_scanned_pdf(file_bytes)

        elif extension in ["png", "jpg", "jpeg", "bmp", "tiff"]:
            extracted_text = extract_from_image(file_bytes)

        else:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")

        update_tracker(upload_id, extracted_text=extracted_text)

        # STEP 4: PII Masking Execution
        update_tracker(upload_id, current_step="PII Masking", progress_pct=70)
        masked_text = mask_pii(extracted_text)
        update_tracker(upload_id, masked_text=masked_text)

        # STEP 5 & 6: Pipeline Completion
        await asyncio.sleep(1)
        update_tracker(
            upload_id, 
            current_step="Completed", 
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
