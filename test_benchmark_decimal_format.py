"""
测试导向基准数值格式化
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

def test_decimal_formatting():
    """测试数值字段自动格式化为4位小数"""
    token = login()
    if not token:
        return
    
    headers = get_headers(token)
    
    # 1. 创建导向规则
    print("\n=== 创建导向规则 ===")
    rule_data = {
        "name": f"测试数值格式_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "测试数值格式化"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        json=rule_data,
        headers=headers
    )
    if response.status_code != 200:
        print(f"创建导向规则失败: {response.text}")
        return
    
    rule_id = response.json()["id"]
    print(f"导向规则ID: {rule_id}")
    
    # 2. 测试不同精度的数值输入
    test_cases = [
        {
            "name": "整数",
            "control_intensity": 1,
            "benchmark_value": 100,
            "expected_control": "1.0000",
            "expected_value": "100.0000"
        },
        {
            "name": "1位小数",
            "control_intensity": 1.5,
            "benchmark_value": 100.5,
            "expected_control": "1.5000",
            "expected_value": "100.5000"
        },
        {
            "name": "2位小数",
            "control_intensity": 1.23,
            "benchmark_value": 100.45,
            "expected_control": "1.2300",
            "expected_value": "100.4500"
        },
        {
            "name": "4位小数",
            "control_intensity": 1.2345,
            "benchmark_value": 100.4567,
            "expected_control": "1.2345",
            "expected_value": "100.4567"
        },
        {
            "name": "超过4位小数（应四舍五入）",
            "control_intensity": 1.23456,
            "benchmark_value": 100.45678,
            "expected_control": "1.2346",
            "expected_value": "100.4568"
        },
        {
            "name": "很多位小数（应四舍五入）",
            "control_intensity": 1.123456789,
            "benchmark_value": 100.987654321,
            "expected_control": "1.1235",
            "expected_value": "100.9877"
        },
    ]
    
    stat_start = datetime.now() - timedelta(days=365)
    stat_end = datetime.now()
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== 测试用例 {i+1}: {test_case['name']} ===")
        
        benchmark_data = {
            "rule_id": rule_id,
            "department_code": f"00{i+1}",
            "department_name": f"科室{i+1}",
            "benchmark_type": "average",
            "control_intensity": test_case["control_intensity"],
            "stat_start_date": stat_start.isoformat(),
            "stat_end_date": stat_end.isoformat(),
            "benchmark_value": test_case["benchmark_value"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/orientation-benchmarks",
            json=benchmark_data,
            headers=headers
        )
        
        if response.status_code == 200:
            benchmark = response.json()
            actual_control = str(benchmark["control_intensity"])
            actual_value = str(benchmark["benchmark_value"])
            
            print(f"输入管控力度: {test_case['control_intensity']}")
            print(f"返回管控力度: {actual_control}")
            print(f"期望管控力度: {test_case['expected_control']}")
            print(f"管控力度匹配: {'✓' if actual_control == test_case['expected_control'] else '✗'}")
            
            print(f"输入基准值: {test_case['benchmark_value']}")
            print(f"返回基准值: {actual_value}")
            print(f"期望基准值: {test_case['expected_value']}")
            print(f"基准值匹配: {'✓' if actual_value == test_case['expected_value'] else '✗'}")
        else:
            print(f"创建失败: {response.text}")
    
    # 清理测试数据
    print("\n=== 清理测试数据 ===")
    response = requests.delete(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
        headers=headers
    )
    print(f"删除导向规则状态码: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_decimal_formatting()
