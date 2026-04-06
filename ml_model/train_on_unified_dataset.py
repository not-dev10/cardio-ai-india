"""
Train models on unified dataset combining blood tests and synthetic reports
Uses the prepared datasets from download_and_prepare_datasets.py
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, 
    recall_score, f1_score, confusion_matrix, roc_curve
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("TRAINING ON UNIFIED DATASET")
print("=" * 70)

# Load unified dataset
print("\n[1/4] Loading unified dataset...")
unified_path = Path('ml_model/data/unified/unified_dataset.json')

if not unified_path.exists():
    print("❌ Unified dataset not found. Run download_and_prepare_datasets.py first")
    exit(1)

with open(unified_path, 'r') as f:
    unified_data = json.load(f)

print(f"✅ Loaded {len(unified_data)} samples")

# Prepare data for training
print("\n[2/4] Preparing data for training...")

X_list = []
y_list = []

for sample in unified_data:
    patient_data = sample.get('patient_data', {})
    
    # Extract features
    features = []
    feature_names = []
    
    # Standard features
    for key in ['age', 'sex', 'cholesterol', 'glucose', 'hemoglobin', 'creatinine']:
        if key in patient_data:
            features.append(float(patient_data[key]))
            feature_names.append(key)
    
    # Blood pressure handling
    if 'blood_pressure' in patient_data:
        bp = patient_data['blood_pressure']
        if isinstance(bp, str) and '/' in bp:
            sys, dia = bp.split('/')
            features.extend([float(sys), float(dia)])
            feature_names.extend(['bp_systolic', 'bp_diastolic'])
    elif 'blood_pressure_systolic' in patient_data:
        features.append(float(patient_data['blood_pressure_systolic']))
        feature_names.append('bp_systolic')
        if 'blood_pressure_diastolic' in patient_data:
            features.append(float(patient_data['blood_pressure_diastolic']))
            feature_names.append('bp_diastolic')
    
    # Additional features
    for key in ['ldl', 'hdl', 'triglycerides', 'trestbps', 'thalach', 'oldpeak']:
        if key in patient_data:
            features.append(float(patient_data[key]))
            feature_names.append(key)
    
    if len(features) > 0:
        X_list.append(features)
        
        # Target: use 'target' or 'heart_disease' field
        target = patient_data.get('target', patient_data.get('heart_disease', 0))
        
        # Handle NaN values
        if pd.isna(target):
            target = 0
        
        y_list.append(int(target))

# Convert to numpy arrays
X = np.array(X_list)
y = np.array(y_list)

print(f"✅ Prepared {len(X)} samples with {X.shape[1]} features")
print(f"   Feature names: {feature_names[:5]}... (showing first 5)")
print(f"   Class distribution: {np.bincount(y)}")

# Split data
print("\n[3/4] Splitting data (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✅ Training set: {len(X_train)} samples")
print(f"✅ Test set: {len(X_test)} samples")

# Train XGBoost model
print("\n[4/4] Training XGBoost model...")
model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=7,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)

model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)

# Evaluate
print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

y_pred = model.predict(X_test_scaled)
y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

auc = roc_auc_score(y_test, y_pred_proba)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print(f"\n📊 Performance Metrics:")
print(f"   AUC-ROC:  {auc:.4f}")
print(f"   Accuracy: {accuracy:.4f}")
print(f"   Precision: {precision:.4f}")
print(f"   Recall:   {recall:.4f}")
print(f"   F1-Score: {f1:.4f}")

# Feature importance
print(f"\n🔍 Top 10 Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']:20s}: {row['importance']:.4f}")

# Save model and scaler
print(f"\n💾 Saving model and scaler...")
models_dir = Path('ml_model/models')
models_dir.mkdir(exist_ok=True)

model.save_model(str(models_dir / 'unified_dataset_model.json'))
joblib.dump(scaler, models_dir / 'unified_dataset_scaler.joblib')

# Save metadata
metadata = {
    'model_type': 'XGBoost',
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'features': feature_names,
    'metrics': {
        'auc': float(auc),
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1)
    },
    'dataset_source': 'unified_dataset (UCI + NHANES + Synthetic Reports)',
    'feature_importance': feature_importance.to_dict('records')
}

with open(models_dir / 'unified_dataset_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Model saved to: ml_model/models/unified_dataset_model.json")
print(f"✅ Scaler saved to: ml_model/models/unified_dataset_scaler.joblib")
print(f"✅ Metadata saved to: ml_model/models/unified_dataset_metadata.json")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE")
print("=" * 70)
print(f"\n🎯 Next Steps:")
print(f"   1. Test model with: python ml_model/predict.py")
print(f"   2. Deploy to backend")
print(f"   3. Integrate with OCR pipeline")
print("=" * 70)
