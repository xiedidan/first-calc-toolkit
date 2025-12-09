"""
检查数据库中步骤113的实际SQL
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_sql():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                id,
                name,
                sort_order,
                code_content
            FROM calculation_steps
            WHERE id = 113
        """))
        
        row = result.fetchone()
        if row:
            print("=" * 80)
            print(f"步骤 {row.id}: {row.name} (排序: {row.sort_order})")
            print("=" * 80)
            print(row.code_content)

if __name__ == '__main__':
    check_sql()
