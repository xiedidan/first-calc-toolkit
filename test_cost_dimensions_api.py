"""
测试成本维度API
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 登录获取token
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": "1"
}

# 测试获取版本12的成本维度
version_id = 12
response = requests.get(
    f"{BASE_URL}/model-nodes/version/{version_id}/cost-dimensions",
    headers=headers
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")

if response.status_code == 200:
    data = response.json()
    print(f"\n找到 {data['total']} 个成本维度:")
    for item in data['items']:
        print(f"  - ID: {item['id']}, 名称: {item['name']}, 编码: {item['code']}")
