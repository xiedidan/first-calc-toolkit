"""
医疗机构管理API测试脚本

用于快速测试医疗机构管理功能是否正常工作
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_hospital_management():
    """测试医疗机构管理功能"""
    
    print("=" * 60)
    print("医疗机构管理API测试")
    print("=" * 60)
    
    # 1. 测试获取医疗机构列表
    print("\n1. 测试获取医疗机构列表...")
    try:
        response = requests.get(f"{BASE_URL}/hospitals")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"总数: {data.get('total', 0)}")
            print(f"医疗机构列表:")
            for item in data.get('items', []):
                print(f"  - ID: {item['id']}, 编码: {item['code']}, 名称: {item['name']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试创建医疗机构
    print("\n2. 测试创建医疗机构...")
    try:
        new_hospital = {
            "code": "test_hospital",
            "name": "测试医院",
            "is_active": True
        }
        response = requests.post(
            f"{BASE_URL}/hospitals",
            json=new_hospital
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"创建成功: ID={data['id']}, 编码={data['code']}, 名称={data['name']}")
            hospital_id = data['id']
        else:
            print(f"错误: {response.text}")
            hospital_id = None
    except Exception as e:
        print(f"请求失败: {e}")
        hospital_id = None
    
    # 3. 测试获取可访问的医疗机构列表
    print("\n3. 测试获取可访问的医疗机构列表...")
    try:
        response = requests.get(f"{BASE_URL}/hospitals/accessible")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"可访问的医疗机构:")
            for item in data:
                print(f"  - ID: {item['id']}, 编码: {item['code']}, 名称: {item['name']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 4. 测试激活医疗机构
    if hospital_id:
        print(f"\n4. 测试激活医疗机构 (ID={hospital_id})...")
        try:
            response = requests.post(f"{BASE_URL}/hospitals/{hospital_id}/activate")
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"激活成功: {data['message']}")
                print(f"医疗机构: {data['hospital_name']}")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 5. 测试更新医疗机构
    if hospital_id:
        print(f"\n5. 测试更新医疗机构 (ID={hospital_id})...")
        try:
            update_data = {
                "name": "测试医院（已更新）",
                "is_active": True
            }
            response = requests.put(
                f"{BASE_URL}/hospitals/{hospital_id}",
                json=update_data
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"更新成功: 名称={data['name']}")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    # 6. 测试删除医疗机构
    if hospital_id:
        print(f"\n6. 测试删除医疗机构 (ID={hospital_id})...")
        try:
            response = requests.delete(f"{BASE_URL}/hospitals/{hospital_id}")
            print(f"状态码: {response.status_code}")
            if response.status_code == 204:
                print("删除成功")
            else:
                print(f"错误: {response.text}")
        except Exception as e:
            print(f"请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    print("注意: 此测试需要后端服务正在运行 (http://localhost:8000)")
    print("注意: 此测试需要有效的认证令牌")
    print()
    
    # 运行测试
    test_hospital_management()
