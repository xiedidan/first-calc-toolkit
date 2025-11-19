@echo off
REM Setup Database - Run in Anaconda Environment

echo ========================================
echo Setup Database
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
    echo Running database initialization...
    echo.
    
    conda run -n hospital-backend python backend\scripts\init_data.py
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo Database setup complete!
        echo ========================================
        echo.
        echo Default admin credentials:
        echo   Username: admin
        echo   Password: admin123
        echo.
        echo Please change the password after first login!
        echo.
    ) else (
        echo.
        echo ERROR: Database initialization failed
        echo.
    )
    
) else (
    echo ERROR: Anaconda not found!
    echo.
    echo Please update the ANACONDA_PATH in this script.
    echo Common installation paths:
    echo   - %USERPROFILE%\anaconda3
    echo   - C:\ProgramData\Anaconda3
    echo   - C:\Anaconda3
    echo   - C:\software\anaconda3
    echo.
)

pause
