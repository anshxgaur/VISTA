import boto3
import io
import json
import os
import tempfile

from boto3.s3.transfer import TransferConfig

from config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY
)

# ==========================================================
# Create MinIO Client
# ==========================================================

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

# ==========================================================
# Multipart Upload Configuration
# ==========================================================

transfer_config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,      # 8 MB
    multipart_chunksize=8 * 1024 * 1024,      # 8 MB
    max_concurrency=8,                        # parallel threads
    use_threads=True
)


# ==========================================================
# Upload DataFrame
# ==========================================================

import time
import io

def upload_dataframe_to_bucket(
    dataframe,
    bucket_name,
    object_name
):
    """
    Upload dataframe to MinIO with detailed timing.
    """

    # -----------------------
    # Convert DataFrame -> CSV
    # -----------------------
    t = time.perf_counter()

    buffer = io.BytesIO()

    dataframe.to_csv(
        buffer,
        index=False,
        encoding="utf-8"
    )

    buffer.seek(0)

    print(
        f"CSV Conversion : {time.perf_counter()-t:.2f} sec"
    )

    # -----------------------
    # Upload to MinIO
    # -----------------------
    t = time.perf_counter()

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=buffer,
        ContentType="text/csv"
    )

    print(
        f"MinIO Upload : {time.perf_counter()-t:.2f} sec"
    )

    print(f"Uploaded CSV -> {bucket_name}/{object_name}")
    """
    Upload a pandas DataFrame to MinIO using multipart upload.
    """

    with tempfile.NamedTemporaryFile(
        suffix=".csv",
        delete=False
    ) as temp:

        dataframe.to_csv(
            temp.name,
            index=False
        )

        temp.flush()

        s3_client.upload_file(
            temp.name,
            bucket_name,
            object_name,
            Config=transfer_config
        )

    os.remove(temp.name)

    print(f"Uploaded CSV -> {bucket_name}/{object_name}")


# ==========================================================
# Upload Existing Local File
# ==========================================================

def upload_file_to_bucket(
    local_file_path,
    bucket_name,
    object_name
):
    """
    Upload an existing file using multipart upload.
    """

    s3_client.upload_file(
        local_file_path,
        bucket_name,
        object_name,
        Config=transfer_config
    )

    print(f"Uploaded {object_name} -> {bucket_name}")


# ==========================================================
# Upload Text
# ==========================================================

def upload_text_to_bucket(
    text,
    bucket_name,
    object_name
):
    """
    Upload extracted text.
    """

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=text.encode("utf-8"),
        ContentType="text/plain"
    )

    print(f"Uploaded Text -> {bucket_name}/{object_name}")


# ==========================================================
# Upload JSON
# ==========================================================

def upload_json_to_bucket(
    data,
    bucket_name,
    object_name
):
    """
    Upload JSON.
    """

    json_buffer = json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_name,
        Body=json_buffer.encode("utf-8"),
        ContentType="application/json"
    )

    print(f"Uploaded JSON -> {bucket_name}/{object_name}")


# ==========================================================
# Download File
# ==========================================================

def download_file_from_bucket(
    bucket_name,
    object_name
):
    """
    Download a file from MinIO.
    """

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_name
    )

    return response["Body"].read()


# ==========================================================
# List Objects
# ==========================================================

def list_bucket_objects(
    bucket_name
):
    """
    List all files in a bucket.
    """

    response = s3_client.list_objects_v2(
        Bucket=bucket_name
    )

    if "Contents" not in response:
        return []

    return [obj["Key"] for obj in response["Contents"]]


# ==========================================================
# Bucket Exists
# ==========================================================

def bucket_exists(
    bucket_name
):
    """
    Check whether bucket exists.
    """

    try:
        s3_client.head_bucket(
            Bucket=bucket_name
        )
        return True

    except Exception:
        return False


# ==========================================================
# Create Bucket
# ==========================================================

def create_bucket(
    bucket_name
):
    """
    Create bucket if it does not exist.
    """

    if not bucket_exists(bucket_name):

        s3_client.create_bucket(
            Bucket=bucket_name
        )

        print(f"Bucket '{bucket_name}' created.")

    else:

        print(f"Bucket '{bucket_name}' already exists.")