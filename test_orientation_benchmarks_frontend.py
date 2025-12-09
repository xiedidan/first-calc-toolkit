"""
测试导向基准前端集成
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的 hospital_id
HOSPITAL_ID = 1

# 登录获取token
def login():
    response = requests.post(
        f"http://localhost:8000/api/v1/auth/login",
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

def test_get_benchmark_ladder_rules(headers):
    """测试获取基准阶梯类别的导向规则"""
    print("\n=== 测试获取基准阶梯类别的导向规则 ===")
    
    response = requests.get(
        f"{BASE_URL}/orientation-rules",
        params={
            "category": "benchmark_ladder",
            "page": 1,
            "size": 1000
        },
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"找到 {len(data['items'])} 个基准阶梯类别的导向规则")
        for rule in data['items']:
            print(f"  - ID: {rule['id']}, 名称: {rule['name']}")
        return data['items']
    else:
        print(f"错误: {response.text}")
        return []

def test_get_departments(headers):
    """测试获取科室列表"""
    print("\n=== 测试获取科室列表 ===")
    
    response = requests.get(
        f"{BASE_URL}/departments",
        params={
            "page": 1,
            "size": 10
        },
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"找到 {len(data['items'])} 个科室")
        if data['items']:
            print(f"科室字段: {data['items'][0].keys()}")
            for dept in data['items'][:5]:
                dept_code = dept.get('his_code') or dept.get('code') or dept.get('dept_code')
                dept_name = dept.get('his_name') or dept.get('name') or dept.get('dept_name')
                print(f"  - 代码: {dept_code}, 名称: {dept_name}")
        return data['items']
    else:
        print(f"错误: {response.text}")
        return []

def test_create_benchmark(headers, rule_id, dept_code, dept_name):
    """测试创建导向基准"""
    print("\n=== 测试创建导向基准 ===")
    
    benchmark_data = {
        "rule_id": rule_id,
        "department_code": dept_code,
        "department_name": dept_name,
        "benchmark_type": "average",
        "control_intensity": 1.2345,
        "stat_start_date": "2024-01-01T00:00:00",
        "stat_end_date": "2024-12-31T23:59:59",
        "benchmark_value": 100.5678
    }
    
    response = requests.post(
        f"{BASE_URL}/orientation-benchmarks",
        json=benchmark_data,
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"创建成功，ID: {data['id']}")
        print(f"管控力度: {data['control_intensity']} (应该是 4 位小数)")
        print(f"基准值: {data['benchmark_value']} (应该是 4 位小数)")
        return data
    else:
        print(f"错误: {response.text}")
        return None

def test_get_benchmarks_by_rule(headers, rule_id):
    """测试按导向筛选基准"""
    print(f"\n=== 测试按导向 {rule_id} 筛选基准 ===")
    
    response = requests.get(
        f"{BASE_URL}/orientation-benchmarks",
        params={
            "rule_id": rule_id,
            "page": 1,
            "size": 20
        },
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"找到 {len(data['items'])} 个基准")
        for benchmark in data['items']:
            print(f"  - ID: {benchmark['id']}, 科室: {benchmark['department_name']}, 基准值: {benchmark['benchmark_value']}")
        return data['items']
    else:
        print(f"错误: {response.text}")
        return []

def test_delete_benchmark(headers, benchmark_id):
    """测试删除导向基准"""
    print(f"\n=== 测试删除导向基准 {benchmark_id} ===")
    
    response = requests.delete(
        f"{BASE_URL}/orientation-benchmarks/{benchmark_id}",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("删除成功")
        return True
    else:
        print(f"错误: {response.text}")
        return False

if __name__ == "__main__":
    print("开始测试导向基准前端集成...")
    
    # 登录
    token = login()
    if not token:
        print("登录失败，退出测试")
        exit(1)
    
    headers = get_headers(token)
    
    # 1. 获取基准阶梯类别的导向规则
    rules = test_get_benchmark_ladder_rules(headers)
    
    if not rules:
        print("\n没有找到基准阶梯类别的导向规则，请先创建一个")
        exit(1)
    
    rule_id = rules[0]['id']
    
    # 2. 获取科室列表
    departments = test_get_departments(headers)
    
    if not departments:
        print("\n没有找到科室，请先创建科室")
        exit(1)
    
    dept = departments[0]
    dept_code = dept.get('his_code') or dept.get('code') or dept.get('dept_code')
    dept_name = dept.get('his_name') or dept.get('name') or dept.get('dept_name')
    
    # 3. 创建导向基准
    benchmark = test_create_benchmark(headers, rule_id, dept_code, dept_name)
    
    if benchmark:
        # 4. 按导向筛选基准
        test_get_benchmarks_by_rule(headers, rule_id)
        
        # 5. 删除测试数据
        test_delete_benchmark(headers, benchmark['id'])
    
    print("\n测试完成！")
