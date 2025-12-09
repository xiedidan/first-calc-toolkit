"""
检查步骤113、114、115的SELECT语句
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
        for step_id in [113, 114, 115]:
            result = conn.execute(text("""
                SELECT name, code_content
                FROM calculation_steps
                WHERE id = :step_id
            """), {"step_id": step_id})
            
            row = result.fetchone()
            if row:
                sql = row.code_content
                
                print("=" * 80)
                print(f"步骤 {step_id}: {row.name}")
                print("=" * 80)
                
                # 找到最后一个SELECT语句
                last_select_pos = sql.rfind('SELECT')
                if last_select_pos > 0:
                    last_select = sql[last_select_pos:]
                    print(f"最后一个SELECT语句:")
                    print(last_select[:500])

if __name__ == '__main__':
    check()
