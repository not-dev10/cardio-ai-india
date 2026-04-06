"""
Test Tesseract OCR Integration
Tests OCR extraction from blood reports with Tesseract
"""
import sys
import os
from pathlib import Path
import json
from PIL import Image, ImageDraw
import numpy as np

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "ml_model"))

# Try to import pytesseract
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[WARN] pytesseract not installed. Install with: pip install pytesseract")

# Set Tesseract path for Windows
if sys.platform == 'win32' and TESSERACT_AVAILABLE:
    pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from backend.services.ocr_service import MedicalReportOCR
from ml_model.medical_validator import MedicalValidator

print("=" * 80)
print("TESSERACT OCR INTEGRATION TEST")
print("=" * 80)

# Create test directory
test_dir = Path("test_reports")
test_dir.mkdir(exist_ok=True)

# ============================================================================
# TEST 1: CREATE HIGH-QUALITY BLOOD REPORT IMAGE
# ============================================================================

def create_high_quality_blood_report():
    """Create a high-quality blood report image for OCR testing"""
    print("\n[TEST 1] Creating high-quality blood report image...")
    
    # Create larger image for better OCR
    img = Image.new('RGB', (1200, 1600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text with better formatting
    text_content = """
BLOOD TEST REPORT
================================================================================

Patient Information:
  Name: John Doe
  Age: 55 years
  Gender: Male
  Date of Test: 2024-04-06
  Lab: Apollo Diagnostics

================================================================================
LIPID PROFILE
================================================================================

Total Cholesterol:        250 mg/dL        [HIGH - Normal: <200]
LDL Cholesterol:          180 mg/dL        [HIGH - Normal: <100]
HDL Cholesterol:          35 mg/dL         [LOW - Normal: >40]
Triglycerides:            200 mg/dL        [HIGH - Normal: <150]

================================================================================
GLUCOSE METABOLISM
================================================================================

Fasting Blood Sugar:      130 mg/dL        [HIGH - Normal: 70-100]
Post-Prandial Blood Sugar: 180 mg/dL       [HIGH - Normal: <140]
HbA1c:                    7.2%             [HIGH - Normal: <6%]

================================================================================
RENAL FUNCTION
================================================================================

Creatinine:               1.2 mg/dL        [NORMAL - Normal: 0.7-1.3]
Urea:                     45 mg/dL         [NORMAL - Normal: 15-45]
BUN:                      42 mg/dL         [NORMAL - Normal: 7-20]

================================================================================
ELECTROLYTES
================================================================================

Sodium:                   138 mEq/L        [NORMAL - Normal: 135-145]
Potassium:                4.5 mEq/L        [NORMAL - Normal: 3.5-5.0]
Calcium:                  9.2 mg/dL        [NORMAL - Normal: 8.5-10.5]
Magnesium:                2.1 mg/dL        [NORMAL - Normal: 1.7-2.2]

================================================================================
CLINICAL INTERPRETATION
================================================================================

The patient shows significant lipid abnormalities with elevated cholesterol,
LDL, and triglycerides. Blood glucose levels are elevated, suggesting possible
diabetes or impaired glucose tolerance. Renal function and electrolytes are
within normal limits.

Recommendation: Cardiology consultation recommended.

================================================================================
    """
    
    # Draw text on image
    y_position = 20
    for line in text_content.split('\n'):
        draw.text((30, y_position), line, fill='black')
        y_position += 30
    
    # Save image
    img_path = test_dir / "blood_report_hq.jpg"
    img.save(img_path, quality=95)
    print(f"[OK] Created high-quality blood report: {img_path}")
    return img_path


# ============================================================================
# TEST 2: TEST TESSERACT OCR DIRECTLY
# ============================================================================

def test_tesseract_direct(img_path):
    """Test Tesseract OCR directly"""
    print("\n[TEST 2] Testing Tesseract OCR directly...")
    
    if not TESSERACT_AVAILABLE:
        print("[FAIL] pytesseract not available")
        return None
    
    try:
        # Open image
        img = Image.open(img_path)
        
        # Extract text using Tesseract
        print("[OK] Extracting text from image...")
        extracted_text = pytesseract.image_to_string(img)
        
        print("[OK] Text extraction successful")
        print("\nExtracted Text (first 500 chars):")
        print("-" * 80)
        print(extracted_text[:500])
        print("-" * 80)
        
        # Count extracted values
        lines = extracted_text.split('\n')
        value_count = sum(1 for line in lines if 'mg/dL' in line or 'mEq/L' in line or '%' in line)
        print(f"\n[OK] Extracted {value_count} lab values")
        
        return extracted_text
        
    except Exception as e:
        print(f"[FAIL] Error in Tesseract OCR: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 3: TEST OCR SERVICE WITH TESSERACT
# ============================================================================

def test_ocr_service(img_path):
    """Test OCR service with Tesseract"""
    print("\n[TEST 3] Testing OCR service with Tesseract...")
    
    try:
        ocr = MedicalReportOCR()
        
        # Process report
        print("[OK] Processing blood report...")
        result = ocr.process_medical_report(str(img_path), report_type="blood")
        
        print("[OK] OCR extraction completed")
        print("\nExtracted Lab Values:")
        print("-" * 80)
        
        extracted_count = 0
        for key, value in result.items():
            if value is not None:
                print(f"  {key}: {value}")
                extracted_count += 1
        
        print("-" * 80)
        print(f"\n[OK] Extracted {extracted_count} values")
        
        # Validate data
        validation = ocr.validate_extracted_data(result)
        print(f"\nValidation Status: {'[OK] Valid' if validation['is_valid'] else '[WARN] Invalid'}")
        
        if validation['warnings']:
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  [WARN] {warning}")
        
        if validation['errors']:
            print("Errors:")
            for error in validation['errors']:
                print(f"  [ERROR] {error}")
        
        return result
        
    except Exception as e:
        print(f"[FAIL] Error in OCR service: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# TEST 4: CALCULATE OCR ACCURACY
# ============================================================================

def test_ocr_accuracy(extracted_data):
    """Calculate OCR accuracy"""
    print("\n[TEST 4] Calculating OCR accuracy...")
    
    # Expected values from the report
    expected_values = {
        "cholesterol_total": 250,
        "cholesterol_ldl": 180,
        "cholesterol_hdl": 35,
        "triglycerides": 200,
        "blood_sugar_fasting": 130,
        "blood_sugar_random": 180,
        "hemoglobin_a1c": 7.2,
        "creatinine": 1.2,
        "potassium": 4.5,
        "sodium": 138,
    }
    
    if not extracted_data:
        print("[FAIL] No extracted data to compare")
        return 0
    
    # Compare extracted vs expected
    matches = 0
    total = 0
    
    print("\nAccuracy Comparison:")
    print("-" * 80)
    print(f"{'Field':<30} {'Expected':<15} {'Extracted':<15} {'Match':<10}")
    print("-" * 80)
    
    for field, expected in expected_values.items():
        extracted = extracted_data.get(field)
        total += 1
        
        # Check if values match (with tolerance for floats)
        if extracted is not None:
            try:
                extracted_val = float(extracted)
                expected_val = float(expected)
                tolerance = expected_val * 0.1  # 10% tolerance
                
                if abs(extracted_val - expected_val) <= tolerance:
                    matches += 1
                    match_status = "YES"
                else:
                    match_status = "NO"
            except:
                match_status = "ERROR"
        else:
            match_status = "MISSING"
        
        print(f"{field:<30} {str(expected):<15} {str(extracted):<15} {match_status:<10}")
    
    print("-" * 80)
    
    accuracy = (matches / total * 100) if total > 0 else 0
    print(f"\nOCR Accuracy: {accuracy:.1f}% ({matches}/{total} values)")
    
    if accuracy >= 85:
        print("[OK] Accuracy meets target (>= 85%)")
    elif accuracy >= 70:
        print("[WARN] Accuracy acceptable but below target")
    else:
        print("[FAIL] Accuracy below acceptable threshold")
    
    return accuracy


# ============================================================================
# TEST 5: INTEGRATE WITH MEDICAL VALIDATOR
# ============================================================================

def test_integration_with_validator(extracted_data):
    """Test integration with medical validator"""
    print("\n[TEST 5] Integrating with medical validator...")
    
    if not extracted_data:
        print("[FAIL] No extracted data")
        return None
    
    try:
        validator = MedicalValidator()
        
        # Validate lab values
        print("[OK] Validating lab values...")
        lab_validation = validator.validate_lab_values(extracted_data)
        
        abnormal_count = sum(1 for v in lab_validation.values() if not v.get('is_normal', True))
        print(f"[OK] Found {abnormal_count} abnormal values")
        
        # Create patient profile
        print("[OK] Creating patient profile...")
        patient_data = {
            "age": 55,
            "sex": 1,
            "chest_pain_type": 2,
            "resting_bp": 140,
            "cholesterol": int(extracted_data.get('cholesterol_total', 250)),
            "fasting_blood_sugar": 1 if extracted_data.get('blood_sugar_fasting', 0) > 120 else 0,
            "resting_ecg": 1,
            "max_heart_rate": 150,
            "exercise_induced_angina": 0,
            "st_depression": 1.5,
            "st_slope": 1,
            "num_major_vessels": 1,
            "thalassemia": 2
        }
        
        # Validate patient data
        print("[OK] Validating patient data...")
        validation = validator.validate_input_data(patient_data)
        
        print(f"\nValidation Result:")
        print(f"  Valid: {validation.is_valid}")
        print(f"  Confidence Level: {validation.confidence_level.value}")
        print(f"  Data Quality Score: {validation.data_quality_score:.2%}")
        print(f"  Clinical Notes: {validation.clinical_notes}")
        
        return validation
        
    except Exception as e:
        print(f"[FAIL] Error in integration: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    
    print("\n" + "=" * 80)
    print("STARTING TESSERACT OCR INTEGRATION TESTS")
    print("=" * 80)
    
    # Check Tesseract availability
    if not TESSERACT_AVAILABLE:
        print("\n[WARN] pytesseract not installed")
        print("Install with: pip install pytesseract")
        print("\nContinuing with OCR service tests...")
    else:
        print("\n[OK] pytesseract is available")
    
    # Create test image
    blood_report_path = create_high_quality_blood_report()
    
    # Test Tesseract directly (if available)
    if TESSERACT_AVAILABLE:
        extracted_text = test_tesseract_direct(blood_report_path)
    else:
        extracted_text = None
    
    # Test OCR service
    extracted_data = test_ocr_service(blood_report_path)
    
    # Calculate accuracy
    if extracted_data:
        accuracy = test_ocr_accuracy(extracted_data)
    else:
        accuracy = 0
    
    # Test integration
    if extracted_data:
        validation = test_integration_with_validator(extracted_data)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("\n[OK] All tests completed!")
    print(f"\nOCR Accuracy: {accuracy:.1f}%")
    print(f"Test reports saved in: {test_dir}")
    
    if accuracy >= 85:
        print("\n[OK] OCR accuracy meets target (>= 85%)")
        print("Ready for hospital data testing!")
    elif accuracy >= 70:
        print("\n[WARN] OCR accuracy acceptable but below target")
        print("Consider improving image preprocessing")
    else:
        print("\n[FAIL] OCR accuracy below acceptable threshold")
        print("Need to improve image quality or preprocessing")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
