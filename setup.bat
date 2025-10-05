@echo off
echo ==========================================
echo Multi-Sport Scraper - Windows Setup
echo ==========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Checking for requirements.txt...
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    echo Make sure you are running this script from the scraper folder!
    echo Current folder should contain: main.py, requirements.txt, etc.
    pause
    exit /b 1
)

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found! Please install Python 3.11 from python.org
    echo https://www.python.org/downloads/windows/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo Removing old virtual environment...
if exist "venv" rmdir /s /q venv

echo Creating fresh virtual environment...
python -m venv venv

echo Installing Python dependencies...
call venv\Scripts\activate & python -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to upgrade pip!
    pause
    exit /b 1
)

call venv\Scripts\activate & pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)

echo Installing Playwright browsers...
call venv\Scripts\activate & python -m playwright install chromium
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install Playwright!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To run the scraper:
echo   venv\Scripts\activate
echo   python main.py --stathead
echo.
echo To run specific sports with premium data:
echo   python main.py --sports bundesliga nfl --stathead
echo.
echo Without premium data:
echo   python main.py --sports bundesliga
echo.
echo For help:
echo   python main.py --help
echo.
pause