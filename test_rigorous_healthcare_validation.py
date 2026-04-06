"""
RIGOROUS HEALTHCARE VALIDATION TEST SUITE
Medical-Grade Testing for Cardiac Health AI System
Comprehensive validation for patient safety and clinical accuracy
"""
import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

# Fix encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Setup comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('healthcare_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "ml_model"))

print("=" * 120)
print("RIGOROUS HEALTHCARE VALIDATION TEST SUITE")
print("Medical-Grade Testing for Cardiac Health AI System")
print("=" * 120)

# ============================================================================
# FEATURE ENGINEERING FUNCTION
# ============================================================================

def engineer_features(data):
    """Convert 13 features to 18 by adding engineered features"""
    engineered = {}
    
    # Remove non-numeric fields
    for key, value in data.items():
        if key not in ["id", "expected_risk", "expected_stemi", "expected_artery", "clinical_notes", "description", "acceptable_risk_range", "should_fail", "min_confidence", "name"]:
            engineered[key] = value
    
    # Map old feature names to new ones if needed
    if "cp" in engineered:
        engineered["chest_pain_type"] = engineered.pop("cp")
    if "trestbps" in engineered:
        engineered["resting_bp"] = engineered.pop("trestbps")
    if "chol" in engineered:
        engineered["cholesterol"] = engineered.pop("chol")
    if "fbs" in engineered:
        engineered["fasting_blood_sugar"] = engineered.pop("fbs")
    if "restecg" in engineered:
        engineered["resting_ecg"] = engineered.pop("restecg")
    if "thalach" in engineered:
        engineered["max_heart_rate"] = engineered.pop("thalach")
    if "exang" in engineered:
        engineered["exercise_induced_angina"] = engineered.pop("exang")
    if "oldpeak" in engineered:
        engineered["st_depression"] = engineered.pop("oldpeak")
    if "slope" in engineered:
        engineered["st_slope"] = engineered.pop("slope")
    if "ca" in engineered:
        engineered["num_major_vessels"] = engineered.pop("ca")
    if "thal" in engineered:
        engineered["thalassemia"] = engineered.pop("thal")
    
    # Add 5 engineered features
    engineered["bp_chol_product"] = engineered["resting_bp"] * engineered["cholesterol"]
    engineered["hr_bp_ratio"] = engineered["max_heart_rate"] / max(engineered["resting_bp"], 1)
    engineered["st_hr_product"] = engineered["st_depression"] * engineered["max_heart_rate"]
    engineered["st_depression_sqrt"] = np.sqrt(max(engineered["st_depression"], 0))
    engineered["chol_bs_ratio"] = engineered["cholesterol"] / max(engineered["fasting_blood_sugar"], 1)
    
    return engineered

# ============================================================================
# IMPORT ALL MODULES
# ============================================================================

print("\n[PHASE 1] Module Import & Initialization")
print("-" * 120)

try:
    from backend.services.ecg_stemi_analyzer import ECGSTEMIAnalyzer
    from ml_model.predict import HeartDiseasePredictor
    from backend.monitoring.clinical_monitor import ClinicalMonitor
    print("✓ All modules imported successfully")
    logger.info("All modules imported successfully")
except Exception as e:
    print(f"✗ CRITICAL: Module import failed: {e}")
    logger.critical(f"Module import failed: {e}")
    sys.exit(1)

# Initialize components
try:
    predictor = HeartDiseasePredictor()
    analyzer = ECGSTEMIAnalyzer()
    monitor = ClinicalMonitor()
    print("✓ All components initialized")
    logger.info("All components initialized")
except Exception as e:
    print(f"✗ CRITICAL: Component initialization failed: {e}")
    logger.critical(f"Component initialization failed: {e}")
    sys.exit(1)

# ============================================================================
# TEST SUITE 1: MODEL ACCURACY VALIDATION
# ============================================================================

print("\n[PHASE 2] Model Accuracy Validation")
print("-" * 120)

test_results = {
    "timestamp": datetime.now().isoformat(),
    "test_suites": {},
    "overall_status": "PENDING"
}

