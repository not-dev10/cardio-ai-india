"""
Download Multiple Open-Source Medical PDFs
Test with various types of medical documents
"""
import sys
import os
from pathlib import Path
import requests
import fitz  # PyMuPDF

# Fix encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 100)
print("DOWNLOADING MULTIPLE OPEN-SOURCE MEDICAL PDFs")
print("=" * 100)

# Create directory
pdfs_dir = Path("real_medical_pdfs")
pdfs_dir.mkdir(exist_ok=True)

# Open-source medical PDFs (publicly available)
medical_pdfs = [
    {
        "name": "STEMI_ECG_Guide.pdf",
        "url": "https://www.emergencymedicinekenya.org/wp-content/uploads/2021/07/STEMI-ECG-Interpretation.pdf",
        "type": "ECG/STEMI Guide",
        "description": "STEMI ECG interpretation guide"
    },
    {
        "name": "ECG_Basics_AHA.pdf",
        "url": "https://www.heart.org/-/media/files/health-topics/answers-by-heart/what-is-an-electrocardiogram.pdf",
        "type": "ECG Basics",
        "description": "American Heart Association ECG basics"
    },
    {
        "name": "Cardiac_Biomarkers.pdf",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3614405/pdf/nihms449630.pdf",
        "type": "Lab Values",
        "description": "Cardiac biomarkers guide from NIH"
    },
    {
        "name": "Cholesterol_Guidelines.pdf",
        "url": "https://www.nhlbi.nih.gov/files/docs/public/heart/chol_tlc.pdf",
        "type": "Lab Values",
        "description": "NHLBI cholesterol guidelines"
    },
    {
        "name": "Blood_Pressure_Guide.pdf",
        "url": "https://www.heart.org/-/media/files/health-topics/high-blood-pressure/hbp-rainbow-chart-english.pdf",
        "type": "Vital Signs",
        "description": "Blood pressure reference chart"
    }
]

print(f"\n[STEP 1] Downloading {len(medical_pdfs)} Medical PDFs...")
print("-" * 100)

downloaded = []
failed = []

for i, pdf in enumerate(medical_pdfs, 1):
    print(f"\n[{i}/{len(medical_pdfs)}] {pdf['name']}")
    print(f"  Type: {pdf['type']}")
    print(f"  Description: {pdf['description']}")
    
    try:
        response = requests.get(pdf['url'], timeout=30, allow_redirects=True, 
                              headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            file_path = pdfs_dir / pdf['name']
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            size_kb = len(response.content) / 1024
            print(f"  ✓ Downloaded: {size_kb:.1f} KB")
            
            downloaded.append({
                "path": file_path,
                "name": pdf['name'],
                "type": pdf['type'],
                "size_kb": size_kb
            })
        else:
            print(f"  ✗ Failed: HTTP {response.status_code}")
            failed.append(pdf['name'])
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:60]}")
        failed.append(pdf['name'])

print(f"\n✓ Downloaded: {len(downloaded)}/{len(medical_pdfs)} PDFs")
if failed:
    print(f"✗ Failed: {', '.join(failed)}")

# Test each downloaded PDF
if downloaded:
    print("\n[STEP 2] Testing PDF Text Extraction...")
    print("-" * 100)
    
    results = []
    
    for pdf_file in downloaded:
        print(f"\n[Processing] {pdf_file['name']}")
        print(f"  Type: {pdf_file['type']}")
        print(f"  Size: {pdf_file['size_kb']:.1f} KB")
        
        try:
            doc = fitz.open(str(pdf_file['path']))
            total_pages = len(doc)
            
            # Extract text from first 2 pages
            total_text = ""
            for page_num in range(min(2, total_pages)):
                page = doc[page_num]
                text = page.get_text()
                total_text += text
            
            doc.close()
            
            # Analyze content
            lines = [line.strip() for line in total_text.split('\n') if line.strip()]
            
            # Medical keywords
            keywords = {
                'ECG': ['ECG', 'electrocardiogram', 'ST segment', 'QRS', 'PR interval'],
                'Lab': ['cholesterol', 'LDL', 'HDL', 'triglycerides', 'glucose', 'HbA1c'],
                'Cardiac': ['heart', 'cardiac', 'myocardial', 'infarction', 'STEMI', 'angina'],
                'Vital': ['blood pressure', 'systolic', 'diastolic', 'hypertension']
            }
            
            found_keywords = []
            for category, kw_list in keywords.items():
                for kw in kw_list:
                    if kw.lower() in total_text.lower():
                        found_keywords.append(f"{category}:{kw}")
            
            print(f"  ✓ Pages: {total_pages}")
            print(f"  ✓ Extracted: {len(total_text)} chars, {len(lines)} lines")
            
            if found_keywords:
                print(f"  ✓ Keywords: {', '.join(found_keywords[:5])}")
            
            # Show sample
            if lines:
                print(f"\n  Sample text:")
                for j, line in enumerate(lines[:3], 1):
                    print(f"    {j}. {line[:70]}")
            
            results.append({
                "name": pdf_file['name'],
                "type": pdf_file['type'],
                "pages": total_pages,
                "chars": len(total_text),
                "lines": len(lines),
                "keywords": len(found_keywords),
                "status": "SUCCESS"
            })
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}")
            results.append({
                "name": pdf_file['name'],
                "type": pdf_file['type'],
                "status": "FAILED",
                "error": str(e)[:60]
            })

    # Summary
    print("\n" + "=" * 100)
    print("EXTRACTION SUMMARY")
    print("=" * 100)
    
    print(f"\nTotal PDFs Downloaded: {len(downloaded)}")
    print(f"Successfully Processed: {sum(1 for r in results if r['status'] == 'SUCCESS')}")
    
    print(f"\nDetailed Results:")
    for r in results:
        if r['status'] == 'SUCCESS':
            print(f"  ✓ {r['name']}: {r['pages']} pages, {r['chars']} chars, {r['keywords']} keywords")
        else:
            print(f"  ✗ {r['name']}: {r.get('error', 'Unknown error')}")
    
    print(f"\nFiles saved to: {pdfs_dir}/")

print("\n" + "=" * 100)
print("COMPLETE")
print("=" * 100)
