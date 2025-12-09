"""简单测试 API 端点，查看详细错误"""
import requests
import json

# 测试数据
data = {
    "session_id": "test-session-id",
    "value_mapping": [
        {
            "value": "测试值",
            "source": "dimension_plan",
            "dimension_codes": ["test-code"]
        }
    ]
}

url = "http://127.0.0.1:8000/api/v1/dimension-items/smart-import/preview"

print("测试 API 端点...")
print(f"URL: {url}")
print(f"\n请求数据:")
print(json.dumps(data, ensure_ascii=False, indent=2))

try:
    # 不带认证头，看看会返回什么错误
    response = requests.post(url, json=data)
    
    print(f"\n状态码: {response.status_code}")
    print(f"\n响应:")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except:
        print(response.text)
        
except Exception as e:
    print(f"\n错误: {e}")
