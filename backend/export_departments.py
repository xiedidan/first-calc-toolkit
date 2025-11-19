"""
导出数据库中的科室信息

使用方法：
    python export_departments.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 直接连接数据库，避免模型依赖问题
# 数据库在backend目录下
import pathlib
db_path = pathlib.Path(__file__).parent / "hospital_value.db"
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

print(f"数据库路径: {db_path}")
print(f"数据库存在: {db_path.exists()}\n")


def export_departments():
    """导出科室信息"""
    db = SessionLocal()
    
    try:
        # 先查看所有表
        tables_result = db.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table'
        """))
        tables = tables_result.fetchall()
        print("数据库中的表：")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # 直接使用SQL查询
        result = db.execute(text("""
            SELECT his_code, his_name, sort_order 
            FROM departments 
            WHERE is_active = 1 
            ORDER BY sort_order
        """))
        
        departments = result.fetchall()
        
        print(f"找到 {len(departments)} 个启用的科室：\n")
        print("="*80)
        
        for dept in departments:
            print(f"科室代码: {dept.his_code}")
            print(f"科室名称: {dept.his_name}")
            print(f"排序: {dept.sort_order}")
            print("-"*80)
        
        # 输出JSON格式
        print("\n\nJSON格式（可直接复制到配置文件）：\n")
        print("  \"departments\": [")
        
        for idx, dept in enumerate(departments):
            comma = "," if idx < len(departments) - 1 else ""
            print(f"    {{")
            print(f"      \"his_code\": \"{dept.his_code}\",")
            print(f"      \"his_name\": \"{dept.his_name}\",")
            print(f"      \"category\": \"待分类\",")
            print(f"      \"business_characteristics\": \"待补充\",")
            print(f"      \"constraints\": []")
            print(f"    }}{comma}")
        
        print("  ]")
        
    finally:
        db.close()


if __name__ == "__main__":
    export_departments()
