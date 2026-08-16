import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

import base64
import json

from ingestion.uploader import create_filename
from ingestion.uploader import create_filename
from ingestion.minio_client import client
from config import (
    BRONZE_BUCKET,
    MAX_FILE_SIZE,
    SUPPORTED_FILES
)

from kafka import KafkaProducer


# ============================================================
# Kafka Configuration
# ============================================================

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "hospital-files"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(
        value
    ).encode("utf-8")
)


# ============================================================
# Upload File
# ============================================================

def upload_file(file_path: str):

    file_path = Path(file_path)

    # --------------------------------------------------------
    # 1. Check file exists
    # --------------------------------------------------------

    if not file_path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    # --------------------------------------------------------
    # 2. Check file extension
    # --------------------------------------------------------

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_FILES:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    # --------------------------------------------------------
    # 3. Check file size
    # --------------------------------------------------------

    file_size = file_path.stat().st_size

    if file_size > MAX_FILE_SIZE:

        raise ValueError(
            "File exceeds maximum allowed size."
        )

    # --------------------------------------------------------
    # 4. Generate unique filename
    # --------------------------------------------------------

    stored_filename = create_filename(
        file_path.name
    )

    # --------------------------------------------------------
    # 5. Read file
    # --------------------------------------------------------

    file_bytes = file_path.read_bytes()

    # --------------------------------------------------------
    # 6. Store original file in MinIO Bronze
    # --------------------------------------------------------

    from io import BytesIO

    client.put_object(
        BRONZE_BUCKET,
        stored_filename,
        BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=get_content_type(extension)
    )

    print(
        f"File stored in MinIO Bronze: "
        f"{stored_filename}"
    )

    # --------------------------------------------------------
    # 7. Determine file type
    # --------------------------------------------------------

    file_type = detect_file_type(
        extension
    )

    # --------------------------------------------------------
    # 8. Send file to Kafka
    # --------------------------------------------------------

    message = {

        "file_name": stored_filename,

        "original_file_name": file_path.name,

        "file_type": file_type,

        "content_type": get_content_type(
            extension
        ),

        "file_size": file_size,

        "image_data": base64.b64encode(
            file_bytes
        ).decode("utf-8")
        if file_type == "image"
        else None
    }

    producer.send(
        TOPIC_NAME,
        value=message
    )

    producer.flush()

    print(
        "File sent successfully to Kafka!"
    )

    print(
        f"Kafka topic: {TOPIC_NAME}"
    )

    return message


# ============================================================
# Detect File Type
# ============================================================

def detect_file_type(extension):

    if extension in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        return "image"

    elif extension == ".pdf":

        return "pdf"

    elif extension == ".csv":

        return "csv"

    elif extension == ".json":

        return "json"

    elif extension == ".txt":

        return "txt"

    else:

        return "unsupported"


# ============================================================
# Content Type
# ============================================================

def get_content_type(extension):

    content_types = {

        ".png": "image/png",

        ".jpg": "image/jpeg",

        ".jpeg": "image/jpeg",

        ".pdf": "application/pdf",

        ".csv": "text/csv",

        ".json": "application/json",

        ".txt": "text/plain"
    }

    return content_types.get(
        extension,
        "application/octet-stream"
    )


# ============================================================
# Command Line Test
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python ingestion/upload_service.py "
            "<file_path>"
        )

        sys.exit(1)

    upload_file(sys.argv[1])