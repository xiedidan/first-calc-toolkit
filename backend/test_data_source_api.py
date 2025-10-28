"""
测试数据源管理API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_create_data_source():
    """测试创建数据源"""
    print("\n=== 测试创建数据源 ===")
    
    data = {
        "name": "测试PostgreSQL数据源",
        "db_type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database_name": "test_db",
        "username": "test_user",
        "password": "test_password",
        "schema_name": "public",
        "is_default": True,
        "is_enabled": True,
        "description": "这是一个测试数据源",
        "pool_size_min": 2,
        "pool_size_max": 10,
        "pool_timeout": 30
    }
    
    response = requests.post(f"{BASE_URL}/data-sources", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        return response.json()["data"]["id"]
    return None


def test_get_data_sources():
    """测试获取数据源列表"""
    print("\n=== 测试获取数据源列表 ===")
    
    response = requests.get(f"{BASE_URL}/data-sources?page=1&size=10")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_get_data_source(data_source_id):
    """测试获取数据源详情"""
    print(f"\n=== 测试获取数据源详情 (ID: {data_source_id}) ===")
    
    response = requests.get(f"{BASE_URL}/data-sources/{data_source_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_update_data_source(data_source_id):
    """测试更新数据源"""
    print(f"\n=== 测试更新数据源 (ID: {data_source_id}) ===")
    
    data = {
        "description": "更新后的描述信息",
        "pool_size_max": 20
    }
    
    response = requests.put(f"{BASE_URL}/data-sources/{data_source_id}", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_test_connection(data_source_id):
    """测试数据源连接"""
    print(f"\n=== 测试数据源连接 (ID: {data_source_id}) ===")
    
    response = requests.post(f"{BASE_URL}/data-sources/{data_source_id}/test")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_toggle_data_source(data_source_id):
    """测试切换数据源状态"""
    print(f"\n=== 测试切换数据源状态 (ID: {data_source_id}) ===")
    
    response = requests.put(f"{BASE_URL}/data-sources/{data_source_id}/toggle")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_set_default(data_source_id):
    """测试设置默认数据源"""
    print(f"\n=== 测试设置默认数据源 (ID: {data_source_id}) ===")
    
    response = requests.put(f"{BASE_URL}/data-sources/{data_source_id}/set-default")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_get_pool_status(data_source_id):
    """测试获取连接池状态"""
    print(f"\n=== 测试获取连接池状态 (ID: {data_source_id}) ===")
    
    response = requests.get(f"{BASE_URL}/data-sources/{data_source_id}/pool-status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete_data_source(data_source_id):
    """测试删除数据源"""
    print(f"\n=== 测试删除数据源 (ID: {data_source_id}) ===")
    
    response = requests.delete(f"{BASE_URL}/data-sources/{data_source_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("开始测试数据源管理API...")
    
    # 创建数据源
    data_source_id = test_create_data_source()
    
    if data_source_id:
        # 获取数据源列表
        test_get_data_sources()
        
        # 获取数据源详情
        test_get_data_source(data_source_id)
        
        # 更新数据源
        test_update_data_source(data_source_id)
        
        # 测试连接
        test_test_connection(data_source_id)
        
        # 切换状态
        test_toggle_data_source(data_source_id)
        
        # 再次切换状态（恢复启用）
        test_toggle_data_source(data_source_id)
        
        # 设置为默认
        test_set_default(data_source_id)
        
        # 获取连接池状态
        test_get_pool_status(data_source_id)
        
        # 删除数据源
        test_delete_data_source(data_source_id)
    
    print("\n测试完成！")
