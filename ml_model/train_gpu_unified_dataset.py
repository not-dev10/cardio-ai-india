"""
GPU-Accelerated Training on Unified Dataset
Uses CUDA/GPU for RTX 3050 with CPU fallback
Optimized for maximum performance and accuracy
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, QuantileTransformer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, 
    recall_score, f1_score, confusion_matrix, roc_curve, matthews_corrcoef
)
import warnings
warnings.filterwarnings('ignore')

# GPU Detection
print("=" * 70)
print("GPU-ACCELERATED TRAINING ON UNIFIED DATASET")
print("=" * 70)

try:
    import cupy as cp
    import cuml
    GPU_AVAILABLE = True
    print("✅ GPU (CUDA) detected - using GPU acceleration")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  GPU libraries not available - using CPU with intensive optimization")

# Load unified dataset
print("\n[1/5] Loading unified dataset...")
unified_path = Path('ml_model/data/unified/unified_dataset.json')

if not unified_path.exists():
    print("❌ Unified dataset not found. Run download_and_prepare_datasets.py first")
    exit(1)

with open(unified_path, 'r') as f:
    unified_data = json.load(f)

print(f"✅ Loaded {len(unified_data)} samples")

# Prepare data for training
print("\n[2/5] Preparing data for training...")

# Define consistent feature set
feature_names = ['age', 'sex', 'cholesterol', 'glucose', 'hemoglobin', 'creatinine', 
                 'bp_systolic', 'bp_diastolic', 'ldl', 'hdl', 'triglycerides']

X_list = []
y_list = []

for sample in unified_data:
    patient_data = sample.get('patient_data', {})
    
    # Extract features in consistent order
    features = []
    
    # Age
    features.append(float(patient_data.get('age', 50)))
    
    # Sex
    features.append(float(patient_data.get('sex', 0)))
    
    # Cholesterol
    features.append(float(patient_data.get('cholesterol', 200)))
    
    # Glucose
    features.append(float(patient_data.get('glucose', 100)))
    
    # Hemoglobin
    features.append(float(patient_data.get('hemoglobin', 13.5)))
    
    # Creatinine
    features.append(float(patient_data.get('creatinine', 1.0)))
    
    # Blood pressure systolic
    bp_sys = 130
    if 'blood_pressure' in patient_data:
        bp = patient_data['blood_pressure']
        if isinstance(bp, str) and '/' in bp:
            try:
                bp_sys = float(bp.split('/')[0])
            except:
                pass
    elif 'blood_pressure_systolic' in patient_data:
        bp_sys = float(patient_data['blood_pressure_systolic'])
    elif 'trestbps' in patient_data:
        bp_sys = float(patient_data['trestbps'])
    features.append(bp_sys)
    
    # Blood pressure diastolic
    bp_dia = 80
    if 'blood_pressure' in patient_data:
        bp = patient_data['blood_pressure']
        if isinstance(bp, str) and '/' in bp:
            try:
                bp_dia = float(bp.split('/')[1])
            except:
                pass
    elif 'blood_pressure_diastolic' in patient_data:
        bp_dia = float(patient_data['blood_pressure_diastolic'])
    features.append(bp_dia)
    
    # LDL
    features.append(float(patient_data.get('ldl', 130)))
    
    # HDL
    features.append(float(patient_data.get('hdl', 50)))
    
    # Triglycerides
    features.append(float(patient_data.get('triglycerides', 150)))
    
    X_list.append(features)
    
    # Target
    target = patient_data.get('target', patient_data.get('heart_disease', 0))
    if pd.isna(target):
        target = 0
    y_list.append(int(target))

# Convert to numpy arrays
X = np.array(X_list, dtype=np.float32)
y = np.array(y_list, dtype=np.int32)

print(f"✅ Prepared {len(X)} samples with {X.shape[1]} features")
print(f"   Class distribution: {np.bincount(y)}")

# Split data
print("\n[3/5] Splitting data (80/20) and preprocessing...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Advanced preprocessing with QuantileTransformer (better for non-normal distributions)
preprocessor = QuantileTransformer(n_quantiles=1000, output_distribution='normal', random_state=42)
X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)

print(f"✅ Training set: {len(X_train)} samples")
print(f"✅ Test set: {len(X_test)} samples")
print(f"✅ Preprocessing: QuantileTransformer applied")

# Train GPU-accelerated XGBoost
print("\n[4/5] Training GPU-accelerated XGBoost model...")

if GPU_AVAILABLE:
    print("   Using GPU (CUDA) for training...")
    tree_method = 'gpu_hist'
    gpu_id = 0
else:
    print("   Using CPU with intensive optimization...")
    tree_method = 'hist'
    gpu_id = None

model = xgb.XGBClassifier(
    n_estimators=1000,
    max_depth=8,
    learning_rate=0.05,
    subsample=0.85,
    colsample_bytree=0.85,
    colsample_bylevel=0.85,
    min_child_weight=1,
    gamma=0.5,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    verbosity=0,
    tree_method=tree_method,
    gpu_id=gpu_id if GPU_AVAILABLE else None,
    predictor='gpu_predictor' if GPU_AVAILABLE else 'auto'
)

# Train with early stopping
model.fit(
    X_train_processed, y_train,
    eval_set=[(X_test_processed, y_test)],
    verbose=False
)

# Evaluate
print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

y_pred = model.predict(X_test_processed)
y_pred_proba = model.predict_proba(X_test_processed)[:, 1] if len(np.unique(y)) == 2 else model.predict_proba(X_test_processed)

# Handle multi-class
if len(np.unique(y)) > 2:
    auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
else:
    auc = roc_auc_score(y_test, y_pred_proba)
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0, average='weighted')
recall = recall_score(y_test, y_pred, zero_division=0, average='weighted')
f1 = f1_score(y_test, y_pred, zero_division=0, average='weighted')
mcc = matthews_corrcoef(y_test, y_pred)

print(f"\n📊 Performance Metrics:")
print(f"   AUC-ROC:  {auc:.4f}")
print(f"   Accuracy: {accuracy:.4f}")
print(f"   Precision: {precision:.4f}")
print(f"   Recall:   {recall:.4f}")
print(f"   F1-Score: {f1:.4f}")
print(f"   MCC:      {mcc:.4f}")

# Feature importance
print(f"\n🔍 Top 15 Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(15).iterrows():
    print(f"   {row['feature']:20s}: {row['importance']:.4f}")

# Save model, preprocessor, and metadata
print(f"\n💾 Saving model, preprocessor, and metadata...")
models_dir = Path('ml_model/models')
models_dir.mkdir(exist_ok=True)

model.save_model(str(models_dir / 'unified_dataset_gpu_model.json'))
joblib.dump(preprocessor, models_dir / 'unified_dataset_preprocessor.joblib')

# Save metadata
metadata = {
    'model_type': 'XGBoost (GPU-Accelerated)',
    'gpu_enabled': GPU_AVAILABLE,
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'features': feature_names,
    'preprocessing': 'QuantileTransformer',
    'metrics': {
        'auc': float(auc),
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'mcc': float(mcc)
    },
    'dataset_source': 'unified_dataset (UCI + NHANES + Synthetic Reports)',
    'feature_importance': feature_importance.to_dict('records'),
    'hyperparameters': {
        'n_estimators': 1000,
        'max_depth': 8,
        'learning_rate': 0.05,
        'subsample': 0.85,
        'colsample_bytree': 0.85,
        'tree_method': tree_method
    }
}

with open(models_dir / 'unified_dataset_gpu_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Model saved to: ml_model/models/unified_dataset_gpu_model.json")
print(f"✅ Preprocessor saved to: ml_model/models/unified_dataset_preprocessor.joblib")
print(f"✅ Metadata saved to: ml_model/models/unified_dataset_gpu_metadata.json")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE")
print("=" * 70)
print(f"\n🎯 Next Steps:")
print(f"   1. Test model with: python ml_model/predict.py")
print(f"   2. Deploy to backend")
print(f"   3. Integrate with OCR pipeline")
print(f"\n💡 GPU Status: {'✅ CUDA Enabled' if GPU_AVAILABLE else '⚠️  CPU Mode (Install RAPIDS for GPU)'}")
print("=" * 70)
