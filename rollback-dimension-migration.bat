@echo off
chcp 65001 >nul
echo ========================================
echo 维度Code迁移回滚脚本
echo ========================================
echo.

echo ⚠️  警告：此操作将回滚数据库迁移！
echo.
echo 回滚后将：
echo   - 删除 dimension_code 字段
echo   - 恢复 dimension_id 字段
echo   - 数据将从 code 转换回 id
echo.

set /p confirm="确定要回滚吗？(输入 YES 继续): "
if not "%confirm%"=="YES" (
    echo 已取消回滚
    pause
    exit /b 0
)

echo.
echo [执行回滚] 正在回滚数据库迁移...
cd backend
call conda activate performance_system
if errorlevel 1 (
    echo ❌ 激活conda环境失败
    pause
    exit /b 1
)

echo.
alembic downgrade -1
if errorlevel 1 (
    echo ❌ 回滚失败
    pause
    exit /b 1
)

echo.
echo ✅ 回滚完成！
echo.
echo 📋 下一步：
echo   1. 重启后端服务
echo   2. 重启前端服务
echo   3. 验证系统功能
echo.

pause
