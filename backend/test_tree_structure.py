"""
测试树形结构数据格式
"""
import json

# 模拟一个简单的维度树
class MockNode:
    def __init__(self, node_id, name, workload, weight, value, business_guide=None, children=None):
        self.node_id = node_id
        self.dimension_name = name
        self.workload = workload
        self.weight = weight
        self.value = value
        self.business_guide = business_guide
        self.children = children or []

# 创建测试数据
dimensions = [
    MockNode(
        node_id=1,
        name="门诊",
        workload=1000,
        weight=None,
        value=0,
        children=[
            MockNode(
                node_id=2,
                name="诊察",
                workload=500,
                weight=None,
                value=0,
                children=[
                    MockNode(node_id=3, name="普通诊察", workload=300, weight=0.55, value=165, business_guide="药占比管控"),
                    MockNode(node_id=4, name="会诊", workload=200, weight=100, value=20000, business_guide="药占比管控")
                ]
            ),
            MockNode(
                node_id=5,
                name="治疗",
                workload=500,
                weight=None,
                value=0,
                children=[
                    MockNode(node_id=6, name="甲级治疗", workload=300, weight=0.19, value=57, business_guide="耗占比管控"),
                    MockNode(node_id=7, name="乙级治疗", workload=200, weight=0.13, value=26, business_guide="耗占比管控")
                ]
            )
        ]
    )
]

def calculate_sum_from_children(node):
    """计算节点的工作量和金额（从子节点汇总）"""
    if not node.children or len(node.children) == 0:
        return node.workload or 0, node.value or 0
    
    total_workload = 0
    total_amount = 0
    for child in node.children:
        child_workload, child_amount = calculate_sum_from_children(child)
        total_workload += child_workload
        total_amount += child_amount
    
    return total_workload, total_amount

def build_tree_node(node, siblings_total=None):
    """构建树形节点数据"""
    is_leaf = not node.children or len(node.children) == 0
    
    if is_leaf:
        current_amount = node.value or 0
        current_workload = node.workload or 0
    else:
        current_workload, current_amount = calculate_sum_from_children(node)
    
    # 计算占比
    if siblings_total and siblings_total > 0:
        ratio = round((current_amount / siblings_total * 100), 2)
    else:
        ratio = 0
    
    # 创建节点数据
    if is_leaf:
        tree_node = {
            "id": node.node_id,
            "dimension_name": node.dimension_name,
            "workload": current_workload,
            "hospital_value": str(node.weight) if node.weight is not None else "-",
            "business_guide": node.business_guide or "-",
            "dept_value": str(node.weight) if node.weight is not None else "-",
            "amount": current_amount,
            "ratio": ratio
        }
    else:
        tree_node = {
            "id": node.node_id,
            "dimension_name": node.dimension_name,
            "workload": current_workload,
            "hospital_value": "-",
            "business_guide": "-",
            "dept_value": "-",
            "amount": current_amount,
            "ratio": ratio,
            "children": []
        }
    
    # 递归处理子节点
    if node.children:
        children_total = sum(
            (calculate_sum_from_children(child)[1] if child.children else (child.value or 0))
            for child in node.children
        )
        
        for child in node.children:
            child_node = build_tree_node(child, children_total)
            tree_node["children"].append(child_node)
    
    return tree_node

# 构建树形数据
first_level_total = sum(
    (calculate_sum_from_children(dim)[1] if dim.children else (dim.value or 0))
    for dim in dimensions
)

rows = []
for dim in dimensions:
    tree_node = build_tree_node(dim, first_level_total)
    rows.append(tree_node)

# 输出结果
print("树形结构数据：")
print(json.dumps(rows, indent=2, ensure_ascii=False))

# 验证数据结构
print("\n数据结构验证：")
print(f"根节点数量: {len(rows)}")
print(f"根节点ID: {rows[0]['id']}")
print(f"根节点名称: {rows[0]['dimension_name']}")
print(f"根节点是否有children: {'children' in rows[0]}")
if 'children' in rows[0]:
    print(f"根节点子节点数量: {len(rows[0]['children'])}")
    print(f"第一个子节点名称: {rows[0]['children'][0]['dimension_name']}")
    if 'children' in rows[0]['children'][0]:
        print(f"第一个子节点的子节点数量: {len(rows[0]['children'][0]['children'])}")
        leaf = rows[0]['children'][0]['children'][0]
        print(f"叶子节点名称: {leaf['dimension_name']}")
        print(f"叶子节点是否有children: {'children' in leaf}")
