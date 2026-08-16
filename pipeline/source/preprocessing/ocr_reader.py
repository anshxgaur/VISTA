from pathlib import Path
from PIL import Image
import pytesseract
import io


# Path to the installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(image_input) -> str:
    """
    Extract text using Tesseract OCR.

    Supports:
    - Image file path (str or Path)
    - Image bytes
    - PIL Image
    """

    # Case 1: Image file path
    if isinstance(image_input, (str, Path)):

        image_path = Path(image_input)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = Image.open(image_path)

    # Case 2: Image bytes
    elif isinstance(image_input, bytes):

        image = Image.open(io.BytesIO(image_input))

    # Case 3: Already a PIL Image
    elif isinstance(image_input, Image.Image):

        image = image_input

    else:

        raise TypeError("Unsupported image input.")

    text = pytesseract.image_to_string(image)

    return text.strip()