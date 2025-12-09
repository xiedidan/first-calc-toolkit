@echo off
powershell.exe -ExecutionPolicy ByPass -Command "& 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'; conda activate hospital-backend; python test_ai_config_service.py"
