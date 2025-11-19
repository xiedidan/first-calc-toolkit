"""
测试 test_code 接口修复
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def get_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data["data"]["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def test_code_without_datasource():
    """测试不带数据源的代码测试"""
    token = get_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试代码测试接口（Python代码） ===")
    response = requests.post(
        f"{BASE_URL}/calculation-steps/test-code",
        headers=headers,
        json={
            "code_type": "python",
            "code_content": "print('Hello World')"
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_code_with_datasource():
    """测试带数据源的SQL代码测试"""
    token = get_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 先获取数据源列表
    print("\n=== 获取数据源列表 ===")
    response = requests.get(
        f"{BASE_URL}/data-sources",
        headers=headers,
        params={"page": 1, "size": 10}
    )
    
    if response.status_code != 200:
        print(f"获取数据源失败: {response.text}")
        return
    
    data = response.json()
    if not data["data"]["items"]:
        print("没有可用的数据源")
        return
    
    data_source_id = data["data"]["items"][0]["id"]
    print(f"使用数据源ID: {data_source_id}")
    
    # 测试SQL代码
    print("\n=== 测试SQL代码 ===")
    response = requests.post(
        f"{BASE_URL}/calculation-steps/test-code",
        headers=headers,
        json={
            "code_type": "sql",
            "code_content": "SELECT 1 as test_column",
            "data_source_id": data_source_id
        }
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("开始测试 test_code 接口修复...")
    test_code_without_datasource()
    test_code_with_datasource()
    print("\n测试完成！")
