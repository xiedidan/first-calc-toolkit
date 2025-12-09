"""
检查特定任务的计算结果
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_results():
    with engine.connect() as conn:
        # 检查最近几个任务的结果
        task_uuids = [
            '83289d5f-df1f-4739-afdb-5aa76934eb2a',  # 任务114
            'fa688021-2783-4559-9ed7-30666eab9414',  # 任务113
            'e363140e-966e-4147-8f81-de7d2f23c414',  # 任务112
        ]
        
        for task_uuid in task_uuids:
            print(f"\n任务 {task_uuid[:8]}... 的结果:")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(DISTINCT node_code) as unique_nodes,
                    COUNT(DISTINCT department_id) as unique_depts
                FROM calculation_results
                WHERE task_id = :task_id
            """), {"task_id": task_uuid})
            
            row = result.fetchone()
            print(f"  总记录数: {row.total_count}")
            print(f"  唯一节点数: {row.unique_nodes}")
            print(f"  唯一科室数: {row.unique_depts}")
            
            # 检查重复
            result = conn.execute(text("""
                SELECT 
                    node_code,
                    node_name,
                    department_id,
                    COUNT(*) as duplicate_count
                FROM calculation_results
                WHERE task_id = :task_id
                GROUP BY node_code, node_name, department_id
                HAVING COUNT(*) > 1
                ORDER BY duplicate_count DESC
                LIMIT 5
            """), {"task_id": task_uuid})
            
            duplicates = list(result)
            if duplicates:
                print(f"  重复记录:")
                for dup in duplicates:
                    print(f"    {dup.node_name} ({dup.node_code}) - 科室{dup.department_id}: {dup.duplicate_count} 次")
            else:
                print(f"  无重复记录")

if __name__ == '__main__':
    check_results()
