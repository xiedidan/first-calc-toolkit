"""
分析时间戳（统一时区）
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def analyze():
    with engine.connect() as conn:
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 获取所有唯一时间戳（转换为UTC+8）
        print("=" * 80)
        print("所有唯一时间戳（转换为UTC+8）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                created_at + INTERVAL '8 hours' as created_at_utc8,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
            GROUP BY created_at
            ORDER BY created_at
        """), {"task_id": task_uuid})
        
        timestamps = list(result)
        for i, ts in enumerate(timestamps):
            print(f"  批次{i+1}: {ts.created_at_utc8} - {ts.count} 条记录")
        
        # 获取步骤执行时间（原始UTC+8）
        print("\n" + "=" * 80)
        print("步骤执行时间（UTC+8）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                csl.start_time,
                csl.end_time
            FROM calculation_step_logs csl
            JOIN calculation_steps cs ON csl.step_id = cs.id
            WHERE csl.task_id = :task_id
            ORDER BY csl.start_time
        """), {"task_id": task_uuid})
        
        steps = list(result)
        for step in steps:
            print(f"  步骤 {step.step_id} ({step.step_name}): {step.start_time} - {step.end_time}")
        
        # 匹配时间戳和步骤
        print("\n" + "=" * 80)
        print("时间戳与步骤的对应关系")
        print("=" * 80)
        
        for i, ts in enumerate(timestamps):
            matched_step = None
            for step in steps:
                if step.start_time <= ts.created_at_utc8 <= step.end_time:
                    matched_step = step
                    break
            
            if matched_step:
                print(f"  批次{i+1} ({ts.created_at_utc8}, {ts.count}条) -> 步骤 {matched_step.step_id} ({matched_step.step_name})")
            else:
                print(f"  批次{i+1} ({ts.created_at_utc8}, {ts.count}条) -> 未匹配到步骤")

if __name__ == '__main__':
    analyze()
