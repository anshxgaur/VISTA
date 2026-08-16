from preprocessing.text_extractor import extract_text

# ---------- CSV ----------
with open("tests/sample.csv", "rb") as f:
    csv_bytes = f.read()

print("CSV")
print(extract_text("sample.csv", csv_bytes))


# ---------- JSON ----------
with open("tests/sample.json", "rb") as f:
    json_bytes = f.read()

print("\nJSON")
print(extract_text("sample.json", json_bytes))


# ---------- PDF ----------
with open("tests/sample.pdf", "rb") as f:
    pdf_bytes = f.read()

print("\nPDF")
print(extract_text("sample.pdf", pdf_bytes))


# ---------- TXT ----------
with open("tests/sample.txt", "rb") as f:
    txt_bytes = f.read()

print("\nTXT")
print(extract_text("sample.txt", txt_bytes))