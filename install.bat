@echo off
REM PDF to CSV Converter Installation Script for Windows
REM This script sets up the PDF to CSV converter with all dependencies

setlocal enabledelayedexpansion

REM Colors for output (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "NC=[0m"

echo ======================================
echo PDF to CSV Converter Installation
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "pdf_to_csv_converter.py" (
    echo %RED%Error: pdf_to_csv_converter.py not found. Are you in the correct directory?%NC%
    exit /b 1
)

REM Check Python installation
echo %YELLOW%Checking Python version...%NC%
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Error: Python is not installed or not in PATH%NC%
    echo Please install Python 3.7 or higher from https://www.python.org/
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%Found Python %PYTHON_VERSION%%NC%

REM Create virtual environment
echo %YELLOW%Creating virtual environment...%NC%
if exist "venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo %RED%Error: Failed to create virtual environment%NC%
        exit /b 1
    )
    echo %GREEN%Virtual environment created%NC%
)

REM Activate virtual environment
echo %YELLOW%Activating virtual environment...%NC%
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo %RED%Error: Failed to activate virtual environment%NC%
    exit /b 1
)
echo %GREEN%Virtual environment activated%NC%

REM Upgrade pip
echo %YELLOW%Upgrading pip...%NC%
python -m pip install --upgrade pip >nul 2>&1
echo %GREEN%pip upgraded successfully%NC%

REM Install requirements
echo %YELLOW%Installing requirements...%NC%
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo %RED%Error: Failed to install requirements%NC%
        exit /b 1
    )
    echo %GREEN%Requirements installed successfully%NC%
) else (
    echo %RED%Error: requirements.txt not found%NC%
    exit /b 1
)

REM Install development requirements if --dev flag is passed
if "%1"=="--dev" (
    echo %YELLOW%Installing development requirements...%NC%
    if exist "requirements-dev.txt" (
        pip install -r requirements-dev.txt
        if %errorlevel% neq 0 (
            echo %RED%Warning: Some development requirements failed to install%NC%
        ) else (
            echo %GREEN%Development requirements installed%NC%
            
            REM Install pre-commit hooks
            echo %YELLOW%Installing pre-commit hooks...%NC%
            pre-commit install
            echo %GREEN%Pre-commit hooks installed%NC%
        )
    ) else (
        echo %RED%Warning: requirements-dev.txt not found%NC%
    )
)

REM Create necessary directories
echo %YELLOW%Creating necessary directories...%NC%
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
echo %GREEN%Directories created%NC%

REM Test installation
echo %YELLOW%Testing installation...%NC%
python pdf_to_csv_converter.py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Error: Installation test failed%NC%
    exit /b 1
)

for /f "tokens=3" %%i in ('python pdf_to_csv_converter.py --version 2^>^&1') do set VERSION=%%i
echo %GREEN%Installation test passed%NC%
echo %GREEN%PDF to CSV Converter %VERSION% is ready to use!%NC%

echo.
echo ======================================
echo %GREEN%Installation completed successfully!%NC%
echo ======================================
echo.
echo To use the converter:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate
echo   2. Run the converter:
echo      python pdf_to_csv_converter.py input.pdf output.csv
echo.
echo For help:
echo      python pdf_to_csv_converter.py --help
echo.

endlocal