"""
创建测试报告 - 使用有计算结果的科室
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)
token = response.json()["access_token"]
print(f"登录成功")

headers = {
    "Authorization": f"Bearer {token}",
    "X-Hospital-ID": str(HOSPITAL_ID)
}

# 使用有计算结果的科室 ID=4
dept_id = 4

# 获取科室信息
response = requests.get(
    f"{BASE_URL}/departments/{dept_id}",
    headers=headers
)

if response.status_code == 200:
    dept = response.json()
    print(f"使用科室: {dept['his_name']} (ID: {dept['id']})")
    
    # 创建报告
    report_data = {
        "department_id": dept_id,
        "period": "2025-10",
        "current_issues": "## 当前问题\n\n- 测试问题1\n- 测试问题2",
        "future_plans": "## 未来计划\n\n- 测试计划1\n- 测试计划2"
    }
    
    response = requests.post(
        f"{BASE_URL}/analysis-reports",
        headers=headers,
        json=report_data
    )
    
    if response.status_code == 200:
        report = response.json()
        print(f"\n报告创建成功:")
        print(f"  ID: {report['id']}")
        print(f"  科室: {report['department_name']}")
        print(f"  年月: {report['period']}")
    else:
        print(f"\n创建报告失败: {response.text}")
else:
    print(f"获取科室失败: {response.text}")
