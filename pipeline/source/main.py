import uuid
import hashlib
import asyncio
import boto3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

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

# Ensure MinIO bucket exists
try:
    existing_buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
    if BUCKET_NAME not in existing_buckets:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    print(f"MinIO Warning: Could not verify/create bucket automatically. Ensure MinIO is running. Error: {e}")

# ======================================================
# Database Configuration (SQLite)
# ======================================================

DATABASE_URL = "sqlite:///./pipeline.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

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
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ======================================================
# Helper Functions
# ======================================================

def calculate_sha256(file_bytes: bytes) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()

# ======================================================
# Upload Endpoint (Full ETL Simulation Stream)
# ======================================================

@app.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    db = SessionLocal()
    upload_id = str(uuid.uuid4())
    
    try:
        # Step 1: Ingestion
        file_bytes = await file.read()
        file_hash = calculate_sha256(file_bytes)
        
        extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
        stored_filename = f"{upload_id}.{extension}"

        # Upload binary stream to MinIO
        file.file.seek(0)
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            stored_filename,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"}
        )

        # Create tracking entry in SQLite
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

        # Step 2: SHA256 Duplicate Check
        await asyncio.sleep(2)  # Pause for dashboard laser animation
        existing_report = db.query(ReportTracker).filter(
            ReportTracker.file_hash == file_hash, 
            ReportTracker.upload_id != upload_id
        ).first()

        if existing_report:
            record.status = "SKIPPED_DUPLICATE"
            record.current_step = "SHA256 Check"
            record.progress_pct = 100
            db.commit()
            return {
                "status": "SKIPPED_DUPLICATE",
                "message": "Duplicate report detected via SHA256 hash.",
                "upload_id": upload_id,
                "file_hash": file_hash
            }

        record.current_step = "SHA256 Check"
        record.progress_pct = 30
        db.commit()

        # Step 3: OCR Phase Simulation
        await asyncio.sleep(3)
        record.current_step = "OCR Engine"
        record.progress_pct = 60
        db.commit()

        # Step 4: Complete Pipeline
        await asyncio.sleep(2)
        record.current_step = "Embeddings"
        record.status = "COMPLETED"
        record.progress_pct = 100
        db.commit()

        return {
            "status": "SUCCESS",
            "upload_id": upload_id,
            "original_name": file.filename,
            "file_hash": file_hash,
            "storage_path": f"{BUCKET_NAME}/{stored_filename}"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ======================================================
# Pipeline Status API
# ======================================================

@app.get("/api/pipeline-status")
def get_pipeline_status():
    db = SessionLocal()
    try:
        records = (
            db.query(ReportTracker)
            .order_by(ReportTracker.created_at.desc())
            .all()
        )
        return [
            {
                "upload_id": r.upload_id,
                "file_name": r.file_name,
                "status": r.status,
                "current_step": r.current_step,
                "progress_pct": r.progress_pct,
                "created_at": r.created_at.strftime("%H:%M:%S"),
            }
            for r in records
        ]
    finally:
        db.close()

# ======================================================
# Dashboard UI
# ======================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Dashboard</h1>
        <p>dashboard.html not found in project root folder.</p>
        """

# ======================================================
# Root Endpoint
# ======================================================

@app.get("/")
def root():
    return {
        "service": "Vista Ingestion Service",
        "status": "Running",
        "dashboard": "http://localhost:8001/dashboard",
        "docs": "http://localhost:8001/docs"
    }

# ======================================================
# Run Server
# ======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
