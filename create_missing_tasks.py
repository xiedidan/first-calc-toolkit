"""
创建缺失月份的计算任务
"""
import requests
import time
import sys

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 需要创建的月份（排除已有completed任务的月份）
# 2024-12已创建，从2025-02继续
PERIODS_TO_CREATE = [
    "2025-02", "2025-03", "2025-04", "2025-05", 
    "2025-06", "2025-07", "2025-08", "2025-09"
]

def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        sys.exit(1)

def get_active_version(headers):
    response = requests.get(f"{BASE_URL}/model-versions", headers=headers)
    if response.status_code == 200:
        data = response.json()
        versions = data.get("items", []) if isinstance(data, dict) else data
        for v in versions:
            if v.get("is_active"):
                return v["id"]
    return None

def get_workflow_id(headers, version_id):
    response = requests.get(
        f"{BASE_URL}/calculation-workflows",
        headers=headers,
        params={"version_id": version_id}
    )
    if response.status_code == 200:
        data = response.json()
        workflows = data.get("items", []) if isinstance(data, dict) else data
        if workflows:
            return workflows[0]["id"]
    return None

def create_task(headers, version_id, workflow_id, period):
    response = requests.post(
        f"{BASE_URL}/calculation/tasks",
        headers=headers,
        json={
            "model_version_id": version_id,
            "workflow_id": workflow_id,
            "period": period,
            "description": f"{period} 月度计算任务"
        },
        timeout=120
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建任务失败 ({period}): {response.status_code} - {response.text}")
        return None

def check_task_status(headers, task_id):
    response = requests.get(f"{BASE_URL}/calculation/tasks/{task_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def wait_for_task(headers, task_id, timeout=600):
    start_time = time.time()
    while time.time() - start_time < timeout:
        task = check_task_status(headers, task_id)
        if task:
            status = task.get("status")
            progress = float(task.get("progress", 0))
            print(f"    状态: {status}, 进度: {progress:.1f}%")
            
            if status == "completed":
                return True
            elif status == "failed":
                print(f"    任务失败: {task.get('error_message')}")
                return False
        
        time.sleep(10)  # 每10秒检查一次
    
    print("    任务超时")
    return False

def main():
    print(f"将创建以下月份的计算任务: {PERIODS_TO_CREATE}")
    print(f"共 {len(PERIODS_TO_CREATE)} 个任务\n")
    
    # 登录
    print("正在登录...")
    token = login()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    print("登录成功\n")
    
    # 获取激活版本
    print("获取激活的模型版本...")
    version_id = get_active_version(headers)
    if not version_id:
        print("未找到激活的模型版本")
        sys.exit(1)
    print(f"激活版本ID: {version_id}\n")
    
    # 获取计算流程
    print("获取计算流程...")
    workflow_id = get_workflow_id(headers, version_id)
    if not workflow_id:
        print("未找到计算流程")
        sys.exit(1)
    print(f"计算流程ID: {workflow_id}\n")
    
    # 逐一创建任务
    results = []
    for i, period in enumerate(PERIODS_TO_CREATE, 1):
        print(f"[{i}/{len(PERIODS_TO_CREATE)}] 创建 {period} 的计算任务...")
        
        task = create_task(headers, version_id, workflow_id, period)
        if task:
            task_id = task.get("task_id")
            print(f"  任务已创建: {task_id}")
            
            # 等待任务完成
            print("  等待任务完成...")
            success = wait_for_task(headers, task_id)
            
            results.append({
                "period": period,
                "task_id": task_id,
                "success": success
            })
            
            if success:
                print(f"  ✓ {period} 计算完成\n")
            else:
                print(f"  ✗ {period} 计算失败\n")
        else:
            results.append({
                "period": period,
                "task_id": None,
                "success": False
            })
            print(f"  ✗ {period} 创建失败\n")
    
    # 汇总结果
    print("\n" + "="*50)
    print("执行结果汇总:")
    print("="*50)
    
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    
    print(f"成功: {success_count}, 失败: {fail_count}")
    print()
    
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['period']}: {r['task_id'] or '创建失败'}")

if __name__ == "__main__":
    main()
