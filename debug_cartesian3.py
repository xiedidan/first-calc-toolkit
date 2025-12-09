"""
检查计算结果的创建时间，确认是否是多次执行导致的重复
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

TASK_ID = '83289d5f-df1f-4739-afdb-5aa76934eb2a'

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print("=" * 80)
    print("1. 检查重复记录的创建时间")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT node_id, department_id, node_name, created_at, workload
        FROM calculation_results
        WHERE task_id = :task_id
          AND (node_id, department_id) IN (
              SELECT node_id, department_id
              FROM calculation_results
              WHERE task_id = :task_id
              GROUP BY node_id, department_id
              HAVING COUNT(*) > 1
              LIMIT 1
          )
        ORDER BY created_at
    """), {"task_id": TASK_ID})
    rows = list(result)
    if rows:
        print(f"  重复记录的创建时间 (node_id={rows[0].node_id}, dept_id={rows[0].department_id}):")
        for row in rows:
            print(f"    {row.created_at}: workload={row.workload}")
    
    print("\n" + "=" * 80)
    print("2. 检查任务的步骤执行日志")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT step_name, status, started_at, completed_at, rows_affected
        FROM calculation_step_logs
        WHERE task_id = :task_id
        ORDER BY started_at
    """), {"task_id": TASK_ID})
    for row in result:
        print(f"  {row.step_name}: {row.status}, rows={row.rows_affected}")
    
    print("\n" + "=" * 80)
    print("3. 检查是否有多个相同的步骤执行")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT step_name, COUNT(*) as cnt
        FROM calculation_step_logs
        WHERE task_id = :task_id
        GROUP BY step_name
        HAVING COUNT(*) > 1
    """), {"task_id": TASK_ID})
    rows = list(result)
    if rows:
        print(f"  发现重复执行的步骤:")
        for row in rows:
            print(f"    {row.step_name}: {row.cnt} 次")
    else:
        print("  没有发现重复执行的步骤")
    
    print("\n" + "=" * 80)
    print("4. 检查计算结果的唯一创建时间")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT DISTINCT created_at
        FROM calculation_results
        WHERE task_id = :task_id
        ORDER BY created_at
    """), {"task_id": TASK_ID})
    rows = list(result)
    print(f"  计算结果有 {len(rows)} 个不同的创建时间:")
    for row in rows:
        print(f"    {row.created_at}")
