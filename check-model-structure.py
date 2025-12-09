import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

version_id = 1

print(f"=== 模型版本 {version_id} 的节点结构 ===\n")

# 查询序列节点
result = db.execute(text(f"""
    SELECT id, code, name, parent_id
    FROM model_nodes
    WHERE version_id = {version_id}
      AND node_type = 'sequence'
    ORDER BY id
"""))

print("=== 序列节点 ===")
print('id | code | name | parent_id')
print('-' * 80)
sequence_ids = []
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
    sequence_ids.append(r[0])

# 查询维度节点，看看哪些维度的 parent_id 指向序列
print("\n=== parent_id 指向序列的维度节点 ===")
result2 = db.execute(text(f"""
    SELECT id, code, name, parent_id
    FROM model_nodes
    WHERE version_id = {version_id}
      AND node_type = 'dimension'
      AND parent_id IN ({','.join(map(str, sequence_ids))})
    ORDER BY parent_id, id
"""))

print('id | code | name | parent_id')
print('-' * 80)
rows = result2.fetchall()
if rows:
    for r in rows:
        print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
else:
    print("没有维度节点的 parent_id 指向序列节点！")

# 查询维度树的根节点（parent_id 为 NULL 或指向非维度节点）
print("\n=== 维度树的根节点 ===")
result3 = db.execute(text(f"""
    SELECT id, code, name, parent_id, node_type
    FROM model_nodes
    WHERE version_id = {version_id}
      AND node_type = 'dimension'
      AND (parent_id IS NULL OR parent_id NOT IN (
          SELECT id FROM model_nodes WHERE version_id = {version_id} AND node_type = 'dimension'
      ))
    ORDER BY id
    LIMIT 20
"""))

print('id | code | name | parent_id | node_type')
print('-' * 100)
for r in result3.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}')

db.close()
