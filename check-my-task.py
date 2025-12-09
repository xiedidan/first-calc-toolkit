import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'

# 查询这个任务的计算结果
result = db.execute(text(f"""
    SELECT 
        task_id,
        node_id,
        node_type,
        node_name,
        parent_id,
        department_id,
        workload,
        weight,
        value
    FROM calculation_results
    WHERE task_id = '{task_id}'
    ORDER BY department_id, node_type, node_id
    LIMIT 30
"""))

print(f"=== 任务 {task_id} 的计算结果 ===")
print('node_id | node_type | node_name | parent_id | dept_id | workload | weight | value')
print('-' * 120)
rows = result.fetchall()
for r in rows:
    print(f'{r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]}')

print(f"\n总记录数: {len(rows)}")

# 检查有多少记录的 parent_id 不为空
result2 = db.execute(text(f"""
    SELECT 
        COUNT(*) as total,
        COUNT(parent_id) as has_parent,
        COUNT(*) - COUNT(parent_id) as null_parent
    FROM calculation_results
    WHERE task_id = '{task_id}'
"""))

stats = result2.fetchone()
print(f"\n=== parent_id 统计 ===")
print(f"总记录数: {stats[0]}")
print(f"有 parent_id: {stats[1]}")
print(f"parent_id 为 NULL: {stats[2]}")

db.close()
