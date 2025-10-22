"""
Celery应用配置
"""
from celery import Celery

from app.config import settings

# 创建Celery应用
celery_app = Celery(
    "hospital_value_assessment",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    task_soft_time_limit=3300,  # 55分钟软超时
)

# 自动发现任务（后续添加）
# celery_app.autodiscover_tasks(['app.services.calculation'])
