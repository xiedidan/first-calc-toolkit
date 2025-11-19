"""
测试单个科室的维度工作量分配

使用方法：
    python test_dimension_allocation.py [科室代码]
    
示例：
    python test_dimension_allocation.py YS01  # 测试白内障专科
    python test_dimension_allocation.py BHL01  # 测试眼科一病区
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from populate_report_data_ai import AIDataGenerator, load_config, load_ai_config_from_file


def test_dimension_allocation(dept_code: str = "YS01"):
    """测试单个科室的维度工作量分配"""
    print("="*70)
    print(f"测试科室维度工作量分配: {dept_code}")
    print("="*70)
    
    # 1. 加载配置
    config_file = "report_data_config_real.json"
    print(f"\n1. 加载配置文件: {config_file}")
    config = load_config(config_file)
    
    # 2. 加载科室分配结果
    print("\n2. 加载科室分配结果")
    with open("department_allocation_result.json", 'r', encoding='utf-8') as f:
        dept_allocations = json.load(f)
    
    if dept_code not in dept_allocations:
        print(f"❌ 错误: 未找到科室 {dept_code}")
        print(f"可用的科室代码: {', '.join(dept_allocations.keys())}")
        return
    
    dept_allocation = dept_allocations[dept_code]
    dept_config = next((d for d in config['departments'] if d['his_code'] == dept_code), None)
    
    if not dept_config:
        print(f"❌ 错误: 配置文件中未找到科室 {dept_code}")
        return
    
    print(f"科室名称: {dept_config['his_name']}")
    print(f"科室类别: {dept_config['category']}")
    print(f"工作量比例: {dept_allocation['workload_based_ratio']:.1f}%")
    
    # 3. 获取数据库中的维度信息
    print("\n3. 获取维度信息")
    db = SessionLocal()
    try:
        model_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if not model_version:
            print("❌ 错误: 未找到激活的模型版本")
            return
        
        print(f"模型版本: {model_version.name}")
        
        dimension_nodes = db.query(ModelNode).filter(
            ModelNode.version_id == model_version.id,
            ModelNode.node_type == "dimension"
        ).order_by(ModelNode.sort_order).all()
        
        print(f"维度数量: {len(dimension_nodes)}")
        
    finally:
        db.close()
    
    # 4. 初始化AI生成器
    print("\n4. 初始化AI生成器")
    ai_config = load_ai_config_from_file(config)
    ai_generator = AIDataGenerator(
        prompts_file="ai_prompts.json",
        **ai_config
    )
    
    # 5. 调用AI分配维度工作量
    print("\n5. 调用AI分配维度工作量")
    print("-"*70)
    
    dim_allocations = ai_generator.allocate_dimensions(
        dept_config,
        dept_allocation,
        dimension_nodes,
        config['total_workload']
    )
    
    # 6. 输出结果
    print("\n" + "="*70)
    print("维度分配结果")
    print("="*70)
    
    # 按父节点分组
    by_parent = {}
    root_dims = []
    
    for node_id, alloc in dim_allocations.items():
        node = next((n for n in dimension_nodes if n.id == node_id), None)
        if node:
            if node.parent_id is None:
                root_dims.append((node, alloc))
            else:
                if node.parent_id not in by_parent:
                    by_parent[node.parent_id] = []
                by_parent[node.parent_id].append((node, alloc))
    
    # 递归显示维度树
    def print_dimension_tree(node, alloc, level=0):
        indent = "  " * level
        print(f"{indent}├─ {node.name} (代码: {node.code})")
        if alloc.get('original_ratio') is not None:
            print(f"{indent}   原始比例: {alloc['original_ratio']:.1f}%")
        if alloc.get('normalized_ratio') is not None:
            print(f"{indent}   归一化比例: {alloc['normalized_ratio']:.1f}%")
        print(f"{indent}   工作量: {alloc['workload']}")
        print(f"{indent}   权重: {node.weight or 0}")
        print(f"{indent}   价值: {alloc['workload'] * (node.weight or 0)}")
        print(f"{indent}   理由: {alloc['reasoning']}")
        
        # 显示子节点
        if node.id in by_parent:
            children = by_parent[node.id]
            for child_node, child_alloc in children:
                print_dimension_tree(child_node, child_alloc, level + 1)
    
    # 显示根节点
    for node, alloc in root_dims:
        print_dimension_tree(node, alloc)
        print()
    
    # 统计总工作量
    total_workload = sum(alloc['workload'] for alloc in dim_allocations.values())
    print(f"\n总工作量: {total_workload}")
    
    # 保存结果到文件
    output_file = f"dimension_allocation_{dept_code}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dim_allocations, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*70)
    print(f"✓ 结果已保存到: {output_file}")
    print("="*70)
    
    return dim_allocations


if __name__ == "__main__":
    dept_code = sys.argv[1] if len(sys.argv) > 1 else "YS01"
    
    try:
        result = test_dimension_allocation(dept_code)
        print("\n✅ 测试完成!")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
