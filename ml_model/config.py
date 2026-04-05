"""
Configuration file for ML model training and prediction
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_CONFIG = {
    "random_state": 42,
    "test_size": 0.2,
    "cv_folds": 5,
}

# XGBoost hyperparameters
XGBOOST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1,
    "random_state": 42,
    "eval_metric": "logloss",
}

# Feature names (standard features)
STANDARD_FEATURES = [
    "age",
    "sex",  # 1=male, 0=female
    "chest_pain_type",  # 0-3
    "resting_bp",  # mm Hg
    "cholesterol",  # mg/dl
    "fasting_blood_sugar",  # >120 mg/dl (1=true, 0=false)
    "resting_ecg",  # 0-2
    "max_heart_rate",
    "exercise_induced_angina",  # 1=yes, 0=no
    "st_depression",
    "st_slope",  # 0-2
    "num_major_vessels",  # 0-3
    "thalassemia",  # 0-3
]

# Indian context features (to be added in Stage 4)
INDIAN_FEATURES = [
    "oil_type",  # 0=refined, 1=mustard, 2=coconut, 3=ghee
    "oil_consumption",  # liters per month
    "stress_level",  # 1-10
    "tobacco_usage",  # 0=none, 1=cigarette, 2=bidi, 3=gutka
    "physical_activity",  # minutes per week
    "diabetes_duration",  # years (if diabetic)
    "family_history",  # 1=yes, 0=no
]

# Risk thresholds
RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.6,
    "high": 1.0,
}

# Model file name
MODEL_FILE = "heart_disease_model.joblib"
SCALER_FILE = "feature_scaler.joblib"
