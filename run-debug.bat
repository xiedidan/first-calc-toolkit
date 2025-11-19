@echo off
chcp 65001 >nul
cd /d "%~dp0backend"
python quick_check_summary.py
pause
