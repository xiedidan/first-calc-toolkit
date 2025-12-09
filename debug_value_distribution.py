"""
调试价值分布数据查询
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

# 获取分析报告
print("=" * 60)
print("1. 查询分析报告")
print("=" * 60)

reports = db.execute(text("""
    SELECT ar.id, ar.hospital_id, ar.department_id, ar.period, 
           d.his_code, d.his_name, d.accounting_unit_name
    FROM analysis_reports ar
    JOIN departments d ON ar.department_id = d.id
    ORDER BY ar.id
""")).fetchall()

for r in reports:
    print(f"报告ID: {r[0]}, 医院ID: {r[1]}, 科室ID: {r[2]}, 年月: {r[3]}")
    print(f"  科室代码: {r[4]}, 科室名称: {r[5]}, 核算单元: {r[6]}")

if not reports:
    print("没有找到分析报告")
    db.close()
    exit()

# 取第二个报告进行分析（科室ID 4 有数据）
report = reports[1] if len(reports) > 1 else reports[0]
hospital_id = report[1]
department_id = report[2]
period = report[3]

print(f"\n使用报告: ID={report[0]}, 科室ID={department_id}, 年月={period}")

# 查找激活的模型版本
print("\n" + "=" * 60)
print("2. 查询激活的模型版本")
print("=" * 60)

versions = db.execute(text("""
    SELECT id, name, is_active, hospital_id
    FROM model_versions
    WHERE hospital_id = :hospital_id AND is_active = true
"""), {"hospital_id": hospital_id}).fetchall()

for v in versions:
    print(f"版本ID: {v[0]}, 名称: {v[1]}, 激活: {v[2]}, 医院ID: {v[3]}")

if not versions:
    print(f"没有找到医院 {hospital_id} 的激活模型版本")
    
    # 查看所有版本
    all_versions = db.execute(text("""
        SELECT id, name, is_active, hospital_id
        FROM model_versions
        WHERE hospital_id = :hospital_id
    """), {"hospital_id": hospital_id}).fetchall()
    
    print(f"\n该医院的所有版本:")
    for v in all_versions:
        print(f"  版本ID: {v[0]}, 名称: {v[1]}, 激活: {v[2]}")
    
    db.close()
    exit()

version_id = versions[0][0]

# 查找计算任务
print("\n" + "=" * 60)
print("3. 查询计算任务")
print("=" * 60)

tasks = db.execute(text("""
    SELECT task_id, model_version_id, period, status, completed_at
    FROM calculation_tasks
    WHERE model_version_id = :version_id AND period = :period
    ORDER BY completed_at DESC NULLS LAST
"""), {"version_id": version_id, "period": period}).fetchall()

for t in tasks:
    print(f"任务ID: {t[0][:20]}..., 版本ID: {t[1]}, 年月: {t[2]}, 状态: {t[3]}, 完成时间: {t[4]}")

if not tasks:
    print(f"没有找到版本 {version_id} 年月 {period} 的计算任务")
    
    # 查看该版本的所有任务
    all_tasks = db.execute(text("""
        SELECT task_id, period, status, completed_at
        FROM calculation_tasks
        WHERE model_version_id = :version_id
        ORDER BY created_at DESC
        LIMIT 10
    """), {"version_id": version_id}).fetchall()
    
    print(f"\n该版本的最近任务:")
    for t in all_tasks:
        print(f"  任务ID: {t[0][:20]}..., 年月: {t[1]}, 状态: {t[2]}")
    
    db.close()
    exit()

# 取第一个完成的任务
completed_tasks = [t for t in tasks if t[3] == 'completed']
if not completed_tasks:
    print("没有找到已完成的任务")
    db.close()
    exit()

task_id = completed_tasks[0][0]
print(f"\n使用任务: {task_id}")

# 查询计算结果
print("\n" + "=" * 60)
print("4. 查询计算结果")
print("=" * 60)

results = db.execute(text("""
    SELECT node_id, node_name, node_code, node_type, value, parent_id
    FROM calculation_results
    WHERE task_id = :task_id AND department_id = :department_id
    ORDER BY value DESC NULLS LAST
    LIMIT 20
"""), {"task_id": task_id, "department_id": department_id}).fetchall()

print(f"科室 {department_id} 的计算结果 (前20条):")
for r in results:
    print(f"  节点ID: {r[0]}, 名称: {r[1]}, 编码: {r[2]}, 类型: {r[3]}, 价值: {r[4]}, 父ID: {r[5]}")

if not results:
    print("没有找到该科室的计算结果")
    
    # 查看该任务有哪些科室的数据
    depts = db.execute(text("""
        SELECT DISTINCT department_id, COUNT(*) as cnt
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY department_id
        ORDER BY department_id
    """), {"task_id": task_id}).fetchall()
    
    print(f"\n该任务包含的科室:")
    for d in depts:
        print(f"  科室ID: {d[0]}, 记录数: {d[1]}")

# 查询维度类型的结果
print("\n" + "=" * 60)
print("5. 查询维度类型的结果")
print("=" * 60)

dim_results = db.execute(text("""
    SELECT node_id, node_name, node_code, value, parent_id
    FROM calculation_results
    WHERE task_id = :task_id 
    AND department_id = :department_id
    AND node_type = 'dimension'
    ORDER BY value DESC NULLS LAST
    LIMIT 20
"""), {"task_id": task_id, "department_id": department_id}).fetchall()

print(f"维度类型结果 (前20条):")
for r in dim_results:
    print(f"  节点ID: {r[0]}, 名称: {r[1]}, 编码: {r[2]}, 价值: {r[3]}, 父ID: {r[4]}")

db.close()
print("\n调试完成")
