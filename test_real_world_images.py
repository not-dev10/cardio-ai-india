"""
Test OCR with Real-World Medical Images
Supports: Blood reports, ECG reports, Cardiac imaging
"""
import sys
import os
from pathlib import Path
import json

# Fix encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "ml_model"))

from backend.services.ocr_service import MedicalReportOCR
from backend.services.image_processor import CardiacImageProcessor
from ml_model.medical_validator import MedicalValidator

print("=" * 80)
print("REAL-WORLD MEDICAL IMAGE TEST SUITE")
print("=" * 80)

# Create directories
real_images_dir = Path("real_medical_images")
real_images_dir.mkdir(exist_ok=True)

results_dir = Path("ocr_results")
results_dir.mkdir(exist_ok=True)

# ============================================================================
# STEP 1: PREPARE REAL IMAGES
# ============================================================================

print("\n[STEP 1] Preparing to test real medical images...")
print("\nSupported image types:")
print("  1. Blood Reports (JPG, PNG, PDF)")
print("  2. ECG Reports (JPG, PNG, PDF)")
print("  3. Cardiac Imaging (JPG, PNG)")
print("     - X-ray")
print("     - Angiography")
print("     - Echocardiography")

print("\n[INSTRUCTION] Place your real medical images in:")
print(f"  {real_images_dir.absolute()}")

print("\nExpected folder structure:")
print("""
real_medical_images/
├── blood_reports/
│   ├── report1.jpg
│   ├── report2.pdf
│   └── ...
├── ecg_reports/
│   ├── ecg1.jpg
│   ├── ecg2.pdf
│   └── ...
└── cardiac_imaging/
    ├── xray1.jpg
    ├── angiography1.jpg
    └── ...
""")

# ============================================================================
# STEP 2: SCAN FOR REAL IMAGES
# ============================================================================

print("\n[STEP 2] Scanning for real medical images...")

blood_reports = list(real_images_dir.glob("blood_reports/*"))
ecg_reports = list(real_images_dir.glob("ecg_reports/*"))
cardiac_images = list(real_images_dir.glob("cardiac_imaging/*"))

print(f"\nFound:")
print(f"  Blood reports: {len(blood_reports)}")
print(f"  ECG reports: {len(ecg_reports)}")
print(f"  Cardiac images: {len(cardiac_images)}")

total_images = len(blood_reports) + len(ecg_reports) + len(cardiac_images)

if total_images == 0:
    print("\n[INFO] No real images found yet.")
    print("Please add images to the folders above and run this script again.")
    print("\nExample:")
    print("  1. Create folder: real_medical_images/blood_reports/")
    print("  2. Copy blood report images there")
    print("  3. Run this script again")
    sys.exit(0)

# ============================================================================
# STEP 3: TEST BLOOD REPORTS
# ============================================================================

if blood_reports:
    print("\n" + "=" * 80)
    print("TESTING BLOOD REPORTS")
    print("=" * 80)
    
    ocr = MedicalReportOCR()
    validator = MedicalValidator()
    
    for idx, report_path in enumerate(blood_reports, 1):
        print(f"\n[BLOOD REPORT {idx}] {report_path.name}")
        print("-" * 80)
        
        try:
            # Extract data
            print("Extracting data...")
            result = ocr.process_medical_report(str(report_path), report_type="blood")
            
            # Count extracted values
            extracted_count = sum(1 for v in result.values() if v is not None)
            print(f"[OK] Extracted {extracted_count} values")
            
            # Validate
            print("Validating data...")
            validation = ocr.validate_extracted_data(result)
            print(f"[OK] Validation: {'Valid' if validation['is_valid'] else 'Invalid'}")
            
            # Show extracted values
            print("\nExtracted Values:")
            for key, value in result.items():
                if value is not None:
                    print(f"  {key}: {value}")
            
            # Validate lab values
            print("\nLab Value Validation:")
            lab_validation = validator.validate_lab_values(result)
            for lab_name, lab_info in lab_validation.items():
                status = "Normal" if lab_info['is_normal'] else "Abnormal"
                print(f"  {lab_name}: {lab_info['value']} {lab_info['unit']} - {status}")
            
            # Save results
            results_file = results_dir / f"blood_report_{idx}_results.json"
            with open(results_file, 'w') as f:
                json.dump({
                    "file": str(report_path),
                    "extracted_data": result,
                    "validation": validation,
                    "lab_validation": {k: {
                        "value": v['value'],
                        "unit": v['unit'],
                        "is_normal": v['is_normal'],
                        "status": v['status']
                    } for k, v in lab_validation.items()}
                }, f, indent=2)
            
            print(f"[OK] Results saved to: {results_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to process: {e}")
            import traceback
            traceback.print_exc()

