@echo off
chcp 65001 >nul
echo ========================================
echo 科室汇总表详细调试
echo ========================================
echo.

cd /d "%~dp0backend"

echo 正在调试最新任务的第一个科室...
echo.

python debug_summary_detail.py

echo.
echo ========================================
echo 调试完成
echo ========================================
echo.
pause
