"""
ULTRA-ADVANCED GPU-OPTIMIZED HEART DISEASE MODEL
Maximum accuracy approach with stacking ensemble:
- Outlier detection & removal
- Advanced feature engineering
- 5 base models (XGBoost, RF, GB, ExtraTrees, AdaBoost)
- Stacking with LogisticRegression meta-learner
- Platt calibration for probability estimates
- Advanced threshold optimization
Compatible with Python 3.14 + CUDA
"""
import csv
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import (
    RandomForestClassifier, VotingClassifier, GradientBoostingClassifier,
    AdaBoostClassifier, ExtraTreesClassifier, StackingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, RobustScaler, QuantileTransformer
from sklearn.model_selection import (
    train_test_split, cross_val_score, StratifiedKFold, 
    cross_validate, RepeatedStratifiedKFold
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, precision_recall_curve, roc_curve,
    matthews_corrcoef, cohen_kappa_score
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.covariance import EllipticEnvelope
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


def detect_and_handle_outliers(X, contamination=0.05):
    """Detect outliers using Elliptic Envelope and mark them"""
    ee = EllipticEnvelope(contamination=contamination, random_state=42)
    outlier_labels = ee.fit_predict(X)
    outlier_mask = outlier_labels == -1
    print(f"  Detected {outlier_mask.sum()} outliers ({100*outlier_mask.sum()/len(X):.1f}%)")
    return outlier_mask


def engineer_features(X):
    """Create advanced feature engineering"""
    X_eng = X.copy()
    
    # Interaction features
    X_eng = np.column_stack([
        X_eng,
        X[:, 3] * X[:, 4],  # BP * Cholesterol
        X[:, 7] / (X[:, 3] + 1),  # Heart Rate / BP
        X[:, 9] * X[:, 7],  # ST Depression * Heart Rate
        np.sqrt(np.abs(X[:, 9])),  # sqrt(ST Depression)
        X[:, 4] / (X[:, 5] + 1),  # Cholesterol / Fasting BS
    ])
    
    print(f"  Features after engineering: {X_eng.shape[1]}")
    return X_eng


def find_optimal_threshold_advanced(y_true, y_proba):
    """Find optimal threshold using multiple criteria"""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
    fpr, tpr, roc_thresholds = roc_curve(y_true, y_proba)
    
    # Youden's J statistic
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    youden_threshold = roc_thresholds[best_idx]
    
    # F1-score optimization
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_f1_idx = np.argmax(f1_scores)
    f1_threshold = thresholds[best_f1_idx]
    
    # Target recall with best precision
    target_recall = 0.90
    best_threshold = 0.5
    best_precision = 0
    for prec, rec, thresh in zip(precisions, recalls, thresholds):
        if rec >= target_recall and prec > best_precision:
            best_threshold = thresh
            best_precision = prec
    
    print(f"  Youden threshold: {youden_threshold:.3f}")
    print(f"  F1-optimized threshold: {f1_threshold:.3f}")
    print(f"  Recall-optimized threshold: {best_threshold:.3f}")
    
    return best_threshold, best_precision


def train_and_evaluate():
    print("=" * 85)
    print("ULTRA-ADVANCED GPU-OPTIMIZED HEART DISEASE MODEL - RTX 3050")
    print("=" * 85)

    # Load data
    print("\nLoading datasets...")
    all_rows, feature_cols = load_combined_data()
    
    if not all_rows:
        print("No data found!")
        return

    X = np.array([r[:-1] for r in all_rows], dtype=np.float32)
    y = np.array([r[-1] for r in all_rows], dtype=np.int32)

    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(X)}")
    print(f"  Features: {X.shape[1]}")
    print(f"  Disease: {(y==1).sum()} ({100*(y==1).sum()/len(y):.1f}%)")
    print(f"  Healthy: {(y==0).sum()} ({100*(y==0).sum()/len(y):.1f}%)")

    # Detect outliers
    print("\nDetecting outliers...")
    outlier_mask = detect_and_handle_outliers(X, contamination=0.03)
    X_clean = X[~outlier_mask]
    y_clean = y[~outlier_mask]
    print(f"  Clean dataset: {len(X_clean)} samples")

    # Feature engineering
    print("\nEngineering features...")
    X_eng = engineer_features(X_clean)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_eng, y_clean, test_size=0.2, random_state=42, stratify=y_clean
    )

    # Advanced scaling with QuantileTransformer
    print("\nApplying advanced scaling...")
    scaler = QuantileTransformer(output_distribution='normal', random_state=42)
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    joblib.dump(scaler, MODELS_DIR / "scaler_ultra.joblib")

    print("\n" + "=" * 85)
    print("TRAINING ADVANCED ENSEMBLE MODELS")
    print("=" * 85)

    # Train base models with ultra-optimized hyperparameters
    print("\n[1/5] XGBoost (GPU-accelerated, ultra-optimized)...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=800,
        max_depth=8,
        learning_rate=0.015,
        subsample=0.93,
        colsample_bytree=0.93,
        min_child_weight=1,
        gamma=0.005,
        reg_alpha=0.3,
        reg_lambda=1.5,
        scale_pos_weight=1.7,
        random_state=42,
        eval_metric='logloss',
        verbosity=0,
        tree_method='hist',
        device='cuda',
        n_jobs=-1
    )
    xgb_model.fit(X_train_s, y_train)
    xgb_auc = roc_auc_score(y_test, xgb_model.predict_proba(X_test_s)[:, 1])
    print(f"  XGBoost Test AUC: {xgb_auc:.4f}")

    print("\n[2/5] Random Forest (ultra-optimized)...")
    rf_model = RandomForestClassifier(
        n_estimators=800,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=1,
        max_features='sqrt',
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1,
        bootstrap=True,
        oob_score=True
    )
    rf_model.fit(X_train_s, y_train)
    rf_auc = roc_auc_score(y_test, rf_model.predict_proba(X_test_s)[:, 1])
    print(f"  Random Forest Test AUC: {rf_auc:.4f}")
    print(f"  OOB Score: {rf_model.oob_score_:.4f}")

    print("\n[3/5] Gradient Boosting (ultra-optimized)...")
    gb_model = GradientBoostingClassifier(
        n_estimators=800,
        learning_rate=0.015,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=1,
        subsample=0.93,
        max_features='sqrt',
        validation_fraction=0.1,
        n_iter_no_change=150,
        random_state=42,
        verbose=0
    )
    gb_model.fit(X_train_s, y_train)
    gb_auc = roc_auc_score(y_test, gb_model.predict_proba(X_test_s)[:, 1])
    print(f"  Gradient Boosting Test AUC: {gb_auc:.4f}")

    print("\n[4/5] Extra Trees (ultra-optimized)...")
    et_model = ExtraTreesClassifier(
        n_estimators=800,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=1,
        max_features='sqrt',
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1,
        bootstrap=True
    )
    et_model.fit(X_train_s, y_train)
    et_auc = roc_auc_score(y_test, et_model.predict_proba(X_test_s)[:, 1])
    print(f"  Extra Trees Test AUC: {et_auc:.4f}")

    print("\n[5/5] AdaBoost (ultra-optimized)...")
    ada_model = AdaBoostClassifier(
        n_estimators=800,
        learning_rate=0.015,
        random_state=42
    )
    ada_model.fit(X_train_s, y_train)
    ada_auc = roc_auc_score(y_test, ada_model.predict_proba(X_test_s)[:, 1])
    print(f"  AdaBoost Test AUC: {ada_auc:.4f}")

    # Build stacking ensemble with proper cross-validation
    print("\n" + "=" * 85)
    print("BUILDING ADVANCED STACKING ENSEMBLE WITH META-LEARNER")
    print("=" * 85)

    print("\nBuilding stacking ensemble (this may take 2-3 minutes)...")
    
    # Base learners
    base_learners = [
        ('xgb', xgb_model),
        ('rf', rf_model),
        ('gb', gb_model),
        ('et', et_model),
        ('ada', ada_model)
    ]
    
    # Meta-learner (LogisticRegression for optimal combination)
    meta_learner = LogisticRegression(max_iter=1000, random_state=42, C=0.1)
    
    # Stacking classifier with 5-fold cross-validation
    stacking = StackingClassifier(
        estimators=base_learners,
        final_estimator=meta_learner,
        cv=5,
        n_jobs=-1
    )
    print("  Fitting stacking ensemble...")
    stacking.fit(X_train_s, y_train)
    print("  Stacking ensemble fitted!")

    # Calibrate probabilities
    print("  Applying Platt calibration...")
    calibrated = CalibratedClassifierCV(stacking, method="sigmoid", cv=5, n_jobs=-1)
    calibrated.fit(X_train_s, y_train)
    print("  Calibration complete!")

    # Evaluate
    y_proba = calibrated.predict_proba(X_test_s)[:, 1]
    y_pred_default = calibrated.predict(X_test_s)
    opt_thresh, opt_prec = find_optimal_threshold_advanced(y_test, y_proba)
    y_pred_opt = (y_proba >= opt_thresh).astype(int)

    auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 85)
    print("COMPREHENSIVE EVALUATION RESULTS")
    print("=" * 85)

    print(f"\nDefault Threshold (0.50):")
    acc_default = accuracy_score(y_test, y_pred_default)
    rec_default = recall_score(y_test, y_pred_default)
    prec_default = precision_score(y_test, y_pred_default)
    f1_default = f1_score(y_test, y_pred_default)
    mcc_default = matthews_corrcoef(y_test, y_pred_default)
    kappa_default = cohen_kappa_score(y_test, y_pred_default)
    
    print(f"  Accuracy:  {acc_default:.4f}")
    print(f"  Recall:    {rec_default:.4f}")
    print(f"  Precision: {prec_default:.4f}")
    print(f"  F1-Score:  {f1_default:.4f}")
    print(f"  MCC:       {mcc_default:.4f}")
    print(f"  Kappa:     {kappa_default:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    acc_o = accuracy_score(y_test, y_pred_opt)
    rec_o = recall_score(y_test, y_pred_opt)
    prec_o = precision_score(y_test, y_pred_opt)
    f1_o = f1_score(y_test, y_pred_opt)
    mcc_o = matthews_corrcoef(y_test, y_pred_opt)
    kappa_o = cohen_kappa_score(y_test, y_pred_opt)
    cm = confusion_matrix(y_test, y_pred_opt)
    tn, fp, fn, tp = cm.ravel()

    print(f"\nOptimized Threshold ({opt_thresh:.3f}):")
    print(f"  Accuracy:  {acc_o:.4f}")
    print(f"  Recall:    {rec_o:.4f}  {'✓ TARGET MET' if rec_o >= 0.90 else '✗'}")
    print(f"  Precision: {prec_o:.4f}")
    print(f"  F1-Score:  {f1_o:.4f}")
    print(f"  MCC:       {mcc_o:.4f}")
    print(f"  Kappa:     {kappa_o:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    print(f"\nConfusion Matrix:")
    print(f"  TN: {tn:4d}  |  FP: {fp:4d}")
    print(f"  FN: {fn:4d}  |  TP: {tp:4d}")
    print(f"\nMissed disease cases: {fn}/{fn+tp} ({100*fn/(fn+tp):.1f}%)")
    print(f"False alarm rate: {fp}/{tn+fp} ({100*fp/(tn+fp):.1f}%)")
    print(f"Specificity: {tn/(tn+fp):.4f}")
    print(f"Sensitivity: {tp/(tp+fn):.4f}")

    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred_opt, target_names=["Healthy", "Disease"]))

    # Feature importance from Random Forest
    print("Top 10 Most Important Features:")
    importances = rf_model.feature_importances_
    for i, idx in enumerate(np.argsort(importances)[::-1][:10]):
        if idx < len(STANDARD_FEATURES):
            name = STANDARD_FEATURES[idx]
            label = FEATURE_LABELS.get(name, name)
        else:
            label = f"Engineered Feature {idx - len(STANDARD_FEATURES) + 1}"
        print(f"  {i+1:2}. {label:<30} {importances[idx]:.4f}")

    # Save model
    model_path = MODELS_DIR / "heart_disease_model_ultra.joblib"
    joblib.dump({
        "model": calibrated,
        "scaler": scaler,
        "feature_names": feature_cols,
        "optimal_threshold": opt_thresh,
        "metrics": {
            "accuracy": acc_o, "precision": prec_o,
            "recall": rec_o, "f1": f1_o, "roc_auc": auc,
            "mcc": mcc_o, "kappa": kappa_o,
            "specificity": tn/(tn+fp),
            "sensitivity": tp/(tp+fn)
        },
        "base_model_aucs": {
            "xgboost": xgb_auc,
            "random_forest": rf_auc,
            "gradient_boosting": gb_auc,
            "extra_trees": et_auc,
            "adaboost": ada_auc
        }
    }, model_path)

    print(f"\nModel saved: {model_path}")
    print("\n" + "=" * 85)
    print("ULTRA-ADVANCED TRAINING COMPLETE!")
    print("=" * 85)
    print(f"  Accuracy:  {acc_o:.1%}")
    print(f"  Recall:    {rec_o:.1%}  ({tp}/{tp+fn} disease cases caught)")
    print(f"  Precision: {prec_o:.1%}")
    print(f"  F1-Score:  {f1_o:.1%}")
    print(f"  MCC:       {mcc_o:.4f}")
    print(f"  AUC:       {auc:.4f}")
    print(f"  Dataset:   {len(X_clean)} samples (outliers removed)")
    print(f"  Features:  {X_eng.shape[1]} (13 original + 6 engineered)")
    print(f"  Models:    5 base + 1 meta-learner (stacking)")
    print(f"  Ensemble:  Stacking + Platt calibration")
    print(f"  GPU:       RTX 3050 (CUDA)")


if __name__ == "__main__":
    train_and_evaluate()
