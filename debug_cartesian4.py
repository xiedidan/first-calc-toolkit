"""
检查步骤执行日志
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
    print("1. 检查任务的步骤执行日志")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT csl.step_id, cs.name as step_name, csl.status, csl.start_time, csl.end_time
        FROM calculation_step_logs csl
        JOIN calculation_steps cs ON csl.step_id = cs.id
        WHERE csl.task_id = :task_id
        ORDER BY csl.start_time
    """), {"task_id": TASK_ID})
    for row in result:
        print(f"  {row.step_name} (id={row.step_id}): {row.status}, {row.start_time} - {row.end_time}")
    
    print("\n" + "=" * 80)
    print("2. 检查是否有多个相同的步骤执行")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT cs.name as step_name, COUNT(*) as cnt
        FROM calculation_step_logs csl
        JOIN calculation_steps cs ON csl.step_id = cs.id
        WHERE csl.task_id = :task_id
        GROUP BY cs.name
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
    print("3. 检查计算结果的唯一创建时间")
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
    
    print("\n" + "=" * 80)
    print("4. 检查每个创建时间的记录数")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT created_at, COUNT(*) as cnt
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY created_at
        ORDER BY created_at
    """), {"task_id": TASK_ID})
    for row in result:
        print(f"    {row.created_at}: {row.cnt} 条")
