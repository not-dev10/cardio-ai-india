"""
Dataset Download Script
Downloads UCI Heart Disease dataset and prepares it for training
"""
import os
import urllib.request
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_uci_heart_disease():
    """
    Download UCI Heart Disease dataset
    
    Dataset: https://archive.ics.uci.edu/ml/datasets/heart+disease
    """
    logger.info("Downloading UCI Heart Disease dataset...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # UCI dataset URL (Cleveland database)
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    
    output_file = data_dir / "processed.cleveland.data"
    
    try:
        # Download file
        urllib.request.urlretrieve(url, output_file)
        logger.info(f"Downloaded to {output_file}")
        
        # Convert to CSV with proper column names
        column_names = [
            'age',
            'sex',
            'chest_pain_type',
            'resting_bp',
            'cholesterol',
            'fasting_blood_sugar',
            'resting_ecg',
            'max_heart_rate',
            'exercise_induced_angina',
            'st_depression',
            'st_slope',
            'num_major_vessels',
            'thalassemia',
            'target'
        ]
        
        # Read data
        df = pd.read_csv(output_file, names=column_names, na_values='?')
        
        # Convert target to binary (0 = no disease, 1-4 = disease)
        df['target'] = (df['target'] > 0).astype(int)
        
        # Save as CSV
        csv_file = data_dir / "heart_disease_data.csv"
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Converted to CSV: {csv_file}")
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Missing values:\n{df.isnull().sum()}")
        logger.info(f"Target distribution:\n{df['target'].value_counts()}")
        
        return csv_file
        
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        return None


def download_kaggle_heart_disease():
    """
    Alternative: Download from Kaggle (requires kaggle API)
    
    Instructions:
    1. Install kaggle: pip install kaggle
    2. Setup API key: https://www.kaggle.com/docs/api
    3. Run this function
    """
    logger.info("Downloading from Kaggle...")
    
    try:
        import kaggle
        
        # Create data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            'johnsmith88/heart-disease-dataset',
            path=data_dir,
            unzip=True
        )
        
        logger.info("Downloaded from Kaggle successfully")
        
        # Find the CSV file
        csv_files = list(data_dir.glob("*.csv"))
        if csv_files:
            logger.info(f"Found CSV: {csv_files[0]}")
            return csv_files[0]
        
    except ImportError:
        logger.error("Kaggle API not installed. Run: pip install kaggle")
    except Exception as e:
        logger.error(f"Error downloading from Kaggle: {e}")
    
    return None


def create_sample_dataset():
    """
    Create a small sample dataset for testing
    """
    logger.info("Creating sample dataset for testing...")
    
    from sklearn.datasets import make_classification
    import numpy as np
    
    # Generate synthetic data
    X, y = make_classification(
        n_samples=500,
        n_features=13,
        n_informative=10,
        n_redundant=3,
        n_classes=2,
        weights=[0.7, 0.3],
        random_state=42
    )
    
    # Create DataFrame with proper column names
    column_names = [
        'age', 'sex', 'chest_pain_type', 'resting_bp', 'cholesterol',
        'fasting_blood_sugar', 'resting_ecg', 'max_heart_rate',
        'exercise_induced_angina', 'st_depression', 'st_slope',
        'num_major_vessels', 'thalassemia'
    ]
    
    df = pd.DataFrame(X, columns=column_names)
    df['target'] = y
    
    # Scale to realistic ranges
    df['age'] = (df['age'] * 20 + 50).astype(int)
    df['sex'] = (df['sex'] > 0).astype(int)
    df['chest_pain_type'] = ((df['chest_pain_type'] + 2) % 4).astype(int)
    df['resting_bp'] = (df['resting_bp'] * 30 + 120).astype(int)
    df['cholesterol'] = (df['cholesterol'] * 80 + 200).astype(int)
    df['fasting_blood_sugar'] = (df['fasting_blood_sugar'] > 0).astype(int)
    df['resting_ecg'] = ((df['resting_ecg'] + 1) % 3).astype(int)
    df['max_heart_rate'] = (df['max_heart_rate'] * 40 + 120).astype(int)
    df['exercise_induced_angina'] = (df['exercise_induced_angina'] > 0).astype(int)
    df['st_depression'] = np.abs(df['st_depression'])
    df['st_slope'] = ((df['st_slope'] + 1) % 3).astype(int)
    df['num_major_vessels'] = ((df['num_major_vessels'] + 2) % 4).astype(int)
    df['thalassemia'] = ((df['thalassemia'] + 1) % 4).astype(int)
    
    # Save
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    csv_file = data_dir / "sample_heart_disease_data.csv"
    df.to_csv(csv_file, index=False)
    
    logger.info(f"Sample dataset created: {csv_file}")
    logger.info(f"Shape: {df.shape}")
    
    return csv_file


def main():
    """Main function to download dataset"""
    
    print("="*70)
    print("HEART DISEASE DATASET DOWNLOADER")
    print("="*70)
    
    print("\nOptions:")
    print("1. Download UCI Heart Disease dataset (recommended)")
    print("2. Download from Kaggle (requires API key)")
    print("3. Create sample dataset (for testing)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        dataset_file = download_uci_heart_disease()
    elif choice == "2":
        dataset_file = download_kaggle_heart_disease()
    elif choice == "3":
        dataset_file = create_sample_dataset()
    else:
        print("Invalid choice")
        return
    
    if dataset_file:
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print(f"Dataset saved to: {dataset_file}")
        print("\nNext steps:")
        print("1. Run: python train_model.py")
        print("2. Or run: python advanced_training.py")
    else:
        print("\n" + "="*70)
        print("FAILED")
        print("="*70)
        print("Could not download dataset")
        print("\nManual download:")
        print("1. Visit: https://archive.ics.uci.edu/ml/datasets/heart+disease")
        print("2. Download: processed.cleveland.data")
        print("3. Save as: ml_model/data/heart_disease_data.csv")


if __name__ == "__main__":
    main()
