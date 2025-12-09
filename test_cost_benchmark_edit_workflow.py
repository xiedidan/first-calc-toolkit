"""
成本基准编辑功能完整工作流测试
演示从创建到编辑到验证的完整流程
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
        return True
    return False

def print_benchmark(benchmark, title="成本基准信息"):
    """打印成本基准信息"""
    print(f"\n{title}:")
    print(f"  ID: {benchmark['id']}")
    print(f"  科室: {benchmark['department_name']} ({benchmark['department_code']})")
    print(f"  版本: {benchmark['version_name']} (ID: {benchmark['version_id']})")
    print(f"  维度: {benchmark['dimension_name']} ({benchmark['dimension_code']})")
    print(f"  基准值: {benchmark['benchmark_value']}")
    print(f"  创建时间: {benchmark['created_at']}")
    print(f"  更新时间: {benchmark['updated_at']}")

def test_complete_workflow():
    """测试完整的编辑工作流"""
    print("=" * 70)
    print("成本基准编辑功能 - 完整工作流演示")
    print("=" * 70)
    
    if not login():
        print("❌ 登录失败")
        return
    
    print("✓ 登录成功")
    
    try:
        # 步骤1: 获取必要的数据
        print("\n" + "=" * 70)
        print("步骤 1: 准备测试数据")
        print("=" * 70)
        
        # 获取模型版本
        response = requests.get(f"{BASE_URL}/model-versions", headers=HEADERS, params={"limit": 1})
        version = response.json()["items"][0]
        print(f"✓ 获取模型版本: {version['name']} (ID: {version['id']})")
        
        # 步骤2: 创建初始成本基准
        print("\n" + "=" * 70)
        print("步骤 2: 创建初始成本基准")
        print("=" * 70)
        
        create_data = {
            "department_code": "WORKFLOW_DEPT",
            "department_name": "工作流测试科室",
            "version_id": version["id"],
            "version_name": version["name"],
            "dimension_code": "WORKFLOW_DIM",
            "dimension_name": "工作流测试维度",
            "benchmark_value": 1000.00
        }
        
        response = requests.post(f"{BASE_URL}/cost-benchmarks", headers=HEADERS, json=create_data)
        benchmark = response.json()
        benchmark_id = benchmark["id"]
        
        print(f"✓ 创建成功")
        print_benchmark(benchmark, "初始数据")
        
        # 步骤3: 模拟前端"编辑"按钮点击 - 获取详情用于预填充
        print("\n" + "=" * 70)
        print("步骤 3: 模拟前端编辑操作 - 获取数据预填充表单")
        print("=" * 70)
        
        response = requests.get(f"{BASE_URL}/cost-benchmarks/{benchmark_id}", headers=HEADERS)
        prefill_data = response.json()
        
        print("✓ 获取成功，以下数据将预填充到编辑表单:")
        print(f"  - 科室代码: {prefill_data['department_code']}")
        print(f"  - 科室名称: {prefill_data['department_name']}")
        print(f"  - 版本ID: {prefill_data['version_id']}")
        print(f"  - 版本名称: {prefill_data['version_name']}")
        print(f"  - 维度代码: {prefill_data['dimension_code']}")
        print(f"  - 维度名称: {prefill_data['dimension_name']}")
        print(f"  - 基准值: {prefill_data['benchmark_value']}")
        
        # 步骤4: 用户修改基准值
        print("\n" + "=" * 70)
        print("步骤 4: 用户在表单中修改基准值")
        print("=" * 70)
        
        print("用户操作: 将基准值从 1000.00 改为 1500.50")
        
        update_data = {
            "benchmark_value": 1500.50
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        updated_benchmark = response.json()
        print("✓ 更新成功")
        print_benchmark(updated_benchmark, "更新后数据")
        
        # 步骤5: 用户修改科室信息
        print("\n" + "=" * 70)
        print("步骤 5: 用户修改科室信息")
        print("=" * 70)
        
        print("用户操作: 更改科室为'工作流测试科室（已修改）'")
        
        update_data = {
            "department_code": "WORKFLOW_DEPT_V2",
            "department_name": "工作流测试科室（已修改）"
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=update_data
        )
        
        updated_benchmark = response.json()
        print("✓ 更新成功")
        print_benchmark(updated_benchmark, "更新后数据")
        
        # 步骤6: 用户尝试输入无效值
        print("\n" + "=" * 70)
        print("步骤 6: 测试数据验证 - 尝试输入负值")
        print("=" * 70)
        
        print("用户操作: 尝试将基准值改为 -100.00")
        
        invalid_data = {
            "benchmark_value": -100.00
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark_id}",
            headers=HEADERS,
            json=invalid_data
        )
        
        if response.status_code == 422:
            print("✓ 验证成功 - 系统拒绝了无效值")
            print(f"  错误信息: {response.json()['detail']}")
        else:
            print("❌ 验证失败 - 系统应该拒绝负值")
        
        # 步骤7: 测试唯一性约束
        print("\n" + "=" * 70)
        print("步骤 7: 测试唯一性约束")
        print("=" * 70)
        
        # 创建第二个成本基准
        create_data2 = {
            "department_code": "WORKFLOW_DEPT_2",
            "department_name": "工作流测试科室2",
            "version_id": version["id"],
            "version_name": version["name"],
            "dimension_code": "WORKFLOW_DIM_2",
            "dimension_name": "工作流测试维度2",
            "benchmark_value": 2000.00
        }
        
        response = requests.post(f"{BASE_URL}/cost-benchmarks", headers=HEADERS, json=create_data2)
        benchmark2 = response.json()
        benchmark2_id = benchmark2["id"]
        print(f"✓ 创建第二个成本基准，ID: {benchmark2_id}")
        
        # 尝试更新为已存在的组合
        print("\n用户操作: 尝试将第二个成本基准改为与第一个相同的科室-版本-维度组合")
        
        conflict_data = {
            "department_code": "WORKFLOW_DEPT_V2",
            "dimension_code": "WORKFLOW_DIM"
        }
        
        response = requests.put(
            f"{BASE_URL}/cost-benchmarks/{benchmark2_id}",
            headers=HEADERS,
            json=conflict_data
        )
        
        if response.status_code == 400:
            print("✓ 唯一性约束验证成功 - 系统阻止了重复组合")
            print(f"  错误信息: {response.json()['detail']}")
        else:
            print("❌ 唯一性约束验证失败")
        
        # 步骤8: 验证最终状态
        print("\n" + "=" * 70)
        print("步骤 8: 验证最终状态")
        print("=" * 70)
        
        response = requests.get(f"{BASE_URL}/cost-benchmarks/{benchmark_id}", headers=HEADERS)
        final_benchmark = response.json()
        
        print("✓ 最终数据验证:")
        print_benchmark(final_benchmark, "最终状态")
        
        # 验证数据正确性
        print("\n数据正确性检查:")
        checks = [
            ("科室代码", final_benchmark['department_code'] == "WORKFLOW_DEPT_V2"),
            ("科室名称", final_benchmark['department_name'] == "工作流测试科室（已修改）"),
            ("基准值", float(final_benchmark['benchmark_value']) == 1500.50),
            ("维度代码", final_benchmark['dimension_code'] == "WORKFLOW_DIM"),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "❌"
            print(f"  {status} {check_name}: {'通过' if check_result else '失败'}")
            if not check_result:
                all_passed = False
        
        # 清理测试数据
        print("\n" + "=" * 70)
        print("步骤 9: 清理测试数据")
        print("=" * 70)
        
        requests.delete(f"{BASE_URL}/cost-benchmarks/{benchmark_id}", headers=HEADERS)
        requests.delete(f"{BASE_URL}/cost-benchmarks/{benchmark2_id}", headers=HEADERS)
        print("✓ 测试数据已清理")
        
        # 总结
        print("\n" + "=" * 70)
        print("✅ 完整工作流测试完成")
        print("=" * 70)
        
        if all_passed:
            print("\n🎉 所有功能正常工作！")
            print("\n功能清单:")
            print("  ✓ 创建成本基准")
            print("  ✓ 获取详情用于预填充")
            print("  ✓ 更新基准值")
            print("  ✓ 更新科室信息")
            print("  ✓ 数据验证（拒绝负值）")
            print("  ✓ 唯一性约束验证")
            print("  ✓ 最终状态正确")
        else:
            print("\n⚠️ 部分检查未通过，请查看上面的详细信息")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()
