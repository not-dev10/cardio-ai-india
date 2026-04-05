"""
Download and integrate Indian Heart Attack Risk Prediction Dataset from Kaggle
Dataset: khushikyad001/heart-attack-risk-prediction-dataset-india
"""
import kagglehub
import csv
import os
import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Standard feature columns our model uses
STANDARD_COLS = [
    "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
    "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
    "exercise_induced_angina", "st_depression", "st_slope",
    "num_major_vessels", "thalassemia", "target"
]


def download_dataset():
    """Download the Indian dataset via kagglehub"""
    print("Downloading Indian Heart Attack dataset from Kaggle...")
    print("(You may be prompted to authenticate with Kaggle)\n")
    try:
        path = kagglehub.dataset_download("khushikyad001/heart-attack-risk-prediction-dataset-india")
        print(f"Downloaded to: {path}")
        return path
    except Exception as e:
        print(f"Download failed: {e}")
        return None


def explore_dataset(path):
    """Explore what files and columns are in the dataset"""
    print("\n--- Dataset Contents ---")
    all_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            full = os.path.join(root, f)
            size = os.path.getsize(full)
            print(f"  {f}  ({size:,} bytes)")
            all_files.append(full)

    # Show columns of each CSV
    csv_files = [f for f in all_files if f.endswith(".csv")]
    for csv_file in csv_files:
        print(f"\n--- Columns in {os.path.basename(csv_file)} ---")
        with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            print(f"  Columns ({len(headers)}): {headers}")
            # Show first 2 rows
            for i, row in enumerate(reader):
                if i >= 2:
                    break
                print(f"  Row {i+1}: {row[:8]}...")

    return csv_files


def map_indian_to_standard(row, headers):
    """
    Map Indian dataset columns to our standard 13 features.
    Column names vary by dataset - this handles common variations.
    """
    h = {col.lower().strip(): i for i, col in enumerate(headers)}

    def get(names, default=0):
        for name in names:
            if name in h:
                val = row[h[name]].strip()
                if val in ("", "?", "na", "nan", "null"):
                    return default
                try:
                    return float(val)
                except ValueError:
                    return default
        return default

    def get_str(names, default=""):
        for name in names:
            if name in h:
                return row[h[name]].strip().lower()
        return default

    # Age
    age = get(["age", "patient age", "age (years)"], 50)

    # Sex: male=1, female=0
    sex_raw = get_str(["sex", "gender", "patient gender"])
    if sex_raw in ("male", "m", "1"):
        sex = 1
    elif sex_raw in ("female", "f", "0"):
        sex = 0
    else:
        sex = get(["sex", "gender"], 1)

    # Chest pain type (0-3)
    cp_raw = get_str(["chest pain type", "chest_pain_type", "cp", "chest pain"])
    cp_map = {
        "typical angina": 0, "typical": 0, "0": 0,
        "atypical angina": 1, "atypical": 1, "1": 1,
        "non-anginal pain": 2, "non-anginal": 2, "2": 2,
        "asymptomatic": 3, "3": 3
    }
    cp = cp_map.get(cp_raw, get(["chest pain type", "cp", "chest_pain_type"], 0))

    # Resting BP
    bp = get(["resting blood pressure", "resting bp", "blood pressure", "bp",
              "resting_bp", "trestbps", "systolic bp", "systolic blood pressure"], 120)

    # Cholesterol
    chol = get(["cholesterol", "serum cholesterol", "chol", "total cholesterol",
                "cholesterol level"], 200)

    # Fasting blood sugar > 120
    fbs_raw = get_str(["fasting blood sugar", "fbs", "blood sugar"])
    if fbs_raw in ("yes", "true", "1", "high"):
        fbs = 1
    elif fbs_raw in ("no", "false", "0", "normal"):
        fbs = 0
    else:
        fbs_val = get(["fasting blood sugar", "fbs", "blood sugar level",
                       "fasting glucose"], 90)
        fbs = 1 if fbs_val > 120 else 0

    # Resting ECG (0-2)
    ecg = get(["resting ecg", "resting_ecg", "restecg", "ecg results", "ecg"], 0)
    ecg = int(min(2, max(0, ecg)))

    # Max heart rate
    hr = get(["max heart rate", "maximum heart rate", "thalach", "max_heart_rate",
              "heart rate", "max hr"], 150)

    # Exercise induced angina
    exang_raw = get_str(["exercise induced angina", "exang", "exercise_angina",
                         "exercise angina"])
    if exang_raw in ("yes", "true", "1"):
        exang = 1
    elif exang_raw in ("no", "false", "0"):
        exang = 0
    else:
        exang = int(get(["exercise induced angina", "exang"], 0))

    # ST depression
    oldpeak = get(["st depression", "oldpeak", "st_depression",
                   "st depression (exercise vs rest)"], 0.0)

    # ST slope (0-2)
    slope = get(["slope", "st slope", "slope of peak exercise st segment"], 1)
    slope = int(min(2, max(0, slope)))

    # Number of major vessels (0-3)
    ca = get(["number of major vessels", "ca", "num_major_vessels",
              "major vessels", "vessels colored"], 0)
    ca = int(min(3, max(0, ca)))

    # Thalassemia (0-3)
    thal_raw = get_str(["thalassemia", "thal", "thalassemia type"])
    thal_map = {
        "normal": 1, "fixed defect": 2, "reversible defect": 3,
        "0": 0, "1": 1, "2": 2, "3": 3
    }
    thal = thal_map.get(thal_raw, int(get(["thalassemia", "thal"], 2)))
    thal = int(min(3, max(0, thal)))

    # Target
    target_raw = get_str(["target", "heart attack risk", "heart disease",
                           "diagnosis", "output", "result", "risk"])
    if target_raw in ("yes", "true", "1", "high", "positive", "disease"):
        target = 1
    elif target_raw in ("no", "false", "0", "low", "negative", "normal"):
        target = 0
    else:
        target_val = get(["target", "heart attack risk", "output", "result",
                          "heart disease", "diagnosis"], 0)
        target = 1 if target_val > 0 else 0

    return [age, sex, cp, bp, chol, fbs, ecg, hr, exang,
            round(oldpeak, 1), slope, ca, thal, target]


