"""
验证业务价值计算公式
检查：业务价值 = 工作量（收入）× 权重
"""
from decimal import Decimal

# 测试数据
test_cases = [
    {
        "name": "门诊诊察",
        "workload": Decimal("1000"),  # 工作量（收入）
        "weight": Decimal("55"),      # 权重/单价
        "expected_value": Decimal("55000")  # 预期业务价值
    },
    {
        "name": "会诊",
        "workload": Decimal("600"),
        "weight": Decimal("60"),
        "expected_value": Decimal("36000")
    },
    {
        "name": "检查化验",
        "workload": Decimal("500"),
        "weight": Decimal("3.49"),
        "expected_value": Decimal("1745")
    },
    {
        "name": "普通治疗甲级",
        "workload": Decimal("600"),
        "weight": Decimal("18"),
        "expected_value": Decimal("10800")
    },
]

print("=" * 80)
print("业务价值计算公式验证")
print("公式：业务价值 = 工作量（收入）× 权重")
print("=" * 80)

all_passed = True

for idx, case in enumerate(test_cases, 1):
    workload = case["workload"]
    weight = case["weight"]
    expected = case["expected_value"]
    
    # 计算业务价值
    calculated_value = workload * weight
    
    # 验证结果
    is_correct = calculated_value == expected
    status = "✓ 通过" if is_correct else "✗ 失败"
    
    print(f"\n测试 {idx}: {case['name']}")
    print(f"  工作量（收入）: {workload}")
    print(f"  权重/单价: {weight}")
    print(f"  计算结果: {calculated_value}")
    print(f"  预期结果: {expected}")
    print(f"  状态: {status}")
    
    if not is_correct:
        all_passed = False
        print(f"  ⚠️  差异: {calculated_value - expected}")

print("\n" + "=" * 80)
if all_passed:
    print("✓ 所有测试通过！")
    print("\n计算公式正确：业务价值 = 工作量（收入）× 权重")
else:
    print("✗ 部分测试失败！")
    print("\n请检查计算公式")
print("=" * 80)
