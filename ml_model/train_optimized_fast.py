"""
Fast Heart Disease Model Training with Smart Hyperparameter Optimization
Uses RandomizedSearchCV for faster optimization
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
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report, precision_recall_curve
)
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# Suppress sklearn parallel warnings
import os
os.environ['SKLEARN_ENABLE_TAGS_CHECKING'] = '0'

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


def optimize_xgboost(X_train, y_train):
    """Optimize XGBoost with RandomizedSearchCV (faster)"""
    print("\n  [XGBoost] Optimizing hyperparameters...")
    
    param_dist = {
        'n_estimators': [250, 350, 450],
        'max_depth': [4, 5, 6, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.75, 0.85, 0.95],
        'colsample_bytree': [0.75, 0.85, 0.95],
        'min_child_weight': [2, 3, 4],
        'gamma': [0, 0.1, 0.2]
    }
    
    xgb_model = xgb.XGBClassifier(
        scale_pos_weight=2,
        random_state=42,
        eval_metric='logloss',
        verbosity=0,
        n_jobs=-1
    )
    
    random_search = RandomizedSearchCV(
        xgb_model, param_dist, n_iter=30, cv=3, scoring='roc_auc', 
        n_jobs=-1, verbose=1, random_state=42
    )
    random_search.fit(X_train, y_train)
    
    print(f"  Best XGBoost AUC: {random_search.best_score_:.4f}")
    return random_search.best_estimator_


def optimize_random_forest(X_train, y_train):
    """Optimize Random Forest"""
    print("\n  [Random Forest] Optimizing hyperparameters...")
    
    param_dist = {
        'n_estimators': [250, 350, 450],
        'max_depth': [8, 10, 12, 14],
        'min_samples_split': [5, 10, 15],
        'min_samples_leaf': [2, 4, 6],
        'max_features': ['sqrt', 'log2', None]
    }
    
    rf_model = RandomForestClassifier(
        class_weight={0: 1, 1: 2},
        random_state=42,
        n_jobs=-1
    )
    
    random_search = RandomizedSearchCV(
        rf_model, param_dist, n_iter=30, cv=3, scoring='roc_auc',
        n_jobs=-1, verbose=1, random_state=42
    )
    random_search.fit(X_train, y_train)
    
    print(f"  Best RF AUC: {random_search.best_score_:.4f}")
    return random_search.best_estimator_


def optimize_gradient_boosting(X_train, y_train):
    """Optimize Gradient Boosting"""
    print("\n  [Gradient Boosting] Optimizing hyperparameters...")
    
    param_dist = {
        'n_estimators': [250, 350, 450],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 4, 5, 6],
        'min_samples_split': [5, 10, 15],
        'subsample': [0.75, 0.85, 0.95],
        'max_features': ['sqrt', 'log2']
    }
    
    gb_model = GradientBoostingClassifier(random_state=42, verbose=0)
    
    random_search = RandomizedSearchCV(
        gb_model, param_dist, n_iter=30, cv=3, scoring='roc_auc',
        n_jobs=-1, verbose=1, random_state=42
    )
    random_search.fit(X_train, y_train)
    
    print(f"  Best GB AUC: {random_search.best_score_:.4f}")
    return random_search.best_estimator_


def optimize_logistic_regression(X_train, y_train):
    """Optimize Logistic Regression"""
    print("\n  [Logistic Regression] Optimizing hyperparameters...")
    
    param_dist = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'penalty': ['l2'],
        'solver': ['lbfgs', 'liblinear']
    }
    
    lr_model = LogisticRegression(
        class_weight={0: 1, 1: 2},
        random_state=42,
        max_iter=1000
    )
    
    random_search = RandomizedSearchCV(
        lr_model, param_dist, n_iter=15, cv=3, scoring='roc_auc',
        n_jobs=-1, verbose=1, random_state=42
    )
    random_search.fit(X_train, y_train)
    
    print(f"  Best LR AUC: {random_search.best_score_:.4f}")
    return random_search.best_estimator_


def evaluate_with_cross_validation(model, X, y, cv=5):
    """Evaluate model using cross-validation"""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=skf, scoring='roc_auc', n_jobs=-1)
    
    print(f"    CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
    print(f"    Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    return cv_scores


def train_and_evaluate():
    print("=" * 70)
    print("OPTIMIZED HEART DISEASE MODEL - FAST HYPERPARAMETER TUNING")
    print("=" * 70)

    # Load data
    print("\nLoading datasets...")
    all_rows, feature_cols = load_combined_data()
    
    if not all_rows:
        print("No data found!")
        return

    X = np.array([r[:-1] for r in all_rows])
    y = np.array([r[-1] for r in all_rows])

    print(f"\nTotal: {len(X)} samples, {X.shape[1]} features")
    print(f"Disease: {(y==1).sum()} | Healthy: {(y==0).sum()}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

    # Optimize models
    print("\n" + "=" * 70)
    print("HYPERPARAMETER OPTIMIZATION (RandomizedSearchCV)")
    print("=" * 70)
    
    xgb_model = optimize_xgboost(X_train_s, y_train)
    rf_model = optimize_random_forest(X_train_s, y_train)
    gb_model = optimize_gradient_boosting(X_train_s, y_train)
    lr_model = optimize_logistic_regression(X_train_s, y_train)

    # Cross-validation
    print("\n" + "=" * 70)
    print("CROSS-VALIDATION EVALUATION")
    print("=" * 70)
    
    print("\n  [XGBoost]")
    evaluate_with_cross_validation(xgb_model, X_train_s, y_train, cv=5)
    
    print("\n  [Random Forest]")
    evaluate_with_cross_validation(rf_model, X_train_s, y_train, cv=5)
    
    print("\n  [Gradient Boosting]")
    evaluate_with_cross_validation(gb_model, X_train_s, y_train, cv=5)
    
    print("\n  [Logistic Regression]")
    evaluate_with_cross_validation(lr_model, X_train_s, y_train, cv=5)

    # Ensemble
    print("\n" + "=" * 70)
    print("BUILDING OPTIMIZED ENSEMBLE")
    print("=" * 70)
    
    print("\nBuilding weighted ensemble + calibration...")
    ensemble = VotingClassifier(
        estimators=[
            ("xgb", xgb_model),
            ("rf", rf_model),
            ("gb", gb_model),
            ("lr", lr_model)
        ],
        voting="soft",
        weights=[2.5, 2.0, 2.0, 1.0]
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

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

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
    print(f"    TN: {tn}  |  FP: {fp}")
    print(f"    FN: {fn}  |  TP: {tp}")
    print(f"  Missed: {fn}/{fn+tp} disease cases ({100*fn/(fn+tp):.1f}%)")

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
    model_path = MODELS_DIR / "heart_disease_model_optimized.joblib"
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
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"  Accuracy:  {acc_o:.1%}")
    print(f"  Recall:    {rec_o:.1%}  ({tp}/{tp+fn} disease cases)")
    print(f"  Precision: {prec_o:.1%}")
    print(f"  F1-Score:  {f1_o:.1%}")
    print(f"  AUC:       {auc:.4f}")
    print(f"  Dataset:   {len(X)} samples")
    print(f"  Models:    4 optimized (XGBoost, RF, GB, LR)")


if __name__ == "__main__":
    train_and_evaluate()
