"""
测试指标项目API
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试用医疗机构ID

# 获取token（需要先登录）
def get_token():
    """获取认证token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json().get("data", {}).get("access_token")
    print(f"登录失败: {response.text}")
    return None


def test_metric_projects_api():
    """测试指标项目API"""
    token = get_token()
    if not token:
        print("无法获取token，跳过测试")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID),
        "Content-Type": "application/json"
    }
    
    print("=" * 50)
    print("测试指标项目API")
    print("=" * 50)
    
    # 1. 获取项目列表
    print("\n1. 获取项目列表...")
    response = requests.get(f"{BASE_URL}/metric-projects", headers=headers)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   项目数量: {data.get('data', {}).get('total', 0)}")
    else:
        print(f"   错误: {response.text}")
    
    # 2. 创建项目
    print("\n2. 创建项目...")
    create_data = {
        "name": "测试项目-API测试",
        "description": "这是一个API测试创建的项目"
    }
    response = requests.post(
        f"{BASE_URL}/metric-projects",
        headers=headers,
        json=create_data
    )
    print(f"   状态码: {response.status_code}")
    project_id = None
    if response.status_code == 200:
        data = response.json()
        project_id = data.get("data", {}).get("id")
        print(f"   创建成功，项目ID: {project_id}")
    else:
        print(f"   错误: {response.text}")
    
    if project_id:
        # 3. 获取项目详情
        print(f"\n3. 获取项目详情 (ID={project_id})...")
        response = requests.get(
            f"{BASE_URL}/metric-projects/{project_id}",
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   项目名称: {data.get('data', {}).get('name')}")
        else:
            print(f"   错误: {response.text}")
        
        # 4. 更新项目
        print(f"\n4. 更新项目 (ID={project_id})...")
        update_data = {
            "name": "测试项目-已更新",
            "description": "描述已更新"
        }
        response = requests.put(
            f"{BASE_URL}/metric-projects/{project_id}",
            headers=headers,
            json=update_data
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   更新后名称: {data.get('data', {}).get('name')}")
        else:
            print(f"   错误: {response.text}")
        
        # 5. 删除项目
        print(f"\n5. 删除项目 (ID={project_id})...")
        response = requests.delete(
            f"{BASE_URL}/metric-projects/{project_id}",
            headers=headers
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   删除成功")
        else:
            print(f"   错误: {response.text}")
    
    # 6. 测试重排序（需要先创建多个项目）
    print("\n6. 测试重排序...")
    # 创建两个测试项目
    project_ids = []
    for i in range(2):
        response = requests.post(
            f"{BASE_URL}/metric-projects",
            headers=headers,
            json={"name": f"排序测试项目{i+1}"}
        )
        if response.status_code == 200:
            pid = response.json().get("data", {}).get("id")
            project_ids.append(pid)
            print(f"   创建项目{i+1}: ID={pid}")
    
    if len(project_ids) == 2:
        # 反转顺序
        reorder_data = {"project_ids": list(reversed(project_ids))}
        response = requests.put(
            f"{BASE_URL}/metric-projects/reorder",
            headers=headers,
            json=reorder_data
        )
        print(f"   重排序状态码: {response.status_code}")
        if response.status_code == 200:
            print("   重排序成功")
        else:
            print(f"   错误: {response.text}")
        
        # 清理测试数据
        for pid in project_ids:
            requests.delete(f"{BASE_URL}/metric-projects/{pid}", headers=headers)
        print("   已清理测试数据")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_metric_projects_api()
