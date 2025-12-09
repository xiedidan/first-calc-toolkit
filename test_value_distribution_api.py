"""
测试价值分布 API
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "X-Hospital-ID": "1",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM0MjU4NjI0fQ.placeholder"
}

# 先登录获取 token
login_resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

if login_resp.status_code == 200:
    token = login_resp.json().get("access_token")
    HEADERS["Authorization"] = f"Bearer {token}"
    print(f"登录成功，获取到 token")
else:
    print(f"登录失败: {login_resp.status_code} - {login_resp.text}")
    exit()

# 获取分析报告列表
print("\n" + "=" * 60)
print("1. 获取分析报告列表")
print("=" * 60)

resp = requests.get(f"{BASE_URL}/analysis-reports", headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    print(f"总数: {data['total']}")
    for item in data['items']:
        print(f"  ID: {item['id']}, 科室: {item['department_name']}, 年月: {item['period']}")
else:
    print(f"请求失败: {resp.status_code} - {resp.text}")
    exit()

# 测试报告ID 3 的价值分布（科室ID 4，有数据）
print("\n" + "=" * 60)
print("2. 获取报告ID 3 的价值分布")
print("=" * 60)

resp = requests.get(f"{BASE_URL}/analysis-reports/3/value-distribution", headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    print(f"总价值: {data['total_value']}")
    print(f"消息: {data['message']}")
    print(f"项目数: {len(data['items'])}")
    for item in data['items']:
        print(f"  排名{item['rank']}: {item['dimension_name']} - 价值: {item['value']}, 占比: {item['ratio']}%")
else:
    print(f"请求失败: {resp.status_code} - {resp.text}")

# 测试报告ID 2 的价值分布（科室ID 3，无数据）
print("\n" + "=" * 60)
print("3. 获取报告ID 2 的价值分布")
print("=" * 60)

resp = requests.get(f"{BASE_URL}/analysis-reports/2/value-distribution", headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    print(f"总价值: {data['total_value']}")
    print(f"消息: {data['message']}")
    print(f"项目数: {len(data['items'])}")
    for item in data['items']:
        print(f"  排名{item['rank']}: {item['dimension_name']} - 价值: {item['value']}, 占比: {item['ratio']}%")
else:
    print(f"请求失败: {resp.status_code} - {resp.text}")

print("\n测试完成")
