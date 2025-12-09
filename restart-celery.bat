@echo off
chcp 65001 >nul
echo ========================================
echo 重启 Celery Worker
echo ========================================
echo.

echo 请按照以下步骤操作:
echo.
echo 1. 在运行 Celery worker 的终端窗口中按 Ctrl+C 停止 worker
echo.
echo 2. 等待 worker 完全停止
echo.
echo 3. 运行以下命令重新启动 worker:
echo.
echo    cd backend
echo    celery -A app.celery_app worker --loglevel=debug --pool=solo
echo.
echo 4. 等待看到 "ready" 消息
echo.
echo 5. 然后在前端创建一个新的计算任务进行测试
echo.

pause
