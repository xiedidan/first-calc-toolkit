@echo off
REM Seed Database - Insert initial data

echo ========================================
echo Seed Database with Initial Data
echo ========================================
echo.

REM Try to find Anaconda installation
set ANACONDA_PATH=%USERPROFILE%\anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=%USERPROFILE%\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\ProgramData\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\software\anaconda3

if exist "%ANACONDA_PATH%\Scripts\activate.bat" (
    echo Found Anaconda at: %ANACONDA_PATH%
    echo.
    
    REM Activate conda base environment
    call "%ANACONDA_PATH%\Scripts\activate.bat" "%ANACONDA_PATH%"
    
    REM Run the initialization script
    echo Inserting initial data...
    echo.
    
    conda run -n hospital-backend python backend\scripts\init_data.py
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo Database seeded successfully!
        echo ========================================
        echo.
    ) else (
        echo.
        echo ERROR: Database seeding failed
        echo.
    )
    
) else (
    echo ERROR: Anaconda not found!
    echo.
    echo Please update the ANACONDA_PATH in this script.
    echo.
)

pause
