@echo off
REM Quick Setup Script
REM This script will setup the entire development environment

echo ========================================
echo Quick Setup - Hospital Value Assessment
echo ========================================
echo.

echo This script will:
echo   1. Setup Conda environment (hospital-backend)
echo   2. Install frontend dependencies (npm install)
echo   3. Start all development services
echo.

pause

echo.
echo ========================================
echo Step 1/3: Setup Conda Environment
echo ========================================
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0scripts\setup-conda-env.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Conda environment setup failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2/3: Install Frontend Dependencies
echo ========================================
echo.

cd frontend
call npm install
cd ..

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Frontend dependencies installation failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3/3: Start All Services
echo ========================================
echo.

echo Starting services in new windows...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0scripts\dev-start-all.ps1"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Services should be starting in new windows.
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
