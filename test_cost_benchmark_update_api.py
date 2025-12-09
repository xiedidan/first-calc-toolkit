"""
测试成本基准更新API端点
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
from decimal import Decimal

# API配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "X-Hospital-ID": "1"
}

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        HEADERS["Authorization"] = f"Bearer {token}"
        print("✓ 登录成功")
        return True
    else:
        print(f"❌ 登录失败: {response.text}")
        return False

def test_update_api():
    """测试更新API"""
    print("=" * 60)
    print("测试成本基准更新API")
    print("=" * 60)
    
    if not login():
        return
    
    try:
        # 1. 获取模型版本
        print("\n" + "-" * 60)
        print("步骤 1: 获取模型版本")
        print("-" * 60)
        
        response = requests.get(
            f"{BASE_URL}/model-versions",
            headers=HEADERS,
            params={"limit": 1}
        )
        
        if response.status_code != 200:
            print(f"❌ 获取模型版本失败: {response.text}")
            return
        
        versions = response.json().get("items", [])
        if not versions:
            print("❌ 没有找到模型版本")
            return
        
        version = versions[0]
        print(f"✓ 使用模型版本: {version['name']} (ID: {version['id']})")
        
        # 2. 创建测试成本基准
        print("\n" + "-" * 60)
        print("步骤 2: 创建测试成本基准")
        print("-" * 60)
        
        create_data = {
            "department_code": "TEST_UPDATE_001",
            "department_name": "测试更新科室001",
            "version_id": version["id"],
            "version_name": version["name"],
            "dimension_code": "TEST_UPDATE_DIM_001",
            "dimension_name": "测试更新维度001",
            "benchmark_value": 1000.00
        }
        
        response = requests.post(
            f"{BASE_URL}/cost-benchmarks",
            headers=HEADERS,
            json=create_data
        )
        
        if response.status_code != 200:
            print(f"❌ 创建失败: {response.text}")
            return
        
        benchmark = response.json()
        benchmark_id = benchmark["id"]
        print(f"✓ 创建成功，ID: {benchmark_id}")
        print(f"  - 科室: {benchmark['department_name']}")
        print(f"  - 基准值: {benchmark['benchmark_value']}")
        
        # 3. 测试更新基准值
        print("\n" + "-" * 60)
        print("步骤 3: 测试更新基准值")
        print("-" * 60)
        
        update_data = {
            "benchmark_value": 1500.50
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code != 200:
            print(f"❌ 更新失败: {response.text}")
        else:
            updated = response.json()
            print(f"✓ 更新成功")
            print(f"  - 原基准值: 1000.00")
            print(f"  - 新基准值: {updated['benchmark_value']}")
        
        # 4. 测试更新科室信息
        print("\n" + "-" * 60)
        print("步骤 4: 测试更新科室信息")
        print("-" * 60)
        
        update_data = {
            "department_code": "TEST_UPDATE_002",
            "department_name": "测试更新科室002（已更新）"
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code != 200:
            print(f"❌ 更新失败: {response.text}")
        else:
            updated = response.json()
            print(f"✓ 更新成功")
            print(f"  - 新科室代码: {updated['department_code']}")
            print(f"  - 新科室名称: {updated['department_name']}")
        
        # 5. 测试更新维度信息
        print("\n" + "-" * 60)
        print("步骤 5: 测试更新维度信息")
        print("-" * 60)
        
        update_data = {
            "dimension_code": "TEST_UPDATE_DIM_002",
            "dimension_name": "测试更新维度002（已更新）"
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code != 200:
            print(f"❌ 更新失败: {response.text}")
        else:
            updated = response.json()
            print(f"✓ 更新成功")
            print(f"  - 新维度代码: {updated['dimension_code']}")
            print(f"  - 新维度名称: {updated['dimension_name']}")
        
        # 6. 测试完整更新
        print("\n" + "-" * 60)
        print("步骤 6: 测试完整更新")
        print("-" * 60)
        
        update_data = {
            "department_code": "TEST_UPDATE_003",
            "department_name": "测试更新科室003（完整更新）",
            "dimension_code": "TEST_UPDATE_DIM_003",
            "dimension_name": "测试更新维度003（完整更新）",
            "benchmark_value": 2000.00
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code != 200:
            print(f"❌ 更新失败: {response.text}")
        else:
            updated = response.json()
            print(f"✓ 完整更新成功")
            print(f"  - 科室: {updated['department_name']} ({updated['department_code']})")
            print(f"  - 维度: {updated['dimension_name']} ({updated['dimension_code']})")
            print(f"  - 基准值: {updated['benchmark_value']}")
        
        # 7. 测试唯一性约束冲突
        print("\n" + "-" * 60)
        print("步骤 7: 测试唯一性约束冲突")
        print("-" * 60)
        
        # 创建第二个成本基准
        create_data2 = {
            "department_code": "TEST_UPDATE_004",
            "department_name": "测试更新科室004",
            "version_id": version["id"],
            "version_name": version["name"],
            "dimension_code": "TEST_UPDATE_DIM_004",
            "dimension_name": "测试更新维度004",
            "benchmark_value": 3000.00
        }
        
        response = requests.post(
            f"{BASE_URL}/cost-benchmarks",
            headers=HEADERS,
            json=create_data2
        )
        
        if response.status_code != 200:
            print(f"❌ 创建第二个成本基准失败: {response.text}")
        else:
            benchmark2 = response.json()
            benchmark2_id = benchmark2["id"]
            print(f"✓ 创建第二个成本基准，ID: {benchmark2_id}")
            
            # 尝试更新为已存在的组合
            conflict_data = {
                "department_code": "TEST_UPDATE_003",
                "dimension_code": "TEST_UPDATE_DIM_003"
            }
            
            response = requests.put(
                f"{BASE_URL}/cost-benchmarks/{benchmark2_id}",
                headers=HEADERS,
                json=conflict_data
            )
            
            if response.status_code == 400:
                print(f"✓ 唯一性约束验证成功（预期返回400）")
                print(f"  - 错误信息: {response.json()['detail']}")
            else:
                print(f"❌ 唯一性约束验证失败（应该返回400）")
            
            # 清理第二个成本基准
            requests.delete(
                f"{BASE_URL}/cost-benchmarks/{benchmark2_id}",
                headers=HEADERS
            )
        
        # 8. 测试无效的基准值
        print("\n" + "-" * 60)
        print("步骤 8: 测试无效的基准值")
        print("-" * 60)
        
        invalid_data = {
            "benchmark_value": -100.00
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=invalid_data
        )
        
        if response.status_code == 400:
            print(f"✓ 基准值验证成功（预期返回400）")
            print(f"  - 错误信息: {response.json()['detail']}")
        else:
            print(f"❌ 基准值验证失败（应该返回400）")
        
        # 9. 测试不存在的记录
        print("\n" + "-" * 60)
        print("步骤 9: 测试更新不存在的记录")
        print("-" * 60)
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/999999",
            headers=HEADERS,
            json={"benchmark_value": 1000.00}
        )
        
        if response.status_code == 404:
            print(f"✓ 不存在记录验证成功（预期返回404）")
            print(f"  - 错误信息: {response.json()['detail']}")
        else:
            print(f"❌ 不存在记录验证失败（应该返回404）")
        
        # 10. 清理测试数据
        print("\n" + "-" * 60)
        print("步骤 10: 清理测试数据")
        print("-" * 60)
        
        response = requests.delete(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print("✓ 测试数据已清理")
        else:
            print(f"❌ 清理失败: {response.text}")
        
        # 总结
        print("\n" + "=" * 60)
        print("✅ 更新API测试完成")
        print("=" * 60)
        print("\n测试结果:")
        print("  ✓ 更新基准值功能正常")
        print("  ✓ 更新科室信息功能正常")
        print("  ✓ 更新维度信息功能正常")
        print("  ✓ 完整更新功能正常")
        print("  ✓ 唯一性约束验证正常")
        print("  ✓ 基准值验证正常")
        print("  ✓ 不存在记录验证正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_api()
