@echo off
chcp 65001 >nul
echo ========================================
echo 收费项目医疗机构关联迁移
echo ========================================
echo.

cd backend

echo 1. 检查并修复迁移状态...
call conda run -n hospital-backend python fix_charge_items_migration.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ 修复失败！
    pause
    exit /b 1
)

echo.
echo 2. 执行数据库迁移...
call conda run -n hospital-backend alembic upgrade head
if %errorlevel% neq 0 (
    echo.
    echo ❌ 迁移失败！
    pause
    exit /b 1
)

echo.
echo 3. 测试收费项目隔离功能...
call conda run -n hospital-backend python test_charge_item_hospital.py

echo.
echo ========================================
echo ✓ 迁移完成
echo ========================================
pause
