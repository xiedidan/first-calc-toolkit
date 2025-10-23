@echo off
chcp 65001 >nul
echo ========================================
echo 修复并执行数据库迁移
echo ========================================
echo.

cd backend

echo 正在执行迁移...
echo.

python -m alembic upgrade heads

if errorlevel 1 (
    echo.
    echo 错误: 迁移失败
    echo.
) else (
    echo.
    echo ========================================
    echo 迁移成功完成！
    echo ========================================
    echo.
    echo 请重启后端服务：
    echo 1. 在后端窗口按 Ctrl+C
    echo 2. 运行: .\scripts\dev-start-backend.ps1
)

echo.
cd ..
pause
