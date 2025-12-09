"""
检查步骤2的SQL内容
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_step2():
    with engine.connect() as conn:
        # 获取工作流29和30的步骤2
        result = conn.execute(text("""
            SELECT 
                ws.workflow_id,
                ws.id as step_id,
                ws.name as step_name,
                ws.sort_order,
                ws.code_content
            FROM calculation_steps ws
            WHERE ws.workflow_id IN (29, 30)
            AND ws.sort_order = 2.00
            ORDER BY ws.workflow_id
        """))
        
        for row in result:
            print("=" * 80)
            print(f"工作流 {row.workflow_id} - 步骤 {row.step_name} (ID: {row.step_id})")
            print("=" * 80)
            print(row.code_content[:3000] if row.code_content else "NULL")
            print("\n... (截断)")

if __name__ == '__main__':
    check_step2()
