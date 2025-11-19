@echo off
echo ========================================
echo 添加 rule 字段到 model_nodes 表
echo ========================================
echo.

cd backend

echo 1. 检查当前迁移状态...
call C:\software\anaconda3\Scripts\activate.bat hospital-backend
alembic current
echo.

echo 2. 执行迁移...
alembic upgrade head
echo.

if %ERRORLEVEL% EQU 0 (
    echo ✓ 迁移成功！
    echo.
    echo 3. 验证迁移结果...
    alembic current
) else (
    echo ✗ 迁移失败！
    echo 请检查错误信息
)

echo.
echo ========================================
echo 迁移完成
echo ========================================
pause

cd ..
