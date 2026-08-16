import pandas as pd


def standardize_dataframe(df):

    # Standardize gender values
    if "gender" in df.columns:

        df["gender"] = (
            df["gender"]
            .replace(
                {
                    "Male": "M",
                    "Female": "F",
                    "male": "M",
                    "female": "F"
                }
            )
        )

    # Split patient name into firstname and lastname
    if "patientname" in df.columns:

        def split_name(name):
            if pd.isna(name):
                return pd.Series(["", ""])

            name = str(name).strip()

            parts = name.split()

            if len(parts) == 1:
                return pd.Series([parts[0], ""])

            firstname = parts[0]
            lastname = " ".join(parts[1:])

            return pd.Series([firstname, lastname])


        df[["firstname", "lastname"]] = (
            df["patientname"]
            .apply(split_name)
        )

        # Remove old patientname column
        df.drop(
            columns=["patientname"],
            inplace=True
        )

    return df