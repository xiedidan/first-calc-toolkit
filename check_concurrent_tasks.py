"""
检查是否有并发任务
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
        # 检查在同一时间段内执行的任务
        print("=" * 80)
        print("检查在 2025-12-05 21:17:00 - 21:18:00 期间执行的任务")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                id,
                task_id,
                workflow_id,
                period,
                status,
                started_at,
                completed_at
            FROM calculation_tasks
            WHERE started_at >= '2025-12-05 21:17:00'
              AND started_at < '2025-12-05 21:18:00'
            ORDER BY started_at
        """))
        
        for row in result:
            print(f"  任务 {row.id} ({row.task_id[:8]}...): {row.started_at} - {row.completed_at}")
        
        # 检查批次1和批次2的数据是否与其他任务的数据相同
        print("\n" + "=" * 80)
        print("检查批次1和批次2的数据来源")
        print("=" * 80)
        
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 检查批次1的数据
        result = conn.execute(text("""
            SELECT 
                node_code,
                node_name,
                department_id,
                workload,
                value
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at + INTERVAL '8 hours' = '2025-12-05 21:17:23.525747'
            ORDER BY node_code, department_id
            LIMIT 10
        """), {"task_id": task_uuid})
        
        print("批次1的数据样本:")
        for row in result:
            print(f"  {row.node_code} - 科室{row.department_id}: workload={row.workload}, value={row.value}")
        
        # 检查批次3的数据（步骤113）
        result = conn.execute(text("""
            SELECT 
                node_code,
                node_name,
                department_id,
                workload,
                value
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at + INTERVAL '8 hours' = '2025-12-05 21:17:25.785584'
            ORDER BY node_code, department_id
            LIMIT 10
        """), {"task_id": task_uuid})
        
        print("\n批次3的数据样本（步骤113）:")
        for row in result:
            print(f"  {row.node_code} - 科室{row.department_id}: workload={row.workload}, value={row.value}")

if __name__ == '__main__':
    check()
