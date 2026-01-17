@echo off
REM Build script for Windows

echo === Garmin Running AI Coach - Build Script ===
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous build
echo Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build with PyInstaller
echo Building application...
pyinstaller garmin_coach.spec

echo.
echo === Build Complete ===
echo Windows executable: dist\GarminRunningCoach\GarminRunningCoach.exe
echo.
echo To create a distributable archive, zip the dist\GarminRunningCoach folder.

pause
