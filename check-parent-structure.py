import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'
dept_id = 3

print(f"=== 检查科室 {dept_id} 的数据结构 ===\n")

# 查询序列节点
result = db.execute(text(f"""
    SELECT node_id, node_name, parent_id, value
    FROM calculation_results
    WHERE task_id = '{task_id}'
      AND department_id = {dept_id}
      AND node_type = 'sequence'
    ORDER BY node_id
"""))

print("=== 序列节点 ===")
print('node_id | node_name | parent_id | value')
print('-' * 60)
sequence_ids = []
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
    sequence_ids.append(r[0])

# 查询维度节点，看看它们的 parent_id 指向哪里
print("\n=== 维度节点的 parent_id 分布 ===")
result2 = db.execute(text(f"""
    SELECT parent_id, COUNT(*) as count
    FROM calculation_results
    WHERE task_id = '{task_id}'
      AND department_id = {dept_id}
      AND node_type = 'dimension'
    GROUP BY parent_id
    ORDER BY parent_id
    LIMIT 20
"""))

print('parent_id | count')
print('-' * 30)
for r in result2.fetchall():
    parent_id = r[0]
    count = r[1]
    # 检查这个 parent_id 是否是序列节点
    is_sequence = parent_id in sequence_ids if parent_id else False
    marker = " <- 序列节点" if is_sequence else ""
    print(f'{parent_id} | {count}{marker}')

# 查询一些维度节点的详细信息
print("\n=== 维度节点示例（前10条）===")
result3 = db.execute(text(f"""
    SELECT node_id, node_name, parent_id, value
    FROM calculation_results
    WHERE task_id = '{task_id}'
      AND department_id = {dept_id}
      AND node_type = 'dimension'
    ORDER BY node_id
    LIMIT 10
"""))

print('node_id | node_name | parent_id | value')
print('-' * 80)
for r in result3.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')

db.close()
