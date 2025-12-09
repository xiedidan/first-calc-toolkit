"""
Celery 任务模块
"""
# 导入所有任务模块，确保Celery worker能够发现这些任务
from app.tasks import calculation_tasks  # noqa: F401
from app.tasks import import_tasks  # noqa: F401
from app.tasks import classification_tasks  # noqa: F401
