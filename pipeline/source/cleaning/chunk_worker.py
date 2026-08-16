import time

from cleaning.cleaner import clean_data


def process_chunk(args):
    """
    Worker function executed by a separate process.
    """

    chunk_number, chunk, dataset_type = args

    start = time.perf_counter()

    if chunk_number == 1:

        cleaned_chunk, errors, dataset_type = clean_data(
            chunk,
            dataset_type=None,
            validate=True
        )

    else:

        cleaned_chunk, errors, _ = clean_data(
            chunk,
            dataset_type=dataset_type,
            validate=False
        )

    elapsed = time.perf_counter() - start

    return (
        chunk_number,
        cleaned_chunk,
        errors,
        dataset_type,
        elapsed
    )