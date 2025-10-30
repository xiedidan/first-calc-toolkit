#!/bin/bash
# Celery Worker 启动脚本
# 用于开发环境

echo "正在启动 Celery Worker..."
echo "环境: 开发环境"
echo "日志级别: INFO"
echo ""

# 启动 Celery Worker
celery -A app.celery_app worker --loglevel=info --pool=solo
