# Tesseract OCR Installation Script for Windows
# This script downloads and installs Tesseract OCR

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tesseract OCR Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "WARNING: This script should be run as Administrator for best results" -ForegroundColor Yellow
}

# Create downloads directory
$downloadDir = "$env:USERPROFILE\Downloads\Tesseract"
if (-not (Test-Path $downloadDir)) {
    New-Item -ItemType Directory -Path $downloadDir | Out-Null
    Write-Host "[OK] Created download directory: $downloadDir" -ForegroundColor Green
}

# Download Tesseract installer
Write-Host "`n[STEP 1] Downloading Tesseract OCR installer..." -ForegroundColor Cyan
$installerUrl = "https://github.com/UB-Mannheim/tesseract/wiki"
$installerPath = "$downloadDir\tesseract-ocr-w64-setup-v5.3.3.exe"

Write-Host "Download URL: https://github.com/UB-Mannheim/tesseract/releases" -ForegroundColor Yellow
Write-Host "Latest Release: tesseract-ocr-w64-setup-v5.3.3.exe" -ForegroundColor Yellow
Write-Host "`nPlease download manually from:" -ForegroundColor Yellow
Write-Host "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-v5.3.3.exe" -ForegroundColor Cyan

# Alternative: Try to download using PowerShell
Write-Host "`n[STEP 2] Attempting automatic download..." -ForegroundColor Cyan
try {
    $downloadUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-v5.3.3.exe"
    Write-Host "Downloading from: $downloadUrl" -ForegroundColor Yellow
    
    # Use WebClient for download
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($downloadUrl, $installerPath)
    
    Write-Host "[OK] Downloaded successfully to: $installerPath" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Automatic download failed. Please download manually." -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/UB-Mannheim/tesseract/releases" -ForegroundColor Cyan
    Write-Host "Save to: $installerPath" -ForegroundColor Cyan
}

# Check if installer exists
if (Test-Path $installerPath) {
    Write-Host "`n[STEP 3] Installing Tesseract OCR..." -ForegroundColor Cyan
    Write-Host "Installer path: $installerPath" -ForegroundColor Yellow
    
    # Run installer silently
    Write-Host "Running installer (this may take a few minutes)..." -ForegroundColor Yellow
    & $installerPath /S /D="C:\Program Files\Tesseract-OCR"
    
    # Wait for installation to complete
    Start-Sleep -Seconds 10
    
    # Verify installation
    Write-Host "`n[STEP 4] Verifying installation..." -ForegroundColor Cyan
    $tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
    
    if (Test-Path $tesseractPath) {
        Write-Host "[OK] Tesseract installed successfully!" -ForegroundColor Green
        Write-Host "Installation path: $tesseractPath" -ForegroundColor Green
        
        # Test tesseract
        Write-Host "`n[STEP 5] Testing Tesseract..." -ForegroundColor Cyan
        & $tesseractPath --version
        
    } else {
        Write-Host "[FAIL] Tesseract not found at expected location" -ForegroundColor Red
        Write-Host "Please verify installation manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[WARN] Installer not found. Please download manually:" -ForegroundColor Yellow
    Write-Host "https://github.com/UB-Mannheim/tesseract/releases" -ForegroundColor Cyan
}

# Add to Python path
Write-Host "`n[STEP 6] Setting up Python integration..." -ForegroundColor Cyan
Write-Host "Add this to your Python code:" -ForegroundColor Yellow
Write-Host @"
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
"@ -ForegroundColor Cyan

# Environment variable setup
Write-Host "`n[STEP 7] Setting environment variable..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("TESSERACT_PATH", "C:\Program Files\Tesseract-OCR\tesseract.exe", "User")
Write-Host "[OK] Environment variable TESSERACT_PATH set" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Verify installation: tesseract --version" -ForegroundColor White
Write-Host "2. Test with OCR: python test_ocr_with_tesseract.py" -ForegroundColor White
Write-Host "3. Run full test suite: python test_ocr_and_processing_fixed.py" -ForegroundColor White
