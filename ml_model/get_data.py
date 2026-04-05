"""Quick dataset download - no pandas needed"""
import urllib.request
import csv
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
raw_file = data_dir / "processed.cleveland.data"
csv_file = data_dir / "heart_disease_data.csv"

print("Downloading UCI Heart Disease dataset...")
urllib.request.urlretrieve(url, raw_file)
print("Download complete!")

columns = [
    "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
    "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
    "exercise_induced_angina", "st_depression", "st_slope",
    "num_major_vessels", "thalassemia", "target"
]

rows = []
with open(raw_file, "r") as f:
    for line in f:
        values = line.strip().split(",")
        if len(values) == 14:
            # Replace ? with empty
            values = ["" if v.strip() == "?" else v.strip() for v in values]
            # Convert target to binary
            try:
                target = int(float(values[-1]))
                values[-1] = "1" if target > 0 else "0"
            except:
                pass
            rows.append(values)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(rows)

no_disease = sum(1 for r in rows if r[-1] == "0")
has_disease = sum(1 for r in rows if r[-1] == "1")

print(f"Total rows: {len(rows)}")
print(f"No disease (0): {no_disease}")
print(f"Has disease (1): {has_disease}")
print(f"Saved to: {csv_file}")
print("\nDataset ready! Now run: python train_model.py")