# Test Case 1.1: Known High-Risk Patients
print("\n[TEST 1.1] High-Risk Patient Detection")
high_risk_patients = [
    {
        "id": "HR-001",
        "age": 75, "sex": 1, "cp": 3, "trestbps": 180, "chol": 350,
        "fbs": 1, "restecg": 1, "thalach": 85, "exang": 1, "oldpeak": 4.5,
        "slope": 1, "ca": 3, "thal": 3,
        "expected_risk": "HIGH",
        "clinical_notes": "Elderly male with multiple risk factors"
    },
    {
        "id": "HR-002",
        "age": 68, "sex": 1, "cp": 3, "trestbps": 170, "chol": 320,
        "fbs": 1, "restecg": 1, "thalach": 95, "exang": 1, "oldpeak": 3.8,
        "slope": 2, "ca": 2, "thal": 3,
        "expected_risk": "HIGH",
        "clinical_notes": "Male with severe angina and ST depression"
    },
    {
        "id": "HR-003",
        "age": 62, "sex": 0, "cp": 3, "trestbps": 160, "chol": 300,
        "fbs": 1, "restecg": 1, "thalach": 100, "exang": 1, "oldpeak": 3.2,
        "slope": 1, "ca": 2, "thal": 3,
        "expected_risk": "HIGH",
        "clinical_notes": "Female with typical angina and abnormal ECG"
    }
]

high_risk_correct = 0
high_risk_total = len(high_risk_patients)

for patient in high_risk_patients:
    try:
        engineered = engineer_features(patient)
        pred = predictor.predict(engineered)
        is_correct = pred['risk_level'].upper() == patient['expected_risk'].upper()
        high_risk_correct += is_correct
        
        status = "✓ PASS" if is_correct else "✗ FAIL"
        risk_pct = pred.get('probability', 0) * 100
        print(f"  {status} | {patient['id']}: Risk {risk_pct:.1f}% ({pred['risk_level']})")
        logger.info(f"High-risk test {patient['id']}: {pred['risk_level']} (expected {patient['expected_risk']})")
        
    except Exception as e:
        print(f"  ✗ ERROR | {patient['id']}: {str(e)[:60]}")
        logger.error(f"High-risk test {patient['id']} failed: {e}")

print(f"\n  High-Risk Detection Rate: {high_risk_correct}/{high_risk_total} ({100*high_risk_correct/high_risk_total:.1f}%)")

# Test Case 1.2: Known Low-Risk Patients
print("\n[TEST 1.2] Low-Risk Patient Detection")
low_risk_patients = [
    {
        "id": "LR-001",
        "age": 30, "sex": 0, "cp": 0, "trestbps": 110, "chol": 180,
        "fbs": 0, "restecg": 0, "thalach": 160, "exang": 0, "oldpeak": 0.0,
        "slope": 2, "ca": 0, "thal": 2,
        "expected_risk": "LOW",
        "clinical_notes": "Young female with no risk factors"
    },
    {
        "id": "LR-002",
        "age": 35, "sex": 1, "cp": 0, "trestbps": 120, "chol": 190,
        "fbs": 0, "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 0.0,
        "slope": 2, "ca": 0, "thal": 2,
        "expected_risk": "LOW",
        "clinical_notes": "Young male with normal vitals"
    },
    {
        "id": "LR-003",
        "age": 40, "sex": 0, "cp": 0, "trestbps": 115, "chol": 200,
        "fbs": 0, "restecg": 0, "thalach": 145, "exang": 0, "oldpeak": 0.0,
        "slope": 2, "ca": 0, "thal": 2,
        "expected_risk": "LOW",
        "clinical_notes": "Middle-aged female with normal findings"
    }
]

low_risk_correct = 0
low_risk_total = len(low_risk_patients)

for patient in low_risk_patients:
    try:
        engineered = engineer_features(patient)
        pred = predictor.predict(engineered)
        is_correct = pred['risk_level'].upper() == patient['expected_risk'].upper()
        low_risk_correct += is_correct
        
        status = "✓ PASS" if is_correct else "✗ FAIL"
        risk_pct = pred.get('probability', 0) * 100
        print(f"  {status} | {patient['id']}: Risk {risk_pct:.1f}% ({pred['risk_level']})")
        logger.info(f"Low-risk test {patient['id']}: {pred['risk_level']} (expected {patient['expected_risk']})")
        
    except Exception as e:
        print(f"  ✗ ERROR | {patient['id']}: {str(e)[:60]}")
        logger.error(f"Low-risk test {patient['id']} failed: {e}")

