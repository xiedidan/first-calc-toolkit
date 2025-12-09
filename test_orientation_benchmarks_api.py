"""
测试导向基准API
"""
import requests
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8000"
HOSPITAL_ID = 1

# 登录获取token
def login():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None

# 获取headers
def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }

def test_benchmark_crud():
    """测试导向基准CRUD操作"""
    token = login()
    if not token:
        return
    
    headers = get_headers(token)
    
    # 1. 首先创建一个"基准阶梯"类别的导向规则
    print("\n=== 1. 创建基准阶梯类别的导向规则 ===")
    rule_data = {
        "name": f"测试基准导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "用于测试基准API的导向规则"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        json=rule_data,
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        rule = response.json()
        rule_id = rule["id"]
        print(f"创建成功，导向规则ID: {rule_id}")
        print(f"导向名称: {rule['name']}")
        print(f"导向类别: {rule['category']}")
    else:
        print(f"创建失败: {response.text}")
        return
    
    # 2. 创建导向基准
    print("\n=== 2. 创建导向基准 ===")
    stat_start = datetime.now() - timedelta(days=365)
    stat_end = datetime.now()
    benchmark_data = {
        "rule_id": rule_id,
        "department_code": "001",
        "department_name": "内科",
        "benchmark_type": "average",
        "control_intensity": 1.2345,
        "stat_start_date": stat_start.isoformat(),
        "stat_end_date": stat_end.isoformat(),
        "benchmark_value": 98765.4321
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        json=benchmark_data,
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        benchmark = response.json()
        benchmark_id = benchmark["id"]
        print(f"创建成功，基准ID: {benchmark_id}")
        print(f"科室: {benchmark['department_name']} ({benchmark['department_code']})")
        print(f"基准类别: {benchmark['benchmark_type']}")
        print(f"管控力度: {benchmark['control_intensity']}")
        print(f"基准值: {benchmark['benchmark_value']}")
        print(f"导向规则名称: {benchmark.get('rule_name', 'N/A')}")
    else:
        print(f"创建失败: {response.text}")
        return
    
    # 3. 获取导向基准列表
    print("\n=== 3. 获取导向基准列表 ===")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"总数: {result['total']}")
        print(f"返回记录数: {len(result['items'])}")
        if result['items']:
            first = result['items'][0]
            print(f"第一条记录: {first['department_name']} - {first.get('rule_name', 'N/A')}")
    else:
        print(f"获取失败: {response.text}")
    
    # 4. 按导向规则筛选
    print("\n=== 4. 按导向规则筛选基准 ===")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers,
        params={"rule_id": rule_id, "page": 1, "size": 10}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"该导向下的基准数量: {result['total']}")
    else:
        print(f"筛选失败: {response.text}")
    
    # 5. 获取导向基准详情
    print("\n=== 5. 获取导向基准详情 ===")
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_id}",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        benchmark = response.json()
        print(f"基准ID: {benchmark['id']}")
        print(f"科室: {benchmark['department_name']}")
        print(f"基准值: {benchmark['benchmark_value']}")
        print(f"导向规则名称: {benchmark.get('rule_name', 'N/A')}")
    else:
        print(f"获取失败: {response.text}")
    
    # 6. 更新导向基准
    print("\n=== 6. 更新导向基准 ===")
    update_data = {
        "control_intensity": 2.5678,
        "benchmark_value": 12345.6789
    }
    response = requests.put(
        f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_id}",
        json=update_data,
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        benchmark = response.json()
        print(f"更新成功")
        print(f"新管控力度: {benchmark['control_intensity']}")
        print(f"新基准值: {benchmark['benchmark_value']}")
    else:
        print(f"更新失败: {response.text}")
    
    # 7. 测试类别验证 - 尝试为"其他"类别创建基准（应该失败）
    print("\n=== 7. 测试类别验证（应该失败）===")
    other_rule_data = {
        "name": f"测试其他导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "other",
        "description": "其他类别导向"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        json=other_rule_data,
        headers=headers
    )
    if response.status_code == 200:
        other_rule = response.json()
        other_rule_id = other_rule["id"]
        
        # 尝试为"其他"类别创建基准
        invalid_benchmark_data = {
            "rule_id": other_rule_id,
            "department_code": "002",
            "department_name": "外科",
            "benchmark_type": "average",
            "control_intensity": 1.0,
            "stat_start_date": stat_start.isoformat(),
            "stat_end_date": stat_end.isoformat(),
            "benchmark_value": 1000.0
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/orientation-benchmarks",
            json=invalid_benchmark_data,
            headers=headers
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print(f"验证成功，正确拒绝: {response.json()['detail']}")
        else:
            print(f"验证失败，应该拒绝但没有: {response.text}")
        
        # 清理测试数据
        requests.delete(
            f"{BASE_URL}/api/v1/orientation-rules/{other_rule_id}",
            headers=headers
        )
    
    # 8. 测试日期范围验证（应该失败）
    print("\n=== 8. 测试日期范围验证（应该失败）===")
    invalid_date_data = {
        "rule_id": rule_id,
        "department_code": "003",
        "department_name": "儿科",
        "benchmark_type": "average",
        "control_intensity": 1.0,
        "stat_start_date": stat_end.isoformat(),  # 开始时间晚于结束时间
        "stat_end_date": stat_start.isoformat(),
        "benchmark_value": 1000.0
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        json=invalid_date_data,
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print(f"验证成功，正确拒绝: {response.json()}")
    else:
        print(f"验证失败，应该拒绝但没有: {response.text}")
    
    # 9. 删除导向基准
    print("\n=== 9. 删除导向基准 ===")
    response = requests.delete(
        f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_id}",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"删除成功: {response.json()['message']}")
    else:
        print(f"删除失败: {response.text}")
    
    # 10. 清理测试数据 - 删除导向规则
    print("\n=== 10. 清理测试数据 ===")
    response = requests.delete(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
        headers=headers
    )
    print(f"删除导向规则状态码: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_benchmark_crud()
