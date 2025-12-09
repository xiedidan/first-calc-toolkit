"""
检查 calculation_tasks 表的列
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_columns():
    with engine.connect() as conn:
        print("calculation_tasks 表的列:")
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'calculation_tasks'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"  {row.column_name}: {row.data_type}")

if __name__ == '__main__':
    check_columns()
