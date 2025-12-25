"""检查2024-11任务状态"""
import requests

BASE_URL = 'http://localhost:8000/api/v1'
HOSPITAL_ID = 1

resp = requests.post(f'{BASE_URL}/auth/login', json={'username': 'admin', 'password': 'admin123'})
token = resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'X-Hospital-ID': str(HOSPITAL_ID)}

resp = requests.get(f'{BASE_URL}/calculation/tasks', headers=headers, params={'page': 1, 'size': 100})
if resp.status_code == 200:
    tasks = resp.json().get('items', [])
    print("2024-11 任务:")
    for t in tasks:
        if t.get('period') == '2024-11':
            print(f"  Task ID: {t.get('task_id')}")
            print(f"  Status: {t.get('status')}")
            print(f"  Progress: {t.get('progress')}%")
            print()
    
    # 统计各月份已有任务
    print("\n各月份任务统计:")
    periods = {}
    for t in tasks:
        p = t.get('period', 'N/A')
        s = t.get('status', 'N/A')
        if p not in periods:
            periods[p] = {'completed': 0, 'running': 0, 'pending': 0, 'failed': 0, 'cancelled': 0}
        if s in periods[p]:
            periods[p][s] += 1
    
    for p in sorted(periods.keys()):
        stats = periods[p]
        print(f"  {p}: completed={stats['completed']}, running={stats['running']}, pending={stats['pending']}, failed={stats['failed']}")
