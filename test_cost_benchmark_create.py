"""
测试成本基准创建功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取token
def login():
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

# 获取医疗机构ID
def get_hospital_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hospitals", headers=headers)
    if response.status_code == 200:
        data = response.json()
        hospitals = data.get("items", data) if isinstance(data, dict) else data
        if hospitals and len(hospitals) > 0:
            return hospitals[0]["id"]
    return None

# 获取模型版本
def get_version(token, hospital_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    response = requests.get(f"{BASE_URL}/model-versions", headers=headers, params={"limit": 1})
    if response.status_code == 200:
        versions = response.json().get("items", [])
        if versions:
            return versions[0]
    else:
        print(f"   获取版本失败: {response.status_code} - {response.text}")
    return None

# 获取科室
def get_department(token, hospital_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    response = requests.get(f"{BASE_URL}/departments", headers=headers, params={"size": 1})
    if response.status_code == 200:
        departments = response.json().get("items", [])
        if departments:
            return departments[0]
    return None

# 获取维度
def get_dimension(token, hospital_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    response = requests.get(f"{BASE_URL}/model-nodes", headers=headers, params={"limit": 1})
    if response.status_code == 200:
        dimensions = response.json().get("items", [])
        if dimensions:
            return dimensions[0]
    return None

# 创建成本基准
def create_cost_benchmark(token, hospital_id, data):
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id),
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{BASE_URL}/cost-benchmarks",
        headers=headers,
        json=data
    )
    return response

# 测试创建功能
def test_create():
    print("=== 测试成本基准创建功能 ===\n")
    
    # 1. 登录
    print("1. 登录...")
    token = login()
    if not token:
        print("❌ 登录失败")
        return
    print("✅ 登录成功\n")
    
    # 2. 获取医疗机构
    print("2. 获取医疗机构...")
    hospital_id = get_hospital_id(token)
    if not hospital_id:
        print("❌ 获取医疗机构失败")
        return
    print(f"✅ 医疗机构ID: {hospital_id}\n")
    
    # 3. 获取模型版本
    print("3. 获取模型版本...")
    version = get_version(token, hospital_id)
    if not version:
        print("❌ 获取模型版本失败")
        return
    print(f"✅ 模型版本: {version['name']} (ID: {version['id']})\n")
    
    # 4. 获取科室
    print("4. 获取科室...")
    department = get_department(token, hospital_id)
    if not department:
        print("❌ 获取科室失败")
        return
    print(f"✅ 科室: {department['his_name']} (代码: {department['his_code']})\n")
    
    # 5. 获取维度
    print("5. 获取维度...")
    dimension = get_dimension(token, hospital_id)
    if not dimension:
        print("❌ 获取维度失败")
        return
    print(f"✅ 维度: {dimension['name']} (代码: {dimension['code']})\n")
    
    # 6. 创建成本基准
    print("6. 创建成本基准...")
    data = {
        "department_code": department["his_code"],
        "department_name": department["his_name"],
        "version_id": version["id"],
        "version_name": version["name"],
        "dimension_code": dimension["code"],
        "dimension_name": dimension["name"],
        "benchmark_value": 12345.67
    }
    
    response = create_cost_benchmark(token, hospital_id, data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 创建成功!")
        print(f"   ID: {result['id']}")
        print(f"   科室: {result['department_name']}")
        print(f"   版本: {result['version_name']}")
        print(f"   维度: {result['dimension_name']}")
        print(f"   基准值: {result['benchmark_value']}")
        print(f"   创建时间: {result['created_at']}")
        
        # 测试重复创建（应该失败）
        print("\n7. 测试唯一性约束（重复创建）...")
        response2 = create_cost_benchmark(token, hospital_id, data)
        if response2.status_code == 400:
            print("✅ 唯一性约束验证成功（重复创建被阻止）")
            print(f"   错误信息: {response2.json()['detail']}")
        else:
            print(f"❌ 唯一性约束验证失败: {response2.status_code}")
        
        # 测试无效基准值（应该失败）
        print("\n8. 测试基准值验证（负数）...")
        invalid_data = data.copy()
        invalid_data["benchmark_value"] = -100
        response3 = create_cost_benchmark(token, hospital_id, invalid_data)
        if response3.status_code == 400:
            print("✅ 基准值验证成功（负数被阻止）")
            print(f"   错误信息: {response3.json()['detail']}")
        else:
            print(f"❌ 基准值验证失败: {response3.status_code}")
            
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(f"   错误信息: {response.text}")

if __name__ == "__main__":
    test_create()
