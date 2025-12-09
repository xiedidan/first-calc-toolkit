"""
检查步骤112的完整SQL
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT name, code_content
            FROM calculation_steps
            WHERE id = 112
        """))
        
        row = result.fetchone()
        if row:
            print("=" * 80)
            print(f"步骤 112: {row.name}")
            print("=" * 80)
            print(row.code_content)

if __name__ == '__main__':
    check()
