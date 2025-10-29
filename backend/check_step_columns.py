"""检查 calculation_steps 表的列"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, inspect
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# 检查表结构
inspector = inspect(engine)
columns = inspector.get_columns('calculation_steps')

print("calculation_steps 表的列:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")
