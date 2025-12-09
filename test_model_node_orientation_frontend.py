"""
测试模型节点业务导向前端集成

验证需求：
- 6.1: 末级节点显示导向规则选择器
- 6.2: 选择导向规则后保存导向规则ID
- 6.3: 节点详情和列表显示关联的导向规则名称
- 6.5: 支持清空选择（设置为NULL）
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的医疗机构ID和认证token（需要根据实际情况调整）
HOSPITAL_ID = 1
TOKEN = None  # 需要先登录获取token

def get_headers():
    """获取请求头"""
    headers = {
        "Content-Type": "application/json",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers

def test_orientation_rule_integration():
    """测试导向规则集成"""
    print("=" * 60)
    print("测试模型节点业务导向前端集成")
    print("=" * 60)
    
    # 1. 创建测试导向规则
    print("\n1. 创建测试导向规则...")
    rule_data = {
        "name": "测试导向规则-前端集成",
        "category": "benchmark_ladder",
        "description": "用于测试前端集成的导向规则"
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        json=rule_data
    )
    
    if response.status_code == 201:
        rule = response.json()
        rule_id = rule["id"]
        print(f"✓ 导向规则创建成功，ID: {rule_id}")
    else:
        print(f"✗ 导向规则创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 2. 获取导向规则列表（模拟前端加载）
    print("\n2. 获取导向规则列表...")
    response = requests.get(
        f"{BASE_URL}/orientation-rules",
        headers=get_headers(),
        params={"limit": 1000}
    )
    
    if response.status_code == 200:
        rules = response.json()
        print(f"✓ 获取到 {rules['total']} 个导向规则")
        print(f"  包含测试规则: {any(r['id'] == rule_id for r in rules['items'])}")
    else:
        print(f"✗ 获取导向规则列表失败: {response.status_code}")
        return
    
    # 3. 获取或创建测试模型版本
    print("\n3. 获取测试模型版本...")
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(),
        params={"limit": 1}
    )
    
    if response.status_code == 200:
        versions = response.json()
        if versions["total"] > 0:
            version_id = versions["items"][0]["id"]
            print(f"✓ 使用现有版本，ID: {version_id}")
        else:
            # 创建测试版本
            version_data = {
                "version": "test-orientation-v1",
                "name": "测试导向集成版本",
                "description": "用于测试导向规则集成"
            }
            response = requests.post(
                f"{BASE_URL}/model-versions",
                headers=get_headers(),
                json=version_data
            )
            if response.status_code == 201:
                version = response.json()
                version_id = version["id"]
                print(f"✓ 创建测试版本，ID: {version_id}")
            else:
                print(f"✗ 创建版本失败: {response.status_code}")
                return
    else:
        print(f"✗ 获取版本列表失败: {response.status_code}")
        return
    
    # 4. 创建末级节点并关联导向规则
    print("\n4. 创建末级节点并关联导向规则...")
    node_data = {
        "version_id": version_id,
        "name": "测试末级节点",
        "code": "TEST_LEAF_NODE",
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": 0.5,
        "unit": "%",
        "orientation_rule_id": rule_id
    }
    
    response = requests.post(
        f"{BASE_URL}/model-nodes",
        headers=get_headers(),
        json=node_data
    )
    
    if response.status_code == 201:
        node = response.json()
        node_id = node["id"]
        print(f"✓ 节点创建成功，ID: {node_id}")
        print(f"  关联导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  导向规则名称: {node.get('orientation_rule_name')}")
    else:
        print(f"✗ 节点创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 5. 获取节点详情，验证导向规则名称显示
    print("\n5. 获取节点详情...")
    response = requests.get(
        f"{BASE_URL}/model-nodes/{node_id}",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点详情获取成功")
        print(f"  节点名称: {node['name']}")
        print(f"  导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  导向规则名称: {node.get('orientation_rule_name')}")
        
        # 验证导向规则名称是否正确
        if node.get('orientation_rule_name') == rule_data['name']:
            print("  ✓ 导向规则名称显示正确")
        else:
            print(f"  ✗ 导向规则名称不匹配，期望: {rule_data['name']}, 实际: {node.get('orientation_rule_name')}")
    else:
        print(f"✗ 获取节点详情失败: {response.status_code}")
        return
    
    # 6. 获取节点列表，验证导向规则名称显示
    print("\n6. 获取节点列表...")
    response = requests.get(
        f"{BASE_URL}/model-nodes",
        headers=get_headers(),
        params={"version_id": version_id}
    )
    
    if response.status_code == 200:
        nodes = response.json()
        print(f"✓ 节点列表获取成功，共 {nodes['total']} 个节点")
        
        # 查找我们创建的节点
        test_node = next((n for n in nodes['items'] if n['id'] == node_id), None)
        if test_node:
            print(f"  找到测试节点")
            print(f"  导向规则名称: {test_node.get('orientation_rule_name')}")
            if test_node.get('orientation_rule_name') == rule_data['name']:
                print("  ✓ 列表中导向规则名称显示正确")
            else:
                print(f"  ✗ 列表中导向规则名称不匹配")
        else:
            print("  ✗ 未找到测试节点")
    else:
        print(f"✗ 获取节点列表失败: {response.status_code}")
        return
    
    # 7. 更新节点，清空导向规则（测试支持NULL）
    print("\n7. 清空导向规则...")
    update_data = {
        "orientation_rule_id": None
    }
    
    response = requests.put(
        f"{BASE_URL}/model-nodes/{node_id}",
        headers=get_headers(),
        json=update_data
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点更新成功")
        print(f"  导向规则ID: {node.get('orientation_rule_id')}")
        print(f"  导向规则名称: {node.get('orientation_rule_name')}")
        
        if node.get('orientation_rule_id') is None:
            print("  ✓ 导向规则已成功清空")
        else:
            print("  ✗ 导向规则未清空")
    else:
        print(f"✗ 节点更新失败: {response.status_code}")
        print(response.text)
        return
    
    # 8. 清理测试数据
    print("\n8. 清理测试数据...")
    
    # 删除节点
    response = requests.delete(
        f"{BASE_URL}/model-nodes/{node_id}",
        headers=get_headers()
    )
    if response.status_code == 204:
        print("✓ 测试节点已删除")
    else:
        print(f"✗ 删除节点失败: {response.status_code}")
    
    # 删除导向规则
    response = requests.delete(
        f"{BASE_URL}/orientation-rules/{rule_id}",
        headers=get_headers()
    )
    if response.status_code == 204:
        print("✓ 测试导向规则已删除")
    else:
        print(f"✗ 删除导向规则失败: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_orientation_rule_integration()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
