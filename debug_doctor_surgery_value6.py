"""
调试白内障专科医生诊断-治疗手术的金额问题 - 第六部分
检查工作流Step 2的SQL逻辑
"""
import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# 查看工作流31的Step 2 SQL
print("=" * 80)
print("工作流31的Step 2 SQL（医生维度统计）：")
print("=" * 80)
result = db.execute(text("""
    SELECT cs.id, cs.name, cs.code_content
    FROM calculation_steps cs
    WHERE cs.workflow_id = 31
      AND cs.sort_order >= 2 AND cs.sort_order < 3
    ORDER BY cs.sort_order
"""))
rows = list(result)
for row in rows:
    print(f"\n步骤 {row.id}: {row.name}")
    print("-" * 40)
    # 只打印前2000个字符
    sql = row.code_content[:3000] if row.code_content else "无SQL"
    print(sql)
    if len(row.code_content or '') > 3000:
        print("\n... (SQL太长，已截断)")

# 检查Step 2中是否有区分开单科室和执行科室的逻辑
print("\n" + "=" * 80)
print("检查Step 2中科室字段的使用：")
print("=" * 80)
result = db.execute(text("""
    SELECT cs.id, cs.name, cs.code_content
    FROM calculation_steps cs
    WHERE cs.workflow_id = 31
      AND cs.sort_order >= 2 AND cs.sort_order < 3
"""))
row = result.fetchone()
if row:
    sql = row.code_content or ""
    # 检查是否使用了prescribing_dept_code
    if 'prescribing_dept_code' in sql:
        print("✓ 使用了 prescribing_dept_code")
    else:
        print("✗ 未使用 prescribing_dept_code")
    
    # 检查是否使用了executing_dept_code
    if 'executing_dept_code' in sql:
        print("✓ 使用了 executing_dept_code")
    else:
        print("✗ 未使用 executing_dept_code")
    
    # 检查是否有CASE WHEN逻辑区分不同维度
    if 'CASE' in sql and 'dim-doc' in sql:
        print("✓ 有CASE逻辑区分维度")
    else:
        print("✗ 无CASE逻辑区分维度")

# 检查计算结果中dim-doc-out-eval-tr的数据
print("\n" + "=" * 80)
print("检查计算结果中dim-doc-out-eval-tr的数据（按科室）：")
print("=" * 80)
result = db.execute(text("""
    SELECT 
        cr.department_id,
        d.his_name,
        d.accounting_unit_code,
        cr.workload,
        cr.weight,
        cr.value
    FROM calculation_results cr
    JOIN departments d ON d.id = cr.department_id
    WHERE cr.task_id = '0795b9cf-3b58-44b2-8bf1-0be573a0ac2f'
      AND cr.node_code = 'dim-doc-out-eval-tr'
    ORDER BY cr.workload DESC
    LIMIT 10
"""))
rows = list(result)
print(f"找到 {len(rows)} 条记录")
for row in rows:
    print(f"  科室: {row.his_name} ({row.accounting_unit_code})")
    print(f"    workload: {row.workload}, weight: {row.weight}, value: {row.value}")

# 检查dim-doc-out-eval-tr维度的统计逻辑
print("\n" + "=" * 80)
print("检查dim-doc-out-eval-tr维度在哪些步骤中被处理：")
print("=" * 80)
result = db.execute(text("""
    SELECT cs.id, cs.name, cs.sort_order
    FROM calculation_steps cs
    WHERE cs.workflow_id = 31
      AND cs.code_content LIKE '%dim-doc-out-eval-tr%'
    ORDER BY cs.sort_order
"""))
rows = list(result)
print(f"找到 {len(rows)} 个步骤涉及 dim-doc-out-eval-tr")
for row in rows:
    print(f"  步骤 {row.id} (sort_order={row.sort_order}): {row.name}")

db.close()
