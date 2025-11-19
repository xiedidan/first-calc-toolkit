@echo off
chcp 65001 >nul
echo ========================================
echo 测试明细表导出功能
echo ========================================
echo.

python backend\test_export_detail.py

echo.
echo ========================================
echo 测试完成！
echo ========================================
pause
