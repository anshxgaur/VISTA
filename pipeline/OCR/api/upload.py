import traceback
import os

from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import time
import os
import shutil

from cleaning.duckdb_cleaner import load_csv

from preprocessing.text_extractor import extract_text

from cleaning.cleaner import clean_data
from ingestion.metadata import generate_metadata

from storage.minio_storage import (
    upload_dataframe_to_bucket,
    upload_text_to_bucket,
    upload_json_to_bucket,
    upload_file_to_bucket
)

from config import SILVER_BUCKET

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "Pipeline Running"
    }


@router.post("/upload")
async def upload(file: UploadFile = File(...)):

    total_start = time.perf_counter()
    temp_path = ""

    try:

        # ==========================================
        # Create temp folder
        # ==========================================

        os.makedirs("temp_uploads", exist_ok=True)

        temp_path = os.path.join(
            "temp_uploads",
            file.filename
        )

        # ==========================================
        # Save uploaded file
        # ==========================================

        t = time.perf_counter()

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✓ File Saved : {time.perf_counter()-t:.2f} sec")

        # ==========================================================
        # LARGE CSV
        # ==========================================================

        if file.filename.lower().endswith(".csv"):

            print("\nLarge CSV detected\n")

            validation_errors = []
            metadata = {}

            t = time.perf_counter()

            t_load = time.perf_counter()

            df = load_csv(temp_path)

            print(f"✓ DuckDB Load : {time.perf_counter()-t_load:.2f} sec")
            print(f"Rows Loaded : {len(df)}")

            # Keep existing pipeline unchanged
            t_clean = time.perf_counter()

            cleaned_df, validation_errors, dataset_type = clean_data(df)

            print(
                f"✓ Cleaning : {time.perf_counter()-t_clean:.2f} sec"
            )

            print(
                f"✓ CSV Processing : {time.perf_counter()-t:.2f} sec"
            )

            # -----------------------------
            # Merge all chunks
            # -----------------------------

            t = time.perf_counter()

            final_df = cleaned_df

            metadata = generate_metadata(
                file.filename,
                final_df,
                final_df,
                validation_errors
            )

            print(
                f"✓ Merge Time : {time.perf_counter()-t:.2f} sec"
            )

            # -----------------------------
            # Upload directly to MinIO
            # -----------------------------

            t = time.perf_counter()

            upload_dataframe_to_bucket(
                final_df,
                SILVER_BUCKET,
                "cleaned_" + file.filename
            )

            print(
                f"✓ Upload : {time.perf_counter()-t:.2f} sec"
            )

            total = time.perf_counter() - total_start

            if os.path.exists(temp_path):
                os.remove(temp_path)

            print("=" * 60)
            print(f"TOTAL TIME : {total:.2f} sec")
            print("=" * 60)

            return {
                "status": "success",
                "filename": file.filename,
                "storage": "Single cleaned CSV uploaded",
                "rows_processed": len(final_df),
                "chunks_processed": 1,
                "validation_errors": validation_errors,
                "metadata": metadata,
                "processing_time": f"{total:.2f} seconds"
            }

        # ==========================================================
        # OTHER FILES (PDF, TXT, IMAGE, JSON)
        # ==========================================================

        with open(temp_path, "rb") as f:
            file_bytes = f.read()

        t = time.perf_counter()

        extracted_data = extract_text(
            file.filename,
            file_bytes
        )

        print(
            f"✓ Extraction : {time.perf_counter()-t:.2f} sec"
        )

        t = time.perf_counter()

        cleaned_data, errors = clean_data(
            extracted_data
        )

        print(
            f"✓ Cleaning : {time.perf_counter()-t:.2f} sec"
        )

        metadata = generate_metadata(
            file.filename,
            extracted_data,
            cleaned_data,
            errors
        )

        if isinstance(cleaned_data, pd.DataFrame):

            upload_dataframe_to_bucket(
                cleaned_data,
                SILVER_BUCKET,
                file.filename + ".csv"
            )

            storage = "CSV uploaded"

        elif isinstance(cleaned_data, str):

            upload_text_to_bucket(
                cleaned_data,
                SILVER_BUCKET,
                file.filename + ".txt"
            )

            storage = "Text uploaded"

        elif isinstance(cleaned_data, dict):

            upload_json_to_bucket(
                cleaned_data,
                SILVER_BUCKET,
                file.filename + ".json"
            )

            storage = "JSON uploaded"

        else:

            storage = "Unsupported output"

        if os.path.exists(temp_path):
            os.remove(temp_path)

        total = time.perf_counter() - total_start

        print("=" * 60)
        print(f"TOTAL TIME : {total:.2f} sec")
        print("=" * 60)

        return {
            "status": "success",
            "filename": file.filename,
            "storage": storage,
            "validation_errors": errors,
            "metadata": metadata,
            "processing_time": f"{total:.2f} seconds"
        }

    except Exception as e:

        print("\n========== ERROR ==========")
        traceback.print_exc()
        print("===========================\n")

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )