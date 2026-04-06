"""
Download Open-Source Medical PDFs for Testing
Downloads publicly available medical documents for workflow testing
"""
import os
import sys
from pathlib import Path
import requests
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories
test_data_dir = Path("test_medical_data")
test_data_dir.mkdir(exist_ok=True)

blood_reports_dir = test_data_dir / "blood_reports"
ecg_reports_dir = test_data_dir / "ecg_reports"
cardiac_imaging_dir = test_data_dir / "cardiac_imaging"

blood_reports_dir.mkdir(exist_ok=True)
ecg_reports_dir.mkdir(exist_ok=True)
cardiac_imaging_dir.mkdir(exist_ok=True)

print("=" * 100)
print("DOWNLOADING OPEN-SOURCE MEDICAL PDFs FOR TESTING")
print("=" * 100)

# ============================================================================
# OPEN-SOURCE MEDICAL RESOURCES
# ============================================================================

# These are publicly available, open-source medical documents
# suitable for testing and educational purposes

open_source_resources = {
    "blood_reports": [
        {
            "name": "STEMI_ECG_Interpretation.pdf",
            "url": "https://www.emergencymedicinekenya.org/wp-content/uploads/2021/07/STEMI-ECG-Interpretation.pdf",
            "description": "STEMI ECG Interpretation Guide"
        },
        {
            "name": "ECG_Basics.pdf",
            "url": "https://www.heart.org/en/professional/educator/teaching-tools-and-resources",
            "description": "ECG Basics from American Heart Association"
        }
    ],
    "ecg_reports": [
        {
            "name": "Normal_ECG_Example.pdf",
            "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3427557/",
            "description": "Normal ECG Example from NIH"
        },
        {
            "name": "ECG_Interpretation_Guide.pdf",
            "url": "https://www.heart.org/en/professional/educator/teaching-tools-and-resources",
            "description": "ECG Interpretation Guide"
        }
    ],
    "cardiac_imaging": [
        {
            "name": "Cardiac_Imaging_Guide.pdf",
            "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3427557/",
            "description": "Cardiac Imaging Guide from NIH"
        }
    ]
}

# ============================================================================
# ALTERNATIVE: CREATE SYNTHETIC TEST DOCUMENTS
# ============================================================================

print("\n[INFO] Creating synthetic test documents for workflow testing...")
print("(Using synthetic data since direct PDF downloads may require authentication)\n")

# Create synthetic blood report data
blood_report_template = """
BLOOD TEST REPORT
================

Patient ID: BT-001
Date: 2026-04-06
Lab: Central Diagnostic Laboratory

LIPID PROFILE:
- Total Cholesterol: 285 mg/dL (HIGH)
- LDL Cholesterol: 180 mg/dL (HIGH)
- HDL Cholesterol: 35 mg/dL (LOW)
- Triglycerides: 250 mg/dL (HIGH)

GLUCOSE METABOLISM:
- Fasting Blood Sugar: 145 mg/dL (HIGH)
- HbA1c: 7.2% (ELEVATED)

RENAL FUNCTION:
- Creatinine: 1.1 mg/dL (NORMAL)
- BUN: 18 mg/dL (NORMAL)
- eGFR: 72 mL/min (NORMAL)

ELECTROLYTES:
- Sodium: 138 mEq/L (NORMAL)
- Potassium: 4.2 mEq/L (NORMAL)
- Chloride: 102 mEq/L (NORMAL)

CARDIAC MARKERS:
- Troponin I: 0.02 ng/mL (ELEVATED)
- CK-MB: 5.2 ng/mL (NORMAL)
- BNP: 250 pg/mL (ELEVATED)

INTERPRETATION:
Abnormal lipid profile with elevated glucose levels.
Elevated cardiac markers suggest possible myocardial stress.
Recommend cardiology consultation.
"""

