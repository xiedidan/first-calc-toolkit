"""
检查导致重复插入的步骤SQL
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_steps():
    with engine.connect() as conn:
        # 获取步骤 113, 114, 115 的 SQL
        result = conn.execute(text("""
            SELECT 
                ws.id as step_id,
                ws.name as step_name,
                ws.sort_order,
                ws.code_content
            FROM calculation_steps ws
            WHERE ws.id IN (113, 114, 115)
            ORDER BY ws.sort_order
        """))
        
        for row in result:
            print("=" * 80)
            print(f"步骤 {row.step_id}: {row.step_name} (排序: {row.sort_order})")
            print("=" * 80)
            # 只显示 INSERT 语句部分
            sql = row.code_content
            if 'INSERT INTO' in sql:
                insert_pos = sql.find('INSERT INTO')
                print(sql[insert_pos:insert_pos+1500])
            else:
                print(sql[:1500])
            print("\n")

if __name__ == '__main__':
    check_steps()
