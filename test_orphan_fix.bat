@echo off
echo ========================================
echo 测试孤儿记录修复
echo ========================================
echo.

cd backend

echo 步骤1: 数据库层面测试
echo ----------------------------------------
call conda run -n performance_system python test_orphan_dimension_items.py
echo.

echo 步骤2: API层面测试
echo ----------------------------------------
call conda run -n performance_system python test_api_orphan_records.py
echo.

echo ========================================
echo 测试完成！
echo ========================================
pause
