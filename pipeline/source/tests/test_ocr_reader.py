from preprocessing.ocr_reader import extract_text_from_image

text = extract_text_from_image("tests/sample.png")

print(text)