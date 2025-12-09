"""
重新检查时间戳，精确到毫秒
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
        
        # 获取所有唯一时间戳
        print("=" * 80)
        print("所有唯一时间戳（精确到毫秒）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                created_at,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
            GROUP BY created_at
            ORDER BY created_at
        """), {"task_id": task_uuid})
        
        timestamps = list(result)
        for i, ts in enumerate(timestamps):
            print(f"  批次{i+1}: {ts.created_at} - {ts.count} 条记录")
        
        # 获取步骤执行时间（原始时间，不转换）
        print("\n" + "=" * 80)
        print("步骤执行时间（原始）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                csl.start_time,
                csl.end_time,
                csl.created_at as log_created_at
            FROM calculation_step_logs csl
            JOIN calculation_steps cs ON csl.step_id = cs.id
            WHERE csl.task_id = :task_id
            ORDER BY csl.start_time
        """), {"task_id": task_uuid})
        
        steps = list(result)
        for step in steps:
            print(f"  步骤 {step.step_id} ({step.step_name}):")
            print(f"    start_time: {step.start_time}")
            print(f"    end_time: {step.end_time}")
            print(f"    log_created_at: {step.log_created_at}")
        
        # 检查时间差
        print("\n" + "=" * 80)
        print("时间差分析")
        print("=" * 80)
        
        # 第一批数据时间 vs 步骤110开始时间
        batch1_time = timestamps[0].created_at
        step110_start = steps[0].start_time
        
        print(f"  第一批数据时间: {batch1_time}")
        print(f"  步骤110开始时间: {step110_start}")
        print(f"  时间差: {step110_start - batch1_time if step110_start > batch1_time else batch1_time - step110_start}")

if __name__ == '__main__':
    check()
