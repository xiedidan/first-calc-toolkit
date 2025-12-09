"""
检查笛卡尔积问题的具体原因
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_issue():
    with engine.connect() as conn:
        print("=" * 80)
        print("检查最近的计算任务和结果")
        print("=" * 80)
        
        # 获取最近的计算任务
        result = conn.execute(text("""
            SELECT 
                ct.id as task_id,
                ct.period,
                ct.status,
                ct.workflow_id,
                cw.name as workflow_name,
                ct.created_at,
                (SELECT COUNT(*) FROM calculation_results cr WHERE cr.task_id = ct.id::text) as result_count
            FROM calculation_tasks ct
            LEFT JOIN calculation_workflows cw ON ct.workflow_id = cw.id
            ORDER BY ct.created_at DESC
            LIMIT 10
        """))
        
        print("\n最近的计算任务:")
        for row in result:
            print(f"  任务 {row.task_id}: {row.period} - {row.status} - 工作流{row.workflow_id}({row.workflow_name}) - {row.result_count} 条结果")
        
        # 检查是否有重复的结果
        print("\n" + "=" * 80)
        print("检查计算结果中的重复记录")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                task_id,
                node_code,
                node_name,
                department_id,
                COUNT(*) as duplicate_count
            FROM calculation_results
            GROUP BY task_id, node_code, node_name, department_id
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
            LIMIT 20
        """))
        
        duplicates = list(result)
        if duplicates:
            print(f"发现 {len(duplicates)} 组重复记录:")
            for row in duplicates:
                print(f"  任务 {row.task_id[:8]}... - {row.node_name} ({row.node_code}) - 科室{row.department_id}: {row.duplicate_count} 次重复")
        else:
            print("没有发现重复记录")
        
        # 检查 dimension_item_mappings 是否有重复
        print("\n" + "=" * 80)
        print("检查 dimension_item_mappings 是否有重复")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                dimension_code,
                item_code,
                COUNT(*) as duplicate_count
            FROM dimension_item_mappings
            GROUP BY dimension_code, item_code
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
            LIMIT 10
        """))
        
        mapping_duplicates = list(result)
        if mapping_duplicates:
            print(f"发现 {len(mapping_duplicates)} 组重复的映射:")
            for row in mapping_duplicates:
                print(f"  {row.dimension_code} - {row.item_code}: {row.duplicate_count} 次重复")
        else:
            print("没有发现重复的映射")

if __name__ == '__main__':
    check_issue()
