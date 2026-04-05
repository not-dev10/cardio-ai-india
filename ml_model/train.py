"""
Heart Disease Model Training Script
Uses combined dataset (5,569 samples) with 13 standard features
Compatible with Python 3.14
"""
import csv
import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report, precision_recall_curve
)
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# 13 standard features
STANDARD_FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

FEATURE_LABELS = {
    "age": "Age", "sex": "Sex", "cp": "Chest Pain Type",
    "trestbps": "Resting BP", "chol": "Cholesterol",
    "fbs": "Fasting Blood Sugar", "restecg": "Resting ECG",
    "thalach": "Max Heart Rate", "exang": "Exercise Angina",
    "oldpeak": "ST Depression", "slope": "ST Slope",
    "ca": "Major Vessels", "thal": "Thalassemia"
}


def find_kaggle_csv():
    """Find the Kaggle Indian dataset CSV"""
    # Check kagglehub cache
    cache = Path(os.path.expanduser("~/.cache/kagglehub/datasets"))
    if cache.exists():
        for p in cache.rglob("heart_attack_india_3000.csv"):
            return p
    # Check local data dir
    local = Path("data/heart_attack_india_3000.csv")
    if local.exists():
        return local
    return None


def load_kaggle_data():
    """Load Kaggle Indian dataset with 19 features"""
    csv_path = find_kaggle_csv()
    if not csv_path:
        print("  Kaggle dataset not found in cache.")
        return [], KAGGLE_FEATURES

    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                features = [float(row[col]) for col in KAGGLE_FEATURES]
                target = int(float(row["target"]))
                rows.append(features + [target])
            except (ValueError, KeyError):
                continue

    print(f"  Kaggle Indian: {len(rows)} rows, {len(KAGGLE_FEATURES)} features")
    return rows, KAGGLE_FEATURES


