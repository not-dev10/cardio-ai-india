"""
Model training script for heart disease prediction
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from config import MODEL_CONFIG, XGBOOST_PARAMS, MODELS_DIR, LOGS_DIR
from data_preprocessing import prepare_data_for_training


class HeartDiseaseModel:
    """Heart disease prediction model trainer"""
    
    def __init__(self, model_type="xgboost"):
        """
        Initialize model
        
        Args:
            model_type: Type of model ('xgboost', 'random_forest', 'logistic')
        """
        self.model_type = model_type
        self.model = self._initialize_model()
        self.metrics = {}
        
    def _initialize_model(self):
        """Initialize the selected model"""
        if self.model_type == "xgboost":
            return xgb.XGBClassifier(**XGBOOST_PARAMS)
        elif self.model_type == "random_forest":
            return RandomForestClassifier(
                n_estimators=100,
                random_state=MODEL_CONFIG["random_state"]
            )
        elif self.model_type == "logistic":
            return LogisticRegression(
                random_state=MODEL_CONFIG["random_state"],
                max_iter=1000
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train, y_train):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        print(f"\nTraining {self.model_type} model...")
        self.model.fit(X_train, y_train)
        print("Training completed!")
        
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        print("\nEvaluating model...")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        self.metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted'),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }
        
        # Print metrics
        print("\n" + "="*50)
        print(f"Model: {self.model_type.upper()}")
        print("="*50)
        for metric, value in self.metrics.items():
            print(f"{metric.capitalize()}: {value:.4f}")
        print("="*50)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:")
        print(cm)
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return self.metrics
    
    def plot_confusion_matrix(self, X_test, y_test):
        """Plot confusion matrix"""
        y_pred = self.model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix - {self.model_type}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = LOGS_DIR / f"confusion_matrix_{self.model_type}_{timestamp}.png"
        plt.savefig(plot_path)
        print(f"\nConfusion matrix saved to {plot_path}")
        plt.close()
    
    def get_feature_importance(self, feature_names):
        """
        Get feature importance
        
        Args:
            feature_names: List of feature names
            
        Returns:
            DataFrame: Feature importance
        """
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Important Features:")
            print(feature_importance.head(10))
            
            # Plot feature importance
            plt.figure(figsize=(10, 6))
            plt.barh(feature_importance['feature'][:10], 
                    feature_importance['importance'][:10])
            plt.xlabel('Importance')
            plt.title(f'Top 10 Feature Importance - {self.model_type}')
            plt.gca().invert_yaxis()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = LOGS_DIR / f"feature_importance_{self.model_type}_{timestamp}.png"
            plt.savefig(plot_path)
            print(f"Feature importance plot saved to {plot_path}")
            plt.close()
            
            return feature_importance
        else:
            print("Model does not support feature importance")
            return None
    
    def save_model(self):
        """Save trained model"""
        model_path = MODELS_DIR / f"{self.model_type}_model.joblib"
        joblib.dump(self.model, model_path)
        print(f"\nModel saved to {model_path}")
        
        # Save metrics
        metrics_path = LOGS_DIR / f"{self.model_type}_metrics.txt"
        with open(metrics_path, 'w') as f:
            f.write(f"Model: {self.model_type}\n")
            f.write(f"Timestamp: {datetime.now()}\n\n")
            for metric, value in self.metrics.items():
                f.write(f"{metric}: {value:.4f}\n")
        print(f"Metrics saved to {metrics_path}")
    
    def load_model(self):
        """Load a saved model"""
        model_path = MODELS_DIR / f"{self.model_type}_model.joblib"
        self.model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")
        return self.model


def train_and_compare_models(data_path):
    """
    Train multiple models and compare performance
    
    Args:
        data_path: Path to dataset
    """
    print("="*70)
    print("HEART DISEASE PREDICTION MODEL TRAINING")
    print("="*70)
    
    # Prepare data
    print("\nPreparing data...")
    result = prepare_data_for_training(data_path)
    
    if result is None:
        print("Error: Could not prepare data")
        return
    
    X_train, X_test, y_train, y_test, preprocessor = result
    
    # Feature names (adjust based on your dataset)
    feature_names = [f"feature_{i}" for i in range(X_train.shape[1])]
    
    # Train multiple models
    models = ["xgboost", "random_forest", "logistic"]
    results = {}
    
    for model_type in models:
        print(f"\n{'='*70}")
        print(f"Training {model_type.upper()} model")
        print(f"{'='*70}")
        
        # Initialize and train
        model = HeartDiseaseModel(model_type=model_type)
        model.train(X_train, y_train)
        
        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        results[model_type] = metrics
        
        # Plot confusion matrix
        model.plot_confusion_matrix(X_test, y_test)
        
        # Feature importance
        if model_type in ["xgboost", "random_forest"]:
            model.get_feature_importance(feature_names)
        
        # Save model
        model.save_model()
    
    # Compare models
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    comparison_df = pd.DataFrame(results).T
    print(comparison_df)
    
    # Find best model
    best_model = comparison_df['accuracy'].idxmax()
    print(f"\nBest Model: {best_model.upper()}")
    print(f"Accuracy: {comparison_df.loc[best_model, 'accuracy']:.4f}")
    
    return results


if __name__ == "__main__":
    # Example usage
    # Replace with actual dataset path
    data_path = "data/heart_disease_data.csv"
    
    print("Note: Please ensure you have the dataset at:", data_path)
    print("You can download UCI Heart Disease dataset from:")
    print("https://archive.ics.uci.edu/ml/datasets/heart+disease")
    
    # Uncomment to run training
    # train_and_compare_models(data_path)
