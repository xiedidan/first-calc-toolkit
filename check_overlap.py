"""
检查步骤110和步骤113插入的记录是否有重叠
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_overlap():
    with engine.connect() as conn:
        task_uuid = '83289d5f-df1f-4739-afdb-5aa76934eb2a'
        
        # 检查步骤110插入的记录中有多少是护理维度
        print("=" * 80)
        print("检查步骤110插入的护理维度记录")
        print("=" * 80)
        
        # 步骤110的时间范围 (UTC)
        step110_start = '2025-12-05 13:17:23'
        step110_end = '2025-12-05 13:17:24.5'
        
        result = conn.execute(text("""
            SELECT 
                node_code,
                node_name,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at >= :start_time
              AND created_at < :end_time
              AND (
                node_code LIKE 'dim-nur-bed%'
                OR node_code LIKE 'dim-nur-trans%'
                OR node_code LIKE 'dim-nur-op%'
                OR node_code LIKE 'dim-nur-or%'
                OR node_code LIKE 'dim-nur-tr%'
                OR node_code LIKE 'dim-nur-base%'
                OR node_code LIKE 'dim-nur-collab%'
              )
            GROUP BY node_code, node_name
            ORDER BY node_code
        """), {
            "task_id": task_uuid,
            "start_time": step110_start,
            "end_time": step110_end
        })
        
        records = list(result)
        print(f"步骤110插入的护理维度记录 ({len(records)} 种):")
        for rec in records:
            print(f"  {rec.node_code} ({rec.node_name}): {rec.count} 条")
        
        # 检查步骤113插入的记录
        print("\n" + "=" * 80)
        print("检查步骤113插入的护理维度记录")
        print("=" * 80)
        
        # 步骤113的时间范围 (UTC)
        step113_start = '2025-12-05 13:17:25.293'
        step113_end = '2025-12-05 13:17:25.976'
        
        result = conn.execute(text("""
            SELECT 
                node_code,
                node_name,
                COUNT(*) as count
            FROM calculation_results
            WHERE task_id = :task_id
              AND created_at >= :start_time
              AND created_at < :end_time
            GROUP BY node_code, node_name
            ORDER BY node_code
        """), {
            "task_id": task_uuid,
            "start_time": step113_start,
            "end_time": step113_end
        })
        
        records = list(result)
        print(f"步骤113插入的记录 ({len(records)} 种):")
        for rec in records:
            print(f"  {rec.node_code} ({rec.node_name}): {rec.count} 条")
        
        # 检查重叠的维度
        print("\n" + "=" * 80)
        print("检查重叠的维度")
        print("=" * 80)
        
        result = conn.execute(text("""
            WITH step110_records AS (
                SELECT DISTINCT node_code
                FROM calculation_results
                WHERE task_id = :task_id
                  AND created_at >= '2025-12-05 13:17:23'
                  AND created_at < '2025-12-05 13:17:24.5'
            ),
            step113_records AS (
                SELECT DISTINCT node_code
                FROM calculation_results
                WHERE task_id = :task_id
                  AND created_at >= '2025-12-05 13:17:25.293'
                  AND created_at < '2025-12-05 13:17:25.976'
            )
            SELECT s110.node_code
            FROM step110_records s110
            INNER JOIN step113_records s113 ON s110.node_code = s113.node_code
            ORDER BY s110.node_code
        """), {"task_id": task_uuid})
        
        overlaps = list(result)
        print(f"重叠的维度 ({len(overlaps)} 个):")
        for rec in overlaps:
            print(f"  {rec.node_code}")

if __name__ == '__main__':
    check_overlap()
