import duckdb


def load_csv(file_path):
    """
    Read CSV using DuckDB.
    Returns a pandas DataFrame.
    """

    df = duckdb.sql(f"""
        SELECT *
        FROM read_csv_auto('{file_path}')
    """).df()

    return df


def remove_duplicates(df):
    """
    Remove duplicate rows using DuckDB.
    """

    duckdb.register("temp_table", df)

    cleaned = duckdb.sql("""
        SELECT DISTINCT *
        FROM temp_table
    """).df()

    duckdb.unregister("temp_table")

    return cleaned