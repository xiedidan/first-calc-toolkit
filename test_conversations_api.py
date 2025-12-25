"""
对话API测试脚本
测试智能问数系统的对话管理功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试用医疗机构ID

# 请求头
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": str(HOSPITAL_ID),
}


def get_auth_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    print(f"登录失败: {response.text}")
    return None


def test_create_conversation(token: str):
    """测试创建对话"""
    print("\n=== 测试创建对话 ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    # 创建指标口径查询对话
    data = {
        "title": f"测试对话-{datetime.now().strftime('%H%M%S')}",
        "description": "这是一个测试对话",
        "conversation_type": "caliber",
    }
    
    response = requests.post(
        f"{BASE_URL}/conversations",
        headers=auth_headers,
        json=data,
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        return result.get("data", {}).get("id")
    return None


def test_list_conversations(token: str):
    """测试获取对话列表"""
    print("\n=== 测试获取对话列表 ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/conversations",
        headers=auth_headers,
        params={"page": 1, "size": 10},
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_search_conversations(token: str, keyword: str):
    """测试搜索对话"""
    print(f"\n=== 测试搜索对话 (关键词: {keyword}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/conversations",
        headers=auth_headers,
        params={"keyword": keyword, "page": 1, "size": 10},
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_get_conversation(token: str, conversation_id: int):
    """测试获取对话详情"""
    print(f"\n=== 测试获取对话详情 (ID: {conversation_id}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/conversations/{conversation_id}",
        headers=auth_headers,
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_update_conversation(token: str, conversation_id: int):
    """测试更新对话"""
    print(f"\n=== 测试更新对话 (ID: {conversation_id}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    data = {
        "title": f"更新后的标题-{datetime.now().strftime('%H%M%S')}",
        "description": "更新后的描述",
    }
    
    response = requests.put(
        f"{BASE_URL}/conversations/{conversation_id}",
        headers=auth_headers,
        json=data,
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_send_message(token: str, conversation_id: int):
    """测试发送消息"""
    print(f"\n=== 测试发送消息 (对话ID: {conversation_id}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    data = {
        "content": "请查询门诊收入指标的口径定义",
    }
    
    response = requests.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=auth_headers,
        json=data,
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_list_messages(token: str, conversation_id: int):
    """测试获取消息列表"""
    print(f"\n=== 测试获取消息列表 (对话ID: {conversation_id}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=auth_headers,
        params={"page": 1, "size": 50},
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def test_delete_conversation(token: str, conversation_id: int):
    """测试删除对话"""
    print(f"\n=== 测试删除对话 (ID: {conversation_id}) ===")
    
    auth_headers = {**headers, "Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/conversations/{conversation_id}",
        headers=auth_headers,
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    return response.status_code == 200


def main():
    """主测试流程"""
    print("=" * 60)
    print("对话API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    print(f"获取到token: {token[:20]}...")
    
    # 测试创建对话
    conversation_id = test_create_conversation(token)
    if not conversation_id:
        print("创建对话失败，测试终止")
        return
    
    # 测试获取对话列表
    test_list_conversations(token)
    
    # 测试搜索对话
    test_search_conversations(token, "测试")
    
    # 测试获取对话详情
    test_get_conversation(token, conversation_id)
    
    # 测试更新对话
    test_update_conversation(token, conversation_id)
    
    # 测试发送消息
    test_send_message(token, conversation_id)
    
    # 再发送一条消息
    test_send_message(token, conversation_id)
    
    # 测试获取消息列表
    test_list_messages(token, conversation_id)
    
    # 测试获取对话详情（包含消息）
    test_get_conversation(token, conversation_id)
    
    # 测试删除对话
    test_delete_conversation(token, conversation_id)
    
    # 验证删除后无法获取
    print("\n=== 验证删除后无法获取 ===")
    test_get_conversation(token, conversation_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
