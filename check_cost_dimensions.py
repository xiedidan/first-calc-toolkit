"""
检查模型版本12中的成本维度结构
"""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.model_node import ModelNode
from sqlalchemy import and_

db = SessionLocal()

try:
    version_id = 12
    
    print(f"\n=== 检查版本 {version_id} 的节点结构 ===\n")
    
    # 1. 查找所有序列节点
    sequences = db.query(ModelNode).filter(
        and_(
            ModelNode.version_id == version_id,
            ModelNode.node_type == 'sequence'
        )
    ).all()
    
    print(f"找到 {len(sequences)} 个序列节点:")
    for seq in sequences:
        print(f"  - ID: {seq.id}, 名称: '{seq.name}', 编码: {seq.code}")
    
    # 2. 查找包含"医护技"的序列
    medical_tech_sequences = db.query(ModelNode).filter(
        and_(
            ModelNode.version_id == version_id,
            ModelNode.node_type == 'sequence',
            ModelNode.name.contains('医护技')
        )
    ).all()
    
    print(f"\n包含'医护技'的序列节点: {len(medical_tech_sequences)} 个")
    for seq in medical_tech_sequences:
        print(f"  - ID: {seq.id}, 名称: '{seq.name}'")
        
        # 查找该序列的直接子节点
        children = db.query(ModelNode).filter(
            ModelNode.parent_id == seq.id
        ).all()
        
        print(f"    直接子节点 ({len(children)} 个):")
        for child in children:
            print(f"      - ID: {child.id}, 名称: '{child.name}', 类型: {child.node_type}, 是否末级: {child.is_leaf}")
    
    # 3. 查找所有名为"成本"的节点
    cost_nodes = db.query(ModelNode).filter(
        and_(
            ModelNode.version_id == version_id,
            ModelNode.name == '成本'
        )
    ).all()
    
    print(f"\n名为'成本'的节点: {len(cost_nodes)} 个")
    for node in cost_nodes:
        print(f"  - ID: {node.id}, 名称: '{node.name}', 父节点ID: {node.parent_id}, 类型: {node.node_type}")
        
        # 查找父节点
        if node.parent_id:
            parent = db.query(ModelNode).filter(ModelNode.id == node.parent_id).first()
            if parent:
                print(f"    父节点: ID={parent.id}, 名称='{parent.name}', 类型={parent.node_type}")
        
        # 查找子节点
        children = db.query(ModelNode).filter(ModelNode.parent_id == node.id).all()
        print(f"    子节点 ({len(children)} 个):")
        for child in children:
            print(f"      - ID: {child.id}, 名称: '{child.name}', 是否末级: {child.is_leaf}")
            
            # 如果不是末级，继续查找其子节点
            if not child.is_leaf:
                grandchildren = db.query(ModelNode).filter(ModelNode.parent_id == child.id).all()
                print(f"        孙节点 ({len(grandchildren)} 个):")
                for gc in grandchildren:
                    print(f"          - ID: {gc.id}, 名称: '{gc.name}', 是否末级: {gc.is_leaf}")
    
    # 4. 查找所有包含"成本"的节点
    cost_like_nodes = db.query(ModelNode).filter(
        and_(
            ModelNode.version_id == version_id,
            ModelNode.name.contains('成本')
        )
    ).all()
    
    print(f"\n名称包含'成本'的节点: {len(cost_like_nodes)} 个")
    for node in cost_like_nodes:
        print(f"  - ID: {node.id}, 名称: '{node.name}', 父节点ID: {node.parent_id}")

finally:
    db.close()
