"""
调试白内障专科（报告ID 3）的数据问题
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

# 1. 检查分析报告
print("=" * 60)
print("1. 分析报告详情")
print("=" * 60)

reports = db.execute(text("""
    SELECT ar.id, ar.hospital_id, ar.department_id, ar.period, 
           d.id as dept_id, d.his_code, d.his_name, d.accounting_unit_name, d.accounting_unit_code
    FROM analysis_reports ar
    JOIN departments d ON ar.department_id = d.id
    ORDER BY ar.id
""")).fetchall()

for r in reports:
    print(f"报告ID: {r[0]}")
    print(f"  医院ID: {r[1]}, 科室ID: {r[2]}, 年月: {r[3]}")
    print(f"  科室表ID: {r[4]}, HIS代码: {r[5]}, HIS名称: {r[6]}")
    print(f"  核算单元名称: {r[7]}, 核算单元代码: {r[8]}")
    print()

# 2. 检查计算结果中的科室
print("=" * 60)
print("2. 计算结果中的科室分布")
print("=" * 60)

task_id = '7c5c88d1-6a71-4ae3-824b-e04c8012b6ae'

dept_results = db.execute(text("""
    SELECT cr.department_id, d.his_code, d.his_name, d.accounting_unit_name, COUNT(*) as cnt
    FROM calculation_results cr
    LEFT JOIN departments d ON cr.department_id = d.id
    WHERE cr.task_id = :task_id
    GROUP BY cr.department_id, d.his_code, d.his_name, d.accounting_unit_name
    ORDER BY cr.department_id
"""), {"task_id": task_id}).fetchall()

print(f"任务 {task_id[:20]}... 的科室分布:")
for r in dept_results:
    print(f"  科室ID: {r[0]}, HIS代码: {r[1]}, HIS名称: {r[2]}, 核算单元: {r[3]}, 记录数: {r[4]}")

# 3. 检查白内障专科的数据
print("\n" + "=" * 60)
print("3. 白内障专科相关科室")
print("=" * 60)

bnz_depts = db.execute(text("""
    SELECT id, his_code, his_name, accounting_unit_name, accounting_unit_code
    FROM departments
    WHERE his_name LIKE '%白内障%' OR accounting_unit_name LIKE '%白内障%'
    ORDER BY id
""")).fetchall()

for d in bnz_depts:
    print(f"科室ID: {d[0]}, HIS代码: {d[1]}, HIS名称: {d[2]}, 核算单元: {d[3]}, 核算代码: {d[4]}")

# 4. 检查科室ID 4 的计算结果
print("\n" + "=" * 60)
print("4. 科室ID 4 的计算结果")
print("=" * 60)

results_4 = db.execute(text("""
    SELECT node_id, node_name, node_code, node_type, value
    FROM calculation_results
    WHERE task_id = :task_id AND department_id = 4
    ORDER BY value DESC NULLS LAST
"""), {"task_id": task_id}).fetchall()

print(f"科室ID 4 的计算结果 ({len(results_4)} 条):")
for r in results_4:
    print(f"  节点ID: {r[0]}, 名称: {r[1]}, 编码: {r[2]}, 类型: {r[3]}, 价值: {r[4]}")

# 5. 检查科室ID 3 的计算结果
print("\n" + "=" * 60)
print("5. 科室ID 3 的计算结果")
print("=" * 60)

results_3 = db.execute(text("""
    SELECT node_id, node_name, node_code, node_type, value
    FROM calculation_results
    WHERE task_id = :task_id AND department_id = 3
    ORDER BY value DESC NULLS LAST
"""), {"task_id": task_id}).fetchall()

print(f"科室ID 3 的计算结果 ({len(results_3)} 条):")
for r in results_3:
    print(f"  节点ID: {r[0]}, 名称: {r[1]}, 编码: {r[2]}, 类型: {r[3]}, 价值: {r[4]}")

if not results_3:
    print("  没有数据！")

db.close()
print("\n调试完成")
