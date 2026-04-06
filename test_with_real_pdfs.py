"""
Test OCR with Real Open-Source Medical PDFs
Downloads and processes actual medical documents
"""
import sys
import os
from pathlib import Path
import requests
from urllib.parse import urlparse

# Fix encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "backend"))

print("=" * 100)
print("TESTING WITH REAL OPEN-SOURCE MEDICAL PDFs")
print("=" * 100)

# Create directory for real PDFs
real_pdfs_dir = Path("real_medical_pdfs")
real_pdfs_dir.mkdir(exist_ok=True)

# Open-source medical PDFs (publicly available, no authentication required)
medical_pdfs = [
    {
        "name": "STEMI_ECG_Interpretation.pdf",
        "url": "https://www.emergencymedicinekenya.org/wp-content/uploads/2021/07/STEMI-ECG-Interpretation.pdf",
        "type": "ECG Guide"
    },
    {
        "name": "WHO_Lab_Manual.pdf",
        "url": "https://apps.who.int/iris/bitstream/handle/10665/44602/9789241548366_eng.pdf",
        "type": "Lab Manual"
    }
]

print("\n[STEP 1] Downloading Open-Source Medical PDFs...")
print("-" * 100)

downloaded_files = []

for pdf in medical_pdfs:
    try:
        print(f"\nDownloading: {pdf['name']}")
        print(f"  Type: {pdf['type']}")
        print(f"  URL: {pdf['url']}")
        
        response = requests.get(pdf['url'], timeout=30, allow_redirects=True)
        
        if response.status_code == 200:
            file_path = real_pdfs_dir / pdf['name']
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024  # KB
            print(f"  ✓ Downloaded: {file_size:.1f} KB")
            downloaded_files.append({
                "path": file_path,
                "name": pdf['name'],
                "type": pdf['type']
            })
        else:
            print(f"  ✗ Failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")

print(f"\n✓ Downloaded {len(downloaded_files)} PDFs")

# Test OCR on downloaded PDFs
if downloaded_files:
    print("\n[STEP 2] Testing OCR on Real PDFs...")
    print("-" * 100)
    
    try:
        from backend.services.ocr_service import OCRService
        
        ocr = OCRService()
        
        for pdf_file in downloaded_files:
            print(f"\n[Processing] {pdf_file['name']}")
            print(f"  Type: {pdf_file['type']}")
            
            try:
                # Extract text from first page
                result = ocr.extract_text_from_pdf(str(pdf_file['path']), max_pages=1)
                
                if result and 'text' in result:
                    text = result['text']
                    print(f"  ✓ Extracted {len(text)} characters")
                    print(f"  Preview: {text[:200]}...")
                else:
                    print(f"  ✗ No text extracted")
                    
            except Exception as e:
                print(f"  ✗ OCR Error: {str(e)[:60]}")
                
    except ImportError:
        print("  ✗ OCR Service not available")
        print("  Install: pip install pytesseract pdf2image")

print("\n" + "=" * 100)
print("REAL PDF TEST COMPLETE")
print("=" * 100)

print(f"""
Downloaded Files: {len(downloaded_files)}
Location: {real_pdfs_dir}

Next Steps:
1. Check the downloaded PDFs in {real_pdfs_dir}/
2. Run OCR tests on these real documents
3. Validate extraction accuracy
4. Test with your own medical PDFs

Note: These are open-source educational materials.
For actual patient data, you need hospital partnerships.
""")
