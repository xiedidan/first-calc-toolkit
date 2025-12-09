@echo off
REM Start Celery worker with conda environment

echo Starting Celery worker...
echo.

set ANACONDA_PATH=C:\software\anaconda3

if exist "%ANACONDA_PATH%\shell\condabin\conda-hook.ps1" (
    powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& '%ANACONDA_PATH%\shell\condabin\conda-hook.ps1'; conda activate hospital-backend; cd '%~dp0backend'; celery -A app.celery_app worker --loglevel=info --pool=solo"
) else (
    echo ERROR: Anaconda not found at %ANACONDA_PATH%
    pause
)
