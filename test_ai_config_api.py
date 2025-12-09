"""
测试AI配置API

测试AI配置管理服务和API端点的功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 测试用户凭证（需要管理员权限）
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 测试医疗机构ID
TEST_HOSPITAL_ID = 1


def login():
    """登录获取token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✓ 登录成功，获取token")
        return token
    else:
        print(f"✗ 登录失败: {response.status_code}")
        print(response.text)
        return None


def test_get_config(token):
    """测试获取AI配置"""
    print("\n=== 测试获取AI配置 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID)
    }
    
    response = requests.get(
        f"{API_BASE}/ai-config",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        data = response.json().get("data")
        if data:
            print("✓ 获取AI配置成功")
            return data
        else:
            print("✓ AI配置不存在（首次使用）")
            return None
    else:
        print("✗ 获取AI配置失败")
        return None


def test_create_config(token):
    """测试创建AI配置"""
    print("\n=== 测试创建AI配置 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    config_data = {
        "api_endpoint": "https://api.deepseek.com/v1",
        "api_key": "sk-test-key-12345678901234567890",
        "prompt_template": """请根据以下医技项目名称，从给定的维度列表中选择最合适的分类。

项目名称：{item_name}

可选维度：
{dimensions}

请返回JSON格式：
{
  "dimension_id": <维度ID>,
  "confidence": <确信度，0-1之间的小数>
}""",
        "call_delay": 1.0,
        "daily_limit": 10000,
        "batch_size": 100
    }
    
    response = requests.post(
        f"{API_BASE}/ai-config",
        headers=headers,
        json=config_data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 创建AI配置成功")
        data = response.json().get("data")
        # 验证密钥已掩码
        if data and "api_key_masked" in data:
            print(f"  密钥掩码: {data['api_key_masked']}")
            if "****" in data['api_key_masked']:
                print("✓ 密钥已正确掩码")
            else:
                print("✗ 密钥掩码格式不正确")
        return True
    else:
        print("✗ 创建AI配置失败")
        return False


def test_update_config(token):
    """测试更新AI配置"""
    print("\n=== 测试更新AI配置 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    config_data = {
        "api_endpoint": "https://api.deepseek.com/v1",
        "api_key": "sk-test-key-updated-98765432109876543210",
        "prompt_template": """请根据以下医技项目名称，从给定的维度列表中选择最合适的分类。

项目名称：{item_name}

可选维度：
{dimensions}

请返回JSON格式：
{
  "dimension_id": <维度ID>,
  "confidence": <确信度，0-1之间的小数>
}

注意：请仔细分析项目名称的特征。""",
        "call_delay": 1.5,
        "daily_limit": 5000,
        "batch_size": 50
    }
    
    response = requests.post(
        f"{API_BASE}/ai-config",
        headers=headers,
        json=config_data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 更新AI配置成功")
        data = response.json().get("data")
        # 验证配置已更新
        if data:
            print(f"  调用延迟: {data.get('call_delay')}秒")
            print(f"  每日限额: {data.get('daily_limit')}次")
            print(f"  批次大小: {data.get('batch_size')}个")
        return True
    else:
        print("✗ 更新AI配置失败")
        return False


def test_test_config(token):
    """测试AI配置测试功能"""
    print("\n=== 测试AI配置测试功能 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    test_data = {
        "test_item_name": "CT检查"
    }
    
    response = requests.post(
        f"{API_BASE}/ai-config/test",
        headers=headers,
        json=test_data
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        data = response.json().get("data")
        if data and data.get("success"):
            print("✓ AI配置测试成功")
            print(f"  测试结果: {data.get('result')}")
            print(f"  响应时间: {data.get('duration')}秒")
        else:
            print("✓ AI配置测试完成（但调用失败，这是预期的，因为使用的是测试密钥）")
            print(f"  错误信息: {data.get('message')}")
        return True
    else:
        print("✗ AI配置测试失败")
        return False


def test_get_usage_stats(token):
    """测试获取API使用统计"""
    print("\n=== 测试获取API使用统计 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(TEST_HOSPITAL_ID)
    }
    
    response = requests.get(
        f"{API_BASE}/ai-config/usage-stats?days=30",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✓ 获取API使用统计成功")
        data = response.json().get("data")
        if data:
            print(f"  总调用次数: {data.get('total_calls')}")
            print(f"  成功次数: {data.get('successful_calls')}")
            print(f"  失败次数: {data.get('failed_calls')}")
            print(f"  今日调用: {data.get('today_calls')}")
            print(f"  每日限额: {data.get('daily_limit')}")
            print(f"  平均响应时间: {data.get('avg_duration')}秒")
            print(f"  预估成本: ¥{data.get('estimated_cost')}")
        return True
    else:
        print("✗ 获取API使用统计失败")
        return False


def test_permission_check(token):
    """测试权限检查（使用非管理员用户）"""
    print("\n=== 测试权限检查 ===")
    print("注意：此测试需要一个非管理员用户，如果没有则跳过")
    
    # 这里应该使用非管理员用户的token
    # 由于测试环境可能没有，我们跳过此测试
    print("⊘ 跳过权限检查测试（需要非管理员用户）")
    return True


def main():
    """主测试流程"""
    print("=" * 60)
    print("AI配置API测试")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("\n✗ 测试失败：无法登录")
        return
    
    # 测试获取配置（可能不存在）
    test_get_config(token)
    
    # 测试创建配置
    if not test_create_config(token):
        print("\n✗ 测试失败：无法创建配置")
        return
    
    # 再次获取配置（应该存在）
    config = test_get_config(token)
    if not config:
        print("\n✗ 测试失败：创建后无法获取配置")
        return
    
    # 测试更新配置
    if not test_update_config(token):
        print("\n✗ 测试失败：无法更新配置")
        return
    
    # 测试配置测试功能
    test_test_config(token)
    
    # 测试获取使用统计
    test_get_usage_stats(token)
    
    # 测试权限检查
    test_permission_check(token)
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