print(f"\n  Low-Risk Detection Rate: {low_risk_correct}/{low_risk_total} ({100*low_risk_correct/low_risk_total:.1f}%)")

test_results["test_suites"]["accuracy"] = {
    "high_risk_detection": f"{high_risk_correct}/{high_risk_total}",
    "low_risk_detection": f"{low_risk_correct}/{low_risk_total}",
    "overall_accuracy": f"{(high_risk_correct + low_risk_correct)/(high_risk_total + low_risk_total):.1%}"
}

# ============================================================================
# TEST SUITE 2: STEMI DETECTION VALIDATION
# ============================================================================

print("\n[PHASE 3] STEMI Detection Validation")
print("-" * 120)

# Test Case 2.1: STEMI Detection
print("\n[TEST 2.1] STEMI Detection Accuracy")

stemi_cases = [
    {
        "id": "STEMI-001",
        "name": "Anterior STEMI",
        "ecg": {
            "heart_rate": 95,
            "pr_interval": 160,
            "qrs_duration": 100,
            "qt_interval": 420,
            "st_elevation": {"V1": 2.5, "V2": 3.0, "V3": 2.8, "V4": 2.2, "I": 1.5, "aVL": 1.2},
            "st_depression": {"II": 0.8, "III": 0.9, "aVF": 0.7},
            "t_wave_inversion": {"V1": 0.6, "V2": 0.7},
            "q_waves": ["V1", "V2"]
        },
        "expected_stemi": True,
        "expected_artery": "LAD"
    },
    {
        "id": "STEMI-002",
        "name": "Inferior STEMI",
        "ecg": {
            "heart_rate": 88,
            "pr_interval": 170,
            "qrs_duration": 95,
            "qt_interval": 430,
            "st_elevation": {"II": 2.0, "III": 2.5, "aVF": 2.2, "V5": 0.5, "V6": 0.3},
            "st_depression": {"V1": 0.7, "V2": 0.8, "V3": 0.6},
            "t_wave_inversion": {"II": 0.5, "III": 0.6, "aVF": 0.5},
            "q_waves": ["II", "III", "aVF"]
        },
        "expected_stemi": True,
        "expected_artery": "RCA"
    },
    {
        "id": "STEMI-003",
        "name": "Normal ECG",
        "ecg": {
            "heart_rate": 72,
            "pr_interval": 160,
            "qrs_duration": 90,
            "qt_interval": 400,
            "st_elevation": {},
            "st_depression": {},
            "t_wave_inversion": {},
            "q_waves": []
        },
        "expected_stemi": False,
        "expected_artery": "None"
    }
]

stemi_correct = 0
artery_correct = 0

for case in stemi_cases:
    try:
        findings = analyzer.analyze_ecg(case["ecg"])
        
        stemi_match = findings.is_stemi == case["expected_stemi"]
        stemi_correct += stemi_match
        
        artery_match = (case["expected_artery"] in findings.affected_artery) if case["expected_stemi"] else True
        artery_correct += artery_match
        
        stemi_status = "✓ PASS" if stemi_match else "✗ FAIL"
        artery_status = "✓ PASS" if artery_match else "✗ FAIL"
        
        print(f"  {stemi_status} | {case['id']}: STEMI={findings.is_stemi} (expected {case['expected_stemi']})")
        print(f"  {artery_status} | {case['id']}: Artery={findings.affected_artery} (expected {case['expected_artery']})")
        logger.info(f"STEMI test {case['id']}: STEMI={findings.is_stemi}, Artery={findings.affected_artery}")
        
    except Exception as e:
        print(f"  ✗ ERROR | {case['id']}: {str(e)[:60]}")
        logger.error(f"STEMI test {case['id']} failed: {e}")

