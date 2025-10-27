@echo off
chcp 65001 >nul
echo ========================================
echo 维度Code迁移执行脚本
echo ========================================
echo.

echo [步骤 1/3] 执行数据库迁移...
cd backend
call conda activate performance_system
if errorlevel 1 (
    echo ❌ 激活conda环境失败
    pause
    exit /b 1
)

echo.
echo 正在执行 alembic upgrade...
alembic upgrade head
if errorlevel 1 (
    echo ❌ 数据库迁移失败
    echo.
    echo 如果需要回滚，请执行：
    echo   cd backend
    echo   conda activate performance_system
    echo   alembic downgrade -1
    pause
    exit /b 1
)

echo.
echo ✅ 数据库迁移完成！
echo.

echo [步骤 2/3] 验证迁移结果...
echo.
echo 请手动验证数据库：
echo   1. 检查表结构：DESC dimension_item_mappings;
echo   2. 应该看到 dimension_code 字段
echo   3. 不应该有 dimension_id 字段
echo.

echo [步骤 3/3] 重启服务...
echo.
echo 请按以下步骤重启服务：
echo.
echo 后端服务：
echo   1. 停止当前后端服务（Ctrl+C）
echo   2. cd backend
echo   3. conda activate performance_system
echo   4. python -m uvicorn app.main:app --reload
echo.
echo 前端服务：
echo   1. 停止当前前端服务（Ctrl+C）
echo   2. cd frontend
echo   3. npm run dev
echo.

echo ========================================
echo ✅ 迁移脚本执行完成！
echo ========================================
echo.
echo 📋 下一步：
echo   1. 验证数据库迁移结果
echo   2. 重启后端和前端服务
echo   3. 执行功能测试
echo.
echo 📖 详细信息请查看：DIMENSION_CODE_MIGRATION_COMPLETED.md
echo.

pause
