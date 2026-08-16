import pdfplumber
import io

from preprocessing.pdf_to_image import convert_pdf_to_images
from preprocessing.ocr_reader import extract_text_from_image


def extract_from_pdf(file_bytes):
    """
    Extract text from a PDF.

    Supports:
    - Digital PDFs (using pdfplumber)
    - Scanned PDFs (using OCR)
    """

    text = ""

    # -----------------------------
    # Try Digital PDF Extraction
    # -----------------------------
    print("Trying digital PDF extraction...")

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    # -----------------------------
    # If text found, return it
    # -----------------------------
    if text.strip():

        print("Digital PDF detected.")

        return text.strip()

    # -----------------------------
    # Otherwise use OCR
    # -----------------------------
    print("No embedded text found.")
    print("Running OCR on scanned PDF...")

    images = convert_pdf_to_images(file_bytes)

    ocr_text = ""

    for page_number, image in enumerate(images, start=1):

        print(f"OCR Page {page_number}")

        page_text = extract_text_from_image(image)

        ocr_text += page_text + "\n"

    print("OCR completed.")

    return ocr_text.strip()