print(f"\n  STEMI Detection Rate: {stemi_correct}/{len(stemi_cases)} ({100*stemi_correct/len(stemi_cases):.1f}%)")
print(f"  Artery Identification Rate: {artery_correct}/{len(stemi_cases)} ({100*artery_correct/len(stemi_cases):.1f}%)")

test_results["test_suites"]["stemi"] = {
    "stemi_detection": f"{stemi_correct}/{len(stemi_cases)}",
    "artery_identification": f"{artery_correct}/{len(stemi_cases)}"
}


# ============================================================================
# TEST SUITE 3: SAFETY & CONFIDENCE VALIDATION
# ============================================================================

print("\n[PHASE 4] Safety & Confidence Validation")
print("-" * 120)

# Test Case 3.1: Confidence Thresholds
print("\n[TEST 3.1] Confidence Threshold Validation")

confidence_tests = [
    {
        "id": "CONF-001",
        "description": "High confidence prediction",
        "patient": {"age": 75, "sex": 1, "cp": 3, "trestbps": 180, "chol": 350, "fbs": 1, "restecg": 1, "thalach": 85, "exang": 1, "oldpeak": 4.5, "slope": 1, "ca": 3, "thal": 3},
        "min_confidence": 0.70
    },
    {
        "id": "CONF-002",
        "description": "Low-risk patient",
        "patient": {"age": 30, "sex": 0, "cp": 0, "trestbps": 110, "chol": 180, "fbs": 0, "restecg": 0, "thalach": 160, "exang": 0, "oldpeak": 0.0, "slope": 2, "ca": 0, "thal": 2},
        "min_confidence": 0.70
    }
]

confidence_pass = 0
for test in confidence_tests:
    try:
        engineered = engineer_features(test["patient"])
        pred = predictor.predict(engineered)
        conf = pred.get('confidence', 0)
        
        if isinstance(conf, str):
            conf = float(conf.strip('%')) / 100
        
        is_pass = conf >= test["min_confidence"]
        confidence_pass += is_pass
        
        status = "✓ PASS" if is_pass else "✗ FAIL"
        print(f"  {status} | {test['id']}: Confidence {conf:.1%} (min {test['min_confidence']:.1%})")
        logger.info(f"Confidence test {test['id']}: {conf:.1%}")
        
    except Exception as e:
        print(f"  ✗ ERROR | {test['id']}: {str(e)[:60]}")
        logger.error(f"Confidence test {test['id']} failed: {e}")

print(f"\n  Confidence Threshold Pass Rate: {confidence_pass}/{len(confidence_tests)} ({100*confidence_pass/len(confidence_tests):.1f}%)")

# Test Case 3.2: False Positive/Negative Analysis
print("\n[TEST 3.2] False Positive/Negative Analysis")

