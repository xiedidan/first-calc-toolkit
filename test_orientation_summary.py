"""
测试导向汇总功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# 登录获取token
def login():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "root"
        }
    )
    
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        raise Exception("登录失败")
    
    return response.json()["access_token"]

# 获取医疗机构列表
def get_hospitals(token):
    response = requests.get(
        f"{BASE_URL}/api/v1/hospitals",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# 激活医疗机构
def activate_hospital(token, hospital_id):
    response = requests.post(
        f"{BASE_URL}/api/v1/hospitals/{hospital_id}/activate",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

# 获取计算任务列表
def get_tasks(token, hospital_id, period="2025-10"):
    response = requests.get(
        f"{BASE_URL}/api/v1/calculation/tasks",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": str(hospital_id)
        },
        params={
            "period": period,
            "status": "completed",
            "page": 1,
            "size": 10
        }
    )
    return response.json()

# 获取导向汇总数据
def get_orientation_summary(token, hospital_id, task_id, dept_id=None):
    params = {"task_id": task_id}
    if dept_id:
        params["dept_id"] = dept_id
    
    response = requests.get(
        f"{BASE_URL}/api/v1/calculation/results/orientation-summary",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": str(hospital_id)
        },
        params=params
    )
    return response.json()

# 获取科室明细（验证导向名称显示）
def get_department_detail(token, hospital_id, task_id, dept_id):
    response = requests.get(
        f"{BASE_URL}/api/v1/calculation/results/detail",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": str(hospital_id)
        },
        params={
            "task_id": task_id,
            "dept_id": dept_id
        }
    )
    return response.json()

def main():
    print("=== 测试导向汇总功能 ===\n")
    
    # 1. 登录
    print("1. 登录...")
    token = login()
    print(f"   Token: {token[:20]}...\n")
    
    # 2. 获取医疗机构
    print("2. 获取医疗机构...")
    hospitals = get_hospitals(token)
    if not hospitals:
        print("   错误：没有医疗机构")
        return
    
    hospital = hospitals[0]
    hospital_id = hospital["id"]
    print(f"   医疗机构: {hospital['name']} (ID: {hospital_id})\n")
    
    # 3. 激活医疗机构
    print("3. 激活医疗机构...")
    activate_hospital(token, hospital_id)
    print("   已激活\n")
    
    # 4. 获取计算任务
    print("4. 获取计算任务...")
    tasks_response = get_tasks(token, hospital_id)
    if not tasks_response.get("items"):
        print("   错误：没有已完成的计算任务")
        return
    
    task = tasks_response["items"][0]
    task_id = task["task_id"]
    print(f"   任务ID: {task_id}")
    print(f"   周期: {task['period']}\n")
    
    # 5. 测试导向汇总（全院）
    print("5. 测试导向汇总（全院）...")
    try:
        orientation_data = get_orientation_summary(token, hospital_id, task_id)
        print(f"   返回数据结构: {list(orientation_data.keys())}")
        print(f"   医生序列记录数: {len(orientation_data.get('doctor', []))}")
        print(f"   护理序列记录数: {len(orientation_data.get('nurse', []))}")
        print(f"   医技序列记录数: {len(orientation_data.get('tech', []))}")
        
        # 显示第一条记录示例
        if orientation_data.get('doctor'):
            print("\n   医生序列第一条记录:")
            first_record = orientation_data['doctor'][0]
            print(f"     科室: {first_record.get('department_name')}")
            print(f"     维度: {first_record.get('node_name')}")
            print(f"     导向规则: {first_record.get('orientation_rule_name')}")
            print(f"     是否调整: {first_record.get('is_adjusted')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n6. 测试科室明细（验证导向名称）...")
    try:
        # 获取第一个科室的明细
        summary_response = requests.get(
            f"{BASE_URL}/api/v1/calculation/results/summary",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Hospital-ID": str(hospital_id)
            },
            params={"task_id": task_id}
        ).json()
        
        if summary_response.get("departments"):
            dept = summary_response["departments"][0]
            dept_id = dept["department_id"]
            dept_name = dept["department_name"]
            
            print(f"   科室: {dept_name} (ID: {dept_id})")
            
            detail_data = get_department_detail(token, hospital_id, task_id, dept_id)
            
            # 检查医生序列的第一个维度
            if detail_data.get("doctor"):
                first_node = detail_data["doctor"][0]
                print(f"   第一个节点: {first_node.get('dimension_name')}")
                print(f"   业务导向: {first_node.get('business_guide', '未设置')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
