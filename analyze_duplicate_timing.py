"""
分析重复记录的插入时间，确定是哪个步骤插入的
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def analyze():
    with engine.connect() as conn:
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 获取步骤执行时间
        print("=" * 80)
        print("步骤执行时间:")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.step_id,
                cs.name as step_name,
                cs.sort_order,
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
        
        # 获取重复记录的插入时间
        print("\n" + "=" * 80)
        print("重复记录的插入时间分析:")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                id,
                node_code,
                node_name,
                department_id,
                created_at
            FROM calculation_results
            WHERE task_id = :task_id
              AND node_code = 'dim-nur-tr-c'
              AND department_id = 4
            ORDER BY created_at
        """), {"task_id": task_uuid})
        
        records = list(result)
        print(f"\n丙级护理治疗 (dim-nur-tr-c) - 科室4 的记录:")
        for rec in records:
            # 找出是哪个步骤插入的
            step_name = "未知"
            for step in steps:
                if step.start_time <= rec.created_at <= step.end_time:
                    step_name = step.step_name
                    break
            print(f"  ID={rec.id}: created_at={rec.created_at} -> 步骤: {step_name}")
        
        # 检查每个步骤插入了多少条记录
        print("\n" + "=" * 80)
        print("每个步骤插入的记录数:")
        print("=" * 80)
        
        for step in steps:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM calculation_results
                WHERE task_id = :task_id
                  AND created_at >= :start_time
                  AND created_at <= :end_time
            """), {
                "task_id": task_uuid,
                "start_time": step.start_time,
                "end_time": step.end_time
            })
            count = result.fetchone().count
            print(f"  步骤 {step.step_id} ({step.step_name}): {count} 条记录")

if __name__ == '__main__':
    analyze()
