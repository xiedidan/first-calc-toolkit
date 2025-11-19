@echo off
chcp 65001 >nul
echo ========================================
echo 数据库迁移 - 简化版
echo ========================================
echo.

cd backend

echo 正在执行迁移...
echo.

python -m alembic upgrade head

if errorlevel 1 (
    echo.
    echo 错误: 迁移失败
    echo 请确保:
    echo 1. Python环境已激活
    echo 2. 已安装alembic: pip install alembic
    echo 3. 数据库连接正常
) else (
    echo.
    echo ========================================
    echo 迁移成功完成！
    echo ========================================
)

echo.
cd ..
pause
