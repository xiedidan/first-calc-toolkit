"""
检查各步骤插入的数据
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
    print("1. 检查每个创建时间对应的节点类型")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT created_at, node_type, COUNT(*) as cnt, COUNT(DISTINCT node_id) as unique_nodes
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY created_at, node_type
        ORDER BY created_at, node_type
    """), {"task_id": TASK_ID})
    for row in result:
        print(f"  {row.created_at}: {row.node_type} - {row.cnt} 条, {row.unique_nodes} 个唯一节点")
    
    print("\n" + "=" * 80)
    print("2. 检查每个创建时间对应的节点名称")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT created_at, node_name, COUNT(*) as cnt
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY created_at, node_name
        ORDER BY created_at, node_name
        LIMIT 50
    """), {"task_id": TASK_ID})
    current_time = None
    for row in result:
        if row.created_at != current_time:
            current_time = row.created_at
            print(f"\n  === {row.created_at} ===")
        print(f"    {row.node_name}: {row.cnt} 条")
