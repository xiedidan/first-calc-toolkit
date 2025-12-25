"""
测试指标主题API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = "1"

# 登录获取token
def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["data"]["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": HOSPITAL_ID,
        "Content-Type": "application/json"
    }

def test_metric_topics_api():
    """测试指标主题API"""
    token = login()
    if not token:
        print("无法获取token，测试终止")
        return
    
    headers = get_headers(token)
    
    print("\n" + "="*60)
    print("测试指标主题API")
    print("="*60)
    
    # 1. 首先创建一个项目（主题需要关联项目）
    print("\n1. 创建测试项目...")
    project_data = {
        "name": "测试项目-主题API测试",
        "description": "用于测试主题API的项目"
    }
    response = requests.post(
        f"{BASE_URL}/metric-projects",
        headers=headers,
        json=project_data
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        project = response.json()["data"]
        project_id = project["id"]
        print(f"   创建成功: id={project_id}, name={project['name']}")
    else:
        print(f"   创建失败: {response.text}")
        return
    
    # 2. 获取主题列表（应该为空）
    print("\n2. 获取主题列表（按项目筛选）...")
    response = requests.get(
        f"{BASE_URL}/metric-topics?project_id={project_id}",
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"   主题数量: {data['total']}")
    else:
        print(f"   获取失败: {response.text}")
    
    # 3. 创建主题
    print("\n3. 创建主题...")
    topic_data = {
        "project_id": project_id,
        "name": "测试主题1",
        "description": "这是第一个测试主题"
    }
    response = requests.post(
        f"{BASE_URL}/metric-topics",
        headers=headers,
        json=topic_data
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        topic1 = response.json()["data"]
        topic1_id = topic1["id"]
        print(f"   创建成功: id={topic1_id}, name={topic1['name']}, project_name={topic1.get('project_name')}")
    else:
        print(f"   创建失败: {response.text}")
        # 清理项目
        requests.delete(f"{BASE_URL}/metric-projects/{project_id}", headers=headers)
        return
    
    # 4. 创建第二个主题
    print("\n4. 创建第二个主题...")
    topic_data2 = {
        "project_id": project_id,
        "name": "测试主题2",
        "description": "这是第二个测试主题"
    }
    response = requests.post(
        f"{BASE_URL}/metric-topics",
        headers=headers,
        json=topic_data2
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        topic2 = response.json()["data"]
        topic2_id = topic2["id"]
        print(f"   创建成功: id={topic2_id}, name={topic2['name']}")
    else:
        print(f"   创建失败: {response.text}")
    
    # 5. 获取主题详情
    print(f"\n5. 获取主题详情 (id={topic1_id})...")
    response = requests.get(
        f"{BASE_URL}/metric-topics/{topic1_id}",
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        topic = response.json()["data"]
        print(f"   主题详情: name={topic['name']}, project_name={topic.get('project_name')}, metric_count={topic.get('metric_count')}")
    else:
        print(f"   获取失败: {response.text}")
    
    # 6. 更新主题
    print(f"\n6. 更新主题 (id={topic1_id})...")
    update_data = {
        "name": "测试主题1-已更新",
        "description": "更新后的描述"
    }
    response = requests.put(
        f"{BASE_URL}/metric-topics/{topic1_id}",
        headers=headers,
        json=update_data
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        topic = response.json()["data"]
        print(f"   更新成功: name={topic['name']}, description={topic.get('description')}")
    else:
        print(f"   更新失败: {response.text}")
    
    # 7. 获取主题列表
    print("\n7. 获取主题列表...")
    response = requests.get(
        f"{BASE_URL}/metric-topics?project_id={project_id}",
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"   主题数量: {data['total']}")
        for item in data["items"]:
            print(f"   - id={item['id']}, name={item['name']}, sort_order={item['sort_order']}")
    else:
        print(f"   获取失败: {response.text}")
    
    # 8. 重新排序主题
    print("\n8. 重新排序主题...")
    reorder_data = {
        "topic_ids": [topic2_id, topic1_id]  # 交换顺序
    }
    response = requests.put(
        f"{BASE_URL}/metric-topics/reorder",
        headers=headers,
        json=reorder_data
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   排序更新成功")
    else:
        print(f"   排序更新失败: {response.text}")
    
    # 9. 验证排序结果
    print("\n9. 验证排序结果...")
    response = requests.get(
        f"{BASE_URL}/metric-topics?project_id={project_id}",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()["data"]
        for item in data["items"]:
            print(f"   - id={item['id']}, name={item['name']}, sort_order={item['sort_order']}")
    
    # 10. 测试重复名称
    print("\n10. 测试重复名称...")
    duplicate_data = {
        "project_id": project_id,
        "name": "测试主题1-已更新",  # 与已存在的名称相同
        "description": "重复名称测试"
    }
    response = requests.post(
        f"{BASE_URL}/metric-topics",
        headers=headers,
        json=duplicate_data
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"   正确拒绝重复名称: {response.json().get('detail')}")
    else:
        print(f"   响应: {response.text}")
    
    # 11. 删除主题
    print(f"\n11. 删除主题 (id={topic1_id})...")
    response = requests.delete(
        f"{BASE_URL}/metric-topics/{topic1_id}",
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()["data"]
        print(f"   删除成功, 级联删除指标数: {result.get('deleted_metrics', 0)}")
    else:
        print(f"   删除失败: {response.text}")
    
    # 12. 清理：删除测试项目（会级联删除剩余主题）
    print(f"\n12. 清理：删除测试项目 (id={project_id})...")
    response = requests.delete(
        f"{BASE_URL}/metric-projects/{project_id}",
        headers=headers
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()["data"]
        print(f"   删除成功, 级联删除主题数: {result.get('deleted_topics', 0)}, 指标数: {result.get('deleted_metrics', 0)}")
    else:
        print(f"   删除失败: {response.text}")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)


if __name__ == "__main__":
    test_metric_topics_api()
