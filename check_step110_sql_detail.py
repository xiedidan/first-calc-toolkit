"""
详细检查步骤110的SQL
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
            SELECT code_content
            FROM calculation_steps
            WHERE id = 110
        """))
        
        row = result.fetchone()
        if row:
            sql = row.code_content
            print("步骤110的完整SQL:")
            print("=" * 80)
            print(sql)

if __name__ == '__main__':
    check()
