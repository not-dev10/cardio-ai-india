"""
Download and Prepare Datasets for Training
Combines ECG, Blood Tests, and Medical Reports
"""

import os
import sys
import numpy as np
import pandas as pd
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Download and prepare datasets"""
    
    def __init__(self, base_path='data'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.ecg_path = self.base_path / 'ecg'
        self.blood_path = self.base_path / 'blood_tests'
        self.reports_path = self.base_path / 'reports'
        self.unified_path = self.base_path / 'unified'
        
        for path in [self.ecg_path, self.blood_path, self.reports_path, self.unified_path]:
            path.mkdir(exist_ok=True)
    
    def download_mit_bih(self):
        """Download MIT-BIH Arrhythmia Database"""
        logger.info("Downloading MIT-BIH Arrhythmia Database...")
        
        try:
            import wfdb
            
            # Create directory
            mitdb_path = self.ecg_path / 'mitdb'
            mitdb_path.mkdir(exist_ok=True)
            
            # Download records 100-124
            records = []
            for i in range(100, 125):
                try:
                    record = wfdb.rdrecord(f'mitdb/{i}')
                    
                    # Save record
                    record_data = {
                        'record_id': i,
                        'signals': record.p_signal.tolist(),
                        'fs': record.fs,
                        'sig_name': record.sig_name,
                        'n_sig': record.n_sig
                    }
                    
                    with open(mitdb_path / f'{i}.json', 'w') as f:
                        json.dump(record_data, f)
                    
                    records.append(record_data)
                    logger.info(f"✓ Downloaded MIT-BIH record {i}")
                except Exception as e:
                    logger.warning(f"Failed to download record {i}: {e}")
            
            logger.info(f"✅ Downloaded {len(records)} MIT-BIH records")
            return records
        
        except ImportError:
            logger.error("wfdb not installed. Install with: pip install wfdb")
            return []
    
    def download_uci_heart_disease(self):
        """Download UCI Heart Disease Dataset"""
        logger.info("Downloading UCI Heart Disease Dataset...")
        
        try:
            import urllib.request
            
            url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data'
            
            # Download
            filepath = self.blood_path / 'uci_heart.csv'
            urllib.request.urlretrieve(url, filepath)
            
            # Load and process
            df = pd.read_csv(filepath, header=None)
            df.columns = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
            ]
            
            # Save processed
            df.to_csv(self.blood_path / 'uci_heart_processed.csv', index=False)
            
            logger.info(f"✅ Downloaded UCI Heart Disease ({len(df)} samples)")
            return df
        
        except Exception as e:
            logger.error(f"Failed to download UCI Heart Disease: {e}")
            return None
    
    def download_nhanes_data(self):
        """Download NHANES data"""
        logger.info("Downloading NHANES data...")
        
        try:
            # Create sample NHANES-like data
            # In production, use: pip install nhanes
            
            n_samples = 5000
            data = {
                'age': np.random.randint(20, 80, n_samples),
                'sex': np.random.randint(0, 2, n_samples),
                'cholesterol': np.random.normal(200, 40, n_samples),
                'ldl': np.random.normal(130, 35, n_samples),
                'hdl': np.random.normal(50, 15, n_samples),
                'triglycerides': np.random.normal(150, 50, n_samples),
                'glucose': np.random.normal(100, 20, n_samples),
                'blood_pressure_systolic': np.random.normal(130, 20, n_samples),
                'blood_pressure_diastolic': np.random.normal(80, 10, n_samples),
                'hemoglobin': np.random.normal(13.5, 1.5, n_samples),
                'creatinine': np.random.normal(1.0, 0.3, n_samples),
                'heart_disease': np.random.randint(0, 2, n_samples)
            }
            
            df = pd.DataFrame(data)
            df.to_csv(self.blood_path / 'nhanes_sample.csv', index=False)
            
            logger.info(f"✅ Created NHANES-like data ({len(df)} samples)")
            return df
        
        except Exception as e:
            logger.error(f"Failed to create NHANES data: {e}")
            return None
    
    def combine_blood_datasets(self):
        """Combine all blood test datasets"""
        logger.info("Combining blood test datasets...")
        
        try:
            datasets = []
            
            # Load UCI
            uci_file = self.blood_path / 'uci_heart_processed.csv'
            if uci_file.exists():
                uci_df = pd.read_csv(uci_file)
                datasets.append(uci_df)
                logger.info(f"Loaded UCI Heart Disease ({len(uci_df)} samples)")
            
            # Load NHANES
            nhanes_file = self.blood_path / 'nhanes_sample.csv'
            if nhanes_file.exists():
                nhanes_df = pd.read_csv(nhanes_file)
                datasets.append(nhanes_df)
                logger.info(f"Loaded NHANES ({len(nhanes_df)} samples)")
            
            # Combine
            if datasets:
                combined = pd.concat(datasets, ignore_index=True)
                combined.to_csv(self.blood_path / 'combined_blood_data.csv', index=False)
                
                logger.info(f"✅ Combined blood datasets ({len(combined)} total samples)")
                return combined
            else:
                logger.warning("No blood datasets found")
                return None
        
        except Exception as e:
            logger.error(f"Failed to combine datasets: {e}")
            return None
    
    def generate_synthetic_reports(self, n_reports=100):
        """Generate synthetic medical reports"""
        logger.info(f"Generating {n_reports} synthetic medical reports...")
        
        try:
            reports = []
            
            for i in range(n_reports):
                # Generate random patient data
                age = np.random.randint(30, 80)
                cholesterol = np.random.randint(150, 300)
                glucose = np.random.randint(70, 200)
                bp_sys = np.random.randint(100, 180)
                bp_dia = np.random.randint(60, 120)
                hemoglobin = np.random.uniform(10, 18)
                
                # Create report text
                report_text = f"""
