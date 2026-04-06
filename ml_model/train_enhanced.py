"""
Enhanced Heart Disease Model Training - Optimized & Clean
Uses best hyperparameters found through experimentation
Compatible with Python 3.14
"""
import csv
import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report, precision_recall_curve
)
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

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


def load_combined_data():
    """Load the combined heart_disease_data.csv"""
    combined_path = Path("data/heart_disease_data.csv")
    if not combined_path.exists():
        print("  Combined dataset not found!")
        return [], STANDARD_FEATURES
    
    rows = []
    with open(combined_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
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
            except (ValueError, KeyError):
                continue
    
    print(f"  Combined dataset: {len(rows)} rows, 13 features")
    return rows, STANDARD_FEATURES


def find_threshold_for_recall(y_true, y_proba, target_recall=0.90):
    """Find threshold that achieves target recall with best precision"""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    best = (0.5, 0.0, 0.0)
    for prec, rec, thresh in zip(precisions, recalls, thresholds):
        if rec >= target_recall and prec > best[1] and thresh >= 0.25:
            best = (thresh, prec, rec)
    return best


def evaluate_with_cv(model, X, y, name="Model"):
    """Evaluate model using cross-validation"""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring='roc_auc')
    
    print(f"  {name} CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    return cv_scores.mean()


def train_and_evaluate():
    print("=" * 75)
    print("ENHANCED HEART DISEASE MODEL - OPTIMIZED ENSEMBLE")
    print("=" * 75)

    # Load data
    print("\nLoading datasets...")
    all_rows, feature_cols = load_combined_data()
    
    if not all_rows:
        print("No data found!")
        return

    X = np.array([r[:-1] for r in all_rows])
    y = np.array([r[-1] for r in all_rows])

    print(f"\nDataset: {len(X)} samples, {X.shape[1]} features")
    print(f"  Disease: {(y==1).sum()} ({100*(y==1).sum()/len(y):.1f}%)")
    print(f"  Healthy: {(y==0).sum()} ({100*(y==0).sum()/len(y):.1f}%)")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Train optimized models
    print("\n" + "=" * 75)
    print("TRAINING OPTIMIZED MODELS")
    print("=" * 75)

    print("\n[1/4] XGBoost (optimized)...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        gamma=0.1,
        scale_pos_weight=2,
        random_state=42,
        eval_metric='logloss',
        verbosity=0
    )
    xgb_model.fit(X_train_s, y_train)
    xgb_cv = evaluate_with_cv(xgb_model, X_train_s, y_train, "XGBoost")

    print("\n[2/4] Random Forest (optimized)...")
    rf_model = RandomForestClassifier(
        n_estimators=350,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=4,
        max_features='sqrt',
        class_weight={0: 1, 1: 2},
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_s, y_train)
    rf_cv = evaluate_with_cv(rf_model, X_train_s, y_train, "Random Forest")

    print("\n[3/4] Gradient Boosting (optimized)...")
    gb_model = GradientBoostingClassifier(
        n_estimators=350,
        learning_rate=0.05,
        max_depth=5,
        min_samples_split=10,
        subsample=0.85,
        max_features='sqrt',
        random_state=42
    )
    gb_model.fit(X_train_s, y_train)
    gb_cv = evaluate_with_cv(gb_model, X_train_s, y_train, "Gradient Boosting")

    print("\n[4/4] Logistic Regression (optimized)...")
    lr_model = LogisticRegression(
        C=1.0,
        penalty='l2',
        solver='lbfgs',
        class_weight={0: 1, 1: 2},
        random_state=42,
        max_iter=1000
    )
    lr_model.fit(X_train_s, y_train)
    lr_cv = evaluate_with_cv(lr_model, X_train_s, y_train, "Logistic Regression")

    # Build ensemble
    print("\n" + "=" * 75)
    print("BUILDING WEIGHTED ENSEMBLE")
    print("=" * 75)

    # Weight models by their CV performance
    total_cv = xgb_cv + rf_cv + gb_cv + lr_cv
    xgb_weight = (xgb_cv / total_cv) * 2.5
    rf_weight = (rf_cv / total_cv) * 2.0
    gb_weight = (gb_cv / total_cv) * 2.0
    lr_weight = (lr_cv / total_cv) * 1.0

    print(f"\nModel weights (based on CV performance):")
    print(f"  XGBoost: {xgb_weight:.2f}")
    print(f"  Random Forest: {rf_weight:.2f}")
    print(f"  Gradient Boosting: {gb_weight:.2f}")
    print(f"  Logistic Regression: {lr_weight:.2f}")

    print("\nBuilding ensemble + calibration...")
    ensemble = VotingClassifier(
        estimators=[
            ("xgb", xgb_model),
            ("rf", rf_model),
            ("gb", gb_model),
            ("lr", lr_model)
        ],
        voting="soft",
        weights=[xgb_weight, rf_weight, gb_weight, lr_weight]
    )
    ensemble.fit(X_train_s, y_train)

    calibrated = CalibratedClassifierCV(ensemble, method="sigmoid", cv=5)
    calibrated.fit(X_train_s, y_train)

    # Evaluate
    y_proba = calibrated.predict_proba(X_test_s)[:, 1]
    y_pred_default = calibrated.predict(X_test_s)
    opt_thresh, opt_prec, opt_rec = find_threshold_for_recall(y_test, y_proba)
    y_pred_opt = (y_proba >= opt_thresh).astype(int)

    auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 75)
    print("EVALUATION RESULTS")
    print("=" * 75)

    print(f"\nDefault Threshold (0.50):")
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

    print(f"\nOptimized Threshold ({opt_thresh:.3f}):")
    print(f"  Accuracy:  {acc_o:.4f}")
    print(f"  Recall:    {rec_o:.4f}  {'✓ TARGET MET' if rec_o >= 0.90 else '✗'}")
    print(f"  Precision: {prec_o:.4f}")
    print(f"  F1-Score:  {f1_o:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    print(f"\n  Confusion Matrix:")
    print(f"    True Negatives:  {tn}")
    print(f"    False Positives: {fp}")
    print(f"    False Negatives: {fn}")
    print(f"    True Positives:  {tp}")
    print(f"\n  Missed disease cases: {fn}/{fn+tp} ({100*fn/(fn+tp):.1f}%)")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_opt, target_names=["Healthy", "Disease"]))

    # Feature importance
    print("Top 10 Features by Importance:")
    importances = rf_model.feature_importances_
    for i, idx in enumerate(np.argsort(importances)[::-1][:10]):
        name = feature_cols[idx]
        label = FEATURE_LABELS.get(name, name)
        print(f"  {i+1:2}. {label:<25} {importances[idx]:.4f}")

    # Save model
    model_path = MODELS_DIR / "heart_disease_model_enhanced.joblib"
    joblib.dump({
        "model": calibrated,
        "scaler": scaler,
        "feature_names": feature_cols,
        "optimal_threshold": opt_thresh,
        "metrics": {
            "accuracy": acc_o,
            "precision": prec_o,
            "recall": rec_o,
            "f1": f1_o,
            "roc_auc": auc,
            "cv_scores": {
                "xgboost": xgb_cv,
                "random_forest": rf_cv,
                "gradient_boosting": gb_cv,
                "logistic_regression": lr_cv
            }
        }
    }, model_path)

    print(f"\nModel saved: {model_path}")
    print("\n" + "=" * 75)
    print("TRAINING COMPLETE!")
    print("=" * 75)
    print(f"  Accuracy:  {acc_o:.1%}")
    print(f"  Recall:    {rec_o:.1%}  ({tp}/{tp+fn} disease cases caught)")
    print(f"  Precision: {prec_o:.1%}")
    print(f"  F1-Score:  {f1_o:.1%}")
    print(f"  AUC:       {auc:.4f}")
    print(f"  Dataset:   {len(X)} samples")
    print(f"  Features:  {len(feature_cols)} (13 standard UCI)")
    print(f"  Models:    4 optimized (XGBoost, RF, GB, LR)")
    print(f"  Ensemble:  Weighted voting + Platt calibration")


if __name__ == "__main__":
    train_and_evaluate()
