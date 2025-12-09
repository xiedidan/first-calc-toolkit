"""
检查任务的参数
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
        
        # 检查任务的详细信息
        print("=" * 80)
        print("任务详细信息")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT *
            FROM calculation_tasks
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        if row:
            for key in row._mapping.keys():
                print(f"  {key}: {row._mapping[key]}")
        
        # 检查步骤日志中的 department_id
        print("\n" + "=" * 80)
        print("步骤日志中的 department_id")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                step_id,
                department_id,
                COUNT(*) as count
            FROM calculation_step_logs
            WHERE task_id = :task_id
            GROUP BY step_id, department_id
            ORDER BY step_id, department_id
        """), {"task_id": task_uuid})
        
        for row in result:
            print(f"  步骤 {row.step_id} - 科室 {row.department_id}: {row.count} 次")

if __name__ == '__main__':
    check()
