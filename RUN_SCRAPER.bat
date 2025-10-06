@echo off
echo ==========================================
echo Bundesliga Match Scraper - Starting...
echo ==========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Checking if virtual environment exists...
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first!
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo ==========================================
echo Starting Bundesliga Match Scraper...
echo ==========================================
echo.
echo This will scrape all 306 Bundesliga matches (2024/25)
echo.
echo What will be scraped:
echo   - All 306 Bundesliga matches (Season 2024/25)
echo   - 6 Player Stats categories per match
echo   - Goalkeeper statistics
echo   - Kicker.de table positions before each match
echo   - Opponent positions
echo.
echo Expected duration: 15-30 minutes
echo Please do NOT close this window!
echo.
echo ==========================================
echo.

python main_match_scraper.py
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ==========================================
if %EXIT_CODE% equ 0 (
    echo Scraper finished successfully! ✅
    echo ==========================================
    echo.
    echo Output Excel file:
    echo   Bundesliga_Matches_2024_25_306_games.xlsx
    echo.
    echo Location:
    echo   %CD%
    echo.
    echo You can now open the Excel file!
) else (
    echo Scraper encountered an error! ❌
    echo ==========================================
    echo.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo   1. No internet connection
    echo   2. Websites blocked by firewall
    echo   3. Python packages missing (run setup.bat again)
    echo.
    echo If the problem persists, send this information:
    echo   - Screenshot of this window
    echo   - bundesliga_match_scraper.log (if exists)
)
echo.
pause
