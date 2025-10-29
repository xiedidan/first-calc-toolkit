@echo off
call conda activate perf_calc
cd backend
python check_datasources.py
pause
