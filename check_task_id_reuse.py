"""
检查是否有 task_id 被重用
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
        
        # 检查所有使用这个 task_id 的记录
        print("=" * 80)
        print(f"检查 task_id = {task_uuid} 的所有记录")
        print("=" * 80)
        
        # 检查 calculation_results 表
        result = conn.execute(text("""
            SELECT 
                MIN(created_at) as min_created,
                MAX(created_at) as max_created,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        print(f"calculation_results 表:")
        print(f"  最早创建时间: {row.min_created}")
        print(f"  最晚创建时间: {row.max_created}")
        print(f"  记录数: {row.count}")
        
        # 检查 calculation_step_logs 表
        result = conn.execute(text("""
            SELECT 
                MIN(created_at) as min_created,
                MAX(created_at) as max_created,
                COUNT(*) as count
            FROM calculation_step_logs
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        print(f"\ncalculation_step_logs 表:")
        print(f"  最早创建时间: {row.min_created}")
        print(f"  最晚创建时间: {row.max_created}")
        print(f"  记录数: {row.count}")
        
        # 检查 calculation_tasks 表
        result = conn.execute(text("""
            SELECT 
                id,
                task_id,
                created_at,
                started_at,
                completed_at
            FROM calculation_tasks
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        print(f"\ncalculation_tasks 表:")
        for row in result:
            print(f"  ID: {row.id}")
            print(f"  task_id: {row.task_id}")
            print(f"  created_at: {row.created_at}")
            print(f"  started_at: {row.started_at}")
            print(f"  completed_at: {row.completed_at}")
        
        # 检查是否有其他任务在批次1之前执行
        print("\n" + "=" * 80)
        print("检查批次1之前的任务")
        print("=" * 80)
        
        # 批次1时间戳（UTC）
        batch1_time_utc = '2025-12-05 13:17:23.525747'
        
        result = conn.execute(text("""
            SELECT 
                id,
                task_id,
                created_at,
                started_at,
                completed_at
            FROM calculation_tasks
            WHERE started_at < '2025-12-05 21:17:23.525747'
              AND started_at > '2025-12-05 21:17:00'
            ORDER BY started_at DESC
            LIMIT 5
        """))
        
        tasks = list(result)
        if tasks:
            print("批次1之前的任务:")
            for row in tasks:
                print(f"  任务 {row.id} ({row.task_id[:8]}...): {row.started_at}")
        else:
            print("没有找到批次1之前的任务")

if __name__ == '__main__':
    check()
