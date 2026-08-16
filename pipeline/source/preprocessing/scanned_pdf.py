from pdf2image import convert_from_bytes
import pytesseract

def extract_from_scanned_pdf(file_bytes):

    images = convert_from_bytes(file_bytes)

    text = ""

    for image in images:

        text += pytesseract.image_to_string(image)

    return text