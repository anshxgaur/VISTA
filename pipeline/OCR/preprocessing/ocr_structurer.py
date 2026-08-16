import pandas as pd
import re


def _extract(pattern, text, default=None, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1).strip()
    return default


def structure_patient_text(text: str) -> pd.DataFrame:
    """
    Convert OCR text into a structured patients DataFrame.
    """

    if not text or not text.strip():
        return pd.DataFrame()

    fields = {
        "patientid": _extract(
            r"patient\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "firstname": _extract(
            r"first\s*name\s*[:\-]?\s*([A-Za-z]+)",
            text
        ),

        "lastname": _extract(
            r"last\s*name\s*[:\-]?\s*([A-Za-z]+)",
            text
        ),

        "gender": _extract(
            r"gender\s*[:\-]?\s*(male|female|m|f)",
            text
        ),

        "age": _extract(
            r"age\s*[:\-]?\s*(\d{1,3})",
            text
        )
    }

    if fields["age"] is not None:
        fields["age"] = int(fields["age"])

    columns = [
        "patientid",
        "firstname",
        "lastname",
        "gender",
        "age"
    ]

    return pd.DataFrame([fields], columns=columns)


def structure_admission_text(text: str) -> pd.DataFrame:
    """
    Convert OCR text into a structured admissions DataFrame.
    """

    if not text or not text.strip():
        return pd.DataFrame()

    fields = {
        "admissionid": _extract(
            r"admission\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "patientid": _extract(
            r"patient\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "doctorid": _extract(
            r"doctor\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "diseaseid": _extract(
            r"disease\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "departmentname": _extract(
            r"department\s*(?:name)?\s*[:\-]?\s*([A-Za-z &]+)",
            text
        ),

        "admitdate": _extract(
            r"admit\s*date\s*[:\-]?\s*([0-9/\-]+)",
            text
        ),

        "dischargedate": _extract(
            r"discharge\s*date\s*[:\-]?\s*([0-9/\-]+)",
            text
        ),

        "severity": _extract(
            r"severity\s*[:\-]?\s*([A-Za-z]+)",
            text
        )
    }

    columns = [
        "admissionid",
        "patientid",
        "doctorid",
        "diseaseid",
        "departmentname",
        "admitdate",
        "dischargedate",
        "severity"
    ]

    return pd.DataFrame([fields], columns=columns)


def structure_billing_text(text: str) -> pd.DataFrame:
    """
    Convert OCR text into a structured billing DataFrame.
    """

    if not text or not text.strip():
        return pd.DataFrame()

    fields = {
        "billingid": _extract(
            r"billing\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "admissionid": _extract(
            r"admission\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "patientid": _extract(
            r"patient\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "insuranceprovider": _extract(
            r"insurance\s*provider\s*[:\-]?\s*([A-Za-z0-9 &]+)",
            text
        ),

        "totalamount": _extract(
            r"total\s*amount\s*[:\-]?\s*([0-9,.]+)",
            text
        ),

        "insurancecoveredamount": _extract(
            r"insurance\s*covered\s*amount\s*[:\-]?\s*([0-9,.]+)",
            text
        ),

        "patientresponsibility": _extract(
            r"patient\s*responsibility\s*[:\-]?\s*([0-9,.]+)",
            text
        ),

        "paymentstatus": _extract(
            r"payment\s*status\s*[:\-]?\s*([A-Za-z]+)",
            text
        ),

        "billingdate": _extract(
            r"billing\s*date\s*[:\-]?\s*([0-9/\-]+)",
            text
        )
    }

    numeric_columns = [
        "totalamount",
        "insurancecoveredamount",
        "patientresponsibility"
    ]

    for column in numeric_columns:
        if fields[column] is not None:
            try:
                fields[column] = float(
                    fields[column].replace(",", "")
                )
            except ValueError:
                pass

    columns = [
        "billingid",
        "admissionid",
        "patientid",
        "insuranceprovider",
        "totalamount",
        "insurancecoveredamount",
        "patientresponsibility",
        "paymentstatus",
        "billingdate"
    ]

    return pd.DataFrame([fields], columns=columns)


