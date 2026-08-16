import pandas as pd
import io

def read_csv(file_bytes):

    dataframe = pd.read_csv(
        io.BytesIO(file_bytes)
    )

    return dataframe