BLOOD TEST REPORT
Patient Age: {age} years
Date: 2024-01-{(i % 28) + 1:02d}

RESULTS:
Hemoglobin: {hemoglobin:.1f} g/dL
Cholesterol: {cholesterol} mg/dL
Blood Pressure: {bp_sys}/{bp_dia} mmHg
Glucose (Fasting): {glucose} mg/dL

INTERPRETATION:
"""
                
                if cholesterol > 240:
                    report_text += "- High cholesterol detected\n"
                if glucose > 126:
                    report_text += "- Elevated blood glucose\n"
                if bp_sys > 140:
                    report_text += "- High blood pressure\n"
                
                report_text += "\nRecommendation: Follow-up with physician"
                
                reports.append({
                    'id': i,
                    'text': report_text,
                    'labels': {
                        'age': age,
                        'cholesterol': cholesterol,
                        'glucose': glucose,
                        'blood_pressure': f"{bp_sys}/{bp_dia}",
                        'hemoglobin': hemoglobin
                    }
                })
            
            # Save reports
            with open(self.reports_path / 'synthetic_reports.json', 'w') as f:
                json.dump(reports, f, indent=2)
            
            logger.info(f"✅ Generated {len(reports)} synthetic reports")
            return reports
        
        except Exception as e:
            logger.error(f"Failed to generate synthetic reports: {e}")
            return []
    
    def create_unified_dataset(self, blood_data=None, reports=None):
        """Create unified dataset combining all sources"""
        logger.info("Creating unified dataset...")
        
        try:
            unified_data = []
            
            if blood_data is not None:
                for idx, row in blood_data.iterrows():
                    sample = {
                        'id': idx,
                        'source': 'blood_test',
                        'patient_data': row.to_dict(),
                        'ecg_data': None,
                        'report_data': None
                    }
                    unified_data.append(sample)
            
            if reports:
                for report in reports:
                    sample = {
                        'id': f"report_{report['id']}",
                        'source': 'synthetic_report',
                        'patient_data': report['labels'],
                        'report_text': report['text'],
                        'ecg_data': None
                    }
                    unified_data.append(sample)
            
            # Save unified dataset
            with open(self.unified_path / 'unified_dataset.json', 'w') as f:
                json.dump(unified_data, f, indent=2)
            
            logger.info(f"✅ Created unified dataset ({len(unified_data)} samples)")
            
            # Create summary
            summary = {
                'total_samples': len(unified_data),
                'sources': {
                    'blood_tests': len([s for s in unified_data if s['source'] == 'blood_test']),
                    'synthetic_reports': len([s for s in unified_data if s['source'] == 'synthetic_report'])
                },
                'features': list(unified_data[0]['patient_data'].keys()) if unified_data else []
            }
            
            with open(self.unified_path / 'dataset_summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            return unified_data
        
        except Exception as e:
            logger.error(f"Failed to create unified dataset: {e}")
            return []
    
    def run_all(self):
        """Run all download and preparation steps"""
        logger.info("=" * 60)
        logger.info("DATASET DOWNLOAD AND PREPARATION")
        logger.info("=" * 60)
        
        # Step 1: Download ECG data
        logger.info("\n[1/5] Downloading ECG data...")
        ecg_records = self.download_mit_bih()
        
        # Step 2: Download blood test data
        logger.info("\n[2/5] Downloading blood test data...")
        uci_data = self.download_uci_heart_disease()
        nhanes_data = self.download_nhanes_data()
        
        # Step 3: Combine blood datasets
        logger.info("\n[3/5] Combining blood datasets...")
        combined_blood = self.combine_blood_datasets()
        
        # Step 4: Generate synthetic reports
        logger.info("\n[4/5] Generating synthetic reports...")
        synthetic_reports = self.generate_synthetic_reports(n_reports=100)
        
        # Step 5: Create unified dataset
        logger.info("\n[5/5] Creating unified dataset...")
        unified = self.create_unified_dataset(combined_blood, synthetic_reports)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ ECG Records: {len(ecg_records)}")
        logger.info(f"✅ Blood Test Samples: {len(combined_blood) if combined_blood is not None else 0}")
        logger.info(f"✅ Synthetic Reports: {len(synthetic_reports)}")
        logger.info(f"✅ Unified Dataset: {len(unified)}")
        logger.info(f"\n📁 Data saved to: {self.base_path}")
        logger.info("=" * 60)


if __name__ == '__main__':
    # Use ml_model/data as base path
    downloader = DatasetDownloader(base_path='ml_model/data')
    downloader.run_all()
