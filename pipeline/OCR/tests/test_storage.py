import pandas as pd

from storage.minio_storage import upload_dataframe_to_bucket
from config import SILVER_BUCKET

df = pd.DataFrame(
    {
        "patientid": [1, 2],
        "firstname": ["Aditi", "Rahul"],
        "lastname": ["Sharma", "Verma"],
        "age": [20, 30],
        "gender": ["F", "M"],
    }
)

upload_dataframe_to_bucket(
    df,
    SILVER_BUCKET,
    "patients.csv"
)

print("Upload Successful!")