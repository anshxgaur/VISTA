from PIL import Image
import pytesseract
from pathlib import Path

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Open image
image_path = Path(__file__).parent / "sample.png"
img = Image.open(image_path)

# Perform OCR
text = pytesseract.image_to_string(img)

# Print extracted text
print(text)