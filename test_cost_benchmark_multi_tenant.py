"""
测试成本基准管理API的多租户隔离和唯一性约束
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID_1 = 1  # 第一个医疗机构
HOSPITAL_ID_2 = 2  # 第二个医疗机构（如果存在）

def login():
    """登录获取访问令牌"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
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

def get_headers(token, hospital_id):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id),
        "Content-Type": "application/json"
    }

def test_multi_tenant_isolation(token):
    """测试多租户数据隔离"""
    print("\n=== 测试多租户数据隔离 ===")
    
    # 获取医院1的模型版本
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(token, HOSPITAL_ID_1),
        params={"page": 1, "size": 1}
    )
    
    if response.status_code != 200 or response.json()["total"] == 0:
        print("医院1没有可用的模型版本")
        return False
    
    version_id = response.json()["items"][0]["id"]
    version_name = response.json()["items"][0]["name"]
    
    # 在医院1创建成本基准
    data = {
        "department_code": "MULTI_TEST_001",
        "department_name": "多租户测试科室",
        "version_id": version_id,
        "version_name": version_name,
        "dimension_code": "MULTI_DIM_001",
        "dimension_name": "多租户测试维度",
        "benchmark_value": 5000.00
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=data
    )
    
    if response.status_code != 200:
        print(f"在医院1创建成本基准失败: {response.text}")
        return False
    
    benchmark_id_h1 = response.json()["id"]
    print(f"✓ 在医院1创建成本基准成功 (ID={benchmark_id_h1})")
    
    # 在医院1查询，应该能看到
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        params={"page": 1, "size": 100}
    )
    
    if response.status_code == 200:
        items = response.json()["items"]
        found = any(item["id"] == benchmark_id_h1 for item in items)
        if found:
            print("✓ 在医院1可以查询到自己的数据")
        else:
            print("✗ 在医院1查询不到自己的数据")
            return False
    else:
        print(f"查询失败: {response.text}")
        return False
    
    # 尝试在医院2查询，应该看不到医院1的数据
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_2),
        params={"page": 1, "size": 100}
    )
    
    if response.status_code == 200:
        items = response.json()["items"]
        found = any(item["id"] == benchmark_id_h1 for item in items)
        if not found:
            print("✓ 在医院2查询不到医院1的数据（数据隔离正确）")
        else:
            print("✗ 在医院2可以查询到医院1的数据（数据隔离失败！）")
            return False
    else:
        print(f"查询失败: {response.text}")
    
    # 尝试在医院2访问医院1的数据详情，应该失败
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id_h1}",
        headers=get_headers(token, HOSPITAL_ID_2)
    )
    
    if response.status_code == 404:
        print("✓ 医院2无法访问医院1的数据详情（跨租户访问控制正确）")
    else:
        print(f"✗ 医院2可以访问医院1的数据（跨租户访问控制失败！）: {response.status_code}")
        return False
    
    # 尝试在医院2删除医院1的数据，应该失败
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id_h1}",
        headers=get_headers(token, HOSPITAL_ID_2)
    )
    
    if response.status_code == 404:
        print("✓ 医院2无法删除医院1的数据（跨租户操作控制正确）")
    else:
        print(f"✗ 医院2可以删除医院1的数据（跨租户操作控制失败！）: {response.status_code}")
        return False
    
    # 清理：删除测试数据
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id_h1}",
        headers=get_headers(token, HOSPITAL_ID_1)
    )
    
    if response.status_code == 200:
        print("✓ 清理测试数据成功")
    
    return True

def test_uniqueness_constraint(token):
    """测试唯一性约束"""
    print("\n=== 测试唯一性约束 ===")
    
    # 获取模型版本
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(token, HOSPITAL_ID_1),
        params={"page": 1, "size": 1}
    )
    
    if response.status_code != 200 or response.json()["total"] == 0:
        print("没有可用的模型版本")
        return False
    
    version_id = response.json()["items"][0]["id"]
    version_name = response.json()["items"][0]["name"]
    
    # 创建第一个成本基准
    data = {
        "department_code": "UNIQUE_TEST_001",
        "department_name": "唯一性测试科室",
        "version_id": version_id,
        "version_name": version_name,
        "dimension_code": "UNIQUE_DIM_001",
        "dimension_name": "唯一性测试维度",
        "benchmark_value": 3000.00
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=data
    )
    
    if response.status_code != 200:
        print(f"创建第一个成本基准失败: {response.text}")
        return False
    
    benchmark_id = response.json()["id"]
    print(f"✓ 创建第一个成本基准成功 (ID={benchmark_id})")
    
    # 尝试创建相同的成本基准（相同科室+版本+维度），应该失败
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=data
    )
    
    if response.status_code == 400:
        print("✓ 正确拒绝了重复的成本基准（唯一性约束生效）")
    else:
        print(f"✗ 允许创建重复的成本基准（唯一性约束失败！）: {response.status_code}")
        # 清理
        requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=get_headers(token, HOSPITAL_ID_1)
        )
        return False
    
    # 创建不同维度的成本基准，应该成功
    data["dimension_code"] = "UNIQUE_DIM_002"
    data["dimension_name"] = "唯一性测试维度2"
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=data
    )
    
    if response.status_code == 200:
        benchmark_id_2 = response.json()["id"]
        print(f"✓ 创建不同维度的成本基准成功 (ID={benchmark_id_2})")
        # 清理
        requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id_2}",
            headers=get_headers(token, HOSPITAL_ID_1)
        )
    else:
        print(f"✗ 创建不同维度的成本基准失败: {response.text}")
    
    # 测试更新时的唯一性约束
    # 尝试将第一个成本基准更新为与自己相同的值，应该成功
    update_data = {
        "benchmark_value": 4000.00
    }
    
    response = requests.put(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=update_data
    )
    
    if response.status_code == 200:
        print("✓ 更新成本基准值成功")
    else:
        print(f"✗ 更新成本基准值失败: {response.text}")
    
    # 清理测试数据
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=get_headers(token, HOSPITAL_ID_1)
    )
    
    if response.status_code == 200:
        print("✓ 清理测试数据成功")
    
    return True

def test_foreign_key_validation(token):
    """测试外键验证"""
    print("\n=== 测试外键验证 ===")
    
    # 尝试创建一个引用不存在的模型版本的成本基准
    data = {
        "department_code": "FK_TEST_001",
        "department_name": "外键测试科室",
        "version_id": 999999,  # 不存在的版本ID
        "version_name": "不存在的版本",
        "dimension_code": "FK_DIM_001",
        "dimension_name": "外键测试维度",
        "benchmark_value": 2000.00
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token, HOSPITAL_ID_1),
        json=data
    )
    
    if response.status_code == 404:
        print("✓ 正确拒绝了引用不存在版本的请求（外键验证生效）")
        return True
    else:
        print(f"✗ 允许创建引用不存在版本的成本基准（外键验证失败！）: {response.status_code}")
        return False

def main():
    """主测试函数"""
    print("开始测试成本基准管理API的多租户隔离和约束")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("登录失败，测试终止")
        return
    
    print(f"登录成功")
    
    # 运行测试
    try:
        test_multi_tenant_isolation(token)
        test_uniqueness_constraint(token)
        test_foreign_key_validation(token)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    main()
