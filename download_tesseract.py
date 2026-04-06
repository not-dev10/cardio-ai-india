"""
Download and install Tesseract OCR for Windows
"""
import os
import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("TESSERACT OCR DOWNLOADER")
print("=" * 80)

# Download URL
download_url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-v5.3.3.exe"
download_path = Path("tesseract-ocr-w64-setup-v5.3.3.exe")

print(f"\n[STEP 1] Downloading Tesseract OCR...")
print(f"URL: {download_url}")
print(f"Saving to: {download_path}")

try:
    import urllib.request
    urllib.request.urlretrieve(download_url, str(download_path))
    print(f"[OK] Downloaded successfully!")
    print(f"File size: {download_path.stat().st_size / (1024*1024):.1f} MB")
except Exception as e:
    print(f"[FAIL] Download failed: {e}")
    print("\nTry downloading manually from:")
    print(download_url)
    sys.exit(1)

# Install
print(f"\n[STEP 2] Installing Tesseract OCR...")
print("This will open the installer. Follow the prompts.")
print("Default installation path: C:\\Program Files\\Tesseract-OCR")

try:
    subprocess.run([str(download_path)], check=False)
    print("[OK] Installer launched!")
except Exception as e:
    print(f"[FAIL] Could not launch installer: {e}")
    print(f"Please run manually: {download_path}")

print("\n[STEP 3] Verifying installation...")
import time
time.sleep(5)

tesseract_path = Path("C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
if tesseract_path.exists():
    print(f"[OK] Tesseract found at: {tesseract_path}")
    
    # Test it
    try:
        result = subprocess.run([str(tesseract_path), "--version"], capture_output=True, text=True)
        print(f"[OK] Tesseract version: {result.stdout.split()[0]}")
    except:
        pass
else:
    print(f"[WARN] Tesseract not found at default location")
    print(f"Expected: {tesseract_path}")
    print("Please verify installation completed successfully")

print("\n" + "=" * 80)
print("DONE!")
print("=" * 80)
