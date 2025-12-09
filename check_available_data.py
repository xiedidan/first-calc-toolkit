"""
检查可用的数据（版本、科室、维度）
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def check_data():
    print("=== 检查可用数据 ===\n")
    
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
    data = response.json()
    hospitals = data.get("items", data) if isinstance(data, dict) else data
    hospital_id = hospitals[0]["id"]
    print(f"✅ 医疗机构ID: {hospital_id}\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    # 3. 检查模型版本
    print("3. 检查模型版本...")
    response = requests.get(f"{BASE_URL}/model-versions", headers=headers, params={"limit": 5})
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        versions = data.get("items", [])
        print(f"   找到 {len(versions)} 个版本:")
        for v in versions[:3]:
            print(f"     - ID: {v['id']}, 名称: {v['name']}")
    else:
        print(f"   错误: {response.text}")
    print()
    
    # 4. 检查科室
    print("4. 检查科室...")
    response = requests.get(f"{BASE_URL}/departments", headers=headers, params={"size": 5})
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        departments = data.get("items", [])
        print(f"   找到 {len(departments)} 个科室:")
        for d in departments[:3]:
            print(f"     - 代码: {d['his_code']}, 名称: {d['his_name']}")
    else:
        print(f"   错误: {response.text}")
    print()
    
    # 5. 检查维度
    print("5. 检查维度...")
    response = requests.get(f"{BASE_URL}/model-nodes", headers=headers, params={"limit": 5})
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        dimensions = data.get("items", [])
        print(f"   找到 {len(dimensions)} 个维度:")
        for d in dimensions[:3]:
            print(f"     - 代码: {d['code']}, 名称: {d['name']}")
    else:
        print(f"   错误: {response.text}")

if __name__ == "__main__":
    check_data()
