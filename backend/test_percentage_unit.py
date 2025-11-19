"""
测试百分比单位的处理
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

def test_percentage_unit():
    """测试百分比单位处理"""
    token = login()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取第一个模型版本
    print("\n1. 获取模型版本...")
    response = requests.get(f"{BASE_URL}/api/model-versions", headers=headers)
    if response.status_code != 200:
        print(f"获取版本列表失败: {response.text}")
        return
    
    versions = response.json()["items"]
    if not versions:
        print("没有找到模型版本，请先创建一个版本")
        return
    
    version_id = versions[0]["id"]
    print(f"✓ 使用版本: {versions[0]['name']} (ID: {version_id})")
    
    # 测试场景1: 创建百分比单位的节点
    print("\n" + "="*60)
    print("测试场景1: 创建百分比单位的节点")
    print("="*60)
    
    # 前端输入: 65.5 (表示65.5%)
    # 前端保存: 65.5 / 100 = 0.655
    frontend_input = 65.5
    backend_value = frontend_input / 100  # 0.655
    
    print(f"\n前端输入: {frontend_input} (用户看到的)")
    print(f"后端存储: {backend_value} (实际存储值)")
    
    node_data = {
        "version_id": version_id,
        "name": "门诊人次占比",
        "code": "TEST_PERCENT_1",
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": backend_value,  # 存储 0.655
        "unit": "%",
        "business_guide": "测试百分比单位",
        "sort_order": 1001
    }
    
    response = requests.post(
        f"{BASE_URL}/api/model-nodes",
        headers=headers,
        json=node_data
    )
    
    if response.status_code == 201:
        node = response.json()
        print(f"\n✓ 节点创建成功!")
        print(f"  - 后端返回的weight: {node['weight']}")
        print(f"  - 前端应显示: {node['weight'] * 100:.2f}%")
        node_id_1 = node['id']
    else:
        print(f"✗ 节点创建失败: {response.text}")
        return
    
    # 测试场景2: 创建其他单位的节点
    print("\n" + "="*60)
    print("测试场景2: 创建其他单位的节点")
    print("="*60)
    
    # 前端输入: 5000 (表示5000元/例)
    # 前端保存: 5000 (不变)
    frontend_input = 5000
    backend_value = frontend_input  # 5000
    
    print(f"\n前端输入: {frontend_input} (用户看到的)")
    print(f"后端存储: {backend_value} (实际存储值)")
    
    node_data = {
        "version_id": version_id,
        "name": "平均住院费用",
        "code": "TEST_COST_1",
        "node_type": "dimension",
        "is_leaf": True,
        "calc_type": "statistical",
        "weight": backend_value,  # 存储 5000
        "unit": "元/例",
        "business_guide": "测试其他单位",
        "sort_order": 1002
    }
    
    response = requests.post(
        f"{BASE_URL}/api/model-nodes",
        headers=headers,
        json=node_data
    )
    
    if response.status_code == 201:
        node = response.json()
        print(f"\n✓ 节点创建成功!")
        print(f"  - 后端返回的weight: {node['weight']}")
        print(f"  - 前端应显示: {node['weight']:.2f} 元/例")
        node_id_2 = node['id']
    else:
        print(f"✗ 节点创建失败: {response.text}")
        return
    
    # 测试场景3: 编辑百分比节点
    print("\n" + "="*60)
    print("测试场景3: 编辑百分比节点")
    print("="*60)
    
    # 获取节点详情
    response = requests.get(
        f"{BASE_URL}/api/model-nodes/{node_id_1}",
        headers=headers
    )
    
    if response.status_code == 200:
        node = response.json()
        print(f"\n后端返回的weight: {node['weight']}")
        print(f"前端编辑框显示: {node['weight'] * 100:.2f} (乘以100)")
        
        # 用户修改为 70.0
        frontend_input = 70.0
        backend_value = frontend_input / 100  # 0.7
        
        print(f"\n用户修改为: {frontend_input}")
        print(f"前端保存值: {backend_value} (除以100)")
        
        update_data = {
            "weight": backend_value
        }
        
        response = requests.put(
            f"{BASE_URL}/api/model-nodes/{node_id_1}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            node = response.json()
            print(f"\n✓ 节点更新成功!")
            print(f"  - 后端返回的weight: {node['weight']}")
            print(f"  - 前端应显示: {node['weight'] * 100:.2f}%")
        else:
            print(f"✗ 节点更新失败: {response.text}")
    else:
        print(f"✗ 获取节点失败: {response.text}")
    
    # 测试场景4: 验证数据对照表
    print("\n" + "="*60)
    print("测试场景4: 数据对照表验证")
    print("="*60)
    
    test_cases = [
        {"name": "手术成功率", "code": "TEST_PERCENT_2", "input": 98.5, "unit": "%"},
        {"name": "人均药品费用", "code": "TEST_COST_2", "input": 150.5, "unit": "元/人天"},
        {"name": "平均住院天数", "code": "TEST_DAYS_1", "input": 7.5, "unit": "天"},
    ]
    
    print("\n创建测试节点...")
    for i, case in enumerate(test_cases):
        # 根据单位决定存储值
        backend_value = case["input"] / 100 if case["unit"] == "%" else case["input"]
        
        node_data = {
            "version_id": version_id,
            "name": case["name"],
            "code": case["code"],
            "node_type": "dimension",
            "is_leaf": True,
            "calc_type": "statistical",
            "weight": backend_value,
            "unit": case["unit"],
            "sort_order": 1003 + i
        }
        
        response = requests.post(
            f"{BASE_URL}/api/model-nodes",
            headers=headers,
            json=node_data
        )
        
        if response.status_code == 201:
            node = response.json()
            display_value = node['weight'] * 100 if case["unit"] == "%" else node['weight']
            print(f"✓ {case['name']}: 输入={case['input']}, 存储={node['weight']}, 显示={display_value:.2f} {case['unit']}")
        else:
            print(f"✗ {case['name']}: 创建失败")
    
    # 获取节点列表验证
    print("\n" + "="*60)
    print("最终验证: 获取节点列表")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/model-nodes?version_id={version_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        nodes = response.json()["items"]
        test_nodes = [n for n in nodes if n['code'].startswith('TEST_')]
        
        if test_nodes:
            print("\n测试节点数据对照:")
            print(f"{'节点名称':<15} {'单位':<10} {'后端存储':<12} {'前端显示':<12}")
            print("-" * 60)
            for node in test_nodes:
                if node.get('weight') is not None:
                    unit = node.get('unit', '%')
                    backend_val = node['weight']
                    display_val = backend_val * 100 if unit == '%' else backend_val
                    print(f"{node['name']:<15} {unit:<10} {backend_val:<12.4f} {display_val:<12.2f}")
    
    print("\n" + "="*60)
    print("✓ 百分比单位处理测试完成!")
    print("="*60)
    print("\n总结:")
    print("  1. 百分比单位: 后端存储小数值，前端显示时乘以100")
    print("  2. 其他单位: 后端和前端使用相同的值")
    print("  3. 编辑时: 百分比需要转换，其他单位不变")
    print("  4. 所有值显示时保留2位小数")

if __name__ == "__main__":
    test_percentage_unit()
