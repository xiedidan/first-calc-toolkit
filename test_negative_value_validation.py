"""
测试负值验证
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests

# API配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "X-Hospital-ID": "1"
}

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        HEADERS["Authorization"] = f"Bearer {token}"
        print("✓ 登录成功")
        return True
    else:
        print(f"❌ 登录失败: {response.text}")
        return False

def test_negative_value():
    """测试负值验证"""
    print("=" * 60)
    print("测试负值验证")
    print("=" * 60)
    
    if not login():
        return
    
    # 获取模型版本
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=HEADERS,
        params={"limit": 1}
    )
    
    if response.status_code != 200:
        print(f"❌ 获取模型版本失败")
        return
    
    versions = response.json().get("items", [])
    if not versions:
        print("❌ 没有找到模型版本")
        return
    
    version = versions[0]
    
    # 创建测试成本基准
    create_data = {
        "department_code": "TEST_NEG_001",
        "department_name": "测试负值科室",
        "version_id": version["id"],
        "version_name": version["name"],
        "dimension_code": "TEST_NEG_DIM_001",
        "dimension_name": "测试负值维度",
        "benchmark_value": 1000.00
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=HEADERS,
        json=create_data
    )
    
    if response.status_code != 200:
        print(f"❌ 创建失败: {response.text}")
        return
    
    benchmark = response.json()
    benchmark_id = benchmark["id"]
    print(f"✓ 创建成功，ID: {benchmark_id}")
    
    # 测试不同的负值
    test_cases = [
        {"value": -100.00, "desc": "负数"},
        {"value": 0, "desc": "零"},
        {"value": -0.01, "desc": "小负数"},
    ]
    
    for test_case in test_cases:
        print(f"\n测试 {test_case['desc']}: {test_case['value']}")
        
        update_data = {
            "benchmark_value": test_case["value"]
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.text}")
        
        if response.status_code == 422 or response.status_code == 400:
            print(f"  ✓ 验证成功（拒绝了无效值）")
        else:
            print(f"  ❌ 验证失败（应该拒绝无效值）")
    
    # 清理
    requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=HEADERS
    )
    print(f"\n✓ 测试数据已清理")

if __name__ == "__main__":
    test_negative_value()
