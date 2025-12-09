import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'
dept_id = 3

print(f"=== 检查维度根节点是否在 calculation_results 中 ===\n")

# 查询模型中的维度根节点
print("=== 模型中的维度根节点（应该在 calculation_results 中）===")
result = db.execute(text("""
    SELECT id, code, name, parent_id
    FROM model_nodes
    WHERE version_id = 1
      AND node_type = 'dimension'
      AND parent_id IN (1, 29, 33)  -- 指向序列节点
    ORDER BY parent_id, id
"""))

print('id | code | name | parent_id (序列)')
print('-' * 80)
root_dimension_ids = []
for r in result.fetchall():
    print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
    root_dimension_ids.append(r[0])

# 检查这些维度根节点是否在 calculation_results 中
print(f"\n=== 这些维度根节点在 calculation_results 中吗？===")
if root_dimension_ids:
    result2 = db.execute(text(f"""
        SELECT node_id, node_name, parent_id, value
        FROM calculation_results
        WHERE task_id = '{task_id}'
          AND department_id = {dept_id}
          AND node_id IN ({','.join(map(str, root_dimension_ids))})
        ORDER BY node_id
    """))
    
    print('node_id | node_name | parent_id | value')
    print('-' * 80)
    rows = result2.fetchall()
    if rows:
        for r in rows:
            print(f'{r[0]} | {r[1]} | {r[2]} | {r[3]}')
    else:
        print("❌ 没有找到！这就是问题所在！")
        print("Step1/Step2 只插入了叶子维度，没有插入中间层级的维度节点。")

db.close()
