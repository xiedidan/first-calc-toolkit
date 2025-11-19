"""
计算流程管理API测试
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用户凭证
USERNAME = "admin"
PASSWORD = "admin123"

# 全局变量存储token和ID
token = None
workflow_id = None
step_id = None


def login():
    """登录获取token"""
    global token
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    print(f"登录: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token: {token[:20]}...")
        return True
    else:
        print(f"登录失败: {response.text}")
        return False


def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def test_create_workflow():
    """测试创建计算流程"""
    global workflow_id
    print("\n=== 测试创建计算流程 ===")
    
    data = {
        "version_id": 1,
        "name": "测试计算流程",
        "description": "这是一个测试用的计算流程",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/calculation-workflows",
        headers=get_headers(),
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        workflow_id = response.json()["id"]
        print(f"创建成功，流程ID: {workflow_id}")
        return True
    return False


def test_get_workflows():
    """测试获取计算流程列表"""
    print("\n=== 测试获取计算流程列表 ===")
    
    response = requests.get(
        f"{BASE_URL}/calculation-workflows",
        headers=get_headers(),
        params={"version_id": 1}
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_get_workflow_detail():
    """测试获取计算流程详情"""
    print("\n=== 测试获取计算流程详情 ===")
    
    response = requests.get(
        f"{BASE_URL}/calculation-workflows/{workflow_id}",
        headers=get_headers()
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_update_workflow():
    """测试更新计算流程"""
    print("\n=== 测试更新计算流程 ===")
    
    data = {
        "name": "测试计算流程（已更新）",
        "description": "更新后的描述"
    }
    
    response = requests.put(
        f"{BASE_URL}/calculation-workflows/{workflow_id}",
        headers=get_headers(),
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_create_step():
    """测试创建计算步骤"""
    global step_id
    print("\n=== 测试创建计算步骤 ===")
    
    data = {
        "workflow_id": workflow_id,
        "name": "测试步骤1",
        "description": "这是第一个测试步骤",
        "code_type": "sql",
        "code_content": "SELECT * FROM departments WHERE id = {department_id}",
        "is_enabled": True
    }
    
    response = requests.post(
        f"{BASE_URL}/calculation-steps",
        headers=get_headers(),
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        step_id = response.json()["id"]
        print(f"创建成功，步骤ID: {step_id}")
        return True
    return False


def test_create_more_steps():
    """测试创建更多步骤"""
    print("\n=== 测试创建更多步骤 ===")
    
    steps = [
        {
            "workflow_id": workflow_id,
            "name": "测试步骤2",
            "description": "这是第二个测试步骤",
            "code_type": "python",
            "code_content": "print('Hello from step 2')",
            "is_enabled": True
        },
        {
            "workflow_id": workflow_id,
            "name": "测试步骤3",
            "description": "这是第三个测试步骤",
            "code_type": "sql",
            "code_content": "SELECT COUNT(*) FROM model_nodes",
            "is_enabled": True
        }
    ]
    
    for step_data in steps:
        response = requests.post(
            f"{BASE_URL}/calculation-steps",
            headers=get_headers(),
            json=step_data
        )
        print(f"创建步骤 '{step_data['name']}': {response.status_code}")
    
    return True


def test_get_steps():
    """测试获取计算步骤列表"""
    print("\n=== 测试获取计算步骤列表 ===")
    
    response = requests.get(
        f"{BASE_URL}/calculation-steps",
        headers=get_headers(),
        params={"workflow_id": workflow_id}
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_move_step():
    """测试移动步骤"""
    print("\n=== 测试移动步骤 ===")
    
    # 下移
    response = requests.post(
        f"{BASE_URL}/calculation-steps/{step_id}/move-down",
        headers=get_headers()
    )
    print(f"下移步骤: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 上移
    response = requests.post(
        f"{BASE_URL}/calculation-steps/{step_id}/move-up",
        headers=get_headers()
    )
    print(f"上移步骤: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return True


def test_test_code():
    """测试代码测试功能"""
    print("\n=== 测试代码测试功能 ===")
    
    data = {
        "test_params": {
            "department_id": 1,
            "current_year_month": "2025-10"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/calculation-steps/{step_id}/test",
        headers=get_headers(),
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_copy_workflow():
    """测试复制计算流程"""
    print("\n=== 测试复制计算流程 ===")
    
    data = {
        "name": "测试计算流程（副本）",
        "description": "这是复制的流程"
    }
    
    response = requests.post(
        f"{BASE_URL}/calculation-workflows/{workflow_id}/copy",
        headers=get_headers(),
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200


def test_delete_step():
    """测试删除计算步骤"""
    print("\n=== 测试删除计算步骤 ===")
    
    response = requests.delete(
        f"{BASE_URL}/calculation-steps/{step_id}",
        headers=get_headers()
    )
    
    print(f"状态码: {response.status_code}")
    return response.status_code == 204


def test_delete_workflow():
    """测试删除计算流程"""
    print("\n=== 测试删除计算流程 ===")
    
    response = requests.delete(
        f"{BASE_URL}/calculation-workflows/{workflow_id}",
        headers=get_headers()
    )
    
    print(f"状态码: {response.status_code}")
    return response.status_code == 204


def main():
    """主测试流程"""
    print("=" * 60)
    print("计算流程管理API测试")
    print("=" * 60)
    
    # 登录
    if not login():
        print("登录失败，测试终止")
        return
    
    # 执行测试
    tests = [
        ("创建计算流程", test_create_workflow),
        ("获取计算流程列表", test_get_workflows),
        ("获取计算流程详情", test_get_workflow_detail),
        ("更新计算流程", test_update_workflow),
        ("创建计算步骤", test_create_step),
        ("创建更多步骤", test_create_more_steps),
        ("获取计算步骤列表", test_get_steps),
        ("移动步骤", test_move_step),
        ("测试代码", test_test_code),
        ("复制计算流程", test_copy_workflow),
        # ("删除计算步骤", test_delete_step),
        # ("删除计算流程", test_delete_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✓" if result else "✗"))
        except Exception as e:
            print(f"测试出错: {e}")
            results.append((test_name, "✗"))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, result in results:
        print(f"{result} {test_name}")
    
    print("\n提示: 如需清理测试数据，请取消注释删除测试")


if __name__ == "__main__":
    main()
