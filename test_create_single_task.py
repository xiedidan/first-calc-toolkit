"""
测试创建单个计算任务
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录
print("登录...")
resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
print(f"登录响应: {resp.status_code}")
token = resp.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": str(HOSPITAL_ID)
}

# 获取版本
print("\n获取版本...")
resp = requests.get(f"{BASE_URL}/model-versions", headers=headers)
print(f"版本响应: {resp.status_code}")
versions = resp.json().get("items", [])
version_id = None
for v in versions:
    if v.get("is_active"):
        version_id = v["id"]
        print(f"激活版本: {v['id']} - {v['name']}")
        break

# 获取流程
print("\n获取流程...")
resp = requests.get(f"{BASE_URL}/calculation-workflows", headers=headers, params={"version_id": version_id})
print(f"流程响应: {resp.status_code}")
workflows = resp.json().get("items", [])
workflow_id = workflows[0]["id"] if workflows else None
print(f"流程ID: {workflow_id}")

# 创建任务
print("\n创建任务 (2024-11)...")
try:
    resp = requests.post(
        f"{BASE_URL}/calculation/tasks",
        headers=headers,
        json={
            "model_version_id": version_id,
            "workflow_id": workflow_id,
            "period": "2024-11"
        },
        timeout=120  # 120秒超时（Redis较慢）
    )
    print(f"创建响应: {resp.status_code}")
    print(f"响应内容: {resp.text[:500]}")

    if resp.status_code == 200:
        task = resp.json()
        print(f"\n任务创建成功: {task.get('task_id')}")
except requests.exceptions.Timeout:
    print("请求超时 - 可能是Celery未运行或连接Redis失败")
except Exception as e:
    print(f"请求异常: {e}")
