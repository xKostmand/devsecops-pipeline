@echo off
echo ====================================================
echo    Running Local Static Security Scans (SAST)
echo ====================================================

:: Ensure reports folder exists
if not exist "reports" mkdir reports

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Cannot run local scans.
    exit /b 1
)

echo [1/3] Checking and installing dependencies (bandit, safety)...
python -m pip install --quiet bandit safety

:: 2. Run Bandit
echo [2/3] Running Bandit SAST scan...
python -m bandit -r app -f json -o reports/bandit_report.json
if %errorlevel% neq 0 (
    echo Bandit found issues (expected). Report saved to reports/bandit_report.json.
) else (
    echo Bandit scan completed with no issues.
)

:: 3. Run Safety
echo [3/3] Running Safety dependency scan...
python -m safety check -r app/requirements.txt --json > reports/safety_report.json 2>nul
echo Safety check completed. Report saved to reports/safety_report.json.

echo.
echo ====================================================
echo    Local scans complete!
echo ====================================================
echo Note: Trivy, SQLMap, and OWASP ZAP scans require Docker.
echo To run them, start Docker Desktop and launch Jenkins:
echo   docker-compose up -d --build
echo.
echo Open reports/dashboard.html in your browser to view findings.
pause
