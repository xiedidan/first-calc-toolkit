@echo off
REM Open Anaconda PowerShell Prompt in project directory

echo Opening Anaconda PowerShell Prompt...
echo.

REM Anaconda installation path
set ANACONDA_PATH=C:\software\anaconda3

if exist "%ANACONDA_PATH%\shell\condabin\conda-hook.ps1" (
    echo Found Anaconda at: %ANACONDA_PATH%
    echo.
    start "Anaconda PowerShell" powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& '%ANACONDA_PATH%\shell\condabin\conda-hook.ps1'; conda activate base; cd '%~dp0'"
) else (
    echo ERROR: Anaconda not found at %ANACONDA_PATH%
    echo.
    echo Please update ANACONDA_PATH in this script.
    echo.
    pause
)
