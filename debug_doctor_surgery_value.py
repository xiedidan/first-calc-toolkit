"""
调试白内障专科医生诊断-治疗手术的金额问题
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

# 1. 查找最近的计算任务
print("=" * 80)
print("最近的计算任务：")
print("=" * 80)
result = db.execute(text("""
    SELECT ct.task_id, ct.period, ct.status, ct.created_at
    FROM calculation_tasks ct
    JOIN model_versions mv ON mv.id = ct.model_version_id
    WHERE mv.hospital_id = 1
    ORDER BY ct.created_at DESC
    LIMIT 3
"""))
tasks = list(result)
for row in tasks:
    print(f"  {row.task_id} | {row.period} | {row.status} | {row.created_at}")

if not tasks:
    print("没有找到计算任务")
    db.close()
    exit()

task_id = tasks[0].task_id
period = tasks[0].period
print(f"\n使用任务: {task_id}, 周期: {period}")

# 2. 查找白内障专科的科室信息
print("\n" + "=" * 80)
print("白内障专科的科室信息：")
print("=" * 80)
result = db.execute(text("""
    SELECT id, his_code, his_name, accounting_unit_code, accounting_unit_name
    FROM departments
    WHERE hospital_id = 1 AND (his_name LIKE '%白内障%' OR accounting_unit_name LIKE '%白内障%')
"""))
depts = list(result)
dept_ids = []
for row in depts:
    print(f"  ID: {row.id}, HIS: {row.his_code} ({row.his_name}), 核算单元: {row.accounting_unit_code} ({row.accounting_unit_name})")
    dept_ids.append(row.id)

# 使用白内障专科的 department_id (ID=4 是 YS01 白内障专科)
dept_id = 4

# 3. 查找医生诊断-治疗手术维度的节点信息
print("\n" + "=" * 80)
print("医生序列下的治疗手术维度节点：")
print("=" * 80)
result = db.execute(text("""
    WITH RECURSIVE node_path AS (
        SELECT id, code, name, node_type, parent_id, 
               CAST(name AS TEXT) as path
        FROM model_nodes
        WHERE parent_id IS NULL 
          AND version_id = (SELECT id FROM model_versions WHERE hospital_id = 1 AND is_active = true LIMIT 1)
        UNION ALL
        SELECT mn.id, mn.code, mn.name, mn.node_type, mn.parent_id,
               np.path || ' > ' || mn.name
        FROM model_nodes mn
        JOIN node_path np ON mn.parent_id = np.id
    )
    SELECT id, code, name, node_type, path
    FROM node_path
    WHERE name LIKE '%治疗手术%'
    ORDER BY path
"""))
nodes = list(result)
for row in nodes:
    print(f"  ID: {row.id}, Code: {row.code}")
    print(f"    路径: {row.path}")
    print()

# 4. 查看计算结果中白内障专科的医生诊断-治疗手术数据
print("\n" + "=" * 80)
print("计算结果 - 白内障专科(ID=4)的治疗手术相关维度：")
print("=" * 80)
result = db.execute(text("""
    SELECT cr.node_id, cr.node_code, cr.node_name, cr.node_type, 
           cr.department_id, d.his_name, d.accounting_unit_name,
           cr.workload, cr.weight, cr.value
    FROM calculation_results cr
    JOIN departments d ON d.id = cr.department_id
    WHERE cr.task_id = :task_id
      AND cr.department_id = :dept_id
      AND cr.node_name LIKE '%治疗手术%'
    ORDER BY cr.node_name
"""), {"task_id": task_id, "dept_id": dept_id})
results = list(result)
print(f"找到 {len(results)} 条记录")
for row in results:
    print(f"  节点: {row.node_name} ({row.node_code})")
    print(f"    科室: {row.department_id} ({row.his_name} / {row.accounting_unit_name})")
    print(f"    工作量: {row.workload}, 权重: {row.weight}, 价值: {row.value}")
    print()

# 5. 查看所有科室的医生诊断-治疗手术数据对比
print("\n" + "=" * 80)
print("所有科室的医生诊断-治疗手术数据对比：")
print("=" * 80)
result = db.execute(text("""
    SELECT cr.department_id, d.his_name, d.accounting_unit_name,
           cr.node_name, cr.workload, cr.weight, cr.value
    FROM calculation_results cr
    JOIN departments d ON d.id = cr.department_id
    WHERE cr.task_id = :task_id
      AND cr.node_name = '治疗手术'
      AND cr.node_code LIKE 'dim-doc%'
    ORDER BY cr.value DESC
    LIMIT 20
