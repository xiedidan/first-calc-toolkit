"""
检查5个时间戳对应的步骤
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
        print("所有唯一时间戳及其记录数")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                created_at,
                COUNT(*) as count,
                COUNT(DISTINCT node_code) as unique_nodes
            FROM calculation_results
            WHERE task_id = :task_id
            GROUP BY created_at
            ORDER BY created_at
        """), {"task_id": task_uuid})
        
        timestamps = list(result)
        for ts in timestamps:
            print(f"  {ts.created_at}: {ts.count} 条记录, {ts.unique_nodes} 个唯一节点")
        
        # 对比步骤执行时间
        print("\n" + "=" * 80)
        print("步骤执行时间（UTC）")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                csl.start_time - INTERVAL '8 hours' as start_time_utc,
                csl.end_time - INTERVAL '8 hours' as end_time_utc
            FROM calculation_step_logs csl
            JOIN calculation_steps cs ON csl.step_id = cs.id
            WHERE csl.task_id = :task_id
            ORDER BY csl.start_time
        """), {"task_id": task_uuid})
        
        steps = list(result)
        for step in steps:
            print(f"  步骤 {step.step_id} ({step.step_name}): {step.start_time_utc} - {step.end_time_utc}")
        
        # 匹配时间戳和步骤
        print("\n" + "=" * 80)
        print("时间戳与步骤的对应关系")
        print("=" * 80)
        
        for ts in timestamps:
            matched_step = None
            for step in steps:
                if step.start_time_utc <= ts.created_at <= step.end_time_utc:
                    matched_step = step
                    break
            
            if matched_step:
                print(f"  {ts.created_at} ({ts.count} 条) -> 步骤 {matched_step.step_id} ({matched_step.step_name})")
            else:
                # 尝试找最近的步骤
                for step in steps:
                    if ts.created_at < step.start_time_utc:
                        print(f"  {ts.created_at} ({ts.count} 条) -> 在步骤 {step.step_id} 之前")
                        break
                else:
                    print(f"  {ts.created_at} ({ts.count} 条) -> 未匹配到步骤")

if __name__ == '__main__':
    check()
