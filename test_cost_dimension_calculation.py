"""
测试成本维度计算
创建一个测试任务并执行成本维度计算步骤
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录获取token
print("登录...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": str(HOSPITAL_ID)
}

# 创建计算任务
print("\n创建计算任务...")
task_data = {
    "workflow_id": 27,  # 标准计算流程-含业务导向_从业务明细开始（版本23）
    "model_version_id": 23,  # 模型版本ID
    "period": "2025-10",
    "description": "测试成本维度计算"
}

response = requests.post(
    f"{BASE_URL}/calculation/tasks",
    headers=headers,
    json=task_data
)

if response.status_code != 200:
    print(f"✗ 创建任务失败: {response.status_code}")
    print(response.text)
    exit(1)

task = response.json()
task_id = task["task_id"]
print(f"✓ 任务已创建: {task_id}")

# 等待任务完成
print("\n等待任务执行...")
max_wait = 120  # 最多等待2分钟
waited = 0
while waited < max_wait:
    response = requests.get(
        f"{BASE_URL}/calculation/tasks/{task_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"✗ 获取任务状态失败: {response.status_code}")
        break
    
    task_status = response.json()
    status = task_status["status"]
    
    if status == "completed":
        print(f"✓ 任务执行完成")
        print(f"  总步骤数: {task_status.get('total_steps', 0)}")
        print(f"  完成步骤数: {task_status.get('completed_steps', 0)}")
        break
    elif status == "failed":
        print(f"✗ 任务执行失败")
        print(f"  错误信息: {task_status.get('error_message', 'Unknown error')}")
        break
    elif status in ["pending", "running"]:
        print(f"  状态: {status}, 已等待 {waited}秒...")
        time.sleep(5)
        waited += 5
    else:
        print(f"  未知状态: {status}")
        break

# 检查成本维度计算结果
print("\n检查成本维度计算结果...")
import psycopg2

conn = psycopg2.connect(
    host="47.108.227.254",
    port=50016,
    user="root",
    password="root",
    database="hospital_value"
)

cursor = conn.cursor()

# 查询成本维度的计算结果
cursor.execute("""
    SELECT 
        d.his_name as dept_name,
        cr.node_name,
        cr.workload,
        cr.weight,
        cr.value
    FROM calculation_results cr
    JOIN departments d ON cr.department_id = d.id
    WHERE cr.task_id = %s
      AND cr.node_name IN ('人员经费', '其他费用')
    ORDER BY d.his_name, cr.node_name
    LIMIT 10
""", (task_id,))

results = cursor.fetchall()

if results:
    print(f"✓ 找到 {len(results)} 条成本维度计算结果")
    print(f"\n{'科室':<20} {'维度':<15} {'工作量':<12} {'权重':<10} {'价值':<15}")
    print("-" * 80)
    for row in results:
        dept_name, node_name, workload, weight, value = row
        workload_val = float(workload) if workload else 0
        weight_val = float(weight) if weight else 0
        value_val = float(value) if value else 0
        print(f"{dept_name:<20} {node_name:<15} {workload_val:<12.2f} {weight_val:<10.4f} {value_val:<15.2f}")
else:
    print("⚠ 未找到成本维度计算结果")
    
    # 检查是否有cost_values数据
    cursor.execute("""
        SELECT COUNT(*) 
        FROM cost_values 
        WHERE hospital_id = %s 
          AND year_month = %s
          AND dimension_name IN ('人员经费', '其他费用')
    """, (HOSPITAL_ID, task_data["period"]))
    
    cost_count = cursor.fetchone()[0]
    print(f"  cost_values表中有 {cost_count} 条相关数据")

cursor.close()
conn.close()
