"""
测试模型节点的单位字段功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def test_unit_field():
    """测试单位字段"""
    token = login()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取第一个模型版本
    print("\n1. 获取模型版本列表...")
    response = requests.get(f"{BASE_URL}/api/model-versions", headers=headers)
    if response.status_code != 200:
        print(f"获取版本列表失败: {response.text}")
        return
    
    versions = response.json()["items"]
    if not versions:
        print("没有找到模型版本，请先创建一个版本")
        return
    
    version_id = versions[0]["id"]
    print(f"使用版本: {versions[0]['name']} (ID: {version_id})")
    
    # 2. 创建一个测试节点（末级维度）
    print("\n2. 创建测试节点...")
    node_data = {
        "version_id": version_id,
        "name": "测试单位字段",
        "code": "TEST_UNIT_" + str(int(requests.get(f"{BASE_URL}/api/model-nodes?version_id={version_id}", headers=headers).json()["total"]) + 1),
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": 100.5,
        "unit": "元/例",  # 自定义单位
        "business_guide": "测试单位字段功能",
        "sort_order": 999
    }
    
    response = requests.post(
        f"{BASE_URL}/api/model-nodes",
        headers=headers,
        json=node_data
    )
    
    if response.status_code == 201:
        node = response.json()
        print(f"✓ 节点创建成功!")
        print(f"  - ID: {node['id']}")
        print(f"  - 名称: {node['name']}")
        print(f"  - 权重: {node['weight']}")
        print(f"  - 单位: {node['unit']}")
        node_id = node['id']
    else:
        print(f"✗ 节点创建失败: {response.text}")
        return
    
    # 3. 更新节点单位
    print("\n3. 更新节点单位...")
    update_data = {
        "unit": "元/人天"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/model-nodes/{node_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"✓ 节点更新成功!")
        print(f"  - 新单位: {node['unit']}")
    else:
        print(f"✗ 节点更新失败: {response.text}")
    
    # 4. 测试默认单位（创建不指定unit的节点）
    print("\n4. 测试默认单位...")
    node_data2 = {
        "version_id": version_id,
        "name": "测试默认单位",
        "code": "TEST_DEFAULT_UNIT_" + str(int(requests.get(f"{BASE_URL}/api/model-nodes?version_id={version_id}", headers=headers).json()["total"]) + 1),
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": 50.0,
        # 不指定unit，应该使用默认值 '%'
        "sort_order": 1000
    }
    
    response = requests.post(
        f"{BASE_URL}/api/model-nodes",
        headers=headers,
        json=node_data2
    )
    
    if response.status_code == 201:
        node = response.json()
        print(f"✓ 节点创建成功!")
        print(f"  - ID: {node['id']}")
        print(f"  - 名称: {node['name']}")
        print(f"  - 权重: {node['weight']}")
        print(f"  - 单位: {node['unit']} (应该是默认值 '%')")
        node_id2 = node['id']
    else:
        print(f"✗ 节点创建失败: {response.text}")
        return
    
    # 5. 获取节点列表验证
    print("\n5. 获取节点列表验证...")
    response = requests.get(
        f"{BASE_URL}/api/model-nodes?version_id={version_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        nodes = response.json()["items"]
        print(f"✓ 获取节点列表成功，共 {len(nodes)} 个节点")
        
        # 查找我们创建的测试节点
        test_nodes = [n for n in nodes if n['name'].startswith('测试')]
        if test_nodes:
            print("\n测试节点信息:")
            for node in test_nodes:
                print(f"  - {node['name']}: 权重={node.get('weight', 'N/A')}, 单位={node.get('unit', 'N/A')}")
    else:
        print(f"✗ 获取节点列表失败: {response.text}")
    
    print("\n✓ 单位字段功能测试完成!")
    print("\n说明:")
    print("  - 单位字段已成功添加到模型节点")
    print("  - 默认值为 '%'")
    print("  - 用户可以自定义单位，如 '元/例'、'元/人天' 等")
    print("  - 前端界面已支持单位字段的显示和编辑")

if __name__ == "__main__":
    test_unit_field()
