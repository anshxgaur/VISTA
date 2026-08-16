import pandas as pd

REQUIRED_COLUMNS = {

    "patients": {
        "patientid",
        "firstname",
        "lastname",
        "gender",
        "age"
    },

    "admissions": {
        "admissionid",
        "patientid",
        "doctorid",
        "diseaseid",
        "departmentname",
        "admitdate",
        "dischargedate",
        "severity"
    },

    "billing": {
        "billingid",
        "admissionid",
        "patientid",
        "insuranceprovider",
        "totalamount",
        "insurancecoveredamount",
        "patientresponsibility",
        "paymentstatus",
        "billingdate"
    },

    "doctors": {
        "doctorid",
        "doctorname",
        "gender",
        "age",
        "specialty",
        "qualification",
        "experienceyears",
        "phone",
        "email"
    }

}

def validate_dataframe(df, dataset_type="patients"):

    errors = []

    if df.empty:
        errors.append("Dataset is empty")

    # Convert uploaded column names to lowercase
    df.columns = [
        column.strip().lower()
        for column in df.columns
    ]

    required = REQUIRED_COLUMNS.get(dataset_type, set())

    for column in required:
        if column not in df.columns:
            errors.append(f"Missing column: {column}")

    return errors