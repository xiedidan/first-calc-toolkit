"""测试智能导入预览 API 并显示详细错误"""
import requests
import json
import sys

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

# API 配置
url = "http://127.0.0.1:8000/api/v1/dimension-items/smart-import/preview"
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": "1",  # 使用医院ID 1
    "Authorization": "Bearer YOUR_TOKEN_HERE"  # 需要替换为实际的 token
}

print("=" * 60)
print("测试智能导入预览 API")
print("=" * 60)
print(f"\nURL: {url}")
print(f"\n请求头:")
for key, value in headers.items():
    if key != "Authorization":
        print(f"  {key}: {value}")
    else:
        print(f"  {key}: Bearer ...")

print(f"\n请求体:")
print(json.dumps(data, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("发送请求...")
print("=" * 60)

try:
    response = requests.post(url, json=data, headers=headers)
    
    print(f"\n状态码: {response.status_code}")
    print(f"\n响应头:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\n响应体:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
        
        # 如果有详细错误信息，打印出来
        if "errors" in response_json:
            print("\n" + "=" * 60)
            print("详细错误信息:")
            print("=" * 60)
            for error in response_json["errors"]:
                print(f"\n错误位置: {error.get('loc', 'N/A')}")
                print(f"错误消息: {error.get('msg', 'N/A')}")
                print(f"错误类型: {error.get('type', 'N/A')}")
                if 'ctx' in error:
                    print(f"上下文: {error['ctx']}")
        
        if "traceback" in response_json:
            print("\n" + "=" * 60)
            print("堆栈跟踪:")
            print("=" * 60)
            print(response_json["traceback"])
            
    except json.JSONDecodeError:
        print(response.text)
    
    sys.exit(0 if response.status_code == 200 else 1)
    
except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败！请确保后端服务正在运行。")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
