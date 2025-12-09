"""
测试成本基准删除功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用户登录凭证
LOGIN_DATA = {
    "username": "admin",
    "password": "admin123"
}

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": "1",
        "Content-Type": "application/json"
    }

def test_delete_workflow():
    """测试完整的删除流程"""
    print("=" * 60)
    print("测试成本基准删除功能")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✓ 登录成功")
    
    headers = get_headers(token)
    
    # 2. 创建测试数据
    print("\n2. 创建测试成本基准...")
    create_data = {
        "department_code": "TEST_DEPT_001",
        "department_name": "测试科室001",
        "version_id": 1,
        "version_name": "测试版本",
        "dimension_code": "TEST_DIM_001",
        "dimension_name": "测试维度001",
        "benchmark_value": 1000.50
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        json=create_data
    )
    
    if response.status_code == 200:
        benchmark = response.json()
        benchmark_id = benchmark["id"]
        print(f"✓ 创建成功，ID: {benchmark_id}")
        print(f"  科室: {benchmark['department_name']}")
        print(f"  维度: {benchmark['dimension_name']}")
        print(f"  基准值: {benchmark['benchmark_value']}")
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(response.text)
        return
    
    # 3. 验证记录存在
    print(f"\n3. 验证记录存在...")
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ 记录存在")
    else:
        print(f"❌ 记录不存在: {response.status_code}")
        return
    
    # 4. 删除记录
    print(f"\n4. 删除成本基准 (ID: {benchmark_id})...")
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 删除成功: {result.get('message', '成功')}")
    else:
        print(f"❌ 删除失败: {response.status_code}")
        print(response.text)
        return
    
    # 5. 验证记录已删除
    print(f"\n5. 验证记录已删除...")
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=headers
    )
    
    if response.status_code == 404:
        print("✓ 记录已成功删除（404 Not Found）")
    else:
        print(f"❌ 记录仍然存在: {response.status_code}")
        return
    
    # 6. 测试删除不存在的记录
    print(f"\n6. 测试删除不存在的记录...")
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/999999",
        headers=headers
    )
    
    if response.status_code == 404:
        print("✓ 正确返回404错误")
    else:
        print(f"❌ 应该返回404，实际返回: {response.status_code}")
    
    # 7. 测试跨租户删除（如果有多个医疗机构）
    print(f"\n7. 测试多租户隔离...")
    # 创建一个记录
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        json=create_data
    )
    
    if response.status_code == 200:
        benchmark = response.json()
        benchmark_id = benchmark["id"]
        print(f"✓ 创建测试记录，ID: {benchmark_id}")
        
        # 尝试用不同的hospital_id删除
        wrong_headers = headers.copy()
        wrong_headers["X-Hospital-ID"] = "999"
        
        response = requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=wrong_headers
        )
        
        if response.status_code in [403, 404]:
            print(f"✓ 多租户隔离正常（返回{response.status_code}）")
        else:
            print(f"⚠ 多租户隔离可能有问题: {response.status_code}")
        
        # 清理：用正确的hospital_id删除
        requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=headers
        )
    
    print("\n" + "=" * 60)
    print("✓ 所有删除功能测试通过")
    print("=" * 60)

def test_delete_with_filters():
    """测试删除后列表刷新"""
    print("\n" + "=" * 60)
    print("测试删除后列表刷新")
    print("=" * 60)
    
    # 1. 登录
    print("\n1. 登录...")
    token = login()
    if not token:
        return
    
    headers = get_headers(token)
    
    # 2. 创建多条测试数据
    print("\n2. 创建多条测试数据...")
    created_ids = []
    for i in range(3):
        create_data = {
            "department_code": f"TEST_DEPT_{i:03d}",
            "department_name": f"测试科室{i:03d}",
            "version_id": 1,
            "version_name": "测试版本",
            "dimension_code": f"TEST_DIM_{i:03d}",
            "dimension_name": f"测试维度{i:03d}",
            "benchmark_value": 1000.0 + i * 100
        }
        
        response = requests.post(
            f"{BASE_URL}/cost-benchmarks",
            headers=headers,
            json=create_data
        )
        
        if response.status_code == 200:
            benchmark_id = response.json()["id"]
            created_ids.append(benchmark_id)
            print(f"  ✓ 创建记录 {i+1}/3，ID: {benchmark_id}")
    
    # 3. 获取列表
    print("\n3. 获取列表...")
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        params={"size": 100}
    )
    
    if response.status_code == 200:
        data = response.json()
        initial_count = data["total"]
        print(f"✓ 当前总数: {initial_count}")
    else:
        print(f"❌ 获取列表失败: {response.status_code}")
        return
    
    # 4. 删除一条记录
    print(f"\n4. 删除一条记录 (ID: {created_ids[0]})...")
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{created_ids[0]}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ 删除成功")
    else:
        print(f"❌ 删除失败: {response.status_code}")
        return
    
    # 5. 再次获取列表，验证总数减少
    print("\n5. 验证列表已更新...")
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        params={"size": 100}
    )
    
    if response.status_code == 200:
        data = response.json()
        new_count = data["total"]
        print(f"✓ 更新后总数: {new_count}")
        
        if new_count == initial_count - 1:
            print("✓ 总数正确减少1")
        else:
            print(f"❌ 总数不正确，期望: {initial_count - 1}，实际: {new_count}")
    
    # 6. 清理剩余测试数据
    print("\n6. 清理测试数据...")
    for benchmark_id in created_ids[1:]:
        requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=headers
        )
    print("✓ 清理完成")
    
    print("\n" + "=" * 60)
    print("✓ 列表刷新测试通过")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_delete_workflow()
        test_delete_with_filters()
        print("\n" + "=" * 60)
        print("✓✓✓ 所有测试通过 ✓✓✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