def structure_doctor_text(text: str) -> pd.DataFrame:
    """
    Convert OCR text into a structured doctors DataFrame.
    """

    if not text or not text.strip():
        return pd.DataFrame()

    fields = {
        "doctorid": _extract(
            r"doctor\s*id\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            text
        ),

        "doctorname": _extract(
            r"doctor\s*name\s*[:\-]?\s*([A-Za-z ]+)",
            text
        ),

        "gender": _extract(
            r"gender\s*[:\-]?\s*(male|female|m|f)",
            text
        ),

        "age": _extract(
            r"age\s*[:\-]?\s*(\d{1,3})",
            text
        ),

        "specialty": _extract(
            r"specialty\s*[:\-]?\s*([A-Za-z &]+)",
            text
        ),

        "qualification": _extract(
            r"qualification\s*[:\-]?\s*([A-Za-z0-9 .&]+)",
            text
        ),

        "experienceyears": _extract(
            r"experience\s*years?\s*[:\-]?\s*(\d{1,2})",
            text
        ),

        "phone": _extract(
            r"phone\s*[:\-]?\s*([0-9+\- ]+)",
            text
        ),

        "email": _extract(
            r"email\s*[:\-]?\s*([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})",
            text
        )
    }

    if fields["age"] is not None:
        try:
            fields["age"] = int(fields["age"])
        except ValueError:
            pass

    if fields["experienceyears"] is not None:
        try:
            fields["experienceyears"] = int(
                fields["experienceyears"]
            )
        except ValueError:
            pass

    columns = [
        "doctorid",
        "doctorname",
        "gender",
        "age",
        "specialty",
        "qualification",
        "experienceyears",
        "phone",
        "email"
    ]

    return pd.DataFrame([fields], columns=columns)


def structure_ocr_text(text: str, dataset_type: str) -> pd.DataFrame:
    """
    Main OCR structuring function.

    dataset_type:
        patients
        admissions
        billing
        doctors
    """

    if dataset_type == "patients":
        return structure_patient_text(text)

    elif dataset_type == "admissions":
        return structure_admission_text(text)

    elif dataset_type == "billing":
        return structure_billing_text(text)

    elif dataset_type == "doctors":
        return structure_doctor_text(text)

    else:
        raise ValueError(
            f"Unsupported dataset type: {dataset_type}"
        )
def detect_ocr_dataset(text: str):
    """
    Detect the hospital dataset type from OCR text.

    Returns:
        patients
        admissions
        billing
        doctors
        None
    """

    if not text or not text.strip():
        return None

    text_lower = text.lower()

    scores = {
        "patients": 0,
        "admissions": 0,
        "billing": 0,
        "doctors": 0
    }

    # Patient fields
    patient_keywords = [
        "patient id",
        "first name",
        "last name",
        "gender",
        "age"
    ]

    # Admission fields
    admission_keywords = [
        "admission id",
        "patient id",
        "doctor id",
        "disease id",
        "department",
        "admit date",
        "discharge date",
        "severity"
    ]

    # Billing fields
    billing_keywords = [
        "billing id",
        "admission id",
        "patient id",
        "insurance provider",
        "total amount",
        "insurance covered amount",
        "patient responsibility",
        "payment status",
        "billing date"
    ]

    # Doctor fields
    doctor_keywords = [
        "doctor id",
        "doctor name",
        "gender",
        "age",
        "specialty",
        "qualification",
        "experience years",
        "phone",
        "email"
    ]

    for keyword in patient_keywords:
        if keyword in text_lower:
            scores["patients"] += 1

    for keyword in admission_keywords:
        if keyword in text_lower:
            scores["admissions"] += 1

    for keyword in billing_keywords:
        if keyword in text_lower:
            scores["billing"] += 1

    for keyword in doctor_keywords:
        if keyword in text_lower:
            scores["doctors"] += 1

    best_dataset = max(scores, key=scores.get)

    print("\nOCR Dataset Detection:")
    print(scores)

    if scores[best_dataset] < 2:
        print("Could not identify dataset type.")
        return None

    print(f"Detected OCR Dataset: {best_dataset}")

    return best_dataset