def process_csv(csv_file):
    """Process a CSV file and return mapped rows"""
    rows = []
    with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        headers = next(reader, [])

        print(f"\nProcessing: {os.path.basename(csv_file)}")
        print(f"Headers: {headers}")

        for i, row in enumerate(reader):
            if len(row) < 2:
                continue
            try:
                mapped = map_indian_to_standard(row, headers)
                # Basic validation
                age, _, _, bp, chol, _, _, hr = mapped[:8]
                if 18 <= age <= 90 and 60 <= bp <= 250 and 50 <= chol <= 700 and 40 <= hr <= 250:
                    rows.append(mapped)
            except Exception:
                continue

    disease = sum(1 for r in rows if r[-1] == 1)
    print(f"Valid rows: {len(rows)} ({disease} disease, {len(rows)-disease} healthy)")
    return rows


def merge_with_existing(new_rows):
    """Merge new Indian data with existing dataset"""
    existing_file = DATA_DIR / "heart_disease_data.csv"
    existing_rows = []

    if existing_file.exists():
        with open(existing_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    r = [float(row[c]) for c in STANDARD_COLS[:-1]]
                    r.append(int(float(row["target"])))
                    existing_rows.append(r)
                except (ValueError, KeyError):
                    continue
        print(f"\nExisting dataset: {len(existing_rows)} rows")

    combined = existing_rows + new_rows
    print(f"Combined dataset: {len(combined)} rows")

    # Save
    with open(existing_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(STANDARD_COLS)
        for row in combined:
            writer.writerow([round(v, 4) if isinstance(v, float) else v for v in row])

    disease = sum(1 for r in combined if r[-1] == 1)
    print(f"Disease: {disease} ({disease/len(combined)*100:.1f}%)")
    print(f"Healthy: {len(combined)-disease} ({(len(combined)-disease)/len(combined)*100:.1f}%)")
    print(f"Saved to: {existing_file}")

    return combined


def main():
    print("=" * 60)
    print("KAGGLE INDIAN HEART DISEASE DATASET INTEGRATION")
    print("=" * 60)

    # Download
    path = download_dataset()
    if not path:
        print("\nFailed to download. Make sure you're logged into Kaggle.")
        print("Run: kagglehub.login() first")
        return

    # Explore
    csv_files = explore_dataset(path)
    if not csv_files:
        print("No CSV files found in dataset!")
        return

    # Process all CSV files
    all_new_rows = []
    for csv_file in csv_files:
        rows = process_csv(csv_file)
        all_new_rows.extend(rows)

    if not all_new_rows:
        print("\nNo valid rows extracted. Check column mapping.")
        return

    print(f"\nTotal new Indian rows: {len(all_new_rows)}")

    # Merge with existing
    print("\nMerging with existing dataset...")
    combined = merge_with_existing(all_new_rows)

    # Update metadata
    meta_file = DATA_DIR / "dataset_metadata.json"
    meta = {}
    if meta_file.exists():
        with open(meta_file) as f:
            meta = json.load(f)

    meta["kaggle_indian"] = len(all_new_rows)
    meta["total_after_kaggle"] = len(combined)
    meta["kaggle_source"] = "khushikyad001/heart-attack-risk-prediction-dataset-india"
    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n{'='*60}")
    print("DONE! Now retrain the model:")
    print("  python train.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
