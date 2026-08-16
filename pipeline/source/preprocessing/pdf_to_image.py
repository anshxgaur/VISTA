from pdf2image import convert_from_bytes


def convert_pdf_to_images(pdf_bytes):
    """
    Convert every page of a PDF into PIL Images.
    """

    images = convert_from_bytes(pdf_bytes)

    return images