"""
测试指标API - 智能问数系统
验证指标管理的CRUD操作和关联管理功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1  # 测试用医疗机构ID

# 请求头
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": str(HOSPITAL_ID),
}


def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers["Authorization"] = f"Bearer {token}"
        print("✓ 登录成功")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False


def test_create_project():
    """测试创建指标项目"""
    print("\n=== 测试创建指标项目 ===")
    response = requests.post(
        f"{BASE_URL}/metric-projects",
        headers=headers,
        json={
            "name": f"测试项目_{datetime.now().strftime('%H%M%S')}",
            "description": "API测试创建的项目",
        },
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    if response.status_code == 200:
        return data.get("data", {}).get("id")
    return None


def test_create_topic(project_id: int):
    """测试创建指标主题"""
    print("\n=== 测试创建指标主题 ===")
    response = requests.post(
        f"{BASE_URL}/metric-topics",
        headers=headers,
        json={
            "project_id": project_id,
            "name": f"测试主题_{datetime.now().strftime('%H%M%S')}",
            "description": "API测试创建的主题",
        },
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    if response.status_code == 200:
        return data.get("data", {}).get("id")
    return None


def test_create_metric(topic_id: int):
    """测试创建指标"""
    print("\n=== 测试创建指标 ===")
    response = requests.post(
        f"{BASE_URL}/metrics",
        headers=headers,
        json={
            "topic_id": topic_id,
            "name_cn": f"测试指标_{datetime.now().strftime('%H%M%S')}",
            "name_en": "test_metric",
            "metric_type": "atomic",
            "metric_level": "L1",
            "business_caliber": "测试业务口径",
            "technical_caliber": "测试技术口径",
            "source_table": "test_table",
            "dimension_tables": ["dim_table1", "dim_table2"],
            "dimensions": ["dim1", "dim2"],
        },
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    if response.status_code == 200:
        return data.get("data", {}).get("id")
    return None


def test_get_metric_tree():
    """测试获取指标树"""
    print("\n=== 测试获取指标树 ===")
    response = requests.get(
        f"{BASE_URL}/metrics/tree",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_list_metrics():
    """测试获取指标列表"""
    print("\n=== 测试获取指标列表 ===")
    response = requests.get(
        f"{BASE_URL}/metrics",
        headers=headers,
        params={"page": 1, "size": 10},
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_get_metric(metric_id: int):
    """测试获取指标详情"""
    print(f"\n=== 测试获取指标详情 (id={metric_id}) ===")
    response = requests.get(
        f"{BASE_URL}/metrics/{metric_id}",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_update_metric(metric_id: int):
    """测试更新指标"""
    print(f"\n=== 测试更新指标 (id={metric_id}) ===")
    response = requests.put(
        f"{BASE_URL}/metrics/{metric_id}",
        headers=headers,
        json={
            "name_cn": f"更新后的指标_{datetime.now().strftime('%H%M%S')}",
            "business_caliber": "更新后的业务口径",
        },
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_create_metric_relation(source_id: int, target_id: int):
    """测试创建指标关联"""
    print(f"\n=== 测试创建指标关联 (source={source_id}, target={target_id}) ===")
    response = requests.post(
        f"{BASE_URL}/metrics/{source_id}/relations",
        headers=headers,
        json={
            "target_metric_id": target_id,
            "relation_type": "component",
        },
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_get_metric_relations(metric_id: int):
    """测试获取指标关联"""
    print(f"\n=== 测试获取指标关联 (id={metric_id}) ===")
    response = requests.get(
        f"{BASE_URL}/metrics/{metric_id}/relations",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_get_affected_metrics(metric_id: int):
    """测试获取受影响的指标"""
    print(f"\n=== 测试获取受影响的指标 (id={metric_id}) ===")
    response = requests.get(
        f"{BASE_URL}/metrics/{metric_id}/affected",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_delete_metric_relation(source_id: int, target_id: int):
    """测试删除指标关联"""
    print(f"\n=== 测试删除指标关联 (source={source_id}, target={target_id}) ===")
    response = requests.delete(
        f"{BASE_URL}/metrics/{source_id}/relations/{target_id}",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def test_delete_metric(metric_id: int, force: bool = False):
    """测试删除指标"""
    print(f"\n=== 测试删除指标 (id={metric_id}, force={force}) ===")
    response = requests.delete(
        f"{BASE_URL}/metrics/{metric_id}",
        headers=headers,
        params={"force": force},
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def cleanup(project_id: int):
    """清理测试数据"""
    print(f"\n=== 清理测试数据 (project_id={project_id}) ===")
    response = requests.delete(
        f"{BASE_URL}/metric-projects/{project_id}",
        headers=headers,
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    return response.status_code == 200


def main():
    """主测试流程"""
    print("=" * 60)
    print("指标API测试")
    print("=" * 60)
    
    # 登录
    if not login():
        return
    
    # 创建测试数据
    project_id = test_create_project()
    if not project_id:
        print("创建项目失败，终止测试")
        return
    
    topic_id = test_create_topic(project_id)
    if not topic_id:
        print("创建主题失败，终止测试")
        cleanup(project_id)
        return
    
    # 创建两个指标用于测试关联
    metric_id_1 = test_create_metric(topic_id)
    if not metric_id_1:
        print("创建指标1失败，终止测试")
        cleanup(project_id)
        return
    
    metric_id_2 = test_create_metric(topic_id)
    if not metric_id_2:
        print("创建指标2失败，终止测试")
        cleanup(project_id)
        return
    
    # 测试指标树
    test_get_metric_tree()
    
    # 测试指标列表
    test_list_metrics()
    
    # 测试获取指标详情
    test_get_metric(metric_id_1)
    
    # 测试更新指标
    test_update_metric(metric_id_1)
    
    # 测试创建关联
    test_create_metric_relation(metric_id_1, metric_id_2)
    
    # 测试获取关联
    test_get_metric_relations(metric_id_1)
    
    # 测试获取受影响的指标（metric_id_2被metric_id_1引用）
    test_get_affected_metrics(metric_id_2)
    
    # 测试删除关联
    test_delete_metric_relation(metric_id_1, metric_id_2)
    
    # 测试删除指标
    test_delete_metric(metric_id_2)
    
    # 清理测试数据
    cleanup(project_id)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
