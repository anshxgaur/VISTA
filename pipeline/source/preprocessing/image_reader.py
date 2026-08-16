from PIL import Image
import pytesseract
import io

def extract_from_image(file_bytes):

    image = Image.open(
        io.BytesIO(file_bytes)
    )

    text = pytesseract.image_to_string(image)

    return text