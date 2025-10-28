"""
直接测试API端点
"""
import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("测试API端点")
print("=" * 60)

# 测试根路径
print("\n1. 测试根路径...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
except Exception as e:
    print(f"   错误: {e}")

# 测试API文档
print("\n2. 测试API文档...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   状态码: {response.status_code}")
    if "系统设置" in response.text:
        print("   ✓ 找到'系统设置'标签")
    else:
        print("   ✗ 未找到'系统设置'标签")
except Exception as e:
    print(f"   错误: {e}")

# 测试系统设置API
print("\n3. 测试系统设置API...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/system/settings")
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   响应: {response.json()}")
    else:
        print(f"   错误响应: {response.text}")
except Exception as e:
    print(f"   错误: {e}")

# 测试数据源API
print("\n4. 测试数据源API...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/data-sources?page=1&size=10")
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   数据源数量: {data['data']['total']}")
    else:
        print(f"   错误响应: {response.text}")
except Exception as e:
    print(f"   错误: {e}")

print("\n" + "=" * 60)
