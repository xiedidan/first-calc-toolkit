@echo off
REM Start backend server with conda environment

echo Starting backend server...
echo.

set ANACONDA_PATH=C:\software\anaconda3

if exist "%ANACONDA_PATH%\shell\condabin\conda-hook.ps1" (
    powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& '%ANACONDA_PATH%\shell\condabin\conda-hook.ps1'; conda activate hospital-backend; cd '%~dp0backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo ERROR: Anaconda not found at %ANACONDA_PATH%
    pause
)
