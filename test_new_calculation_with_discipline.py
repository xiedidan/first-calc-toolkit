"""
创建新的计算任务来验证学科规则是否生效
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录获取 token
def get_token():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    print(f"登录失败: {resp.status_code} - {resp.text}")
    return None

token = get_token()
if not token:
    print("无法获取 token，退出")
    exit(1)

headers = {
    "X-Hospital-ID": str(HOSPITAL_ID),
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# 创建计算任务
print("创建计算任务...")
resp = requests.post(
    f"{BASE_URL}/calculation/tasks",
    json={
        "model_version_id": 32,
        "workflow_id": 37,
        "period": "2025-10",
        "description": "测试学科规则应用"
    },
    headers=headers
)

if resp.status_code != 200:
    print(f"创建任务失败: {resp.status_code} - {resp.text}")
    exit(1)

task = resp.json()
task_id = task["task_id"]
print(f"任务已创建: {task_id}")

# 等待任务完成
print("等待任务完成...")
max_wait = 300  # 最多等待5分钟
waited = 0
while waited < max_wait:
    resp = requests.get(
        f"{BASE_URL}/calculation/tasks/{task_id}",
        headers=headers
    )
    if resp.status_code == 200:
        task = resp.json()
        status = task["status"]
        print(f"  状态: {status}, 进度: {task.get('progress', 0)}%")
        
        if status == "completed":
            print("任务完成!")
            break
        elif status == "failed":
            print(f"任务失败: {task.get('error_message', '未知错误')}")
            exit(1)
    
    time.sleep(5)
    waited += 5

if waited >= max_wait:
    print("等待超时")
    exit(1)

# 检查学科规则是否生效
print("\n检查学科规则是否生效...")
print("白内障专科(YS01) - 住院乙级手术(dim-doc-sur-in-3) - 系数0.5")

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# 查询新任务的结果
result = session.execute(text("""
    SELECT cr.value, cr.node_name, cr.node_code
    FROM calculation_results cr
    WHERE cr.task_id = :task_id
      AND cr.department_id = 4
      AND cr.node_code = 'dim-doc-sur-in-3'
"""), {"task_id": task_id})

row = result.fetchone()
if row:
    print(f"  新任务结果: {row[1]} ({row[2]}) = {row[0]}")
else:
    print("  未找到结果")

# 对比旧任务的结果
result = session.execute(text("""
    SELECT cr.value, cr.node_name, cr.node_code
    FROM calculation_results cr
    WHERE cr.task_id = '65990c6a-538b-4944-8afd-eb56e3a58c2a'
      AND cr.department_id = 4
      AND cr.node_code = 'dim-doc-sur-in-3'
"""))

row = result.fetchone()
if row:
    print(f"  旧任务结果: {row[1]} ({row[2]}) = {row[0]}")

session.close()
print(f"\n新任务ID: {task_id}")
