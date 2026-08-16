def remove_duplicates(df):

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    removed = before - after

    return df, removed