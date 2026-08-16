from pathlib import Path


def detect_file_type(file_path: str):
    """
    Detect the type of the uploaded file.

    Returns:
        csv
        json
        pdf
        image
        unsupported
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".csv":
        return "csv"

    elif extension == ".json":
        return "json"

    elif extension == ".pdf":
        return "pdf"

    elif extension == ".txt":
        return "txt"

    elif extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return "image"

    else:
        return "unsupported"