import os

# MinIO Configuration

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")

MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

# Buckets
BRONZE_BUCKET = "bronze"
SILVER_BUCKET = "silver"
REJECTED_BUCKET = "rejected"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pipeline.db")

MAX_FILE_SIZE = 100 * 1024 * 1024   # 100 MB

SUPPORTED_FILES = [
    ".csv",
    ".json",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
]