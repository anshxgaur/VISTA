import pandas as pd
import time

from storage.minio_storage import upload_dataframe_to_bucket
from config import SILVER_BUCKET

df = pd.DataFrame({
    "A": [1, 2, 3],
    "B": [4, 5, 6]
})

start = time.perf_counter()

upload_dataframe_to_bucket(
    df,
    SILVER_BUCKET,
    "speed_test.csv"
)

print(f"Upload Time = {time.perf_counter() - start:.2f} seconds")