@echo off
REM NEPSE Investment Dashboard Startup Script for Windows

echo ========================================
echo   NEPSE Investment Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo Installing dependencies...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
echo [OK] Dependencies installed

REM Install Playwright browsers
echo Installing Playwright browsers (one-time setup)...
python -m playwright install chromium
echo [OK] Playwright browsers installed

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo [OK] .env file created
    echo.
    echo WARNING: Please edit .env file and add your email credentials!
    echo    Open .env in a text editor and configure:
    echo    - EMAIL_FROM your Gmail address
    echo    - EMAIL_PASSWORD your Gmail app password
    echo.
    pause
)

REM Create necessary directories
if not exist "data\" mkdir data
if not exist "logs\" mkdir logs

echo.
echo ========================================
echo   Starting NEPSE Dashboard...
echo ========================================
echo.
echo Dashboard will be accessible at:
echo   http://localhost:8050
echo.
echo Login credentials:
echo   Username: NitYes
echo   Password: hackmeifucan@0101
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Run the application
python app.py

pause
