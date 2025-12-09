"""
测试模型节点与导向规则关联功能
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 测试用的认证token（需要先登录获取）
def get_auth_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

def test_model_node_orientation_integration():
    """测试模型节点与导向规则的集成"""
    
    # 获取token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": "1"
    }
    
    print("\n=== 测试模型节点与导向规则关联功能 ===\n")
    
    # 1. 创建一个导向规则
    print("1. 创建导向规则...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    orientation_rule_data = {
        "name": f"测试导向规则-模型节点集成-{timestamp}",
        "category": "benchmark_ladder",
        "description": "用于测试模型节点关联的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers,
        json=orientation_rule_data
    )
    
    if response.status_code in [200, 201]:
        orientation_rule = response.json()
        orientation_rule_id = orientation_rule["id"]
        print(f"✓ 导向规则创建成功，ID: {orientation_rule_id}")
        print(f"  名称: {orientation_rule['name']}")
    else:
        print(f"✗ 导向规则创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 2. 获取一个模型版本（假设ID为1）
    print("\n2. 获取模型版本...")
    response = requests.get(
        f"{BASE_URL}/api/v1/model-versions",
        headers=headers
    )
    
    if response.status_code == 200:
        versions = response.json()["items"]
        if not versions:
            print("✗ 没有可用的模型版本")
            return
        version_id = versions[0]["id"]
        print(f"✓ 使用模型版本 ID: {version_id}")
    else:
        print(f"✗ 获取模型版本失败: {response.status_code}")
        return
    
    # 3. 创建一个末级节点并关联导向规则
    print("\n3. 创建末级节点并关联导向规则...")
    node_data = {
        "version_id": version_id,
        "name": f"测试末级节点-{timestamp}",
        "code": f"TEST_LEAF_NODE_{timestamp}",
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": 1.0,
        "unit": "%",
        "orientation_rule_id": orientation_rule_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/model-nodes",
        headers=headers,
        json=node_data
    )
    
    if response.status_code == 201:
        node = response.json()
        node_id = node["id"]
        print(f"✓ 末级节点创建成功，ID: {node_id}")
        print(f"  名称: {node['name']}")
        print(f"  关联导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  关联导向规则名称: {node.get('orientation_rule_name')}")
    else:
        print(f"✗ 末级节点创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 4. 获取节点详情，验证导向规则名称是否正确预加载
    print("\n4. 获取节点详情...")
    response = requests.get(
        f"{BASE_URL}/api/v1/model-nodes/{node_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点详情获取成功")
        print(f"  关联导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  关联导向规则名称: {node.get('orientation_rule_name')}")
        
        if node.get('orientation_rule_name') == orientation_rule_data['name']:
            print("  ✓ 导向规则名称预加载正确")
        else:
            print(f"  ✗ 导向规则名称预加载错误，期望: {orientation_rule_data['name']}, 实际: {node.get('orientation_rule_name')}")
    else:
        print(f"✗ 获取节点详情失败: {response.status_code}")
    
    # 5. 更新节点的导向规则
    print("\n5. 创建另一个导向规则并更新节点关联...")
    orientation_rule_data_2 = {
        "name": f"测试导向规则2-模型节点集成-{timestamp}",
        "category": "direct_ladder",
        "description": "用于测试更新模型节点关联的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        headers=headers,
        json=orientation_rule_data_2
    )
    
    if response.status_code in [200, 201]:
        orientation_rule_2 = response.json()
        orientation_rule_id_2 = orientation_rule_2["id"]
        print(f"✓ 第二个导向规则创建成功，ID: {orientation_rule_id_2}")
    else:
        print(f"✗ 第二个导向规则创建失败: {response.status_code}")
        return
    
    # 更新节点关联
    response = requests.put(
        f"{BASE_URL}/api/v1/model-nodes/{node_id}",
        headers=headers,
        json={"orientation_rule_id": orientation_rule_id_2}
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点关联更新成功")
        print(f"  新的导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  新的导向规则名称: {node.get('orientation_rule_name')}")
        
        if node.get('orientation_rule_name') == orientation_rule_data_2['name']:
            print("  ✓ 导向规则名称更新正确")
        else:
            print(f"  ✗ 导向规则名称更新错误")
    else:
        print(f"✗ 节点关联更新失败: {response.status_code}")
        print(response.text)
    
    # 6. 清空节点的导向规则关联
    print("\n6. 清空节点的导向规则关联...")
    response = requests.put(
        f"{BASE_URL}/api/v1/model-nodes/{node_id}",
        headers=headers,
        json={"orientation_rule_id": None}
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点关联清空成功")
        print(f"  导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  导向规则名称: {node.get('orientation_rule_name')}")
    else:
        print(f"✗ 节点关联清空失败: {response.status_code}")
    
    # 7. 测试非末级节点不能关联导向规则
    print("\n7. 测试非末级节点不能关联导向规则...")
    non_leaf_node_data = {
        "version_id": version_id,
        "name": f"测试非末级节点-{timestamp}",
        "code": f"TEST_NON_LEAF_NODE_{timestamp}",
        "node_type": "sequence",
        "is_leaf": False,
        "orientation_rule_id": orientation_rule_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/model-nodes",
        headers=headers,
        json=non_leaf_node_data
    )
    
    if response.status_code == 400:
        print(f"✓ 正确拒绝非末级节点关联导向规则")
        print(f"  错误信息: {response.json().get('detail')}")
    else:
        print(f"✗ 应该拒绝非末级节点关联导向规则，但返回: {response.status_code}")
    
    # 8. 获取节点列表，验证导向规则名称是否正确预加载
    print("\n8. 获取节点列表...")
    response = requests.get(
        f"{BASE_URL}/api/v1/model-nodes?version_id={version_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        nodes = response.json()["items"]
        print(f"✓ 节点列表获取成功，共 {len(nodes)} 个节点")
        
        # 查找我们创建的节点
        test_node = None
        for n in nodes:
            if n["id"] == node_id:
                test_node = n
                break
        
        if test_node:
            print(f"  找到测试节点: {test_node['name']}")
            print(f"  导向规则名称: {test_node.get('orientation_rule_name')}")
        else:
            print(f"  未找到测试节点")
    else:
        print(f"✗ 获取节点列表失败: {response.status_code}")
    
    # 清理：删除测试数据
    print("\n9. 清理测试数据...")
    
    # 删除节点
    response = requests.delete(
        f"{BASE_URL}/api/v1/model-nodes/{node_id}",
        headers=headers
    )
    if response.status_code == 204:
        print(f"✓ 测试节点删除成功")
    else:
        print(f"✗ 测试节点删除失败: {response.status_code}")
    
    # 删除导向规则
    for rule_id in [orientation_rule_id, orientation_rule_id_2]:
        response = requests.delete(
            f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
            headers=headers
        )
        if response.status_code == 204:
            print(f"✓ 导向规则 {rule_id} 删除成功")
        else:
            print(f"✗ 导向规则 {rule_id} 删除失败: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_model_node_orientation_integration()
