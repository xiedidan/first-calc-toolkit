"""
测试新的业务价值明细表结构
"""
from decimal import Decimal

# 模拟维度节点
class MockDimension:
    def __init__(self, name, workload=None, weight=None, value=None, ratio=None, business_guide=None, children=None):
        self.dimension_name = name
        self.workload = Decimal(workload) if workload else None
        self.weight = Decimal(weight) if weight else None
        self.value = Decimal(value) if value else None
        self.ratio = Decimal(ratio) if ratio else None
        self.business_guide = business_guide
        self.children = children or []

# 构建测试数据 - 医生序列（3级结构）
doctor_tree = [
    MockDimension("门诊", workload=5000, value=5000, ratio=50, children=[
        MockDimension("门诊诊察", workload=2000, value=2000, ratio=20, children=[
            MockDimension("普通诊察", workload=1000, weight=55, value=1000, ratio=10, business_guide="基础诊疗"),
            MockDimension("会诊", workload=600, weight=60, value=600, ratio=6, business_guide="疑难病例"),
            MockDimension("MDT多方总绩效", workload=400, weight=70, value=400, ratio=4, business_guide="多学科协作"),
        ]),
        MockDimension("门诊诊断", workload=1500, value=1500, ratio=15, children=[
            MockDimension("检查化验", workload=500, weight=3.49, value=500, ratio=5, business_guide="辅助诊断"),
            MockDimension("中草药", workload=500, weight=3.49, value=500, ratio=5, business_guide="中医治疗"),
            MockDimension("本科治疗手术", workload=500, weight=4.33, value=500, ratio=5, business_guide="专科治疗"),
        ]),
        MockDimension("门诊治疗", workload=1500, value=1500, ratio=15, children=[
            MockDimension("普通治疗甲级", workload=600, weight=18, value=600, ratio=6, business_guide="高难度治疗"),
            MockDimension("普通治疗乙级", workload=500, weight=15, value=500, ratio=5, business_guide="中等难度治疗"),
            MockDimension("普通治疗丙级", workload=400, weight=8, value=400, ratio=4, business_guide="基础治疗"),
        ]),
    ]),
    MockDimension("住院", workload=5000, value=5000, ratio=50, children=[
        MockDimension("住院诊察", workload=2000, value=2000, ratio=20, children=[
            MockDimension("普通诊察", workload=1000, weight=50, value=1000, ratio=10, business_guide="日常查房"),
            MockDimension("会诊", workload=600, weight=60, value=600, ratio=6, business_guide="疑难病例"),
            MockDimension("MDT多方总绩效", workload=400, weight=70, value=400, ratio=4, business_guide="多学科协作"),
        ]),
    ]),
]

# 医技序列（2级结构）
tech_tree = [
    MockDimension("检验", workload=3000, value=3000, ratio=60, children=[
        MockDimension("常规检验", workload=1500, weight=2.5, value=1500, ratio=30, business_guide="基础检验"),
        MockDimension("特殊检验", workload=1500, weight=5.0, value=1500, ratio=30, business_guide="专项检验"),
    ]),
    MockDimension("影像", workload=2000, value=2000, ratio=40, children=[
        MockDimension("X光", workload=800, weight=3.0, value=800, ratio=16, business_guide="基础影像"),
        MockDimension("CT", workload=700, weight=8.0, value=700, ratio=14, business_guide="断层扫描"),
        MockDimension("MRI", workload=500, weight=12.0, value=500, ratio=10, business_guide="磁共振"),
    ]),
]

