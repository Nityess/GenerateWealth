#!/bin/bash

# NEPSE Investment Dashboard Startup Script

echo "========================================"
echo "  NEPSE Investment Dashboard"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Install Playwright browsers
echo "Installing Playwright browsers (one-time setup)..."
python -m playwright install chromium
echo "✓ Playwright browsers installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your email credentials!"
    echo "   Open .env in a text editor and configure:"
    echo "   - EMAIL_FROM (your Gmail address)"
    echo "   - EMAIL_PASSWORD (your Gmail app password)"
    echo ""
    read -p "Press Enter to continue..."
fi

# Create necessary directories
mkdir -p data logs

echo ""
echo "========================================"
echo "  Starting NEPSE Dashboard..."
echo "========================================"
echo ""
echo "Dashboard will be accessible at:"
echo "  http://localhost:8050"
echo ""
echo "Login credentials:"
echo "  Username: NitYes"
echo "  Password: hackmeifucan@0101"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Run the application
python app.py
