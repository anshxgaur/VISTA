from preprocessing.folder_scanner import scan_dataset
from preprocessing.text_extractor import extract_text
from cleaning.cleaner import clean_data


def process_folder(folder_path: str):
    """
    Process every supported file inside a folder.
    """

    files = scan_dataset(folder_path)

    print(f"\nFound {len(files)} files.\n")

    for file in files:

        print("=" * 60)
        print(f"Processing: {file.name}")

        with open(file, "rb") as f:
            file_bytes = f.read()

        try:
            # Step 1: Extract the data
            data = extract_text(file.name, file_bytes)

            # Step 2: Clean the data
            cleaned_data, errors = clean_data(data)

            print("SUCCESS")

            # Step 3: Display cleaned output
            if hasattr(cleaned_data, "head"):
                 print(cleaned_data.head())

            elif isinstance(cleaned_data, str):
                print(cleaned_data[:300])

            else:
                print(cleaned_data)

            # Step 4: Display validation errors (if any)
            if errors:
                print("\nValidation Errors:")
                for error in errors:
                    print(f"- {error}")

        except Exception as e:

            print("FAILED")
            print(e)