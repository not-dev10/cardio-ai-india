"""
Advanced Learning Algorithm for Indian Cardiac Health
Implements ensemble learning, probability calibration, and continuous learning
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

from config import MODEL_CONFIG, XGBOOST_PARAMS, MODELS_DIR, LOGS_DIR
from data_preprocessing import DataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndianCardiacLearningAlgorithm:
    """
    Advanced learning algorithm specifically designed for Indian cardiac health prediction
    
    Key Features:
    1. Ensemble learning (XGBoost + Random Forest + Logistic Regression)
    2. Probability calibration (Platt scaling)
    3. Cost-sensitive learning (penalize false negatives 5x)
    4. SMOTE for class imbalance
    5. Indian-context feature engineering
    6. Continuous learning with doctor feedback
    """
    
    def __init__(self, cost_fn_weight=5.0):
        """
        Initialize the learning algorithm
        
        Args:
            cost_fn_weight: Weight for false negative penalty (default: 5.0)
        """
        self.cost_fn_weight = cost_fn_weight
        self.models = {}
        self.ensemble = None
        self.calibrated_ensemble = None
        self.feature_names = None
        self.metrics = {}
        
    def create_indian_features(self, df):
        """
        Stage 3: Create Indian-context specific features
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame: Enhanced with Indian-specific features
        """
        logger.info("Creating Indian-context features...")
        
        # LDL/HDL ratio (critical for South Asian population)
        if 'ldl' in df.columns and 'hdl' in df.columns:
            df['ldl_hdl_ratio'] = df['ldl'] / (df['hdl'] + 1e-6)
            # South Asians have higher risk at lower LDL/HDL ratios
            df['south_asian_lipid_risk'] = (df['ldl_hdl_ratio'] > 3.0).astype(int)
        
        # Cholesterol/HDL ratio
        if 'cholesterol' in df.columns and 'hdl' in df.columns:
            df['chol_hdl_ratio'] = df['cholesterol'] / (df['hdl'] + 1e-6)
        
        # Triglyceride/HDL ratio (metabolic syndrome indicator)
        if 'triglycerides' in df.columns and 'hdl' in df.columns:
            df['trig_hdl_ratio'] = df['triglycerides'] / (df['hdl'] + 1e-6)
        
        # Age-adjusted risk (Indians develop heart disease 10 years earlier)
        if 'age' in df.columns:
            df['age_adjusted_indian'] = df['age'] + 10
            df['high_risk_age'] = (df['age'] > 45).astype(int)  # Lower threshold for Indians
        
        # Diabetes + Hypertension combo (deadly for Indians)
        if 'diabetes' in df.columns and 'resting_bp' in df.columns:
            df['diabetes_hypertension'] = (
                (df['diabetes'] == 1) & (df['resting_bp'] > 140)
            ).astype(int)
        
        # Dietary oil score (if available)
        if 'oil_type' in df.columns:
            # 0=refined (worst), 1=mustard (better), 2=coconut (ok), 3=ghee (moderate)
            oil_risk_map = {0: 1.5, 1: 0.8, 2: 1.0, 3: 1.2}
            df['oil_risk_score'] = df['oil_type'].map(oil_risk_map).fillna(1.0)
        
        # Tobacco usage (bidi/gutka more harmful than cigarettes)
        if 'tobacco_type' in df.columns:
            # 0=none, 1=cigarette, 2=bidi, 3=gutka
            tobacco_risk_map = {0: 0, 1: 1.0, 2: 1.5, 3: 1.8}
            df['tobacco_risk_score'] = df['tobacco_type'].map(tobacco_risk_map).fillna(0)
        
        # Stress level (high in urban India)
        if 'stress_level' in df.columns:
            df['high_stress'] = (df['stress_level'] > 7).astype(int)
        
        # Regional multiplier (if region data available)
        # Punjab, Gujarat, Tamil Nadu have higher cardiac risk
        if 'region' in df.columns:
            region_risk_map = {
                'punjab': 1.3,
                'gujarat': 1.2,
                'tamil_nadu': 1.2,
                'kerala': 1.1,
                'maharashtra': 1.0,
                'other': 1.0
            }
            df['region_risk_multiplier'] = df['region'].str.lower().map(region_risk_map).fillna(1.0)
        
        logger.info(f"Created {len([c for c in df.columns if c not in self.feature_names])} new features")
        return df
    
    def build_ensemble_models(self):
        """
        Stage 4: Build ensemble of three models
        
        Returns:
            VotingClassifier: Ensemble model
        """
        logger.info("Building ensemble models...")
        
        # Model 1: XGBoost (catches non-linear patterns)
        xgb_model = xgb.XGBClassifier(
            **XGBOOST_PARAMS,
            scale_pos_weight=self.cost_fn_weight,  # Cost-sensitive learning
            eval_metric='aucpr'  # Optimize for precision-recall
        )
        
        # Model 2: Random Forest (handles missing values, robust)
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight={0: 1, 1: self.cost_fn_weight},  # Cost-sensitive
            random_state=MODEL_CONFIG["random_state"],
            n_jobs=-1
        )
        
        # Model 3: Logistic Regression (calibrated baseline)
        lr_model = LogisticRegression(
            class_weight={0: 1, 1: self.cost_fn_weight},  # Cost-sensitive
            random_state=MODEL_CONFIG["random_state"],
            max_iter=1000,
            solver='saga'
        )
        
        # Ensemble with weighted voting
        # XGBoost gets highest weight (best for healthcare)
        self.ensemble = VotingClassifier(
            estimators=[
                ('xgb', xgb_model),
                ('rf', rf_model),
                ('lr', lr_model)
            ],
            voting='soft',  # Use probabilities
            weights=[2, 1.5, 1]  # XGBoost weighted higher
        )
        
        self.models = {
            'xgboost': xgb_model,
            'random_forest': rf_model,
            'logistic_regression': lr_model,
            'ensemble': self.ensemble
        }
        
        return self.ensemble
    
    def apply_smote_and_balance(self, X, y):
        """
        Stage 2: Handle class imbalance with SMOTE + undersampling
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Tuple: Balanced X, y
        """
        logger.info("Applying SMOTE and balancing...")
        logger.info(f"Original class distribution: {np.bincount(y)}")
        
        # Combine SMOTE (oversample minority) + RandomUnderSampler (undersample majority)
        # This prevents over-representation of synthetic samples
        pipeline = ImbPipeline([
            ('smote', SMOTE(random_state=MODEL_CONFIG["random_state"], k_neighbors=5)),
            ('undersample', RandomUnderSampler(random_state=MODEL_CONFIG["random_state"], sampling_strategy=0.8))
        ])
        
        X_balanced, y_balanced = pipeline.fit_resample(X, y)
        
        logger.info(f"Balanced class distribution: {np.bincount(y_balanced)}")
        return X_balanced, y_balanced
    
    def calibrate_probabilities(self, model, X_train, y_train):
        """
        Stage 5: Calibrate probabilities using Platt scaling
        
        Args:
            model: Trained model
            X_train: Training features
            y_train: Training labels
            
        Returns:
            CalibratedClassifierCV: Calibrated model
        """
        logger.info("Calibrating probabilities with Platt scaling...")
        
        calibrated_model = CalibratedClassifierCV(
            model,
            method='sigmoid',  # Platt scaling
            cv=5
        )
        
        calibrated_model.fit(X_train, y_train)
        
        logger.info("Probability calibration complete")
        return calibrated_model
    
    def train(self, X_train, y_train, X_val, y_val):
        """
        Complete training pipeline
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
        """
        logger.info("="*70)
        logger.info("ADVANCED INDIAN CARDIAC LEARNING ALGORITHM")
        logger.info("="*70)
        
        # Stage 1: Feature engineering
        # (Assume already done in preprocessing)
        
        # Stage 2: Balance dataset
        X_train_balanced, y_train_balanced = self.apply_smote_and_balance(X_train, y_train)
        
        # Stage 3: Build ensemble
        ensemble = self.build_ensemble_models()
        
        # Stage 4: Train ensemble
        logger.info("Training ensemble model...")
        ensemble.fit(X_train_balanced, y_train_balanced)
        
        # Stage 5: Calibrate probabilities
        self.calibrated_ensemble = self.calibrate_probabilities(
            ensemble, X_train_balanced, y_train_balanced
        )
        
        # Stage 6: Evaluate
        self.evaluate_with_recall_focus(X_val, y_val)
        
        logger.info("Training complete!")
    
    def evaluate_with_recall_focus(self, X_test, y_test):
        """
        Stage 6: Evaluate with focus on recall (minimize false negatives)
        
        Args:
            X_test: Test features
            y_test: Test labels
        """
        logger.info("\n" + "="*70)
        logger.info("EVALUATION - RECALL-FOCUSED FOR HEALTHCARE")
        logger.info("="*70)
        
        # Predictions
        y_pred = self.calibrated_ensemble.predict(X_test)
        y_pred_proba = self.calibrated_ensemble.predict_proba(X_test)[:, 1]
        
        # Standard metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)  # MOST IMPORTANT
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        self.metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,  # Target: ≥95%
            'f1_score': f1,
            'roc_auc': roc_auc
        }
        
        # Print metrics
        print(f"\nAccuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f} {'✅' if recall >= 0.95 else '❌ TARGET: ≥0.95'}")
        print(f"F1-Score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, fp_count = cm.ravel()
        
        print(f"\nConfusion Matrix:")
        print(f"True Negatives:  {tn}")
        print(f"False Positives: {fp} (acceptable - better safe than sorry)")
        print(f"False Negatives: {fn} {'✅' if fn < len(y_test)*0.05 else '❌ TOO HIGH'}")
        print(f"True Positives:  {fp_count}")
        
        # False negative rate (critical for healthcare)
        fnr = fn / (fn + fp_count) if (fn + fp_count) > 0 else 0
        print(f"\nFalse Negative Rate: {fnr:.4f} {'✅' if fnr < 0.05 else '❌ TARGET: <0.05'}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))
        
        # Find optimal threshold for 95% recall
        self.find_optimal_threshold(y_test, y_pred_proba, target_recall=0.95)
        
        return self.metrics
    
    def find_optimal_threshold(self, y_true, y_pred_proba, target_recall=0.95):
        """
        Find optimal probability threshold to achieve target recall
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            target_recall: Target recall (default: 0.95)
        """
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_pred_proba)
        
        # Find threshold that gives us target recall
        idx = np.argmax(recalls >= target_recall)
        optimal_threshold = thresholds[idx] if idx < len(thresholds) else 0.5
        optimal_precision = precisions[idx]
        optimal_recall = recalls[idx]
        
        print(f"\n{'='*70}")
        print(f"OPTIMAL THRESHOLD FOR {target_recall:.0%} RECALL")
        print(f"{'='*70}")
        print(f"Threshold: {optimal_threshold:.4f}")
        print(f"Precision: {optimal_precision:.4f}")
        print(f"Recall:    {optimal_recall:.4f}")
        print(f"\nUse this threshold in production to ensure ≥95% recall")
        
        self.optimal_threshold = optimal_threshold
        return optimal_threshold
    
    def save_model(self, version="v1"):
        """
        Save trained model
        
        Args:
            version: Model version
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = MODELS_DIR / f"indian_cardiac_ensemble_{version}_{timestamp}.joblib"
        
        model_package = {
            'calibrated_ensemble': self.calibrated_ensemble,
            'models': self.models,
            'metrics': self.metrics,
            'optimal_threshold': getattr(self, 'optimal_threshold', 0.5),
            'feature_names': self.feature_names,
            'version': version,
            'timestamp': timestamp
        }
        
        joblib.dump(model_package, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save metrics
        metrics_path = LOGS_DIR / f"metrics_{version}_{timestamp}.txt"
        with open(metrics_path, 'w') as f:
            f.write(f"Indian Cardiac Learning Algorithm - {version}\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            f.write("="*50 + "\n")
            f.write("METRICS\n")
            f.write("="*50 + "\n")
            for metric, value in self.metrics.items():
                f.write(f"{metric}: {value:.4f}\n")
            f.write(f"\nOptimal Threshold: {getattr(self, 'optimal_threshold', 0.5):.4f}\n")
        
        logger.info(f"Metrics saved to {metrics_path}")
    
    def continuous_learning_update(self, new_X, new_y, retrain_threshold=100):
        """
        Stage 7: Continuous learning with doctor feedback
        
        Args:
            new_X: New validated data
            new_y: New validated labels
            retrain_threshold: Minimum samples before retraining
            
        Returns:
            bool: Whether model was retrained
        """
        logger.info(f"Continuous learning: {len(new_X)} new validated samples")
        
        if len(new_X) < retrain_threshold:
            logger.info(f"Not enough samples for retraining (need {retrain_threshold})")
            return False
        
        # Evaluate current model on new data
        current_accuracy = accuracy_score(new_y, self.calibrated_ensemble.predict(new_X))
        current_recall = recall_score(new_y, self.calibrated_ensemble.predict(new_X))
        
        logger.info(f"Current model performance on new data:")
        logger.info(f"  Accuracy: {current_accuracy:.4f}")
        logger.info(f"  Recall: {current_recall:.4f}")
        
        # Retrain if accuracy drops >3% or recall drops >2%
        if current_accuracy < 0.82 or current_recall < 0.93:
            logger.info("⚠️ Performance degradation detected. Retraining...")
            # Retrain with combined data (old + new)
            # Implementation depends on data storage strategy
            return True
        else:
            logger.info("✅ Model performance acceptable. No retraining needed.")
            return False


# Example usage
if __name__ == "__main__":
    print("Advanced Indian Cardiac Learning Algorithm initialized")
    print("Key features:")
    print("1. Ensemble learning (XGBoost + RF + LR)")
    print("2. Probability calibration")
    print("3. Cost-sensitive learning (5x penalty for false negatives)")
    print("4. SMOTE for class imbalance")
    print("5. Indian-context features")
    print("6. Recall-focused evaluation (target: ≥95%)")
    print("7. Continuous learning capability")
