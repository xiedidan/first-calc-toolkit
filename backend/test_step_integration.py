"""测试步骤与数据源集成"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取 token
def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

# 获取数据源列表
def get_data_sources(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/data-sources", headers=headers, params={"page": 1, "size": 10})
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print(f"获取数据源失败: {response.text}")
        return []

# 获取计算流程列表
def get_workflows(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/calculation-workflows", headers=headers, params={"page": 1, "size": 10})
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print(f"获取计算流程失败: {response.text}")
        return []

# 创建测试步骤
def create_test_step(token, workflow_id, data_source_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "workflow_id": workflow_id,
        "name": "测试SQL步骤",
        "description": "测试数据源集成",
        "code_type": "sql",
        "code_content": "SELECT 1 as test_col, 'hello' as message",
        "data_source_id": data_source_id,
        "is_enabled": True
    }
    response = requests.post(f"{BASE_URL}/calculation-steps", headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"创建步骤失败: {response.text}")
        return None

# 测试步骤
def test_step(token, step_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/calculation-steps/{step_id}/test", headers=headers, json={})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"测试步骤失败: {response.text}")
        return None

def main():
    print("=" * 60)
    print("测试步骤与数据源集成")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录...")
    token = login()
    if not token:
        return
    print("✓ 登录成功")
    
    # 2. 获取数据源
    print("\n2. 获取数据源列表...")
    data_sources = get_data_sources(token)
    if not data_sources:
        print("✗ 没有可用的数据源，请先创建数据源")
        return
    print(f"✓ 找到 {len(data_sources)} 个数据源")
    for ds in data_sources:
        print(f"  - ID: {ds['id']}, 名称: {ds['name']}, 类型: {ds['db_type']}")
    
    # 3. 获取计算流程
    print("\n3. 获取计算流程列表...")
    workflows = get_workflows(token)
    if not workflows:
        print("✗ 没有可用的计算流程，请先创建计算流程")
        return
    print(f"✓ 找到 {len(workflows)} 个计算流程")
    for wf in workflows:
        print(f"  - ID: {wf['id']}, 名称: {wf['name']}")
    
    # 4. 创建测试步骤
    print("\n4. 创建测试SQL步骤...")
    workflow_id = workflows[0]['id']
    data_source_id = data_sources[0]['id']
    step = create_test_step(token, workflow_id, data_source_id)
    if not step:
        return
    print(f"✓ 创建成功，步骤ID: {step['id']}")
    print(f"  - 名称: {step['name']}")
    print(f"  - 代码类型: {step['code_type']}")
    print(f"  - 数据源: {step.get('data_source_name', 'N/A')}")
    
    # 5. 测试步骤
    print("\n5. 测试SQL步骤...")
    result = test_step(token, step['id'])
    if result:
        print(f"✓ 测试完成")
        print(f"  - 成功: {result['success']}")
        print(f"  - 执行时间: {result.get('duration_ms', 0)}ms")
        if result['success']:
            print(f"  - 结果: {json.dumps(result.get('result', {}), indent=2, ensure_ascii=False)}")
        else:
            print(f"  - 错误: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