"""), {"task_id": task_id})
for row in result:
    print(f"  {row.accounting_unit_name or row.his_name}: 工作量={row.workload}, 权重={row.weight}, 价值={row.value}")

# 6. 查看原始收费明细中白内障专科的治疗手术数据
print("\n" + "=" * 80)
print("收费明细 - 白内障专科的治疗手术相关数据：")
print("=" * 80)

# 先找到治疗手术维度的节点ID
result = db.execute(text("""
    SELECT id, code, name FROM model_nodes 
    WHERE name = '治疗手术' 
      AND code LIKE 'dim-doc%'
      AND version_id = (SELECT id FROM model_versions WHERE hospital_id = 1 AND is_active = true LIMIT 1)
"""))
surgery_nodes = list(result)
print(f"治疗手术维度节点: {[(n.id, n.code, n.name) for n in surgery_nodes]}")

if surgery_nodes:
    node_ids = [n.id for n in surgery_nodes]
    result = db.execute(text("""
        SELECT 
            cd.prescribing_dept_code,
            cd.prescribing_dept_name,
            cd.executing_dept_code,
            cd.executing_dept_name,
            COUNT(*) as cnt,
            SUM(cd.amount) as total_amount
        FROM charge_details cd
        JOIN dimension_mappings dm ON dm.charge_item_code = cd.charge_item_code
        WHERE cd.hospital_id = 1
          AND cd.year_month = :period
          AND dm.node_id = ANY(:node_ids)
          AND (cd.prescribing_dept_code IN ('YS01', '134') OR cd.executing_dept_code IN ('YS01', '134'))
        GROUP BY cd.prescribing_dept_code, cd.prescribing_dept_name, 
                 cd.executing_dept_code, cd.executing_dept_name
        ORDER BY total_amount DESC
    """), {"period": period, "node_ids": node_ids})
    rows = list(result)
    print(f"\n找到 {len(rows)} 条分组记录")
    for row in rows:
        print(f"  开单: {row.prescribing_dept_code} ({row.prescribing_dept_name})")
        print(f"  执行: {row.executing_dept_code} ({row.executing_dept_name})")
        print(f"  数量: {row.cnt}, 金额: {row.total_amount}")
        print()

# 7. 检查维度映射中治疗手术的映射情况
print("\n" + "=" * 80)
print("维度映射 - 治疗手术相关的映射数量：")
print("=" * 80)
result = db.execute(text("""
    SELECT mn.name as dimension_name, mn.code as dimension_code,
           COUNT(dm.id) as mapping_count
    FROM model_nodes mn
    LEFT JOIN dimension_mappings dm ON dm.node_id = mn.id
    WHERE mn.name = '治疗手术'
      AND mn.version_id = (SELECT id FROM model_versions WHERE hospital_id = 1 AND is_active = true LIMIT 1)
    GROUP BY mn.id, mn.name, mn.code
    ORDER BY mn.code
"""))
for row in result:
    print(f"  {row.dimension_name} ({row.dimension_code}): {row.mapping_count} 个映射")

# 8. 检查执行维度的数据对比
print("\n" + "=" * 80)
print("对比：白内障专科的执行维度数据：")
print("=" * 80)
result = db.execute(text("""
    SELECT cr.node_name, cr.node_code, cr.workload, cr.weight, cr.value
    FROM calculation_results cr
    WHERE cr.task_id = :task_id
      AND cr.department_id = :dept_id
      AND cr.node_name LIKE '%执行%'
    ORDER BY cr.value DESC
    LIMIT 10
"""), {"task_id": task_id, "dept_id": dept_id})
for row in result:
    print(f"  {row.node_name} ({row.node_code}): 工作量={row.workload}, 权重={row.weight}, 价值={row.value}")

db.close()
