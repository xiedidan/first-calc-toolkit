"""
测试修复后的业务导向调整步骤
"""
import requests
import time

BASE_URL = "http://localhost:8000"
HOSPITAL_ID = 1

headers = {
    "X-Hospital-ID": str(HOSPITAL_ID)
}

print("=" * 80)
print("测试修复后的业务导向调整步骤")
print("=" * 80)

# 1. 创建新的计算任务
print("\n1. 创建计算任务...")
create_data = {
    "workflow_id": 26,  # 标准计算流程-含业务导向_从业务明细开始
    "version_id": 12,   # 2025年迭代版-宁波眼科
    "year_month": "2025-10",
    "description": "测试修复后的导向调整"
}

response = requests.post(
    f"{BASE_URL}/api/v1/calculation-tasks",
    json=create_data,
    headers=headers
)

if response.status_code != 200:
    print(f"✗ 创建任务失败: {response.status_code}")
    print(response.text)
    exit(1)

task = response.json()
task_id = task["task_id"]
print(f"✓ 任务已创建: {task_id}")

# 2. 等待任务完成
print("\n2. 等待任务执行...")
max_wait = 120
waited = 0

while waited < max_wait:
    response = requests.get(
        f"{BASE_URL}/api/v1/calculation-tasks/{task_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 查询任务失败: {response.status_code}")
        break
    
    task = response.json()
    status = task["status"]
    
    print(f"  状态: {status}", end="\r")
    
    if status == "completed":
        print(f"\n✓ 任务完成")
        break
    elif status == "failed":
        print(f"\n✗ 任务失败")
        print(f"  错误: {task.get('error_message', 'Unknown')}")
        exit(1)
    
    time.sleep(2)
    waited += 2

if waited >= max_wait:
    print(f"\n✗ 任务超时")
    exit(1)

# 3. 检查业务导向调整步骤的执行结果
print("\n3. 检查业务导向调整步骤...")
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 检查步骤日志
    result = conn.execute(text("""
        SELECT cs.name, csl.status, csl.execution_info
        FROM calculation_step_logs csl
        JOIN calculation_steps cs ON csl.step_id = cs.id
        WHERE csl.task_id = :task_id
        AND cs.name = '业务导向调整'
    """), {"task_id": task_id})
    
    log = result.fetchone()
    if log:
        print(f"  步骤: {log.name}")
        print(f"  状态: {log.status}")
        print(f"  信息: {log.execution_info}")
    else:
        print("  ✗ 未找到步骤日志")
    
    # 检查orientation_adjustment_details表
    result = conn.execute(text("""
        SELECT COUNT(*) as count
        FROM orientation_adjustment_details
        WHERE task_id = :task_id
    """), {"task_id": task_id})
    
    count = result.fetchone().count
    print(f"\n4. 业务导向过程表记录数: {count}")
    
    if count > 0:
        # 显示一些示例数据
        result = conn.execute(text("""
            SELECT 
                oad.department_code,
                d.name as dept_name,
                mn.name as node_name,
                oad.orientation_ratio,
                oad.adjustment_intensity,
                oad.original_weight,
                oad.adjusted_weight
            FROM orientation_adjustment_details oad
            LEFT JOIN departments d ON oad.department_code = d.his_code AND d.hospital_id = :hospital_id
            LEFT JOIN model_nodes mn ON oad.node_id = mn.id
            WHERE oad.task_id = :task_id
            LIMIT 5
        """), {"task_id": task_id, "hospital_id": HOSPITAL_ID})
        
        print("\n示例数据:")
        print(f"{'科室':<15} {'节点':<15} {'导向比例':<10} {'管控力度':<10} {'原始权重':<10} {'调整权重':<10}")
        print("-" * 80)
        for row in result:
            print(f"{row.dept_name or row.department_code:<15} "
                  f"{row.node_name:<15} "
                  f"{float(row.orientation_ratio or 0):<10.4f} "
                  f"{float(row.adjustment_intensity or 0):<10.4f} "
                  f"{float(row.original_weight or 0):<10.4f} "
                  f"{float(row.adjusted_weight or 0):<10.4f}")

print("\n" + "=" * 80)
if count > 0:
    print("✓ 测试成功！业务导向调整步骤已正常工作")
else:
    print("✗ 测试失败：未生成业务导向过程表数据")
print("=" * 80)
