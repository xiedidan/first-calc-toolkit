"""
测试连接修复验证脚本
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1/data-sources"

# 测试数据 - 故意使用错误的配置
test_config = {
    "name": "测试错误连接",
    "db_type": "postgresql",
    "host": "wrong-host.example.com",
    "port": 5432,
    "database_name": "wrong_database",
    "username": "wrong_user",
    "password": "wrong_password",
    "is_default": False,
    "is_enabled": True,
    "pool_size_min": 2,
    "pool_size_max": 10,
    "pool_timeout": 30
}

print("测试使用错误配置的连接...")
print(f"配置: {json.dumps(test_config, indent=2, ensure_ascii=False)}")
print("\n发送测试请求...")

try:
    response = requests.post(
        f"{BASE_URL}/test-connection",
        json=test_config,
        timeout=10
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        result = response.json()
        data = result.get("data", {})
        
        if data.get("success"):
            print("\n❌ 错误：使用错误配置的连接测试通过了！这不应该发生。")
        else:
            print("\n✅ 正确：连接测试失败，符合预期。")
            print(f"错误信息: {data.get('error')}")
    else:
        print(f"\n请求失败: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n✅ 正确：连接超时，符合预期。")
except Exception as e:
    print(f"\n发生异常: {str(e)}")
