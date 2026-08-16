from preprocessing.file_detector import detect_file_type

print(detect_file_type("employees.csv"))
print(detect_file_type("data.json"))
print(detect_file_type("report.pdf"))
print(detect_file_type("scan.png"))
print(detect_file_type("notes.docx"))