from cleaning.validate import REQUIRED_COLUMNS

def detect_dataset(df):
    columns = {
        column.strip().lower()
        for column in df.columns
    }

    print("\nUploaded Columns:")
    print(columns)

    best_dataset = None
    best_score = 0

    for dataset, required in REQUIRED_COLUMNS.items():

        score = len(columns.intersection(required))

        print(f"{dataset} -> {score} matches")

        if score > best_score:
            best_score = score
            best_dataset = dataset

    print(f"Best Score : {best_score}")

    if best_score < 3:
        return None

    return best_dataset