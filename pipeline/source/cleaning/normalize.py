import pandas as pd

def normalize_dataframe(df):

    # remove extra spaces
    df = df.apply(
        lambda col: col.str.strip()
        if col.dtype == "object"
        else col
    )

    # lowercase column names
    df.columns = [
        c.lower().strip().replace(" ", "_")
        for c in df.columns
    ]

    return df