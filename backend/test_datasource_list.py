"""测试数据源列表API"""
import requests

# 测试获取数据源列表
response = requests.get('http://127.0.0.1:3000/api/v1/data-sources?page=1&size=1000')
print(f'状态码: {response.status_code}')
try:
    print(f'响应: {response.json()}')
except Exception as e:
    print(f'响应文本: {response.text}')
    print(f'错误: {e}')
