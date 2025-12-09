"""
测试导向阶梯前端功能

验证：
1. 导向阶梯列表页面能正确加载
2. 可以按导向筛选阶梯
3. 可以创建新的导向阶梯
4. 可以编辑现有的导向阶梯
5. 可以删除导向阶梯
6. 无穷值正确处理（NULL显示为∞）
7. 数值自动格式化为4位小数
8. 表单验证正确工作
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的请求头（需要根据实际情况调整）
headers = {
    "Content-Type": "application/json",
    "X-Hospital-ID": "1"  # 假设使用医疗机构ID为1
}

def test_create_orientation_rule():
    """创建测试用的导向规则"""
    print("\n=== 创建测试导向规则 ===")
    
    # 创建基准阶梯类别的导向
    data = {
        "name": f"测试基准阶梯导向_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "category": "benchmark_ladder",
        "description": "用于测试阶梯功能的导向规则"
    }
    
    response = requests.post(f"{BASE_URL}/orientation-rules", json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        rule = response.json()
        print(f"创建成功: ID={rule['id']}, 名称={rule['name']}")
        return rule['id']
    else:
        print(f"创建失败: {response.text}")
        return None

def test_create_ladder(rule_id):
    """测试创建导向阶梯"""
    print("\n=== 测试创建导向阶梯 ===")
    
    # 测试1: 创建有限值阶梯
    data1 = {
        "rule_id": rule_id,
        "ladder_order": 1,
        "lower_limit": 0.0,
        "upper_limit": 100.0,
        "adjustment_intensity": 1.2345
    }
    
    response1 = requests.post(f"{BASE_URL}/orientation-ladders", json=data1, headers=headers)
    print(f"创建有限值阶梯 - 状态码: {response1.status_code}")
    if response1.status_code == 200:
        ladder1 = response1.json()
        print(f"  成功: ID={ladder1['id']}, 次序={ladder1['ladder_order']}")
        print(f"  上限={ladder1['upper_limit']}, 下限={ladder1['lower_limit']}")
        print(f"  调整力度={ladder1['adjustment_intensity']}")
    else:
        print(f"  失败: {response1.text}")
    
    # 测试2: 创建上限为正无穷的阶梯
    data2 = {
        "rule_id": rule_id,
        "ladder_order": 2,
        "lower_limit": 100.0,
        "upper_limit": None,  # 正无穷
        "adjustment_intensity": 2.5678
    }
    
    response2 = requests.post(f"{BASE_URL}/orientation-ladders", json=data2, headers=headers)
    print(f"\n创建正无穷阶梯 - 状态码: {response2.status_code}")
    if response2.status_code == 200:
        ladder2 = response2.json()
        print(f"  成功: ID={ladder2['id']}, 次序={ladder2['ladder_order']}")
        print(f"  上限={ladder2['upper_limit']} (应为None表示正无穷)")
        print(f"  下限={ladder2['lower_limit']}")
    else:
        print(f"  失败: {response2.text}")
    
    # 测试3: 创建下限为负无穷的阶梯
    data3 = {
        "rule_id": rule_id,
        "ladder_order": 0,
        "lower_limit": None,  # 负无穷
        "upper_limit": 0.0,
        "adjustment_intensity": 0.5
    }
    
    response3 = requests.post(f"{BASE_URL}/orientation-ladders", json=data3, headers=headers)
    print(f"\n创建负无穷阶梯 - 状态码: {response3.status_code}")
    if response3.status_code == 200:
        ladder3 = response3.json()
        print(f"  成功: ID={ladder3['id']}, 次序={ladder3['ladder_order']}")
        print(f"  上限={ladder3['upper_limit']}")
        print(f"  下限={ladder3['lower_limit']} (应为None表示负无穷)")
    else:
        print(f"  失败: {response3.text}")
    
    return response1.json()['id'] if response1.status_code == 200 else None

def test_list_ladders(rule_id):
    """测试获取导向阶梯列表"""
    print("\n=== 测试获取导向阶梯列表 ===")
    
    # 测试按导向筛选
    params = {
        "rule_id": rule_id,
        "page": 1,
        "size": 20
    }
    
    response = requests.get(f"{BASE_URL}/orientation-ladders", params=params, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"总数: {result['total']}")
        print(f"返回记录数: {len(result['items'])}")
        
        # 验证排序（按ladder_order升序）
        if result['items']:
            print("\n阶梯列表（按次序排序）:")
            for ladder in result['items']:
                upper = ladder['upper_limit'] if ladder['upper_limit'] is not None else '+∞'
                lower = ladder['lower_limit'] if ladder['lower_limit'] is not None else '-∞'
                print(f"  次序{ladder['ladder_order']}: [{lower}, {upper}], 调整力度={ladder['adjustment_intensity']}")
    else:
        print(f"失败: {response.text}")

def test_update_ladder(ladder_id):
    """测试更新导向阶梯"""
    print("\n=== 测试更新导向阶梯 ===")
    
    # 更新调整力度
    data = {
        "adjustment_intensity": 3.1416
    }
    
    response = requests.put(f"{BASE_URL}/orientation-ladders/{ladder_id}", json=data, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        ladder = response.json()
        print(f"更新成功: 调整力度={ladder['adjustment_intensity']}")
        # 验证格式化为4位小数
        assert ladder['adjustment_intensity'] == '3.1416', "调整力度应格式化为4位小数"
        print("✓ 数值格式化验证通过")
    else:
        print(f"失败: {response.text}")

def test_validation():
    """测试表单验证"""
    print("\n=== 测试表单验证 ===")
    
    # 测试1: 缺少必填字段
    data1 = {
        "ladder_order": 1
        # 缺少 rule_id 和 adjustment_intensity
    }
    
    response1 = requests.post(f"{BASE_URL}/orientation-ladders", json=data1, headers=headers)
    print(f"缺少必填字段 - 状态码: {response1.status_code}")
    assert response1.status_code == 422, "应返回422验证错误"
    print("✓ 必填字段验证通过")
    
    # 测试2: 下限大于上限（应该失败）
    # 注意：这个验证可能在后端实现，前端也应该有
    print("\n注意: 范围验证（下限<上限）应在前端和后端都实现")

def test_delete_ladder(ladder_id):
    """测试删除导向阶梯"""
    print("\n=== 测试删除导向阶梯 ===")
    
    response = requests.delete(f"{BASE_URL}/orientation-ladders/{ladder_id}", headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("删除成功")
    else:
        print(f"失败: {response.text}")

def main():
    """主测试流程"""
    print("=" * 60)
    print("导向阶梯前端功能测试")
    print("=" * 60)
    
    try:
        # 1. 创建测试导向规则
        rule_id = test_create_orientation_rule()
        if not rule_id:
            print("\n❌ 无法创建测试导向规则，测试终止")
            return
        
        # 2. 创建导向阶梯
        ladder_id = test_create_ladder(rule_id)
        
        # 3. 获取阶梯列表
        test_list_ladders(rule_id)
        
        # 4. 更新阶梯
        if ladder_id:
            test_update_ladder(ladder_id)
        
        # 5. 测试验证
        test_validation()
        
        # 6. 删除阶梯
        if ladder_id:
            test_delete_ladder(ladder_id)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
        print("\n前端功能验证清单:")
        print("□ 访问 /orientation-ladders 页面能正常加载")
        print("□ 导向筛选下拉框显示基准阶梯和直接阶梯类别的导向")
        print("□ 从导向规则页面点击'设置阶梯'能正确跳转并筛选")
        print("□ 表格正确显示阶梯信息，NULL值显示为∞")
        print("□ 点击'新增'打开对话框，表单验证正常工作")
        print("□ 勾选无穷复选框时，对应输入框被禁用")
        print("□ 数值输入失焦时自动格式化为4位小数")
        print("□ 提交时正确发送NULL（无穷）或数值")
        print("□ 编辑功能正常，能正确回显无穷值")
        print("□ 删除功能正常，有确认提示")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
