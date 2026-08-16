from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".json",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".txt"
}


def scan_dataset(folder_path: str):
    """
    Recursively scan a folder and return all supported files.
    """

    folder = Path(folder_path)

    files = []

    for file in folder.rglob("*"):

        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file)

    return files