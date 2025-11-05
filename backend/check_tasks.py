"""检查最近的计算任务"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.calculation_task import CalculationTask

db = SessionLocal()
try:
    tasks = db.query(CalculationTask).order_by(
        CalculationTask.created_at.desc()
    ).limit(5).all()
    
    if tasks:
        print("最近的任务:")
        for t in tasks:
            print(f"  {t.task_id}")
            print(f"    周期: {t.period}")
            print(f"    状态: {t.status}")
            print(f"    创建时间: {t.created_at}")
            print()
    else:
        print("未找到任务")
finally:
    db.close()
