@echo off
REM Family CFO - Backend Restart Script with AI Activation
REM This script restarts the backend with all environment variables loaded

echo ========================================
echo Family CFO - Backend Restart
echo ========================================
echo.

echo Stopping current backend...
echo Please press Ctrl+C in the backend terminal window first!
echo.
pause

echo.
echo Starting backend with AI configuration...
echo.

cd /d "%~dp0"

set DATABASE_URL=postgresql://admin:password123@localhost:6500/family_cfo

echo Environment variables set:
echo - DATABASE_URL: %DATABASE_URL%
echo.

echo Starting uvicorn...
python -m uvicorn main:app --reload --host 0.0.0.0 --port 6501

pause
