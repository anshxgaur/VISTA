from datetime import datetime
import pandas as pd

from preprocessing.dataset_detector import detect_dataset


def generate_metadata(
    filename,
    extracted_data,
    cleaned_data,
    validation_errors
):
    """
    Generate metadata for every processed file.
    """

    metadata = {}

    # File name
    metadata["filename"] = filename

    # Processing time
    metadata["processed_at"] = datetime.now().isoformat()

    # Validation
    metadata["validation_errors"] = validation_errors

    # Success/Failed
    metadata["status"] = (
        "Processed Successfully"
        if len(validation_errors) == 0
        else "Processed with Validation Errors"
    )

    # DataFrame
    if isinstance(cleaned_data, pd.DataFrame):

        metadata["file_type"] = "csv"

        metadata["dataset_type"] = detect_dataset(
            cleaned_data
        )

        metadata["records"] = len(cleaned_data)

        metadata["columns"] = list(cleaned_data.columns)

    # Text
    elif isinstance(cleaned_data, str):

        metadata["file_type"] = "text"

        metadata["dataset_type"] = "document"

        metadata["characters"] = len(cleaned_data)

        metadata["words"] = len(cleaned_data.split())

    # JSON
    elif isinstance(cleaned_data, dict):

        metadata["file_type"] = "json"

        metadata["dataset_type"] = "structured_json"

        metadata["keys"] = list(cleaned_data.keys())

    else:

        metadata["file_type"] = "unknown"

    return metadata