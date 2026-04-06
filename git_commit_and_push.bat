@echo off
echo ========================================
echo Git Commit and Push Script
echo ========================================
echo.

REM Stage all changes
echo [1/3] Staging all changes...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to stage changes
    pause
    exit /b 1
)
echo ✓ Changes staged successfully
echo.

REM Commit with message
echo [2/3] Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Model fix: Improved AUC to 97.7%% and added next steps guide

git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit changes
    pause
    exit /b 1
)
echo ✓ Changes committed successfully
echo.

REM Push to GitHub
echo [3/3] Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Failed to push to GitHub
    echo Trying 'master' branch instead...
    git push origin master
    if %errorlevel% neq 0 (
        echo ERROR: Failed to push to both main and master branches
        pause
        exit /b 1
    )
)
echo ✓ Changes pushed successfully
echo.

echo ========================================
echo All done! Changes are now on GitHub
echo ========================================
pause
