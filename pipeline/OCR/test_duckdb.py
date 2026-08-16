from cleaning.duckdb_cleaner import load_csv

df = load_csv(
    r"D:\PROGRAM\VISTA2\pipeline\source\temp_uploads\lab_reports.csv"
)

print(df.head())
print(df.shape)