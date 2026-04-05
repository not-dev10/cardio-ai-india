@echo off
REM Git Push Script for Cardiac Health AI Platform (Windows)

echo ==========================================
echo Cardiac Health AI Platform - Git Push
echo ==========================================

REM Check if git is initialized
if not exist ".git" (
    echo Initializing git repository...
    git init
    git branch -M main
)

REM Add all files
echo.
echo Adding files to git...
git add .

REM Show status
echo.
echo Git status:
git status

REM Commit
echo.
set /p commit_msg="Enter commit message (or press Enter for default): "

if "%commit_msg%"=="" (
    set commit_msg=feat: Complete production-ready cardiac health AI platform - Advanced ML model with ensemble learning - Feature selection and Indian-specific features - Format-specific OCR for Indian labs - DPDP Act compliant consent management - Complete documentation and research paper template - Status: Stage 1-4 Partial Complete
)

echo.
echo Committing with message:
echo %commit_msg%
git commit -m "%commit_msg%"

REM Check if remote exists
git remote | findstr "origin" >nul
if errorlevel 1 (
    echo.
    echo No remote repository found.
    echo Your GitHub repository: https://github.com/not-dev10/psu-changes.git
    set /p add_remote="Add this remote? (y/n): "
    
    if /i "%add_remote%"=="y" (
        git remote add origin https://github.com/not-dev10/psu-changes.git
        echo Remote added!
    )
)

REM Push to GitHub
echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ==========================================
echo Push complete!
echo ==========================================
echo.
echo View your repository at:
echo https://github.com/not-dev10/psu-changes

pause
