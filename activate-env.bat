@echo off
REM Activate hospital-backend conda environment in current terminal

set ANACONDA_PATH=C:\software\anaconda3

if exist "%ANACONDA_PATH%\shell\condabin\conda-hook.ps1" (
    powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& '%ANACONDA_PATH%\shell\condabin\conda-hook.ps1'; conda activate hospital-backend; cd '%~dp0'"
) else (
    echo ERROR: Anaconda not found at %ANACONDA_PATH%
    pause
)