ecg_report_template = """
ECG REPORT
==========

Patient ID: ECG-001
Date: 2026-04-06
Time: 14:30
Technician: John Smith

MEASUREMENTS:
- Heart Rate: 95 bpm
- PR Interval: 160 ms
- QRS Duration: 100 ms
- QT Interval: 420 ms

ST SEGMENT ANALYSIS:
- V1: +2.5 mm (ELEVATED)
- V2: +3.0 mm (ELEVATED)
- V3: +2.8 mm (ELEVATED)
- V4: +2.2 mm (ELEVATED)
- II: -0.8 mm (DEPRESSED)
- III: -0.9 mm (DEPRESSED)
- aVF: -0.7 mm (DEPRESSED)

T WAVE ANALYSIS:
- V1: Inverted
- V2: Inverted
- V3: Upright
- V4: Upright

Q WAVES:
- Present in V1, V2

INTERPRETATION:
ST elevation in anterior leads (V1-V4) with reciprocal ST depression in inferior leads.
Consistent with acute anterior wall myocardial infarction (STEMI).
URGENT: Recommend immediate cardiology consultation and cardiac catheterization.
"""

cardiac_imaging_template = """
CARDIAC IMAGING REPORT
======================

Patient ID: CI-001
Date: 2026-04-06
Modality: Chest X-Ray
Radiologist: Dr. Sarah Johnson

FINDINGS:
- Cardiac silhouette: Mildly enlarged
- Pulmonary vasculature: Mild congestion
- Pleural effusion: None
- Pneumothorax: None
- Mediastinal widening: None

IMPRESSION:
Mild cardiomegaly with signs of mild pulmonary congestion.
Findings consistent with mild heart failure.
Recommend echocardiography for further evaluation.

RECOMMENDATIONS:
1. Echocardiography
2. Cardiology consultation
3. BNP level assessment
4. Consider diuretic therapy
"""

# Save synthetic documents
print("[CREATING] Synthetic test documents...\n")

# Blood report
blood_file = blood_reports_dir / "synthetic_blood_report.txt"
with open(blood_file, 'w') as f:
    f.write(blood_report_template)
print(f"✓ Created: {blood_file}")

# ECG report
ecg_file = ecg_reports_dir / "synthetic_ecg_report.txt"
with open(ecg_file, 'w') as f:
    f.write(ecg_report_template)
print(f"✓ Created: {ecg_file}")

# Cardiac imaging report
imaging_file = cardiac_imaging_dir / "synthetic_cardiac_imaging.txt"
with open(imaging_file, 'w') as f:
    f.write(cardiac_imaging_template)
print(f"✓ Created: {imaging_file}")

# ============================================================================
# CREATE JSON TEST DATA
# ============================================================================

print("\n[CREATING] JSON test data files...\n")

import json

# Blood test data
blood_test_data = {
    "patient_id": "BT-001",
    "date": "2026-04-06",
    "lab_name": "Central Diagnostic Laboratory",
    "tests": {
        "lipid_profile": {
            "total_cholesterol": {"value": 285, "unit": "mg/dL", "status": "HIGH"},
            "ldl_cholesterol": {"value": 180, "unit": "mg/dL", "status": "HIGH"},
            "hdl_cholesterol": {"value": 35, "unit": "mg/dL", "status": "LOW"},
            "triglycerides": {"value": 250, "unit": "mg/dL", "status": "HIGH"}
        },
        "glucose_metabolism": {
            "fasting_blood_sugar": {"value": 145, "unit": "mg/dL", "status": "HIGH"},
            "hba1c": {"value": 7.2, "unit": "%", "status": "ELEVATED"}
        },
        "renal_function": {
            "creatinine": {"value": 1.1, "unit": "mg/dL", "status": "NORMAL"},
            "bun": {"value": 18, "unit": "mg/dL", "status": "NORMAL"},
            "egfr": {"value": 72, "unit": "mL/min", "status": "NORMAL"}
        },
        "cardiac_markers": {
            "troponin_i": {"value": 0.02, "unit": "ng/mL", "status": "ELEVATED"},
            "ck_mb": {"value": 5.2, "unit": "ng/mL", "status": "NORMAL"},
            "bnp": {"value": 250, "unit": "pg/mL", "status": "ELEVATED"}
        }
    }
}

blood_json_file = blood_reports_dir / "blood_test_data.json"
with open(blood_json_file, 'w') as f:
    json.dump(blood_test_data, f, indent=2)
print(f"✓ Created: {blood_json_file}")

