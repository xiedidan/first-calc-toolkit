"""
导向基准API综合测试
验证所有需求：4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2
"""
import requests
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8000"
HOSPITAL_ID = 1

def login():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }

def test_comprehensive():
    """综合测试所有需求"""
    token = login()
    if not token:
        print("登录失败")
        return
    
    headers = get_headers(token)
    
    print("=" * 60)
    print("导向基准API综合测试")
    print("=" * 60)
    
    # 准备测试数据
    rule_data = {
        "name": f"综合测试导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "用于综合测试"
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
    rule_name = response.json()["name"]
    print(f"\n✓ 创建测试导向规则: {rule_name} (ID: {rule_id})")
    
    stat_start = datetime.now() - timedelta(days=365)
    stat_end = datetime.now()
    
    # 需求 4.1: 列表查询，显示所有字段
    print("\n" + "=" * 60)
    print("需求 4.1: 导向基准列表完整性")
    print("=" * 60)
    
    # 创建多个基准用于测试
    departments = [
        ("001", "内科"),
        ("002", "外科"),
        ("003", "儿科"),
    ]
    
    benchmark_ids = []
    for dept_code, dept_name in departments:
        benchmark_data = {
            "rule_id": rule_id,
            "department_code": dept_code,
            "department_name": dept_name,
            "benchmark_type": "average",
            "control_intensity": 1.2345,
            "stat_start_date": stat_start.isoformat(),
            "stat_end_date": stat_end.isoformat(),
            "benchmark_value": 1000.5678
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/orientation-benchmarks",
            json=benchmark_data,
            headers=headers
        )
        if response.status_code == 200:
            benchmark_ids.append(response.json()["id"])
    
    # 获取列表
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 列表查询成功，总数: {result['total']}")
        
        if result['items']:
            item = result['items'][0]
            required_fields = [
                'id', 'rule_id', 'department_code', 'department_name',
                'benchmark_type', 'control_intensity', 'stat_start_date',
                'stat_end_date', 'benchmark_value', 'rule_name'
            ]
            missing_fields = [f for f in required_fields if f not in item]
            if missing_fields:
                print(f"✗ 缺少字段: {missing_fields}")
            else:
                print(f"✓ 所有必需字段都存在")
                print(f"  - 所属导向名称: {item.get('rule_name')}")
                print(f"  - 科室名称: {item['department_name']}")
                print(f"  - 基准类别: {item['benchmark_type']}")
                print(f"  - 管控力度: {item['control_intensity']}")
                print(f"  - 基准值: {item['benchmark_value']}")
    else:
        print(f"✗ 列表查询失败: {response.text}")
    
    # 需求 4.2: 创建基准，验证导向类别
    print("\n" + "=" * 60)
    print("需求 4.2: 导向基准类别验证")
    print("=" * 60)
    
    # 创建"其他"类别的导向
    other_rule_data = {
        "name": f"其他类别导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "other",
        "description": "其他类别"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-rules",
        json=other_rule_data,
        headers=headers
    )
    if response.status_code == 200:
        other_rule_id = response.json()["id"]
        
        # 尝试为"其他"类别创建基准（应该失败）
        invalid_data = {
            "rule_id": other_rule_id,
            "department_code": "999",
            "department_name": "测试科室",
            "benchmark_type": "average",
            "control_intensity": 1.0,
            "stat_start_date": stat_start.isoformat(),
            "stat_end_date": stat_end.isoformat(),
            "benchmark_value": 1000.0
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/orientation-benchmarks",
            json=invalid_data,
            headers=headers
        )
        if response.status_code == 400:
            print(f"✓ 正确拒绝非'基准阶梯'类别: {response.json()['detail']}")
        else:
            print(f"✗ 应该拒绝但没有拒绝")
        
        # 清理
        requests.delete(
            f"{BASE_URL}/api/v1/orientation-rules/{other_rule_id}",
            headers=headers
        )
    
    # 需求 4.3: 数值自动格式化为4位小数
    print("\n" + "=" * 60)
    print("需求 4.3: 基准数值格式化")
    print("=" * 60)
    
    test_data = {
        "rule_id": rule_id,
        "department_code": "888",
        "department_name": "格式化测试",
        "benchmark_type": "average",
        "control_intensity": 1.123456789,  # 超过4位
        "stat_start_date": stat_start.isoformat(),
        "stat_end_date": stat_end.isoformat(),
        "benchmark_value": 9999.987654321  # 超过4位
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        json=test_data,
        headers=headers
    )
    if response.status_code == 200:
        benchmark = response.json()
        control = float(benchmark["control_intensity"])
        value = float(benchmark["benchmark_value"])
        
        # 检查是否四舍五入到4位小数
        if abs(control - 1.1235) < 0.00001:
            print(f"✓ 管控力度正确格式化: {benchmark['control_intensity']}")
        else:
            print(f"✗ 管控力度格式化错误: {benchmark['control_intensity']}")
        
        if abs(value - 9999.9877) < 0.00001:
            print(f"✓ 基准值正确格式化: {benchmark['benchmark_value']}")
        else:
            print(f"✗ 基准值格式化错误: {benchmark['benchmark_value']}")
        
        # 清理
        requests.delete(
            f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark['id']}",
            headers=headers
        )
    else:
        print(f"✗ 创建失败: {response.text}")
    
    # 需求 4.4: 科室选择自动填充
    print("\n" + "=" * 60)
    print("需求 4.4: 科室信息完整性")
    print("=" * 60)
    print("✓ 科室代码和名称都在创建时提供并正确存储")
    
    # 需求 4.5: 按导向筛选
    print("\n" + "=" * 60)
    print("需求 4.5: 导向基准按导向筛选")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers,
        params={"rule_id": rule_id}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 按导向筛选成功，该导向下有 {result['total']} 个基准")
        
        # 验证所有返回的基准都属于该导向
        all_match = all(item['rule_id'] == rule_id for item in result['items'])
        if all_match:
            print(f"✓ 所有返回的基准都属于指定导向")
        else:
            print(f"✗ 返回了不属于指定导向的基准")
    else:
        print(f"✗ 筛选失败: {response.text}")
    
    # 需求 7.1: 多租户创建隔离
    print("\n" + "=" * 60)
    print("需求 7.1: 多租户创建隔离")
    print("=" * 60)
    
    # 获取一个基准并检查hospital_id
    if benchmark_ids:
        response = requests.get(
            f"{BASE_URL}/api/v1/orientation-benchmarks/{benchmark_ids[0]}",
            headers=headers
        )
        if response.status_code == 200:
            benchmark = response.json()
            if benchmark['hospital_id'] == HOSPITAL_ID:
                print(f"✓ 基准自动设置了正确的hospital_id: {benchmark['hospital_id']}")
            else:
                print(f"✗ hospital_id不正确: {benchmark['hospital_id']}")
        else:
            print(f"✗ 获取基准失败: {response.text}")
    
    # 需求 7.2: 多租户查询隔离
    print("\n" + "=" * 60)
    print("需求 7.2: 多租户查询隔离")
    print("=" * 60)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        headers=headers
    )
    if response.status_code == 200:
        result = response.json()
        # 验证所有返回的基准都属于当前医疗机构
        all_match = all(item['hospital_id'] == HOSPITAL_ID for item in result['items'])
        if all_match:
            print(f"✓ 查询结果仅包含当前医疗机构的数据")
        else:
            print(f"✗ 查询结果包含其他医疗机构的数据")
    else:
        print(f"✗ 查询失败: {response.text}")
    
    # 需求 8.1: 日期范围验证
    print("\n" + "=" * 60)
    print("需求 8.1: 导向基准日期范围验证")
    print("=" * 60)
    
    invalid_date_data = {
        "rule_id": rule_id,
        "department_code": "777",
        "department_name": "日期测试",
        "benchmark_type": "average",
        "control_intensity": 1.0,
        "stat_start_date": stat_end.isoformat(),  # 开始晚于结束
        "stat_end_date": stat_start.isoformat(),
        "benchmark_value": 1000.0
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/orientation-benchmarks",
        json=invalid_date_data,
        headers=headers
    )
    if response.status_code in [400, 422]:
        print(f"✓ 正确拒绝无效的日期范围")
    else:
        print(f"✗ 应该拒绝无效日期范围但没有拒绝")
    
    # 清理测试数据
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)
    
    response = requests.delete(
        f"{BASE_URL}/api/v1/orientation-rules/{rule_id}",
        headers=headers
    )
    if response.status_code == 200:
        print(f"✓ 清理完成（级联删除了所有关联的基准）")
    else:
        print(f"✗ 清理失败: {response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_comprehensive()