# ============================================================================
# STEP 4: TEST ECG REPORTS
# ============================================================================

if ecg_reports:
    print("\n" + "=" * 80)
    print("TESTING ECG REPORTS")
    print("=" * 80)
    
    ocr = MedicalReportOCR()
    
    for idx, report_path in enumerate(ecg_reports, 1):
        print(f"\n[ECG REPORT {idx}] {report_path.name}")
        print("-" * 80)
        
        try:
            # Extract data
            print("Extracting ECG data...")
            result = ocr.process_medical_report(str(report_path), report_type="ecg")
            
            # Count extracted values
            extracted_count = sum(1 for v in result.values() if v is not None)
            print(f"[OK] Extracted {extracted_count} values")
            
            # Show extracted values
            print("\nExtracted ECG Parameters:")
            for key, value in result.items():
                if value is not None:
                    print(f"  {key}: {value}")
            
            # Save results
            results_file = results_dir / f"ecg_report_{idx}_results.json"
            with open(results_file, 'w') as f:
                json.dump({
                    "file": str(report_path),
                    "extracted_data": result
                }, f, indent=2)
            
            print(f"[OK] Results saved to: {results_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to process: {e}")
            import traceback
            traceback.print_exc()

# ============================================================================
# STEP 5: TEST CARDIAC IMAGING
# ============================================================================

if cardiac_images:
    print("\n" + "=" * 80)
    print("TESTING CARDIAC IMAGING")
    print("=" * 80)
    
    processor = CardiacImageProcessor()
    
    for idx, image_path in enumerate(cardiac_images, 1):
        print(f"\n[CARDIAC IMAGE {idx}] {image_path.name}")
        print("-" * 80)
        
        try:
            # Determine image type
            filename = image_path.name.lower()
            if 'xray' in filename or 'x-ray' in filename:
                image_type = "xray"
            elif 'angio' in filename:
                image_type = "angiography"
            elif 'echo' in filename:
                image_type = "ecg"
            else:
                image_type = "xray"  # default
            
            print(f"Image type: {image_type}")
            print("Processing image...")
            
            # Process image
            result = processor.process_image(str(image_path), image_type=image_type)
            
            print(f"[OK] Image processed successfully")
            print(f"\nImage Analysis Results:")
            print(f"  Image Type: {result.image_type}")
            print(f"  Abnormality Score: {result.abnormality_score:.2f}")
            print(f"  Confidence: {result.confidence:.2f}")
            print(f"  Quality Score: {result.quality_score:.2f}")
            print(f"  Findings: {result.findings}")
            
            # Save results
            results_file = results_dir / f"cardiac_image_{idx}_results.json"
            with open(results_file, 'w') as f:
                json.dump({
                    "file": str(image_path),
                    "image_type": result.image_type,
                    "abnormality_score": float(result.abnormality_score),
                    "confidence": float(result.confidence),
                    "quality_score": float(result.quality_score),
                    "findings": result.findings
                }, f, indent=2)
            
            print(f"[OK] Results saved to: {results_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to process: {e}")
            import traceback
            traceback.print_exc()

# ============================================================================
# STEP 6: SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\nImages processed:")
print(f"  Blood reports: {len(blood_reports)}")
print(f"  ECG reports: {len(ecg_reports)}")
print(f"  Cardiac images: {len(cardiac_images)}")
print(f"  Total: {total_images}")

print(f"\nResults saved to: {results_dir.absolute()}")

print("\nNext steps:")
print("1. Review results in ocr_results/ folder")
print("2. Check accuracy of extracted data")
print("3. Validate against manual review")
print("4. Calculate OCR accuracy metrics")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
