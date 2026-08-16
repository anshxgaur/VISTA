from minio import Minio
from config import *

client = Minio(
    "localhost:9000",
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

if not client.bucket_exists(BRONZE_BUCKET):
    client.make_bucket(BRONZE_BUCKET)