"""
对话分组API测试脚本
测试需求 2.1, 2.2, 2.5
"""
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_URL = f"{BASE_URL}/api/v1"

# 测试用户凭据
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 测试医疗机构ID
HOSPITAL_ID = 1


def get_auth_token():
    """获取认证token"""
    response = requests.post(
        f"{API_URL}/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("data", {}).get("access_token")
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None


def get_headers(token):
    """获取请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json",
    }


def test_list_groups(headers):
    """测试获取分组列表"""
    print("\n=== 测试获取分组列表 ===")
    response = requests.get(f"{API_URL}/conversation-groups", headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"分组数量: {data.get('data', {}).get('total', 0)}")
        return data.get("data", {}).get("items", [])
    else:
        print(f"错误: {response.text}")
        return []


def test_create_group(headers, name):
    """测试创建分组"""
    print(f"\n=== 测试创建分组: {name} ===")
    response = requests.post(
        f"{API_URL}/conversation-groups",
        headers=headers,
        json={"name": name}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"创建成功: {data.get('data', {})}")
        return data.get("data", {})
    else:
        print(f"错误: {response.text}")
        return None


def test_update_group(headers, group_id, update_data):
    """测试更新分组"""
    print(f"\n=== 测试更新分组: {group_id} ===")
    response = requests.put(
        f"{API_URL}/conversation-groups/{group_id}",
        headers=headers,
        json=update_data
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"更新成功: {data.get('data', {})}")
        return data.get("data", {})
    else:
        print(f"错误: {response.text}")
        return None


def test_delete_group(headers, group_id):
    """测试删除分组"""
    print(f"\n=== 测试删除分组: {group_id} ===")
    response = requests.delete(
        f"{API_URL}/conversation-groups/{group_id}",
        headers=headers
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"删除成功: {data.get('data', {})}")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def test_reorder_groups(headers, group_ids):
    """测试重排序分组"""
    print(f"\n=== 测试重排序分组: {group_ids} ===")
    response = requests.put(
        f"{API_URL}/conversation-groups/reorder",
        headers=headers,
        json={"group_ids": group_ids}
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("重排序成功")
        return True
    else:
        print(f"错误: {response.text}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("对话分组API测试")
    print("=" * 60)
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("无法获取认证token，测试终止")
        return
    
    headers = get_headers(token)
    
    # 1. 获取初始分组列表
    initial_groups = test_list_groups(headers)
    
    # 2. 创建测试分组
    group1 = test_create_group(headers, "测试分组1")
    group2 = test_create_group(headers, "测试分组2")
    
    if group1 and group2:
        # 3. 测试更新分组
        test_update_group(headers, group1["id"], {
            "name": "测试分组1-已更新",
            "is_collapsed": True
        })
        
        # 4. 测试重排序
        test_reorder_groups(headers, [group2["id"], group1["id"]])
        
        # 5. 获取更新后的列表
        test_list_groups(headers)
        
        # 6. 清理测试数据
        print("\n=== 清理测试数据 ===")
        test_delete_group(headers, group1["id"])
        test_delete_group(headers, group2["id"])
    
    # 7. 验证清理结果
    final_groups = test_list_groups(headers)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
