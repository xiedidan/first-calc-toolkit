"""
测试分类任务管理服务和API

测试内容：
1. 创建分类任务
2. 查询任务列表
3. 查询任务详情
4. 查询任务进度
5. 查询任务日志
6. 继续处理任务
7. 删除任务
"""
import requests
import time
import json

# 配置
BASE_URL = "http://localhost:8000"
TEST_HOSPITAL_ID = 1

# 登录获取token
def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("access_token")
        print(f"✅ 登录成功，token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def get_headers(token):
    """构建请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID),
        "Content-Type": "application/json"
    }


def test_create_task(token):
    """测试创建分类任务"""
    print("\n" + "="*60)
    print("测试1: 创建分类任务")
    print("="*60)
    
    headers = get_headers(token)
    
    # 首先获取一个模型版本ID
    response = requests.get(
        f"{BASE_URL}/api/v1/model-versions",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 获取模型版本失败: {response.text}")
        return None
    
    versions = response.json().get("data", {}).get("items", [])
    if not versions:
        print("❌ 没有找到模型版本")
        return None
    
    model_version_id = versions[0]["id"]
    print(f"✅ 使用模型版本ID: {model_version_id}")
    
    # 创建任务
    task_data = {
        "task_name": f"测试分类任务_{int(time.time())}",
        "model_version_id": model_version_id,
        "charge_categories": ["检查费", "化验费"]
    }
    
    print(f"\n创建任务数据: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/classification-tasks",
        headers=headers,
        json=task_data
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        task = response.json().get("data", {})
        task_id = task.get("id")
        print(f"\n✅ 任务创建成功，任务ID: {task_id}")
        print(f"   任务名称: {task.get('task_name')}")
        print(f"   任务状态: {task.get('status')}")
        print(f"   Celery任务ID: {task.get('celery_task_id')}")
        return task_id
    else:
        print(f"\n❌ 任务创建失败: {response.text}")
        return None


def test_get_tasks(token):
    """测试查询任务列表"""
    print("\n" + "="*60)
    print("测试2: 查询任务列表")
    print("="*60)
    
    headers = get_headers(token)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-tasks?skip=0&limit=10",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json().get("data", {})
        total = data.get("total", 0)
        items = data.get("items", [])
        
        print(f"\n✅ 查询成功，共 {total} 个任务")
        
        for idx, task in enumerate(items[:5], 1):
            print(f"\n任务 {idx}:")
            print(f"  ID: {task.get('id')}")
            print(f"  名称: {task.get('task_name')}")
            print(f"  状态: {task.get('status')}")
            print(f"  进度: {task.get('processed_items')}/{task.get('total_items')}")
            if task.get('progress_percentage') is not None:
                print(f"  进度百分比: {task.get('progress_percentage'):.2f}%")
    else:
        print(f"\n❌ 查询失败: {response.text}")


def test_get_task_detail(token, task_id):
    """测试查询任务详情"""
    print("\n" + "="*60)
    print("测试3: 查询任务详情")
    print("="*60)
    
    headers = get_headers(token)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-tasks/{task_id}",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        task = response.json().get("data", {})
        print(f"\n✅ 查询成功")
        print(f"  任务ID: {task.get('id')}")
        print(f"  任务名称: {task.get('task_name')}")
        print(f"  模型版本ID: {task.get('model_version_id')}")
        print(f"  收费类别: {', '.join(task.get('charge_categories', []))}")
        print(f"  任务状态: {task.get('status')}")
        print(f"  总项目数: {task.get('total_items')}")
        print(f"  已处理: {task.get('processed_items')}")
        print(f"  失败: {task.get('failed_items')}")
        if task.get('progress_percentage') is not None:
            print(f"  进度: {task.get('progress_percentage'):.2f}%")
        print(f"  创建时间: {task.get('created_at')}")
        if task.get('started_at'):
            print(f"  开始时间: {task.get('started_at')}")
        if task.get('completed_at'):
            print(f"  完成时间: {task.get('completed_at')}")
    else:
        print(f"\n❌ 查询失败: {response.text}")


def test_get_task_progress(token, task_id):
    """测试查询任务进度"""
    print("\n" + "="*60)
    print("测试4: 查询任务进度")
    print("="*60)
    
    headers = get_headers(token)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-tasks/{task_id}/progress",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        progress = response.json().get("data", {})
        print(f"\n✅ 查询成功")
        print(f"  任务ID: {progress.get('task_id')}")
        print(f"  状态: {progress.get('status')}")
        print(f"  总项目数: {progress.get('total_items')}")
        print(f"  已处理: {progress.get('processed_items')}")
        print(f"  失败: {progress.get('failed_items')}")
        print(f"  进度: {progress.get('progress_percentage'):.2f}%")
        if progress.get('current_item'):
            print(f"  当前处理: {progress.get('current_item')}")
        if progress.get('estimated_remaining_time'):
            print(f"  预计剩余时间: {progress.get('estimated_remaining_time')} 秒")
    else:
        print(f"\n❌ 查询失败: {response.text}")


def test_get_task_logs(token, task_id):
    """测试查询任务日志"""
    print("\n" + "="*60)
    print("测试5: 查询任务日志")
    print("="*60)
    
    headers = get_headers(token)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/classification-tasks/{task_id}/logs",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        logs = response.json().get("data", {})
        print(f"\n✅ 查询成功")
        print(f"  任务ID: {logs.get('task_id')}")
        print(f"  任务名称: {logs.get('task_name')}")
        print(f"  状态: {logs.get('status')}")
        print(f"  总项目数: {logs.get('total_items')}")
        print(f"  已处理: {logs.get('processed_items')}")
        print(f"  失败: {logs.get('failed_items')}")
        if logs.get('started_at'):
            print(f"  开始时间: {logs.get('started_at')}")
        if logs.get('completed_at'):
            print(f"  完成时间: {logs.get('completed_at')}")
        if logs.get('duration'):
            print(f"  执行时长: {logs.get('duration')} 秒")
        
        failed_records = logs.get('failed_records', [])
        if failed_records:
            print(f"\n  失败记录 ({len(failed_records)} 条):")
            for idx, record in enumerate(failed_records[:5], 1):
                print(f"    {idx}. {record.get('charge_item_name')}")
                print(f"       错误: {record.get('error_message')}")
    else:
        print(f"\n❌ 查询失败: {response.text}")


def test_continue_task(token, task_id):
    """测试继续处理任务"""
    print("\n" + "="*60)
    print("测试6: 继续处理任务")
    print("="*60)
    
    headers = get_headers(token)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/classification-tasks/{task_id}/continue",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        data = response.json().get("data", {})
        print(f"\n✅ 继续处理成功")
        print(f"  新的Celery任务ID: {data.get('celery_task_id')}")
    else:
        print(f"\n❌ 继续处理失败: {response.text}")


def test_delete_task(token, task_id):
    """测试删除任务"""
    print("\n" + "="*60)
    print("测试7: 删除任务")
    print("="*60)
    
    headers = get_headers(token)
    
    # 先等待任务完成或失败
    print("\n等待任务完成...")
    for i in range(10):
        response = requests.get(
            f"{BASE_URL}/api/v1/classification-tasks/{task_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            task = response.json().get("data", {})
            status = task.get("status")
            print(f"  当前状态: {status}")
            
            if status in ["completed", "failed"]:
                break
        
        time.sleep(2)
    
    # 删除任务
    response = requests.delete(
        f"{BASE_URL}/api/v1/classification-tasks/{task_id}",
        headers=headers
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ 任务删除成功")
    else:
        print(f"\n❌ 任务删除失败: {response.text}")


def main():
    """主测试流程"""
    print("="*60)
    print("分类任务管理服务和API测试")
    print("="*60)
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    # 测试1: 创建任务
    task_id = test_create_task(token)
    if not task_id:
        print("\n❌ 创建任务失败，后续测试跳过")
        return
    
    # 等待一下让任务开始处理
    print("\n等待3秒让任务开始处理...")
    time.sleep(3)
    
    # 测试2: 查询任务列表
    test_get_tasks(token)
    
    # 测试3: 查询任务详情
    test_get_task_detail(token, task_id)
    
    # 测试4: 查询任务进度
    test_get_task_progress(token, task_id)
    
    # 测试5: 查询任务日志
    test_get_task_logs(token, task_id)
    
    # 测试6: 继续处理任务（如果任务失败或暂停）
    # test_continue_task(token, task_id)
    
    # 测试7: 删除任务
    # test_delete_task(token, task_id)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
