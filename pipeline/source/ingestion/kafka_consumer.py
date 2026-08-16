import sys
from pathlib import Path

# Allow imports from the source folder
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from kafka import KafkaConsumer
import json
import base64

from preprocessing.ocr_reader import extract_text_from_image
from preprocessing.ocr_structurer import (
    detect_ocr_dataset,
    structure_ocr_text
)
from cleaning.cleaner import clean_data


KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "hospital-files"


consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="vista2-ocr-consumer",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    )
)


print("VISTA2 OCR Kafka Consumer started...")
print("Waiting for images...")


for message in consumer:

    data = message.value

    print("\n========================================")
    print("Message received!")
    print(f"File: {data.get('file_name')}")
    print(f"Type: {data.get('file_type')}")
    print("========================================")

    # Only process images
    if data.get("file_type") != "image":
        print("Not an image. Skipping...")
        continue

    try:

        # -----------------------------------------
        # STEP 1: Decode image
        # -----------------------------------------

        image_bytes = base64.b64decode(
            data["image_data"]
        )

        print("Image received successfully.")

        # -----------------------------------------
        # STEP 2: OCR
        # -----------------------------------------

        print("Running OCR...")

        extracted_text = extract_text_from_image(
            image_bytes
        )

        print("\n========== OCR OUTPUT ==========")
        print(extracted_text)
        print("================================")

        if not extracted_text.strip():

            print("OCR returned no text.")
            print("Skipping this image.")
            continue

        # -----------------------------------------
        # STEP 3: Detect dataset
        # -----------------------------------------

        print("\nDetecting hospital dataset type...")

        dataset_type = detect_ocr_dataset(
            extracted_text
        )

        if dataset_type is None:

            print(
                "Could not identify hospital dataset."
            )

            print(
                "Image will not be structured."
            )

            continue

        print(
            f"Dataset detected: {dataset_type}"
        )

        # -----------------------------------------
        # STEP 4: Structure OCR text
        # -----------------------------------------

        print("\nStructuring OCR data...")

        structured_data = structure_ocr_text(
            extracted_text,
            dataset_type
        )

        print("\n========== STRUCTURED DATA ==========")
        print(structured_data.to_string(index=False))
        print("=====================================")

        # -----------------------------------------
        # STEP 5: Role 3 Cleaning
        # -----------------------------------------

        print("\nRunning Role 3 cleaning...")

        cleaned_data, errors, detected_dataset = clean_data(
            structured_data,
            dataset_type=dataset_type
        )

        # -----------------------------------------
        # STEP 6: Final output
        # -----------------------------------------

        print("\n========== FINAL CLEAN DATA ==========")

        print(
            cleaned_data.to_string(index=False)
        )

        print("\n========== VALIDATION ERRORS ==========")

        if errors:
            for error in errors:
                print(f"- {error}")
        else:
            print("No validation errors.")

        print("\n========== DATASET TYPE ==========")
        print(detected_dataset)

        print("\n========================================")
        print("IMAGE PROCESSING COMPLETED")
        print("========================================")

    except Exception as e:

        print(
            f"\nPipeline processing failed: {e}"
        )