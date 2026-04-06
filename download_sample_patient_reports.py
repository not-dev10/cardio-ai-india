"""
Download Sample Patient Reports from Open Datasets
Uses de-identified/synthetic patient data for testing
"""
import sys
import os
from pathlib import Path
import requests

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 100)
print("DOWNLOADING SAMPLE PATIENT REPORTS")
print("De-identified/Synthetic Data for Testing")
print("=" * 100)

# Create directory
samples_dir = Path("sample_patient_reports")
samples_dir.mkdir(exist_ok=True)

# Open-source sample patient reports
# These are de-identified or synthetic data from research/educational sources
sample_reports = [
    {
        "name": "MIMIC_Sample_ECG.pdf",
        "url": "https://physionet.org/files/mimic-iv-ecg/1.0/files/p100/p10000032/s42341066.pdf",
        "type": "ECG Report",
        "source": "MIMIC-IV (PhysioNet)"
    },
    {
        "name": "PTB_XL_Sample.pdf", 
        "url": "https://physionet.org/static/published-projects/ptb-xl/ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip",
        "type": "ECG Dataset",
        "source": "PTB-XL Database"
    }
]

print("\nNote: Real patient data requires:")
print("  1. PhysioNet account (free registration)")
print("  2. CITI training completion")
print("  3. Data use agreement")
print("\nFor testing without registration, use synthetic data below...")

# Alternative: Generate realistic synthetic reports
print("\n[GENERATING] Synthetic Patient Reports for Testing...")
print("-" * 100)

# Synthetic Blood Report
blood_report = """
PATIENT BLOOD TEST REPORT
========================

Patient ID: SYNTH-001
Date: 2026-04-06
Lab: Test Laboratory

LIPID PROFILE:
--------------
Total Cholesterol: 285 mg/dL (HIGH)
LDL Cholesterol: 180 mg/dL (HIGH)
HDL Cholesterol: 35 mg/dL (LOW)
Triglycerides: 250 mg/dL (HIGH)
VLDL: 50 mg/dL

GLUCOSE METABOLISM:
------------------
Fasting Blood Sugar: 145 mg/dL (HIGH)
HbA1c: 7.2% (ELEVATED)
Random Blood Sugar: 180 mg/dL

RENAL FUNCTION:
--------------
Creatinine: 1.1 mg/dL (NORMAL)
BUN: 18 mg/dL (NORMAL)
eGFR: 72 mL/min (NORMAL)
Uric Acid: 6.5 mg/dL

CARDIAC MARKERS:
---------------
Troponin I: 0.02 ng/mL (ELEVATED)
CK-MB: 5.2 ng/mL (NORMAL)
BNP: 250 pg/mL (ELEVATED)
LDH: 180 U/L

COMPLETE BLOOD COUNT:
--------------------
Hemoglobin: 13.5 g/dL
WBC: 8,500 /μL
Platelets: 250,000 /μL
RBC: 4.5 million/μL

INTERPRETATION:
--------------
Abnormal lipid profile with elevated glucose levels.
Elevated cardiac markers suggest possible myocardial stress.
Recommend cardiology consultation.

Physician: Dr. Sample
License: TEST-12345
"""

