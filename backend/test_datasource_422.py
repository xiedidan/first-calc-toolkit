"""测试数据源 API 422 错误"""
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 测试不同的参数组合
test_cases = [
    {"name": "无参数", "params": {}},
    {"name": "只有 page", "params": {"page": 1}},
    {"name": "page 和 size", "params": {"page": 1, "size": 10}},
    {"name": "page 和 size (字符串)", "params": {"page": "1", "size": "10"}},
    {"name": "完整参数", "params": {"page": 1, "size": 1000, "keyword": "", "db_type": None, "is_enabled": None}},
]

print("=" * 70)
print("测试数据源 API 参数")
print("=" * 70)

for test in test_cases:
    print(f"\n测试: {test['name']}")
    print(f"参数: {test['params']}")
    
    try:
        response = requests.get(f"{BASE_URL}/data-sources", params=test['params'])
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 成功! 返回 {data.get('data', {}).get('total', 0)} 条数据")
        else:
            print(f"✗ 失败!")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 异常: {e}")

print("\n" + "=" * 70)
