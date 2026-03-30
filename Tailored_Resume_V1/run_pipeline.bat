@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo      🚀 ROBUST AI RESUME PIPELINE v2.0 (AGENTIC) 🚀
echo ============================================================

:: Check for jd.txt
if not exist jd.txt (
    echo [ERROR] jd.txt not found.
    echo Please create jd.txt and paste the job description inside.
    pause
    exit /b 1
)

:: Run the Agentic Pipeline
echo [STEP 1/1] Running Multi-Agent Selection ^& Scoring Pipeline...
C:/Users/krish/AppData/Local/Microsoft/WindowsApps/python3.12.exe pipeline.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Pipeline execution failed. 
    echo Check your API key in .env or your internet connection.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ============================================================
echo [SUCCESS] Your tailored, high-score resume is ready!
echo [PDF] Tailored_Resume.pdf
echo ============================================================
pause
