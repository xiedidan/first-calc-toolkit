import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = 'http://localhost:8000/api'

# 登录获取token
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
print('正在登录...')
response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
if response.status_code != 200:
    print(f'登录失败: {response.text}')
    exit(1)

token = response.json()['access_token']
headers = {
    'Authorization': f'Bearer {token}',
    'X-Hospital-ID': '1'
}
print('登录成功')

# 创建计算任务
task_data = {
    'model_version_id': 7,
    'workflow_id': 22,
    'period': '2025-01',
    'description': 'API测试-标准计算流程验证'
}

print(f'\n创建计算任务...')
print(f'参数: {json.dumps(task_data, ensure_ascii=False, indent=2)}')

response = requests.post(
    f'{BASE_URL}/calculation-tasks/tasks',
    json=task_data,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f'\n✓ 任务创建成功!')
    print(f'任务ID: {result["task_id"]}')
    print(f'状态: {result["status"]}')
    print(f'创建时间: {result["created_at"]}')
    print(f'\n请等待任务执行完成，可以通过以下命令查询任务状态:')
    print(f'GET {BASE_URL}/calculation-tasks/tasks/{result["task_id"]}')
else:
    print(f'\n✗ 任务创建失败')
    print(f'状态码: {response.status_code}')
    print(f'错误信息: {response.text}')
