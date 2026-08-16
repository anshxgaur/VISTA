from preprocessing.folder_scanner import scan_dataset

folder = r"C:\Users\aditi\OneDrive\Desktop\Dataset"

files = scan_dataset(folder)

print(f"Found {len(files)} files:\n")

for file in files:
    print(file)