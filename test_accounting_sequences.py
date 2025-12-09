"""
测试科室核算序列字段功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的认证信息
def get_auth_headers():
    """获取认证头"""
    # 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        hospital_id = response.json()["user"]["hospital_id"]
        return {
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": str(hospital_id)
        }
    else:
        print(f"登录失败: {response.text}")
        return None

def test_get_departments():
    """测试获取科室列表"""
    print("\n=== 测试获取科室列表 ===")
    headers = get_auth_headers()
    if not headers:
        return
    
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"总数: {data['total']}")
        if data['items']:
            dept = data['items'][0]
            print(f"第一个科室: {dept['his_name']}")
            print(f"核算序列: {dept.get('accounting_sequences', [])}")
    else:
        print(f"错误: {response.text}")

def test_create_department():
    """测试创建科室（带核算序列）"""
    print("\n=== 测试创建科室 ===")
    headers = get_auth_headers()
    if not headers:
        return
    
    dept_data = {
        "his_code": "TEST001",
        "his_name": "测试科室001",
        "accounting_sequences": ["医生", "护理"],
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/departments", headers=headers, json=dept_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        dept = response.json()
        print(f"创建成功: ID={dept['id']}, 名称={dept['his_name']}")
        print(f"核算序列: {dept.get('accounting_sequences', [])}")
        return dept['id']
    else:
        print(f"错误: {response.text}")
        return None

def test_update_department(dept_id):
    """测试更新科室核算序列"""
    print(f"\n=== 测试更新科室 (ID={dept_id}) ===")
    headers = get_auth_headers()
    if not headers:
        return
    
    update_data = {
        "accounting_sequences": ["医生", "护理", "医技"]
    }
    
    response = requests.put(f"{BASE_URL}/departments/{dept_id}", headers=headers, json=update_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        dept = response.json()
        print(f"更新成功: {dept['his_name']}")
        print(f"核算序列: {dept.get('accounting_sequences', [])}")
    else:
        print(f"错误: {response.text}")

def test_clear_sequences(dept_id):
    """测试清空核算序列"""
    print(f"\n=== 测试清空核算序列 (ID={dept_id}) ===")
    headers = get_auth_headers()
    if not headers:
        return
    
    update_data = {
        "accounting_sequences": []
    }
    
    response = requests.put(f"{BASE_URL}/departments/{dept_id}", headers=headers, json=update_data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        dept = response.json()
        print(f"清空成功: {dept['his_name']}")
        print(f"核算序列: {dept.get('accounting_sequences', [])}")
    else:
        print(f"错误: {response.text}")

def test_delete_department(dept_id):
    """测试删除科室"""
    print(f"\n=== 测试删除科室 (ID={dept_id}) ===")
    headers = get_auth_headers()
    if not headers:
        return
    
    response = requests.delete(f"{BASE_URL}/departments/{dept_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("删除成功")
    else:
        print(f"错误: {response.text}")

if __name__ == '__main__':
    print("开始测试科室核算序列功能...")
    
    # 1. 获取现有科室列表
    test_get_departments()
    
    # 2. 创建新科室（带核算序列）
    dept_id = test_create_department()
    
    if dept_id:
        # 3. 更新核算序列
        test_update_department(dept_id)
        
        # 4. 清空核算序列
        test_clear_sequences(dept_id)
        
        # 5. 删除测试科室
        test_delete_department(dept_id)
    
    print("\n测试完成！")
