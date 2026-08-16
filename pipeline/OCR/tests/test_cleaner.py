import pandas as pd

from cleaning.cleaner import clean_data


df = pd.DataFrame({

    "PatientID": [1, 1, 2],

    "PatientName": [
        "Aditi",
        "Aditi",
        "Rahul"
    ],

    "Age": [20, 20, 30],

    "Gender": [
        "Female",
        "Female",
        "Male"
    ]

})

cleaned_df, errors = clean_data(df)

print("\nCleaned Data\n")
print(cleaned_df)

print("\nValidation Errors\n")
print(errors)