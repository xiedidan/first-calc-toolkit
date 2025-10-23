@echo off
chcp 65001 >nul
echo ========================================
echo 执行数据库迁移
echo ========================================
echo.

cd backend

echo 激活Conda环境...
call conda activate hospital_value
if errorlevel 1 (
    echo 错误: Conda环境 hospital_value 不存在
    echo 请先运行: .\scripts\setup-conda-env.ps1
    echo.
    pause
    exit /b 1
)

echo.
echo 执行迁移...
call alembic upgrade head
if errorlevel 1 (
    echo 错误: 迁移执行失败
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 迁移完成！
echo ========================================
echo.
pause
