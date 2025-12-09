"""
测试导向规则API
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1/orientation-rules"

# 测试用的认证token和hospital_id
# 需要先登录获取token
def get_auth_token():
    """获取认证token"""
    login_url = f"{BASE_URL}/api/v1/auth/login"
    response = requests.post(
        login_url,
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return None


def test_create_orientation_rule(token, hospital_id):
    """测试创建导向规则"""
    print("\n=== 测试创建导向规则 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id),
        "Content-Type": "application/json"
    }
    
    data = {
        "name": "测试导向规则1",
        "category": "benchmark_ladder",
        "description": "这是一个测试导向规则"
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None


def test_get_orientation_rules(token, hospital_id):
    """测试获取导向规则列表"""
    print("\n=== 测试获取导向规则列表 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = requests.get(API_URL, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_get_orientation_rule_detail(token, hospital_id, rule_id):
    """测试获取导向规则详情"""
    print(f"\n=== 测试获取导向规则详情 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = requests.get(f"{API_URL}/{rule_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_update_orientation_rule(token, hospital_id, rule_id):
    """测试更新导向规则"""
    print(f"\n=== 测试更新导向规则 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id),
        "Content-Type": "application/json"
    }
    
    data = {
        "description": "更新后的描述信息"
    }
    
    response = requests.put(f"{API_URL}/{rule_id}", headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete_orientation_rule(token, hospital_id, rule_id):
    """测试删除导向规则"""
    print(f"\n=== 测试删除导向规则 (ID: {rule_id}) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    response = requests.delete(f"{API_URL}/{rule_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_search_orientation_rules(token, hospital_id):
    """测试搜索导向规则"""
    print("\n=== 测试搜索导向规则 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(hospital_id)
    }
    
    # 测试按关键词搜索
    response = requests.get(f"{API_URL}?keyword=测试", headers=headers)
    print(f"按关键词搜索 - 状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 测试按类别筛选
    response = requests.get(f"{API_URL}?category=benchmark_ladder", headers=headers)
    print(f"\n按类别筛选 - 状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def main():
    """主测试流程"""
    print("开始测试导向规则API...")
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    print(f"成功获取token: {token[:20]}...")
    
    # 使用默认的hospital_id（假设为1）
    hospital_id = 1
    
    # 测试创建
    rule_id = test_create_orientation_rule(token, hospital_id)
    
    if rule_id:
        # 测试列表查询
        test_get_orientation_rules(token, hospital_id)
        
        # 测试详情查询
        test_get_orientation_rule_detail(token, hospital_id, rule_id)
        
        # 测试更新
        test_update_orientation_rule(token, hospital_id, rule_id)
        
        # 测试搜索
        test_search_orientation_rules(token, hospital_id)
        
        # 测试删除
        test_delete_orientation_rule(token, hospital_id, rule_id)
        
        # 再次查询列表确认删除
        test_get_orientation_rules(token, hospital_id)
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()
