"""
Data preprocessing module for heart disease prediction
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib
from config import MODEL_CONFIG, MODELS_DIR


class DataPreprocessor:
    """Handle all data preprocessing tasks"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def load_data(self, filepath):
        """
        Load dataset from CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame: Loaded data
        """
        try:
            df = pd.read_csv(filepath)
            print(f"Data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def handle_missing_values(self, df):
        """
        Handle missing values in the dataset
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame: Cleaned data
        """
        # Check for missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"Missing values found:\n{missing[missing > 0]}")
            
            # Fill numeric columns with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            
            # Fill categorical columns with mode
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                df[col] = df[col].fillna(df[col].mode()[0])
        
        return df
    
    def remove_outliers(self, df, columns, threshold=3):
        """
        Remove outliers using Z-score method
        
        Args:
            df: Input DataFrame
            columns: List of columns to check for outliers
            threshold: Z-score threshold (default: 3)
            
        Returns:
            DataFrame: Data without outliers
        """
        from scipy import stats
        
        z_scores = np.abs(stats.zscore(df[columns]))
        df_clean = df[(z_scores < threshold).all(axis=1)]
        
        removed = len(df) - len(df_clean)
        print(f"Removed {removed} outliers ({removed/len(df)*100:.2f}%)")
        
        return df_clean
    
    def scale_features(self, X_train, X_test):
        """
        Scale features using StandardScaler
        
        Args:
            X_train: Training features
            X_test: Test features
            
        Returns:
            Tuple: Scaled training and test features
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def balance_dataset(self, X, y):
        """
        Balance dataset using SMOTE
        
        Args:
            X: Features
            y: Target variable
            
        Returns:
            Tuple: Balanced features and target
        """
        smote = SMOTE(random_state=MODEL_CONFIG["random_state"])
        X_balanced, y_balanced = smote.fit_resample(X, y)
        
        print(f"Original dataset: {len(y)} samples")
        print(f"Balanced dataset: {len(y_balanced)} samples")
        print(f"Class distribution: {np.bincount(y_balanced)}")
        
        return X_balanced, y_balanced
    
    def split_data(self, X, y):
        """
        Split data into training and testing sets
        
        Args:
            X: Features
            y: Target variable
            
        Returns:
            Tuple: X_train, X_test, y_train, y_test
        """
        return train_test_split(
            X, y,
            test_size=MODEL_CONFIG["test_size"],
            random_state=MODEL_CONFIG["random_state"],
            stratify=y
        )
    
    def save_scaler(self):
        """Save the fitted scaler"""
        scaler_path = MODELS_DIR / "feature_scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        print(f"Scaler saved to {scaler_path}")
    
    def load_scaler(self):
        """Load a saved scaler"""
        scaler_path = MODELS_DIR / "feature_scaler.joblib"
        self.scaler = joblib.load(scaler_path)
        print(f"Scaler loaded from {scaler_path}")
        return self.scaler


def prepare_data_for_training(filepath):
    """
    Complete preprocessing pipeline
    
    Args:
        filepath: Path to dataset
        
    Returns:
        Tuple: X_train, X_test, y_train, y_test, preprocessor
    """
    preprocessor = DataPreprocessor()
    
    # Load data
    df = preprocessor.load_data(filepath)
    if df is None:
        return None
    
    # Handle missing values
    df = preprocessor.handle_missing_values(df)
    
    # Separate features and target
    # Assuming last column is target
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    # Split data
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)
    
    # Balance training data
    X_train_balanced, y_train_balanced = preprocessor.balance_dataset(X_train, y_train)
    
    # Scale features
    X_train_scaled, X_test_scaled = preprocessor.scale_features(
        X_train_balanced, X_test
    )
    
    # Save scaler
    preprocessor.save_scaler()
    
    return X_train_scaled, X_test_scaled, y_train_balanced, y_test, preprocessor


if __name__ == "__main__":
    # Test preprocessing
    print("Data preprocessing module loaded successfully")
