"""
模型管理API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的token（需要先登录获取）
TOKEN = None


def set_token(token: str):
    """设置认证token"""
    global TOKEN
    TOKEN = token


def get_headers():
    """获取请求头"""
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def login(username: str = "admin", password: str = "admin123"):
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get("data", {}).get("token")
        set_token(token)
        print(f"✅ 登录成功，token: {token[:20]}...")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None


def test_create_version():
    """测试创建模型版本"""
    print("\n=== 测试创建模型版本 ===")
    response = requests.post(
        f"{BASE_URL}/model-versions",
        headers=get_headers(),
        json={
            "version": "v1.0",
            "name": "2025年标准版",
            "description": "初始版本"
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json().get("id") if response.status_code == 201 else None


def test_get_versions():
    """测试获取模型版本列表"""
    print("\n=== 测试获取模型版本列表 ===")
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers()
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_create_node(version_id: int, parent_id: int = None):
    """测试创建模型节点"""
    print(f"\n=== 测试创建模型节点 (version_id={version_id}, parent_id={parent_id}) ===")
    
    if parent_id is None:
        # 创建根节点（序列）
        data = {
            "version_id": version_id,
            "name": "医生序列",
            "code": "DOCTOR",
            "node_type": "sequence",
            "business_guide": "医生工作量评估"
        }
    else:
        # 创建子节点（维度）
        data = {
            "version_id": version_id,
            "parent_id": parent_id,
            "name": "门诊诊察",
            "code": "OUTPATIENT",
            "node_type": "dimension",
            "calc_type": "statistical",
            "weight": 0.3000,
            "business_guide": "门诊工作量",
            "script": "SELECT department_id, COUNT(*) as count FROM outpatient_visits"
        }
    
    response = requests.post(
        f"{BASE_URL}/model-nodes",
        headers=get_headers(),
        json=data
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json().get("id") if response.status_code == 201 else None


def test_get_nodes(version_id: int):
    """测试获取模型节点列表"""
    print(f"\n=== 测试获取模型节点列表 (version_id={version_id}) ===")
    response = requests.get(
        f"{BASE_URL}/model-nodes",
        headers=get_headers(),
        params={"version_id": version_id}
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_activate_version(version_id: int):
    """测试激活模型版本"""
    print(f"\n=== 测试激活模型版本 (version_id={version_id}) ===")
    response = requests.put(
        f"{BASE_URL}/model-versions/{version_id}/activate",
        headers=get_headers()
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_copy_version(base_version_id: int):
    """测试复制模型版本"""
    print(f"\n=== 测试复制模型版本 (base_version_id={base_version_id}) ===")
    response = requests.post(
        f"{BASE_URL}/model-versions",
        headers=get_headers(),
        json={
            "version": "v1.1",
            "name": "2025年标准版-修订",
            "description": "基于v1.0的修订版本",
            "base_version_id": base_version_id
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json().get("id") if response.status_code == 201 else None


def test_test_code(node_id: int):
    """测试节点代码测试"""
    print(f"\n=== 测试节点代码测试 (node_id={node_id}) ===")
    response = requests.post(
        f"{BASE_URL}/model-nodes/{node_id}/test-code",
        headers=get_headers(),
        json={
            "script": "SELECT department_id, COUNT(*) FROM visits WHERE date >= '2025-10-01'",
            "test_params": {"current_year_month": "2025-10"}
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("模型管理API测试")
    print("=" * 60)
    
    # 1. 登录
    if not login():
        print("❌ 登录失败，无法继续测试")
        return
    
    # 2. 创建版本
    version_id = test_create_version()
    if not version_id:
        print("❌ 创建版本失败，无法继续测试")
        return
    
    # 3. 获取版本列表
    test_get_versions()
    
    # 4. 创建根节点
    root_node_id = test_create_node(version_id)
    if not root_node_id:
        print("❌ 创建根节点失败")
        return
    
    # 5. 创建子节点
    child_node_id = test_create_node(version_id, root_node_id)
    
    # 6. 获取节点列表
    test_get_nodes(version_id)
    
    # 7. 测试代码
    if child_node_id:
        test_test_code(child_node_id)
    
    # 8. 激活版本
    test_activate_version(version_id)
    
    # 9. 复制版本
    new_version_id = test_copy_version(version_id)
    if new_version_id:
        test_get_nodes(new_version_id)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
