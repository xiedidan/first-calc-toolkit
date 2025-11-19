@echo off
REM Open Anaconda PowerShell Prompt in project directory

echo Opening Anaconda PowerShell Prompt...
echo.

REM Try to find Anaconda installation
set ANACONDA_PATH=%USERPROFILE%\anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=%USERPROFILE%\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\ProgramData\Anaconda3
if not exist "%ANACONDA_PATH%" set ANACONDA_PATH=C:\Anaconda3

if exist "%ANACONDA_PATH%\Scripts\activate.bat" (
    echo Found Anaconda at: %ANACONDA_PATH%
    echo.
    start "Anaconda PowerShell" powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& '%ANACONDA_PATH%\shell\condabin\conda-hook.ps1'; conda activate base; cd '%~dp0'"
) else (
    echo ERROR: Anaconda not found!
    echo.
    echo Please install Anaconda or update the path in this script.
    echo Common installation paths:
    echo   - %USERPROFILE%\anaconda3
    echo   - C:\ProgramData\Anaconda3
    echo   - C:\Anaconda3
    echo.
    pause
)
