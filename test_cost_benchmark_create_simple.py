"""
简单测试成本基准创建功能 - 使用已知数据
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试数据（需要根据实际数据库调整）
TEST_DATA = {
    "department_code": "001",
    "department_name": "内科",
    "version_id": 1,
    "version_name": "测试版本",
    "dimension_code": "DIM001",
    "dimension_name": "测试维度",
    "benchmark_value": 12345.67
}

def test_create_with_known_data():
    print("=== 测试成本基准创建功能（使用已知数据）===\n")
    
    # 1. 登录
    print("1. 登录...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    token = response.json()["access_token"]
    print("✅ 登录成功\n")
    
    # 2. 获取医疗机构
    print("2. 获取医疗机构...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hospitals", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取医疗机构失败: {response.text}")
        return
    
    data = response.json()
    hospitals = data.get("items", data) if isinstance(data, dict) else data
    if not hospitals:
        print("❌ 没有医疗机构")
        return
    
    hospital_id = hospitals[0]["id"]
    print(f"✅ 医疗机构ID: {hospital_id}\n")
    
    # 3. 创建成本基准
    print("3. 创建成本基准...")
    print(f"   数据: {json.dumps(TEST_DATA, ensure_ascii=False, indent=2)}\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id),
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        json=TEST_DATA
    )
    
    print(f"   响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 创建成功!")
        print(f"   返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ 创建失败")
        print(f"   错误信息: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_create_with_known_data()
