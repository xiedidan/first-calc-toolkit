"""
检查所有任务的结果，看看是否有多个任务写入了相同的 task_id
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
        
        # 检查这个 task_id 的所有结果
        print("=" * 80)
        print(f"检查 task_id = {task_uuid} 的所有结果")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                MIN(id) as min_id,
                MAX(id) as max_id,
                COUNT(*) as total_count,
                COUNT(DISTINCT created_at) as unique_timestamps
            FROM calculation_results
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        print(f"  ID范围: {row.min_id} - {row.max_id}")
        print(f"  总记录数: {row.total_count}")
        print(f"  唯一时间戳数: {row.unique_timestamps}")
        
        # 检查是否有其他任务也写入了这个 task_id
        print("\n" + "=" * 80)
        print("检查是否有其他任务使用了相同的 task_id")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                task_id,
                COUNT(*) as count
            FROM calculation_tasks
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        print(f"  calculation_tasks 中有 {row.count} 条记录使用此 task_id")
        
        # 检查 Celery 任务是否被重复执行
        print("\n" + "=" * 80)
        print("检查步骤日志的时间分布")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                step_id,
                start_time,
                end_time,
                created_at
            FROM calculation_step_logs
            WHERE task_id = :task_id
            ORDER BY start_time
        """), {"task_id": task_uuid})
        
        for row in result:
            print(f"  步骤 {row.step_id}: start={row.start_time}, end={row.end_time}, created={row.created_at}")
        
        # 检查是否有多个相同步骤的日志
        print("\n" + "=" * 80)
        print("检查是否有重复的步骤日志")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                step_id,
                COUNT(*) as count
            FROM calculation_step_logs
            WHERE task_id = :task_id
            GROUP BY step_id
            HAVING COUNT(*) > 1
        """), {"task_id": task_uuid})
        
        duplicates = list(result)
        if duplicates:
            print("发现重复的步骤日志:")
            for row in duplicates:
                print(f"  步骤 {row.step_id}: {row.count} 条日志")
        else:
            print("没有发现重复的步骤日志")

if __name__ == '__main__':
    check()
