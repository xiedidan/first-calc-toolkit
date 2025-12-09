"""
详细检查时间戳
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
        
        # 获取批次1的时间戳
        print("=" * 80)
        print("时间戳详细分析")
        print("=" * 80)
        
        # 批次1时间戳（UTC+8）
        batch1_time = '2025-12-05 21:17:23.525747'
        
        # 步骤110开始时间
        step110_start = '2025-12-05 21:17:23.817106'
        
        print(f"批次1时间戳: {batch1_time}")
        print(f"步骤110开始时间: {step110_start}")
        print(f"时间差: {step110_start} - {batch1_time} = 约 0.29 秒")
        
        # 这说明批次1是在步骤110开始之前插入的
        # 但这不可能，因为步骤110是第一个执行的步骤
        
        # 检查是否有其他任务在同一时间执行
        print("\n" + "=" * 80)
        print("检查是否有其他任务在同一时间执行")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                id,
                task_id,
                started_at,
                completed_at
            FROM calculation_tasks
            WHERE started_at >= '2025-12-05 21:17:00'
              AND started_at < '2025-12-05 21:18:00'
            ORDER BY started_at
        """))
        
        for row in result:
            print(f"  任务 {row.id} ({row.task_id[:8]}...): {row.started_at} - {row.completed_at}")
        
        # 检查批次1的数据是否与其他任务的数据相同
        print("\n" + "=" * 80)
        print("检查是否有其他任务使用了相同的 task_id")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM calculation_tasks
            WHERE task_id = :task_id
        """), {"task_id": task_uuid})
        
        row = result.fetchone()
        print(f"使用 task_id = {task_uuid} 的任务数量: {row.count}")
        
        # 检查 NOW() 函数的行为
        print("\n" + "=" * 80)
        print("检查 NOW() 函数的行为")
        print("=" * 80)
        
        result = conn.execute(text("SELECT NOW() as now_time"))
        row = result.fetchone()
        print(f"当前 NOW() 返回: {row.now_time}")

if __name__ == '__main__':
    check()
