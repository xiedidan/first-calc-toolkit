@echo off
REM Quick seed database script

echo Running database seed...
echo.

REM Try to find Anaconda
set ANACONDA_PATH=C:\software\anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=%USERPROFILE%\anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=%USERPROFILE%\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\ProgramData\Anaconda3

if exist "%ANACONDA_PATH%\Scripts\activate.bat" (
    call "%ANACONDA_PATH%\Scripts\activate.bat" "%ANACONDA_PATH%"
    conda run -n hospital-backend python backend\scripts\init_data.py
) else (
    echo ERROR: Anaconda not found
    echo Please run in Anaconda PowerShell Prompt:
    echo   .\scripts\db-seed.ps1
)

pause