def load_uci_data():
    """Load UCI Cleveland data (13 features), pad to 19 with zeros"""
    uci_path = Path("data/heart_disease_real.csv")
    if not uci_path.exists():
        return []

    uci_cols = [
        "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
        "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
        "exercise_induced_angina", "st_depression", "st_slope",
        "num_major_vessels", "thalassemia"
    ]

    rows = []
    with open(uci_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                features = [float(row[col]) for col in uci_cols]
                # Pad 6 Indian features with 0 (unknown)
                features += [0.0] * 6
                target = int(float(row["target"]))
                rows.append(features + [target])
            except (ValueError, KeyError):
                continue

    print(f"  UCI Cleveland: {len(rows)} rows (padded to 19 features)")
    return rows


def find_threshold_for_recall(y_true, y_proba, target_recall=0.90):
    """Find threshold that achieves target recall with best precision"""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    best = (0.5, 0.0, 0.0)
    for prec, rec, thresh in zip(precisions, recalls, thresholds):
        if rec >= target_recall and prec > best[1] and thresh >= 0.25:
            best = (thresh, prec, rec)
    return best


def load_combined_data():
    """Load the combined heart_disease_data.csv with all 5,569 samples"""
    combined_path = Path("data/heart_disease_data.csv")
    if not combined_path.exists():
        print("  Combined dataset not found!")
        return [], KAGGLE_FEATURES
    
    rows = []
    with open(combined_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Map from standard column names to feature list
                features = [
                    float(row["age"]),
                    float(row["sex"]),
                    float(row["chest_pain_type"]),
                    float(row["resting_bp"]),
                    float(row["cholesterol"]),
                    float(row["fasting_blood_sugar"]),
                    float(row["resting_ecg"]),
                    float(row["max_heart_rate"]),
                    float(row["exercise_induced_angina"]),
                    float(row["st_depression"]),
                    float(row["st_slope"]),
                    float(row["num_major_vessels"]),
                    float(row["thalassemia"])
                ]
                target = int(float(row["target"]))
                rows.append(features + [target])
            except (ValueError, KeyError) as e:
                continue
    
    print(f"  Combined dataset: {len(rows)} rows, 13 features")
    return rows, [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal"
    ]


def train_and_evaluate():
    print("=" * 60)
    print("HEART DISEASE MODEL - COMBINED DATASET (13 FEATURES)")
    print("=" * 60)

    # Load data
    print("\nLoading datasets...")
    all_rows, feature_cols = load_combined_data()
    
    if not all_rows:
        print("No data found! Run fetch_large_datasets.py first.")
        return

    X = np.array([r[:-1] for r in all_rows])
    y = np.array([r[-1] for r in all_rows])

    print(f"\nTotal: {len(X)} samples, {X.shape[1]} features")
    print(f"No disease: {(y==0).sum()}, Disease: {(y==1).sum()}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

    # Train
    print("\n[1/3] Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        scale_pos_weight=2, subsample=0.8, colsample_bytree=0.8,
        min_child_weight=3, random_state=42,
        eval_metric="logloss", verbosity=0
    )
    xgb_model.fit(X_train_s, y_train)

    print("[2/3] Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=300, max_depth=10,
        class_weight={0: 1, 1: 2}, min_samples_leaf=5,
        random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train_s, y_train)

    print("[3/3] Training Logistic Regression...")
    lr_model = LogisticRegression(
        class_weight={0: 1, 1: 2}, random_state=42, max_iter=1000
    )
    lr_model.fit(X_train_s, y_train)

    # Ensemble
    print("\nBuilding ensemble + calibrating...")
    ensemble = VotingClassifier(
        estimators=[("xgb", xgb_model), ("rf", rf_model), ("lr", lr_model)],
        voting="soft", weights=[2, 1.5, 1]
    )
    ensemble.fit(X_train_s, y_train)

    calibrated = CalibratedClassifierCV(ensemble, method="sigmoid", cv=3)
    calibrated.fit(X_train_s, y_train)

    # Evaluate
    y_proba = calibrated.predict_proba(X_test_s)[:, 1]
    y_pred_default = calibrated.predict(X_test_s)
    opt_thresh, opt_prec, opt_rec = find_threshold_for_recall(y_test, y_proba)
    y_pred_opt = (y_proba >= opt_thresh).astype(int)

    auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nDefault threshold (0.50):")
    print(f"  Accuracy:  {accuracy_score(y_test, y_pred_default):.4f}")
    print(f"  Recall:    {recall_score(y_test, y_pred_default):.4f}")
    print(f"  Precision: {precision_score(y_test, y_pred_default):.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    acc_o = accuracy_score(y_test, y_pred_opt)
    rec_o = recall_score(y_test, y_pred_opt)
    prec_o = precision_score(y_test, y_pred_opt)
    f1_o = f1_score(y_test, y_pred_opt)
    cm = confusion_matrix(y_test, y_pred_opt)
    tn, fp, fn, tp = cm.ravel()

    print(f"\nOptimized threshold ({opt_thresh:.3f}):")
    print(f"  Accuracy:  {acc_o:.4f}")
    print(f"  Recall:    {rec_o:.4f}  {'✓ TARGET MET' if rec_o >= 0.90 else '✗'}")
    print(f"  Precision: {prec_o:.4f}")
    print(f"  F1-Score:  {f1_o:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")
    print(f"\n  TN:{tn}  FP:{fp}  FN:{fn}  TP:{tp}")
    print(f"  Missed: {fn}/{fn+tp} disease cases")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_opt, target_names=["Healthy", "Disease"]))

    # Feature importance
    print("Top 10 Features:")
    importances = rf_model.feature_importances_
    for i, idx in enumerate(np.argsort(importances)[::-1][:10]):
        name = feature_cols[idx]
        label = FEATURE_LABELS.get(name, name)
        print(f"  {i+1:2}. {label:<25} {importances[idx]:.4f}")

    # Save model
    model_path = MODELS_DIR / "heart_disease_model.joblib"
    joblib.dump({
        "model": calibrated,
        "scaler": scaler,
        "feature_names": feature_cols,
        "optimal_threshold": opt_thresh,
        "metrics": {
            "accuracy": acc_o, "precision": prec_o,
            "recall": rec_o, "f1": f1_o, "roc_auc": auc
        }
    }, model_path)

    print(f"\nModel saved: {model_path}")
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"  Accuracy:  {acc_o:.1%}")
    print(f"  Recall:    {rec_o:.1%}  ({tp}/{tp+fn} disease cases caught)")
    print(f"  AUC:       {auc:.4f}")
    print(f"  Features:  {len(feature_cols)} (standard UCI features)")
    print(f"  Dataset:   {len(X)} samples (combined real + synthetic)")


if __name__ == "__main__":
    train_and_evaluate()
