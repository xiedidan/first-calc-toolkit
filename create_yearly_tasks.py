"""
批量创建12个月份的计算任务（2024-11 到 2025-11）
"""
import requests
import time
import sys

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 医疗机构ID

# 登录获取token
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
    """获取激活的模型版本"""
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        versions = data.get("items", []) if isinstance(data, dict) else data
        print(f"  找到 {len(versions)} 个版本")
        for v in versions:
            print(f"    版本 {v.get('id')}: {v.get('name')}, is_active={v.get('is_active')}")
            if v.get("is_active"):
                return v["id"]
    else:
        print(f"  获取版本失败: {response.status_code} - {response.text}")
    print("未找到激活的模型版本")
    return None

def get_workflow_id(headers, version_id):
    """获取该版本的计算流程ID"""
    response = requests.get(
        f"{BASE_URL}/calculation-workflows",
        headers=headers,
        params={"version_id": version_id}
    )
    if response.status_code == 200:
        data = response.json()
        workflows = data.get("items", []) if isinstance(data, dict) else data
        print(f"  找到 {len(workflows)} 个流程")
        if workflows:
            for w in workflows:
                print(f"    流程 {w.get('id')}: {w.get('name')}")
            return workflows[0]["id"]
    else:
        print(f"  获取流程失败: {response.status_code} - {response.text}")
    print("未找到计算流程")
    return None

def create_task(headers, version_id, workflow_id, period):
    """创建计算任务"""
    response = requests.post(
        f"{BASE_URL}/calculation/tasks",
        headers=headers,
        json={
            "model_version_id": version_id,
            "workflow_id": workflow_id,
            "period": period,
            "description": f"{period} 月度计算任务"
        },
        timeout=120  # Redis较慢，增加超时
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"创建任务失败 ({period}): {response.status_code} - {response.text}")
        return None

def check_task_status(headers, task_id):
    """检查任务状态"""
    response = requests.get(
        f"{BASE_URL}/calculation/tasks/{task_id}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return None

def wait_for_task(headers, task_id, timeout=600):
    """等待任务完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        task = check_task_status(headers, task_id)
        if task:
            status = task.get("status")
            progress = task.get("progress", 0)
            print(f"  状态: {status}, 进度: {progress}%")
            
            if status == "completed":
                return True
            elif status == "failed":
                print(f"  任务失败: {task.get('error_message')}")
                return False
        
        time.sleep(5)
    
    print("  任务超时")
    return False

def main():
    # 生成月份列表：2024-11 到 2025-11
    periods = []
    for year in [2024, 2025]:
        for month in range(1, 13):
            period = f"{year}-{month:02d}"
            if period >= "2024-11" and period <= "2025-11":
                periods.append(period)
    
    print(f"将创建以下月份的计算任务: {periods}")
    print(f"共 {len(periods)} 个任务\n")
    
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
        sys.exit(1)
    print(f"激活版本ID: {version_id}\n")
    
    # 获取计算流程
    print("获取计算流程...")
    workflow_id = get_workflow_id(headers, version_id)
    if not workflow_id:
        sys.exit(1)
    print(f"计算流程ID: {workflow_id}\n")
    
    # 逐一创建任务
    results = []
    for i, period in enumerate(periods, 1):
        print(f"[{i}/{len(periods)}] 创建 {period} 的计算任务...")
        
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
