#!/bin/bash
# Build script for macOS/Linux

set -e

echo "=== Garmin Running AI Coach - Build Script ==="
echo ""

# Use Python 3.11 from Homebrew if available (has framework support)
if [ -f "/opt/homebrew/bin/python3.11" ]; then
    PYTHON="/opt/homebrew/bin/python3.11"
elif command -v python3.11 &> /dev/null; then
    PYTHON="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    echo "Error: Python3 is required but not installed."
    exit 1
fi

echo "Using Python: $PYTHON"
$PYTHON --version
echo ""

# Remove old virtual environment if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build with PyInstaller
echo "Building application..."
pyinstaller garmin_coach.spec

echo ""
echo "=== Build Complete ==="

if [ "$(uname)" == "Darwin" ]; then
    echo "macOS app bundle: dist/GarminRunningCoach.app"
    echo "Run with: open dist/GarminRunningCoach.app"
else
    echo "Linux executable: dist/GarminRunningCoach/GarminRunningCoach"
    echo "Run with: ./dist/GarminRunningCoach/GarminRunningCoach"
fi

echo ""
echo "To create a distributable archive:"
if [ "$(uname)" == "Darwin" ]; then
    echo "  cd dist && zip -r GarminRunningCoach-macOS.zip GarminRunningCoach.app"
else
    echo "  tar -czvf GarminRunningCoach-linux.tar.gz -C dist GarminRunningCoach"
fi
