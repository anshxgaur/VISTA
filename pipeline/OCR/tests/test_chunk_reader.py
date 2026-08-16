from preprocessing.csv_chunk_reader import read_csv_in_chunks

file_path = r"C:\Users\aditi\OneDrive\Desktop\Dataset\Full_Medical_Data_Lake\lab_reports.csv"

total = 0

for chunk in read_csv_in_chunks(file_path, chunk_size=50000):

    print(f"Chunk size : {len(chunk)}")

    total += len(chunk)

print()
print(f"Total rows : {total}")