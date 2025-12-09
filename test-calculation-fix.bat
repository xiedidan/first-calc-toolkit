@echo off
chcp 65001 >nul
echo ========================================
echo 计算任务执行修复验证
echo ========================================
echo.

echo 1. 检查Redis是否运行...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Redis未运行，请先启动Redis
    echo 提示: 运行 redis-server
    pause
    exit /b 1
)
echo [成功] Redis正在运行
echo.

echo 2. 检查数据库连接...
psql -U admin -d hospital_value -c "SELECT 1" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 无法连接到数据库，请确保PostgreSQL正在运行
)
echo.

echo 3. 检查最近的任务状态...
echo.
psql -U admin -d hospital_value -c "SELECT task_id, status, error_message, created_at FROM calculation_tasks ORDER BY created_at DESC LIMIT 5;"
echo.

echo 4. 检查Celery worker状态...
echo.
echo 请确保Celery worker正在运行:
echo   cd backend
echo   celery -A app.celery_app worker --loglevel=debug --pool=solo
echo.

echo 5. 测试建议...
echo.
echo 创建一个新的计算任务，然后观察:
echo   - 后端日志: 应该看到 [INFO] 提交Celery任务
echo   - Celery日志: 应该看到 [INFO] 任务开始执行
echo   - 数据库: calculation_results 表应该有新记录
echo.

pause
