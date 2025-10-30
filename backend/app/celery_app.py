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
    broker_connection_retry_on_startup=True,  # 启动时重试连接
    broker_connection_retry=True,  # 启用连接重试
    broker_connection_max_retries=3,  # 最多重试3次
)

# 导入任务模块（必须在配置之后）
# 这样 Celery worker 启动时会自动注册这些任务
from app.tasks import import_tasks  # noqa: F401
from app.tasks import calculation_tasks  # noqa: F401
