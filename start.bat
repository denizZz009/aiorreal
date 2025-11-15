@echo off
echo ========================================
echo AI Detection System - Starting...
echo ========================================
echo.

echo [1/2] Starting Backend API Server...
start "AI Detection API" cmd /k "python run_server.py"

timeout /t 5 /nobreak >nul

echo [2/2] Opening Frontend...
python open_app.py

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:8000
echo.
echo Press any key to exit...
pause >nul
