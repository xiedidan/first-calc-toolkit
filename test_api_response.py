#!/usr/bin/env python3
"""测试API返回的hospital_value和dept_value字段"""
import requests

BASE_URL = "http://localhost:8000"

# 先登录获取token
login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
if login_resp.status_code != 200:
    print(f"登录失败: {login_resp.text}")
    exit(1)

token = login_resp.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": "1"
}

# 调用results/detail API
resp = requests.get(
    f"{BASE_URL}/api/v1/calculation/results/detail",
    params={"dept_id": 4, "task_id": "f33539f4-bdd5-4100-91e9-a7fd9d43adc1"},
    headers=headers
)

if resp.status_code != 200:
    print(f"API调用失败: {resp.status_code} - {resp.text}")
    exit(1)

data = resp.json()
print("API响应成功！")
print(f"返回的keys: {data.keys()}")
print(f"sequences: {data.get('sequences')}")
print(f"doctor: {len(data.get('doctor', []))} items")

# 检查doctor字段中的维度
if data.get("doctor"):
    for item in data["doctor"][:3]:
        print(f"\n维度: {item.get('dimension_name')}")
        print(f"  - hospital_value: {item.get('hospital_value')}")
        print(f"  - dept_value: {item.get('dept_value')}")
        print(f"  - weight: {item.get('weight')}")

# 检查第一个维度的字段
if data.get("sequences"):
    seq = data["sequences"][0]
    print(f"\n序列: {seq['sequence_name']}")
    if seq.get("dimensions"):
        dim = seq["dimensions"][0]
        print(f"\n第一个维度: {dim['dimension_name']}")
        print(f"  - weight: {dim.get('weight')}")
        print(f"  - hospital_value: {dim.get('hospital_value')}")
        print(f"  - dept_value: {dim.get('dept_value')}")
        
        # 找一个有调整的维度
        for d in seq["dimensions"]:
            if d.get("hospital_value") != d.get("dept_value"):
                print(f"\n找到有调整的维度: {d['dimension_name']}")
                print(f"  - hospital_value: {d.get('hospital_value')}")
                print(f"  - dept_value: {d.get('dept_value')}")
                break
        else:
            print("\n没有找到hospital_value != dept_value的维度")
else:
    print("没有sequences数据")
