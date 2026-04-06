# ML Model - Stage 1

## Overview
This module contains the machine learning model for heart disease prediction.

## Files
- `config.py`: Configuration and hyperparameters
- `data_preprocessing.py`: Data cleaning and preprocessing
- `train_model.py`: Model training script
- `predict.py`: Prediction module
- `requirements.txt`: Python dependencies

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Dataset
Download the UCI Heart Disease dataset:
- URL: https://archive.ics.uci.edu/ml/datasets/heart+disease
- Or use Kaggle: https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset

Place the CSV file in `ml_model/data/heart_disease_data.csv`

### 3. Train Models
```bash
python train_model.py
```

This will:
- Preprocess the data
- Train multiple models (XGBoost, Random Forest, Logistic Regression)
- Evaluate and compare models
- Save the best model

### 4. Make Predictions
```bash
python predict.py
```

## Data Format

### Input Features (Standard)
1. age: Age in years
2. sex: 1=male, 0=female
3. chest_pain_type: 0-3 (typical angina, atypical angina, non-anginal, asymptomatic)
4. resting_bp: Resting blood pressure (mm Hg)
5. cholesterol: Serum cholesterol (mg/dl)
6. fasting_blood_sugar: >120 mg/dl (1=true, 0=false)
7. resting_ecg: 0-2 (normal, ST-T abnormality, left ventricular hypertrophy)
8. max_heart_rate: Maximum heart rate achieved
9. exercise_induced_angina: 1=yes, 0=no
10. st_depression: ST depression induced by exercise
11. st_slope: 0-2 (upsloping, flat, downsloping)
12. num_major_vessels: Number of major vessels colored by fluoroscopy (0-3)
13. thalassemia: 0=normal, 1=fixed defect, 2=reversible defect

### Output
- Risk Level: Low, Medium, High
- Probability: 0-1
- Recommendations: List of health recommendations

## Model Performance (Expected)
- Accuracy: >85%
- Precision: >80%
- Recall: >80%
- F1-Score: >80%
- ROC-AUC: >0.85

## Next Steps (Stage 2)
- Integrate model with FastAPI backend
- Add API endpoints for predictions
- Implement model versioning
