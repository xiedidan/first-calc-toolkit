"""
检查所有步骤的执行结果
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
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        print("=" * 80)
        print("所有步骤的执行结果")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                csl.result_data,
                csl.execution_info
            FROM calculation_step_logs csl
            JOIN calculation_steps cs ON csl.step_id = cs.id
            WHERE csl.task_id = :task_id
            ORDER BY csl.start_time
        """), {"task_id": task_uuid})
        
        for row in result:
            print(f"\n步骤 {row.step_id} ({row.step_name}):")
            print(f"  result_data: {row.result_data}")
            print(f"  execution_info: {row.execution_info}")

if __name__ == '__main__':
    check()