# Borderline cases that could be misclassified
borderline_cases = [
    {
        "id": "BORDER-001",
        "description": "Borderline high-risk",
        "patient": {"age": 50, "sex": 1, "cp": 2, "trestbps": 140, "chol": 280, "fbs": 1, "restecg": 1, "thalach": 120, "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3},
        "acceptable_risk_range": (0.40, 0.80)
    },
    {
        "id": "BORDER-002",
        "description": "Borderline low-risk",
        "patient": {"age": 45, "sex": 0, "cp": 1, "trestbps": 130, "chol": 250, "fbs": 0, "restecg": 0, "thalach": 130, "exang": 0, "oldpeak": 0.5, "slope": 2, "ca": 0, "thal": 2},
        "acceptable_risk_range": (0.10, 0.50)
    }
]

borderline_pass = 0
for case in borderline_cases:
    try:
        engineered = engineer_features(case["patient"])
        pred = predictor.predict(engineered)
        risk = pred.get('probability', 0)
        
        in_range = case["acceptable_risk_range"][0] <= risk <= case["acceptable_risk_range"][1]
        borderline_pass += in_range
        
        status = "✓ PASS" if in_range else "✗ FAIL"
        print(f"  {status} | {case['id']}: Risk {risk:.1%} (acceptable {case['acceptable_risk_range'][0]:.1%}-{case['acceptable_risk_range'][1]:.1%})")
        logger.info(f"Borderline test {case['id']}: {risk:.1%}")
        
    except Exception as e:
        print(f"  ✗ ERROR | {case['id']}: {str(e)[:60]}")
        logger.error(f"Borderline test {case['id']} failed: {e}")

print(f"\n  Borderline Case Handling: {borderline_pass}/{len(borderline_cases)} ({100*borderline_pass/len(borderline_cases):.1f}%)")

test_results["test_suites"]["safety"] = {
    "confidence_validation": f"{confidence_pass}/{len(confidence_tests)}",
    "borderline_handling": f"{borderline_pass}/{len(borderline_cases)}"
}

# ============================================================================
# TEST SUITE 4: DATA INTEGRITY & VALIDATION
# ============================================================================

print("\n[PHASE 5] Data Integrity & Validation")
print("-" * 120)

# Test Case 4.1: Input Validation
print("\n[TEST 4.1] Input Data Validation")

invalid_inputs = [
    {
        "id": "INVALID-001",
        "description": "Age out of range (negative)",
        "patient": {"age": -5, "sex": 1, "cp": 1, "trestbps": 120, "chol": 200, "fbs": 0, "restecg": 0, "thalach": 130, "exang": 0, "oldpeak": 0.5, "slope": 2, "ca": 0, "thal": 2},
        "should_fail": True
    },
    {
        "id": "INVALID-002",
        "description": "Age out of range (>150)",
        "patient": {"age": 200, "sex": 1, "cp": 1, "trestbps": 120, "chol": 200, "fbs": 0, "restecg": 0, "thalach": 130, "exang": 0, "oldpeak": 0.5, "slope": 2, "ca": 0, "thal": 2},
        "should_fail": True
    },
    {
        "id": "INVALID-003",
        "description": "Invalid sex value",
        "patient": {"age": 50, "sex": 5, "cp": 1, "trestbps": 120, "chol": 200, "fbs": 0, "restecg": 0, "thalach": 130, "exang": 0, "oldpeak": 0.5, "slope": 2, "ca": 0, "thal": 2},
        "should_fail": True
    }
]

validation_pass = 0
for test in invalid_inputs:
    try:
        engineered = engineer_features(test["patient"])
        pred = predictor.predict(engineered)
        # If we get here without error, check if it should have failed
        if test["should_fail"]:
            print(f"  ✗ FAIL | {test['id']}: Should have rejected invalid input")
            logger.warning(f"Validation test {test['id']}: Did not reject invalid input")
        else:
            validation_pass += 1
            print(f"  ✓ PASS | {test['id']}: Accepted valid input")
            
    except Exception as e:
        if test["should_fail"]:
            validation_pass += 1
            print(f"  ✓ PASS | {test['id']}: Correctly rejected invalid input")
            logger.info(f"Validation test {test['id']}: Correctly rejected")
        else:
            print(f"  ✗ FAIL | {test['id']}: Should have accepted valid input")
            logger.warning(f"Validation test {test['id']}: Incorrectly rejected")

print(f"\n  Input Validation Pass Rate: {validation_pass}/{len(invalid_inputs)} ({100*validation_pass/len(invalid_inputs):.1f}%)")

# Test Case 4.2: Output Consistency
print("\n[TEST 4.2] Output Consistency Validation")

consistency_patient = {"age": 55, "sex": 1, "cp": 2, "trestbps": 140, "chol": 280, "fbs": 1, "restecg": 1, "thalach": 120, "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3}

predictions = []
for i in range(3):
    try:
        engineered = engineer_features(consistency_patient)
        pred = predictor.predict(engineered)
        predictions.append(pred.get('probability', 0))
    except Exception as e:
        logger.error(f"Consistency test iteration {i} failed: {e}")

is_consistent = False
if len(predictions) == 3:
    # Check if predictions are consistent (within 1% tolerance)
    max_diff = (max(predictions) - min(predictions)) * 100
    is_consistent = max_diff <= 1.0
    
    status = "✓ PASS" if is_consistent else "✗ FAIL"
    print(f"  {status} | Predictions: {predictions[0]*100:.2f}%, {predictions[1]*100:.2f}%, {predictions[2]*100:.2f}%")
    print(f"  Max difference: {max_diff:.2f}%")
    logger.info(f"Consistency test: Max diff {max_diff:.2f}%")
else:
    print(f"  ✗ ERROR | Could not complete consistency test")
    logger.error("Consistency test failed to complete")

test_results["test_suites"]["data_integrity"] = {
    "input_validation": f"{validation_pass}/{len(invalid_inputs)}",
    "output_consistency": "PASS" if is_consistent else "FAIL"
}

# ============================================================================
# TEST SUITE 5: PERFORMANCE & LATENCY
# ============================================================================

print("\n[PHASE 6] Performance & Latency Validation")
print("-" * 120)

import time

# Test Case 5.1: Prediction Latency
print("\n[TEST 5.1] Prediction Latency")

test_patient = {"age": 55, "sex": 1, "cp": 2, "trestbps": 140, "chol": 280, "fbs": 1, "restecg": 1, "thalach": 120, "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3}

latencies = []
for i in range(5):
    try:
        engineered = engineer_features(test_patient)
        start = time.time()
        pred = predictor.predict(engineered)
        latency = (time.time() - start) * 1000  # Convert to ms
        latencies.append(latency)
    except Exception as e:
        logger.error(f"Latency test iteration {i} failed: {e}")

if latencies:
    avg_latency = np.mean(latencies)
    max_latency = np.max(latencies)
    min_latency = np.min(latencies)
    
    # Medical-grade requirement: <500ms
    latency_pass = avg_latency < 500
    status = "✓ PASS" if latency_pass else "✗ FAIL"
    
    print(f"  {status} | Average: {avg_latency:.2f}ms, Min: {min_latency:.2f}ms, Max: {max_latency:.2f}ms")
    print(f"  Requirement: <500ms (Medical-grade)")
    logger.info(f"Latency test: Avg {avg_latency:.2f}ms")
else:
    print(f"  ✗ ERROR | Could not measure latency")
    logger.error("Latency test failed")

# Test Case 5.2: STEMI Analysis Latency
print("\n[TEST 5.2] STEMI Analysis Latency")

test_ecg = {
    "heart_rate": 95,
    "pr_interval": 160,
    "qrs_duration": 100,
    "qt_interval": 420,
    "st_elevation": {"V1": 2.5, "V2": 3.0, "V3": 2.8, "V4": 2.2},
    "st_depression": {"II": 0.8, "III": 0.9},
    "t_wave_inversion": {"V1": 0.6, "V2": 0.7},
    "q_waves": ["V1", "V2"]
}

stemi_latencies = []
for i in range(5):
    try:
        start = time.time()
        findings = analyzer.analyze_ecg(test_ecg)
        latency = (time.time() - start) * 1000
        stemi_latencies.append(latency)
    except Exception as e:
        logger.error(f"STEMI latency test iteration {i} failed: {e}")

if stemi_latencies:
    avg_stemi_latency = np.mean(stemi_latencies)
    stemi_latency_pass = avg_stemi_latency < 100
    status = "✓ PASS" if stemi_latency_pass else "✗ FAIL"
    
    print(f"  {status} | Average: {avg_stemi_latency:.2f}ms")
    print(f"  Requirement: <100ms (Real-time)")
    logger.info(f"STEMI latency test: Avg {avg_stemi_latency:.2f}ms")
else:
    print(f"  ✗ ERROR | Could not measure STEMI latency")
    logger.error("STEMI latency test failed")

test_results["test_suites"]["performance"] = {
    "prediction_latency": f"{avg_latency:.2f}ms" if latencies else "ERROR",
    "stemi_latency": f"{avg_stemi_latency:.2f}ms" if stemi_latencies else "ERROR"
}

# ============================================================================
# TEST SUITE 6: CLINICAL DECISION SUPPORT
# ============================================================================

print("\n[PHASE 7] Clinical Decision Support Validation")
print("-" * 120)

# Test Case 6.1: Risk Stratification
print("\n[TEST 6.1] Risk Stratification Accuracy")

stratification_cases = [
    {"patient": {"age": 75, "sex": 1, "cp": 3, "trestbps": 180, "chol": 350, "fbs": 1, "restecg": 1, "thalach": 85, "exang": 1, "oldpeak": 4.5, "slope": 1, "ca": 3, "thal": 3}, "expected": "HIGH"},
    {"patient": {"age": 50, "sex": 1, "cp": 2, "trestbps": 140, "chol": 280, "fbs": 1, "restecg": 1, "thalach": 120, "exang": 1, "oldpeak": 1.5, "slope": 1, "ca": 1, "thal": 3}, "expected": "MEDIUM"},
    {"patient": {"age": 30, "sex": 0, "cp": 0, "trestbps": 110, "chol": 180, "fbs": 0, "restecg": 0, "thalach": 160, "exang": 0, "oldpeak": 0.0, "slope": 2, "ca": 0, "thal": 2}, "expected": "LOW"},
]

stratification_correct = 0
for case in stratification_cases:
    try:
        engineered = engineer_features(case["patient"])
        pred = predictor.predict(engineered)
        is_correct = pred['risk_level'].upper() == case["expected"].upper()
        stratification_correct += is_correct
        
        status = "✓ PASS" if is_correct else "✗ FAIL"
        print(f"  {status} | {pred['risk_level']} (expected {case['expected']})")
        logger.info(f"Stratification test: {pred['risk_level']}")
        
    except Exception as e:
        print(f"  ✗ ERROR | {str(e)[:60]}")
        logger.error(f"Stratification test failed: {e}")

print(f"\n  Risk Stratification Accuracy: {stratification_correct}/{len(stratification_cases)} ({100*stratification_correct/len(stratification_cases):.1f}%)")

test_results["test_suites"]["clinical_support"] = {
    "risk_stratification": f"{stratification_correct}/{len(stratification_cases)}"
}

# ============================================================================
# FINAL REPORT
# ============================================================================

print("\n" + "=" * 120)
print("HEALTHCARE VALIDATION TEST REPORT")
print("=" * 120)

# Calculate overall metrics
total_tests = (high_risk_total + low_risk_total + len(stemi_cases) + 
               len(confidence_tests) + len(borderline_cases) + len(invalid_inputs) + 
               len(stratification_cases))

total_passed = (high_risk_correct + low_risk_correct + stemi_correct + 
                confidence_pass + borderline_pass + validation_pass + stratification_correct)

overall_pass_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0

print(f"\nOVERALL RESULTS:")
print(f"  Total Tests: {total_tests}")
print(f"  Tests Passed: {total_passed}")
print(f"  Pass Rate: {overall_pass_rate:.1f}%")
print(f"  Status: {'✓ APPROVED' if overall_pass_rate >= 90 else '✗ NEEDS REVIEW'}")

print(f"\nDETAILED RESULTS:")
print(f"  Model Accuracy: {(high_risk_correct + low_risk_correct)/(high_risk_total + low_risk_total):.1%}")
print(f"  STEMI Detection: {stemi_correct}/{len(stemi_cases)}")
print(f"  Safety Validation: {(confidence_pass + borderline_pass)}/{len(confidence_tests) + len(borderline_cases)}")
print(f"  Data Integrity: {(validation_pass)}/{len(invalid_inputs)}")
print(f"  Clinical Support: {stratification_correct}/{len(stratification_cases)}")

print(f"\nPERFORMANCE METRICS:")
if latencies:
    print(f"  Prediction Latency: {np.mean(latencies):.2f}ms (Requirement: <500ms)")
if stemi_latencies:
    print(f"  STEMI Analysis: {np.mean(stemi_latencies):.2f}ms (Requirement: <100ms)")

# Save detailed report
test_results["overall_status"] = "APPROVED" if overall_pass_rate >= 90 else "NEEDS_REVIEW"
test_results["pass_rate"] = f"{overall_pass_rate:.1f}%"
test_results["total_tests"] = total_tests
test_results["tests_passed"] = total_passed

report_file = "healthcare_validation_report.json"
with open(report_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n✓ Detailed report saved to: {report_file}")
logger.info(f"Healthcare validation complete. Pass rate: {overall_pass_rate:.1f}%")

print("\n" + "=" * 120)
print("VALIDATION COMPLETE")
print("=" * 120)