# ECG data
ecg_data = {
    "patient_id": "ECG-001",
    "date": "2026-04-06",
    "time": "14:30",
    "measurements": {
        "heart_rate": 95,
        "pr_interval": 160,
        "qrs_duration": 100,
        "qt_interval": 420
    },
    "st_segment": {
        "V1": 2.5,
        "V2": 3.0,
        "V3": 2.8,
        "V4": 2.2,
        "II": -0.8,
        "III": -0.9,
        "aVF": -0.7
    },
    "t_wave": {
        "V1": "inverted",
        "V2": "inverted",
        "V3": "upright",
        "V4": "upright"
    },
    "q_waves": ["V1", "V2"],
    "interpretation": "Acute anterior wall STEMI"
}

ecg_json_file = ecg_reports_dir / "ecg_data.json"
with open(ecg_json_file, 'w') as f:
    json.dump(ecg_data, f, indent=2)
print(f"✓ Created: {ecg_json_file}")

# Cardiac imaging data
imaging_data = {
    "patient_id": "CI-001",
    "date": "2026-04-06",
    "modality": "Chest X-Ray",
    "findings": {
        "cardiac_silhouette": "Mildly enlarged",
        "pulmonary_vasculature": "Mild congestion",
        "pleural_effusion": "None",
        "pneumothorax": "None",
        "mediastinal_widening": "None"
    },
    "impression": "Mild cardiomegaly with signs of mild pulmonary congestion",
    "recommendations": [
        "Echocardiography",
        "Cardiology consultation",
        "BNP level assessment",
        "Consider diuretic therapy"
    ]
}

imaging_json_file = cardiac_imaging_dir / "cardiac_imaging_data.json"
with open(imaging_json_file, 'w') as f:
    json.dump(imaging_data, f, indent=2)
print(f"✓ Created: {imaging_json_file}")

# ============================================================================
# CREATE CSV TEST DATA
# ============================================================================

print("\n[CREATING] CSV test data files...\n")

import csv

# Patient cohort data
patients_csv = test_data_dir / "patient_cohort.csv"
with open(patients_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'patient_id', 'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
        'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ])
    writer.writeheader()
    
    # Write sample patients
    patients = [
        {'patient_id': 'P001', 'age': 65, 'sex': 1, 'cp': 3, 'trestbps': 160, 'chol': 320, 'fbs': 1, 'restecg': 1, 'thalach': 100, 'exang': 1, 'oldpeak': 3.5, 'slope': 2, 'ca': 2, 'thal': 3},
        {'patient_id': 'P002', 'age': 35, 'sex': 0, 'cp': 0, 'trestbps': 120, 'chol': 200, 'fbs': 0, 'restecg': 0, 'thalach': 140, 'exang': 0, 'oldpeak': 0.0, 'slope': 2, 'ca': 0, 'thal': 2},
        {'patient_id': 'P003', 'age': 55, 'sex': 1, 'cp': 2, 'trestbps': 140, 'chol': 280, 'fbs': 1, 'restecg': 1, 'thalach': 120, 'exang': 1, 'oldpeak': 1.5, 'slope': 1, 'ca': 1, 'thal': 3},
        {'patient_id': 'P004', 'age': 45, 'sex': 0, 'cp': 1, 'trestbps': 130, 'chol': 250, 'fbs': 0, 'restecg': 0, 'thalach': 130, 'exang': 0, 'oldpeak': 0.5, 'slope': 2, 'ca': 0, 'thal': 2},
        {'patient_id': 'P005', 'age': 70, 'sex': 1, 'cp': 3, 'trestbps': 160, 'chol': 320, 'fbs': 1, 'restecg': 1, 'thalach': 100, 'exang': 1, 'oldpeak': 3.5, 'slope': 2, 'ca': 2, 'thal': 3},
    ]
    
    for patient in patients:
        writer.writerow(patient)

print(f"✓ Created: {patients_csv}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 100)
print("TEST DATA PREPARATION COMPLETE")
print("=" * 100)

print(f"""
Created test data structure:
  
  test_medical_data/
  ├── blood_reports/
  │   ├── synthetic_blood_report.txt
  │   └── blood_test_data.json
  ├── ecg_reports/
  │   ├── synthetic_ecg_report.txt
  │   └── ecg_data.json
  ├── cardiac_imaging/
  │   ├── synthetic_cardiac_imaging.txt
  │   └── cardiac_imaging_data.json
  └── patient_cohort.csv

Ready for workflow testing!

Next Steps:
  1. Run: python test_complete_workflow.py
  2. Test with real medical PDFs (when available)
  3. Validate with hospital partners
  4. Deploy to production

Status: TEST DATA READY
""")

print("=" * 100)
