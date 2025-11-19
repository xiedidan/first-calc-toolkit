"""
测试结构表格式转换
"""
from decimal import Decimal

# 模拟树形数据
class MockDimension:
    def __init__(self, name, level, value=100, ratio=10, weight=None, business_guide="-", children=None):
        self.dimension_name = name
        self.level = level
        self.value = Decimal(value)
        self.ratio = Decimal(ratio)
        self.weight = Decimal(weight) if weight else None
        self.business_guide = business_guide
        self.children = children or []

# 构建测试数据 - 医生序列
doctor_tree = [
    MockDimension("门诊", 1, 5000, 50, children=[
        MockDimension("门诊诊察", 2, 2000, 20, children=[
            MockDimension("普通诊察", 3, 1000, 10, weight=55),
            MockDimension("会诊", 3, 600, 6, weight=60),
            MockDimension("MDT多方总绩效", 3, 400, 4, weight=70),
        ]),
        MockDimension("门诊诊断", 2, 1500, 15, children=[
            MockDimension("检查化验", 3, 500, 5, weight=3.49),
            MockDimension("中草药", 3, 500, 5, weight=3.49),
            MockDimension("本科治疗手术", 3, 500, 5, weight=4.33),
        ]),
        MockDimension("门诊治疗", 2, 1500, 15, children=[
            MockDimension("普通治疗甲级", 3, 600, 6, weight=18),
            MockDimension("普通治疗乙级", 3, 500, 5, weight=15),
            MockDimension("普通治疗丙级", 3, 400, 4, weight=8),
        ]),
    ]),
    MockDimension("住院", 1, 5000, 50, children=[
        MockDimension("住院诊察", 2, 2000, 20, children=[
            MockDimension("普通诊察", 3, 1000, 10, weight=50),
            MockDimension("会诊", 3, 600, 6, weight=60),
            MockDimension("MDT多方总绩效", 3, 400, 4, weight=70),
        ]),
    ]),
]

def flatten_tree_to_rows(dimensions, max_level=3):
    """将树形结构扁平化为Excel行格式 - 只输出叶子节点"""
    rows = []
    
    def collect_leaf_nodes(node, ancestors):
        """递归收集叶子节点（最底层维度）"""
        # 如果有子节点，继续递归
        if node.children:
            for child in node.children:
                new_ancestors = ancestors + [node.dimension_name]
                collect_leaf_nodes(child, new_ancestors)
        else:
            # 叶子节点，创建行数据
            row = {
                "workload_cost": "工作量绩效",
                "level1": ancestors[0] if len(ancestors) > 0 else None,
                "level2": ancestors[1] if len(ancestors) > 1 else None,
                "level3": node.dimension_name if max_level >= 3 else None,
                "hospital_value": f"{node.weight}" if node.weight else None,
                "business_guide": node.business_guide or "-",
                "dept_value": node.value,
                "level1_ratio": None,
                "level1_amount": None,
                "level2_ratio": None,
                "level2_amount": None,
                "level3_ratio": node.ratio,
                "level3_amount": node.value,
                "performance_mom": None,
                "last_month_income": None,
                "current_month_income": None,
                "income_mom": None,
            }
            
            # 对于医技序列（2级），调整列映射
            if max_level == 2:
                row["level2"] = node.dimension_name
                row["level3"] = None
                row["level2_ratio"] = node.ratio
                row["level2_amount"] = node.value
                row["level3_ratio"] = None
                row["level3_amount"] = None
            
            rows.append(row)
    
    # 处理每个一级维度
    for dim in dimensions:
        collect_leaf_nodes(dim, [])
    
    # 计算合并单元格
    if rows:
        # 工作量/成本列：所有行合并
        rows[0]["_workloadCostSpan"] = len(rows)
        for i in range(1, len(rows)):
            rows[i]["_workloadCostSpan"] = None
        
        # 一级维度列：相同一级维度的行合并
        i = 0
        while i < len(rows):
            level1_value = rows[i]["level1"]
            span = 1
            j = i + 1
            while j < len(rows) and rows[j]["level1"] == level1_value:
                span += 1
                j += 1
            rows[i]["_level1Span"] = span
            for k in range(i + 1, j):
                rows[k]["_level1Span"] = None
            i = j
        
        # 二级维度列：相同二级维度的行合并
        i = 0
        while i < len(rows):
            level2_value = rows[i]["level2"]
            span = 1
            j = i + 1
            while j < len(rows) and rows[j]["level2"] == level2_value and rows[j]["level1"] == rows[i]["level1"]:
                span += 1
                j += 1
            rows[i]["_level2Span"] = span
            for k in range(i + 1, j):
                rows[k]["_level2Span"] = None
            i = j
    
    return rows

# 测试
print("=== 医生序列扁平化结果 ===")
rows = flatten_tree_to_rows(doctor_tree, max_level=3)
for idx, row in enumerate(rows):
    print(f"\n第{idx+1}行:")
    print(f"  工作量/成本: {row['workload_cost']} (span={row['_workloadCostSpan']})")
    print(f"  一级维度: {row['level1']} (span={row['_level1Span']})")
    print(f"  二级维度: {row['level2']} (span={row['_level2Span']})")
    print(f"  三级维度: {row['level3']}")
    print(f"  全院学科业务价值: {row['hospital_value']}")
    print(f"  业务导向: {row['business_guide']}")
    print(f"  科室综合价值: {row['dept_value']}")
    print(f"  三级占比: {row['level3_ratio']}")
    print(f"  三级金额: {row['level3_amount']}")

print(f"\n总行数: {len(rows)}")
