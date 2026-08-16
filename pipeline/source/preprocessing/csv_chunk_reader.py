import pandas as pd


def read_csv_in_chunks(file_path, chunk_size=50000):
    """
    Read CSV in chunks using Pandas.
    """

    return pd.read_csv(
        file_path,
        chunksize=chunk_size
    )