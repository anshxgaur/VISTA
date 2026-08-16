import pandas as pd
import time

from cleaning.normalize import normalize_dataframe
from cleaning.standardize import standardize_dataframe
from cleaning.duplicate import remove_duplicates
from cleaning.masking import mask_pii
from cleaning.validate import validate_dataframe
from preprocessing.dataset_detector import detect_dataset


def clean_data(
    data,
    dataset_type=None,
    validate=True
):
    """
    Main cleaning pipeline.

    Parameters
    ----------
    dataset_type:
        Dataset type detected from the first chunk.
        Remaining chunks reuse it.

    validate:
        True  -> Perform validation
        False -> Skip validation (faster)
    """

    if isinstance(data, pd.DataFrame):

        total = time.perf_counter()

        t = time.perf_counter()
        data = normalize_dataframe(data)
        print(f"Normalize : {time.perf_counter()-t:.2f} sec")

        t = time.perf_counter()
        data = standardize_dataframe(data)
        print(f"Standardize : {time.perf_counter()-t:.2f} sec")

        t = time.perf_counter()
        data, removed = remove_duplicates(data)
        print(f"Duplicates : {time.perf_counter()-t:.2f} sec")

        if dataset_type is None:

            t = time.perf_counter()

            dataset_type = detect_dataset(data)

            print(f"Dataset Detection : {time.perf_counter()-t:.2f} sec")
            print(f"Detected Dataset : {dataset_type}")

        if validate:

            t = time.perf_counter()

            if dataset_type:
                errors = validate_dataframe(
                    data,
                    dataset_type
                )
            else:
                errors = []

            print(f"Validation : {time.perf_counter()-t:.2f} sec")

        else:
            errors = []

        print(f"Total Cleaning : {time.perf_counter()-total:.2f} sec")

        return data, errors, dataset_type

    # =====================================================
    # Text Cleaning
    # =====================================================

    elif isinstance(data, str):

        cleaned_text = mask_pii(data)

        return cleaned_text, [], "document"

    # =====================================================
    # Unsupported Data
    # =====================================================

    else:

        return data, [], None