"""
测试成本基准维度显示
验证维度名称是否显示为完整路径（如：医生-成本-人员经费）
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录获取token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": str(HOSPITAL_ID)
}

# 获取成本基准列表
print("获取成本基准列表...")
response = requests.get(
    f"{BASE_URL}/cost-benchmarks",
    headers=headers,
    params={"page": 1, "size": 10}
)

if response.status_code == 200:
    data = response.json()
    print(f"✓ 获取成功，共 {data['total']} 条记录")
    print(f"\n前10条记录的维度显示：")
    print(f"{'科室':<15} {'维度代码':<20} {'维度名称':<40} {'基准值':<12}")
    print("-" * 90)
    for item in data['items'][:10]:
        benchmark_value = float(item['benchmark_value']) if isinstance(item['benchmark_value'], str) else item['benchmark_value']
        print(f"{item['department_name']:<15} {item['dimension_code']:<20} {item['dimension_name']:<40} {benchmark_value:<12.2f}")
    
    # 检查是否有完整路径格式的维度名称
    has_full_path = any('-' in item['dimension_name'] for item in data['items'])
    if has_full_path:
        print("\n✓ 维度名称已显示为完整路径格式")
    else:
        print("\n⚠ 维度名称未显示为完整路径格式")
else:
    print(f"✗ 获取失败: {response.status_code}")
    print(response.text)
