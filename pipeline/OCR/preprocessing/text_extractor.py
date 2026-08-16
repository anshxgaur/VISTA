from preprocessing.file_detector import detect_file_type
from preprocessing.csv_reader import read_csv
from preprocessing.json_reader import read_json
from preprocessing.pdf_reader import extract_from_pdf
from preprocessing.ocr_reader import extract_text_from_image
from preprocessing.txt_reader import read_txt

def extract_text(file_name: str, file_bytes: bytes):
    """
    Detect the uploaded file type and extract its content.
    """

    file_type = detect_file_type(file_name)

    if file_type == "csv":
        return read_csv(file_bytes)

    elif file_type == "json":
        return read_json(file_bytes)

    elif file_type == "pdf":
        return extract_from_pdf(file_bytes)

    elif file_type == "txt":
        return read_txt(file_bytes)

    elif file_type == "image":
        return extract_text_from_image(file_bytes)

    else:
        raise ValueError(f"Unsupported file type: {file_type}")