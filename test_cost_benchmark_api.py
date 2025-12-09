"""
测试成本基准管理API
"""
import requests
import json
from decimal import Decimal

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试医疗机构ID

# 登录获取token
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

# 获取headers
def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }

def test_create_cost_benchmark(token):
    """测试创建成本基准"""
    print("\n=== 测试创建成本基准 ===")
    
    # 首先获取一个模型版本ID
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(token),
        params={"page": 1, "size": 1}
    )
    
    if response.status_code != 200:
        print(f"获取模型版本失败: {response.text}")
        return None
    
    versions = response.json()
    if versions["total"] == 0:
        print("没有可用的模型版本")
        return None
    
    version_id = versions["items"][0]["id"]
    version_name = versions["items"][0]["name"]
    print(f"使用模型版本: {version_name} (ID: {version_id})")
    
    # 创建成本基准
    data = {
        "department_code": "TEST_DEPT_001",
        "department_name": "测试科室001",
        "version_id": version_id,
        "version_name": version_name,
        "dimension_code": "TEST_DIM_001",
        "dimension_name": "测试维度001",
        "benchmark_value": 1000.50
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"创建成功: ID={result['id']}")
        return result["id"]
    else:
        print(f"创建失败: {response.status_code}")
        print(response.text)
        return None

def test_get_cost_benchmarks(token):
    """测试获取成本基准列表"""
    print("\n=== 测试获取成本基准列表 ===")
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        params={"page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"获取成功: 总数={result['total']}, 当前页={len(result['items'])}条")
        if result["items"]:
            print(f"第一条: {result['items'][0]['department_name']} - {result['items'][0]['dimension_name']}")
        return True
    else:
        print(f"获取失败: {response.status_code}")
        print(response.text)
        return False

def test_get_cost_benchmark_detail(token, benchmark_id):
    """测试获取成本基准详情"""
    print(f"\n=== 测试获取成本基准详情 (ID={benchmark_id}) ===")
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"获取成功: {result['department_name']} - {result['dimension_name']}")
        print(f"基准值: {result['benchmark_value']}")
        return True
    else:
        print(f"获取失败: {response.status_code}")
        print(response.text)
        return False

def test_update_cost_benchmark(token, benchmark_id):
    """测试更新成本基准"""
    print(f"\n=== 测试更新成本基准 (ID={benchmark_id}) ===")
    
    data = {
        "benchmark_value": 2000.75
    }
    
    response = requests.put(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=get_headers(token),
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"更新成功: 新基准值={result['benchmark_value']}")
        return True
    else:
        print(f"更新失败: {response.status_code}")
        print(response.text)
        return False

