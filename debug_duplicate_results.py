"""
调试重复结果的具体原因
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def debug_duplicates():
    with engine.connect() as conn:
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 检查一个具体的重复记录
        print("=" * 80)
        print(f"检查任务 {task_uuid[:8]}... 中的重复记录")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                id,
                node_id,
                node_code,
                node_name,
                department_id,
                workload,
                weight,
                value,
                created_at
            FROM calculation_results
            WHERE task_id = :task_id
              AND node_code = 'dim-nur-tr-c'
              AND department_id = 4
            ORDER BY id
        """), {"task_id": task_uuid})
        
        print("\n丙级护理治疗 (dim-nur-tr-c) - 科室4 的所有记录:")
        for row in result:
            print(f"  ID={row.id}: node_id={row.node_id}, workload={row.workload}, weight={row.weight}, value={row.value}, created_at={row.created_at}")
        
        # 检查这些记录的 node_id 是否相同
        result = conn.execute(text("""
            SELECT 
                node_id,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
              AND node_code = 'dim-nur-tr-c'
              AND department_id = 4
            GROUP BY node_id
        """), {"task_id": task_uuid})
        
        print("\n按 node_id 分组:")
        for row in result:
            print(f"  node_id={row.node_id}: {row.count} 条记录")
        
        # 检查是否有多个步骤插入了数据
        print("\n" + "=" * 80)
        print("检查步骤执行日志")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'calculation_step_logs'
            ORDER BY ordinal_position
        """))
        
        print("calculation_step_logs 表的列:")
        for row in result:
            print(f"  {row.column_name}")
        
        # 检查该任务的步骤日志
        result = conn.execute(text("""
            SELECT *
            FROM calculation_step_logs
            WHERE task_id = :task_id
            ORDER BY id
        """), {"task_id": task_uuid})
        
        print(f"\n任务 {task_uuid[:8]}... 的步骤日志:")
        for row in result:
            print(f"  {row}")

if __name__ == '__main__':
    debug_duplicates()