# Synthetic ECG Report
ecg_report = """
ELECTROCARDIOGRAM REPORT
========================

Patient ID: SYNTH-001
Date: 2026-04-06
Time: 14:30
Technician: Test Tech

MEASUREMENTS:
------------
Heart Rate: 95 bpm (ELEVATED)
PR Interval: 160 ms (NORMAL)
QRS Duration: 100 ms (NORMAL)
QT Interval: 420 ms (NORMAL)
QTc: 445 ms (BORDERLINE)

RHYTHM ANALYSIS:
---------------
Rhythm: Sinus Rhythm
Axis: Normal Axis
Rate: 95 bpm

ST SEGMENT ANALYSIS:
-------------------
Lead V1: ST elevation +2.5 mm (ABNORMAL)
Lead V2: ST elevation +3.0 mm (ABNORMAL)
Lead V3: ST elevation +2.8 mm (ABNORMAL)
Lead V4: ST elevation +2.2 mm (ABNORMAL)
Lead I: ST elevation +1.5 mm (ABNORMAL)
Lead aVL: ST elevation +1.2 mm (ABNORMAL)

Lead II: ST depression -0.8 mm (RECIPROCAL)
Lead III: ST depression -0.9 mm (RECIPROCAL)
Lead aVF: ST depression -0.7 mm (RECIPROCAL)

T WAVE ANALYSIS:
---------------
Lead V1: T wave inversion
Lead V2: T wave inversion
Other leads: Normal

Q WAVES:
--------
Present in V1, V2 (PATHOLOGICAL)

INTERPRETATION:
--------------
ACUTE ANTERIOR WALL STEMI

ST elevation in anterior leads (V1-V4) with reciprocal
ST depression in inferior leads (II, III, aVF).
Findings consistent with acute myocardial infarction
involving LAD (Left Anterior Descending) territory.

*** URGENT: ACTIVATE STEMI PROTOCOL ***
*** IMMEDIATE CARDIOLOGY CONSULTATION REQUIRED ***
*** CONSIDER PRIMARY PCI OR THROMBOLYTIC THERAPY ***

Interpreted by: Dr. Sample Cardiologist
License: CARD-12345
"""

# Synthetic Cardiac Imaging Report
imaging_report = """
CARDIAC IMAGING REPORT
======================

Patient ID: SYNTH-001
Date: 2026-04-06
Modality: Chest X-Ray PA View
Radiologist: Dr. Sample

TECHNICAL QUALITY:
-----------------
Adequate inspiration
Good penetration
No rotation

CARDIAC SILHOUETTE:
------------------
Size: Mildly enlarged (Cardiothoracic ratio: 0.55)
Shape: Normal contour
Borders: Well-defined

PULMONARY VASCULATURE:
---------------------
Mild pulmonary vascular congestion
Cephalization present
No pleural effusion

LUNG FIELDS:
-----------
Clear bilaterally
No infiltrates
No pneumothorax
No masses

MEDIASTINUM:
-----------
Normal width
Aortic knob: Normal
No widening

BONES:
------
No acute fractures
Degenerative changes in thoracic spine

IMPRESSION:
----------
1. Mild cardiomegaly (CTR 0.55)
2. Mild pulmonary vascular congestion
3. Findings consistent with mild heart failure

RECOMMENDATIONS:
---------------
1. Echocardiography for cardiac function assessment
2. BNP level measurement
3. Cardiology consultation
4. Consider diuretic therapy

Reported by: Dr. Sample Radiologist
License: RAD-12345
Date: 2026-04-06 15:00
"""

# Save synthetic reports
reports = [
    ("blood_test_report.txt", blood_report),
    ("ecg_report.txt", ecg_report),
    ("cardiac_imaging_report.txt", imaging_report)
]

for filename, content in reports:
    filepath = samples_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filename}")

print(f"\n✓ Generated 3 synthetic patient reports")
print(f"  Location: {samples_dir}/")

print("\n" + "=" * 100)
print("SAMPLE REPORTS READY")
print("=" * 100)

print(f"""
Generated Synthetic Reports:
  1. blood_test_report.txt - Complete blood panel with cardiac markers
  2. ecg_report.txt - ECG with STEMI findings
  3. cardiac_imaging_report.txt - Chest X-ray with cardiomegaly

These are SYNTHETIC reports for testing only.
They contain realistic medical values but are not real patient data.

To test with these reports:
  python test_all_medical_pdfs.py

For REAL patient data, you need:
  1. Your own medical reports
  2. Hospital partnership with IRB approval
  3. PhysioNet credentialed access (requires CITI training)

Open-Source Medical Datasets (Require Registration):
  - MIMIC-IV: https://physionet.org/content/mimic-iv/
  - PTB-XL ECG: https://physionet.org/content/ptb-xl/
  - UK Biobank: https://www.ukbiobank.ac.uk/
  
All require:
  - Free registration
  - Research ethics training (CITI)
  - Data use agreement
  - Institutional affiliation (for some)
""")

print("=" * 100)