def test_search_cost_benchmarks(token):
    """测试搜索成本基准"""
    print("\n=== 测试搜索成本基准 ===")
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        params={"keyword": "测试", "page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"搜索成功: 找到{result['total']}条记录")
        return True
    else:
        print(f"搜索失败: {response.status_code}")
        print(response.text)
        return False

def test_filter_cost_benchmarks(token):
    """测试筛选成本基准"""
    print("\n=== 测试筛选成本基准 ===")
    
    # 获取一个版本ID用于筛选
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(token),
        params={"page": 1, "size": 1}
    )
    
    if response.status_code != 200:
        print("获取模型版本失败")
        return False
    
    versions = response.json()
    if versions["total"] == 0:
        print("没有可用的模型版本")
        return False
    
    version_id = versions["items"][0]["id"]
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        params={"version_id": version_id, "page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"筛选成功: 找到{result['total']}条记录")
        return True
    else:
        print(f"筛选失败: {response.status_code}")
        print(response.text)
        return False

def test_delete_cost_benchmark(token, benchmark_id):
    """测试删除成本基准"""
    print(f"\n=== 测试删除成本基准 (ID={benchmark_id}) ===")
    
    response = requests.delete(
        f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"删除成功: {result['message']}")
        return True
    else:
        print(f"删除失败: {response.status_code}")
        print(response.text)
        return False

def test_export_cost_benchmarks(token):
    """测试导出成本基准"""
    print("\n=== 测试导出成本基准 ===")
    
    response = requests.get(
        f"{BASE_URL}/cost-benchmarks/export",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        print(f"导出成功: 文件大小={len(response.content)}字节")
        # 保存文件
        with open("test_cost_benchmarks_export.xlsx", "wb") as f:
            f.write(response.content)
        print("文件已保存为: test_cost_benchmarks_export.xlsx")
        return True
    elif response.status_code == 400:
        print("没有可导出的数据（这是正常的）")
        return True
    else:
        print(f"导出失败: {response.status_code}")
        print(response.text)
        return False

def test_validation_errors(token):
    """测试数据验证"""
    print("\n=== 测试数据验证 ===")
    
    # 获取一个模型版本ID
    response = requests.get(
        f"{BASE_URL}/model-versions",
        headers=get_headers(token),
        params={"page": 1, "size": 1}
    )
    
    if response.status_code != 200:
        print("获取模型版本失败")
        return False
    
    versions = response.json()
    if versions["total"] == 0:
        print("没有可用的模型版本")
        return False
    
    version_id = versions["items"][0]["id"]
    version_name = versions["items"][0]["name"]
    
    # 测试1: 基准值为0（应该失败）
    print("\n测试1: 基准值为0")
    data = {
        "department_code": "TEST_DEPT_002",
        "department_name": "测试科室002",
        "version_id": version_id,
        "version_name": version_name,
        "dimension_code": "TEST_DIM_002",
        "dimension_name": "测试维度002",
        "benchmark_value": 0
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        json=data
    )
    
    if response.status_code in [400, 422]:
        print("✓ 正确拒绝了基准值为0的请求")
    else:
        print(f"✗ 应该拒绝但返回了: {response.status_code}")
    
    # 测试2: 基准值为负数（应该失败）
    print("\n测试2: 基准值为负数")
    data["benchmark_value"] = -100
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        json=data
    )
    
    if response.status_code in [400, 422]:
        print("✓ 正确拒绝了基准值为负数的请求")
    else:
        print(f"✗ 应该拒绝但返回了: {response.status_code}")
    
    # 测试3: 缺少必填字段（应该失败）
    print("\n测试3: 缺少必填字段")
    incomplete_data = {
        "department_code": "TEST_DEPT_003",
        "version_id": version_id
        # 缺少其他必填字段
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=get_headers(token),
        json=incomplete_data
    )
    
    if response.status_code in [400, 422]:
        print("✓ 正确拒绝了缺少必填字段的请求")
    else:
        print(f"✗ 应该拒绝但返回了: {response.status_code}")
    
    return True

def main():
    """主测试函数"""
    print("开始测试成本基准管理API")
    print("=" * 50)
    
    # 登录
    token = login()
    if not token:
        print("登录失败，测试终止")
        return
    
    print(f"登录成功，Token: {token[:20]}...")
    
    # 运行测试
    benchmark_id = None
    
    try:
        # 测试创建
        benchmark_id = test_create_cost_benchmark(token)
        
        # 测试列表查询
        test_get_cost_benchmarks(token)
        
        # 测试详情查询
        if benchmark_id:
            test_get_cost_benchmark_detail(token, benchmark_id)
        
        # 测试更新
        if benchmark_id:
            test_update_cost_benchmark(token, benchmark_id)
        
        # 测试搜索
        test_search_cost_benchmarks(token)
        
        # 测试筛选
        test_filter_cost_benchmarks(token)
        
        # 测试导出
        test_export_cost_benchmarks(token)
        
        # 测试数据验证
        test_validation_errors(token)
        
        # 测试删除
        if benchmark_id:
            test_delete_cost_benchmark(token, benchmark_id)
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main()