def flatten_tree_to_rows(dimensions):
    """将树形结构扁平化为表格行格式 - 包含所有节点"""
    rows = []
    
    def calculate_sum_from_children(node):
        """计算节点的工作量和金额（从子节点汇总）"""
        if not node.children or len(node.children) == 0:
            # 叶子节点，直接返回自己的值
            return node.workload or 0, node.value or 0
        
        # 非叶子节点，汇总子节点
        total_workload = 0
        total_amount = 0
        for child in node.children:
            child_workload, child_amount = calculate_sum_from_children(child)
            total_workload += child_workload
            total_amount += child_amount
        
        return total_workload, total_amount
    
    def collect_all_nodes(node, level_names):
        """递归收集所有节点（末级和非末级）
        
        level_names: 当前路径上各级维度的名称 [level1, level2, level3, ...]
        """
        # 判断是否为末级维度
        is_leaf = not node.children or len(node.children) == 0
        
        # 更新level_names，添加当前节点
        new_level_names = level_names + [node.dimension_name]
        
        # 构建维度名称列（最多支持4级）
        level1_name = new_level_names[0] if len(new_level_names) >= 1 else None
        level2_name = new_level_names[1] if len(new_level_names) >= 2 else None
        level3_name = new_level_names[2] if len(new_level_names) >= 3 else None
        level4_name = new_level_names[3] if len(new_level_names) >= 4 else None
        
        # 创建行数据
        if is_leaf:
            # 末级维度：显示工作量、全院业务价值、业务导向、科室业务价值、金额、占比
            row = {
                "level1": level1_name,
                "level2": level2_name,
                "level3": level3_name,
                "level4": level4_name,
                "workload": node.workload,
                "hospital_value": str(node.value) if node.value is not None else "-",
                "business_guide": node.business_guide or "-",
                "dept_value": str(node.value) if node.value is not None else "-",
                "amount": node.value,
                "ratio": node.ratio,
            }
        else:
            # 非末级维度：工作量和金额由子维度之和计算
            sum_workload, sum_amount = calculate_sum_from_children(node)
            row = {
                "level1": level1_name,
                "level2": level2_name,
                "level3": level3_name,
                "level4": level4_name,
                "workload": sum_workload,
                "hospital_value": "-",
                "business_guide": "-",
                "dept_value": "-",
                "amount": sum_amount,
                "ratio": node.ratio,
            }
        
        rows.append(row)
        
        # 递归处理子节点
        if node.children:
            for child in node.children:
                collect_all_nodes(child, new_level_names)
    
    # 处理每个一级维度
    for dim in dimensions:
        collect_all_nodes(dim, [])
    
    return rows

# 测试医生序列
print("=" * 80)
print("医生序列业务价值明细表")
print("=" * 80)
doctor_rows = flatten_tree_to_rows(doctor_tree)
print(f"\n总行数: {len(doctor_rows)}\n")

for idx, row in enumerate(doctor_rows, 1):
    print(f"第{idx}行:")
    print(f"  一级维度: {row['level1']}")
    print(f"  二级维度: {row['level2']}")
    print(f"  三级维度: {row['level3']}")
    print(f"  工作量: {row['workload']}")
    print(f"  全院业务价值: {row['hospital_value']}")
    print(f"  业务导向: {row['business_guide']}")
    print(f"  科室业务价值: {row['dept_value']}")
    print(f"  金额: {row['amount']}")
    print(f"  占比: {row['ratio']}%")
    print()

# 测试医技序列
print("=" * 80)
print("医技序列业务价值明细表")
print("=" * 80)
tech_rows = flatten_tree_to_rows(tech_tree)
print(f"\n总行数: {len(tech_rows)}\n")

for idx, row in enumerate(tech_rows, 1):
    print(f"第{idx}行:")
    print(f"  一级维度: {row['level1']}")
    print(f"  二级维度: {row['level2']}")
    print(f"  工作量: {row['workload']}")
    print(f"  全院业务价值: {row['hospital_value']}")
    print(f"  业务导向: {row['business_guide']}")
    print(f"  科室业务价值: {row['dept_value']}")
    print(f"  金额: {row['amount']}")
    print(f"  占比: {row['ratio']}%")
    print()

print("=" * 80)
print("测试完成！")
print("=" * 80)
