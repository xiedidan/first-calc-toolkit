"""
测试数据源ID=1的连接
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/data-sources"

print("1. 获取数据源ID=1的详细信息...")
try:
    response = requests.get(f"{BASE_URL}/1")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"\n数据源信息:")
        print(f"名称: {data['name']}")
        print(f"数据库类型: {data['db_type']}")
        print(f"主机: {data['host']}")
        print(f"端口: {data['port']}")
        print(f"数据库名: {data['database_name']}")
        print(f"用户名: {data['username']}")
        print(f"Schema: {data.get('schema_name', 'N/A')}")
    else:
        print(f"获取失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"请求失败: {str(e)}")

print("\n2. 测试数据源ID=1的连接...")
try:
    response = requests.post(f"{BASE_URL}/1/test")
    if response.status_code == 200:
        result = response.json()["data"]
        print(f"\n测试结果:")
        print(f"成功: {result['success']}")
        print(f"消息: {result['message']}")
        print(f"耗时: {result.get('duration_ms', 'N/A')}ms")
        if not result['success']:
            print(f"错误: {result.get('error', 'N/A')}")
    else:
        print(f"测试失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"请求失败: {str(e)}")
