"""
检查工作流相关的表名
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_tables():
    with engine.connect() as conn:
        print("查找工作流相关的表:")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%workflow%' OR table_name LIKE '%step%'
            ORDER BY table_name
        """))
        for row in result:
            print(f"  {row.table_name}")

if __name__ == '__main__':
    check_tables()
