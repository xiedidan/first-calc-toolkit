import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'

# 统计不同 node_type 的数量
result = db.execute(text(f"""
    SELECT 
        node_type,
        COUNT(*) as count
    FROM calculation_results
    WHERE task_id = '{task_id}'
    GROUP BY node_type
"""))

print(f"=== 任务 {task_id} 的 node_type 统计 ===")
print('node_type | count')
print('-' * 40)
for r in result.fetchall():
    print(f'{r[0]} | {r[1]}')

# 查看模型节点中有哪些 node_type
result2 = db.execute(text("""
    SELECT 
        node_type,
        COUNT(*) as count
    FROM model_nodes
    WHERE version_id = 1
    GROUP BY node_type
"""))

print(f"\n=== 模型版本 1 的 node_type 统计 ===")
print('node_type | count')
print('-' * 40)
for r in result2.fetchall():
    print(f'{r[0]} | {r[1]}')

# 查看是否有序列节点
result3 = db.execute(text("""
    SELECT id, code, name, node_type, parent_id
    FROM model_nodes
    WHERE version_id = 1 AND node_type = 'sequence'
    LIMIT 10
"""))

print(f"\n=== 模型版本 1 的序列节点示例 ===")
print('id | code | name | node_type | parent_id')
print('-' * 100)
rows = result3.fetchall()
if rows:
    for r in rows:
        print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}')
else:
    print("没有序列节点！")

db.close()
