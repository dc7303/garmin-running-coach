#!/bin/bash
# Build script for macOS/Linux

set -e

echo "=== Garmin Running AI Coach - Build Script ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is required but not installed."
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

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
    echo "  zip -r GarminRunningCoach-macOS.zip dist/GarminRunningCoach.app"
else
    echo "  tar -czvf GarminRunningCoach-linux.tar.gz -C dist GarminRunningCoach"
fi
