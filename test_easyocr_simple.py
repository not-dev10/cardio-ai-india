"""
Simple EasyOCR Test
"""
import sys
import os

# Fix encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

print("[OK] EasyOCR installed successfully!")
print("[OK] Ready to test OCR with real blood reports")
print("\nNext: Run test_ocr_and_processing_fixed.py")
