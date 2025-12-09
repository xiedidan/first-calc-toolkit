"""测试智能导入预览API"""
import requests
import json

# 测试数据
data = {
    "session_id": "16bfb418-a9e8-4090-80c8-bdd657803a3f",
    "value_mapping": [
        {
            "value": "护理-病区护理-术中护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-op"]
        },
        {
            "value": "护理-病区护理-拓展护理",
            "source": "dimension_plan",
            "dimension_codes": ["dim-nur-ward-extra"]
        }
    ]
}

# 发送请求
url = "http://127.0.0.1:3000/api/v1/dimension-items/smart-import/preview"
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": "1"  # 添加医院ID
}

print("发送请求...")
print(json.dumps(data, ensure_ascii=False, indent=2))

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\n状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")
