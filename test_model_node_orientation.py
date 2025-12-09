"""
测试 ModelNode 与 OrientationRule 的关联
"""
import sys
sys.path.insert(0, 'backend')

from app.models import (
    OrientationRule, OrientationCategory,
    Hospital, ModelNode, ModelVersion
)
from app.database import SessionLocal
from datetime import datetime


def test_model_node_orientation():
    """测试模型节点与导向规则的关联"""
    print("=" * 60)
    print("测试 ModelNode 与 OrientationRule 关联")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. 获取或创建测试医疗机构
        hospital = db.query(Hospital).filter(Hospital.code == "TEST_HOSPITAL").first()
        if not hospital:
            hospital = Hospital(
                code="TEST_HOSPITAL",
                name="测试医疗机构",
                is_active=True
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)
        print(f"✅ 医疗机构: {hospital.name} (ID: {hospital.id})")
        
        # 2. 创建测试模型版本
        version = ModelVersion(
            hospital_id=hospital.id,
            version="v1.0.0",
            name="测试版本_导向关联",
            description="用于测试导向规则关联",
            is_active=False
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        print(f"✅ 创建模型版本: {version.name} (ID: {version.id})")
        
        # 3. 创建测试节点（序列节点）
        sequence_node = ModelNode(
            version_id=version.id,
            name="测试序列",
            code="SEQ001",
            node_type="sequence",
            is_leaf=False,
            sort_order=1.0
        )
        db.add(sequence_node)
        db.commit()
        db.refresh(sequence_node)
        print(f"✅ 创建序列节点: {sequence_node.name} (ID: {sequence_node.id})")
        
        # 4. 创建测试节点（末级维度节点）
        leaf_node = ModelNode(
            version_id=version.id,
            parent_id=sequence_node.id,
            name="测试末级维度",
            code="DIM001",
            node_type="dimension",
            is_leaf=True,
            sort_order=1.0
        )
        db.add(leaf_node)
        db.commit()
        db.refresh(leaf_node)
        print(f"✅ 创建末级节点: {leaf_node.name} (ID: {leaf_node.id})")
        
        # 5. 创建导向规则
        rule = OrientationRule(
            hospital_id=hospital.id,
            name="测试导向规则_节点关联",
            category=OrientationCategory.direct_ladder,
            description="用于测试节点关联"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        print(f"✅ 创建导向规则: {rule.name} (ID: {rule.id})")
        
        # 6. 关联末级节点到导向规则
        leaf_node.orientation_rule_id = rule.id
        db.commit()
        db.refresh(leaf_node)
        print(f"✅ 关联末级节点到导向规则")
        
        # 7. 验证关系
        print(f"\n验证关系:")
        
        # ModelNode -> OrientationRule
        assert leaf_node.orientation_rule is not None, "ModelNode.orientation_rule 为空"
        assert leaf_node.orientation_rule.id == rule.id, "ModelNode.orientation_rule.id 不匹配"
        assert leaf_node.orientation_rule.name == rule.name, "导向规则名称不匹配"
        print(f"  ✅ ModelNode.orientation_rule 关系正常")
        print(f"     - 导向规则名称: {leaf_node.orientation_rule.name}")
        print(f"     - 导向类别: {leaf_node.orientation_rule.category.value}")
        
        # OrientationRule -> ModelNode
        db.refresh(rule)
        assert len(rule.model_nodes) > 0, "OrientationRule.model_nodes 为空"
        assert any(n.id == leaf_node.id for n in rule.model_nodes), "未找到关联的节点"
        print(f"  ✅ OrientationRule.model_nodes 反向关系正常")
        print(f"     - 关联节点数: {len(rule.model_nodes)}")
        
        # 8. 测试清空关联
        print(f"\n测试清空关联:")
        leaf_node.orientation_rule_id = None
        db.commit()
        db.refresh(leaf_node)
        
        assert leaf_node.orientation_rule is None, "清空后 orientation_rule 应为 None"
        print(f"  ✅ 成功清空节点的导向规则关联")
        
        db.refresh(rule)
        assert not any(n.id == leaf_node.id for n in rule.model_nodes), "清空后节点仍在规则的关联列表中"
        print(f"  ✅ 反向关系也已清空")
        
        # 9. 测试删除导向规则时节点的处理（ON DELETE SET NULL）
        print(f"\n测试删除导向规则:")
        leaf_node.orientation_rule_id = rule.id
        db.commit()
        db.refresh(leaf_node)
        print(f"  重新关联节点到导向规则")
        
        rule_id = rule.id
        db.delete(rule)
        db.commit()
        print(f"  删除导向规则")
        
        db.refresh(leaf_node)
        assert leaf_node.orientation_rule_id is None, "删除规则后节点的 orientation_rule_id 应为 None"
        assert leaf_node.orientation_rule is None, "删除规则后节点的 orientation_rule 应为 None"
        print(f"  ✅ ON DELETE SET NULL 正常工作")
        
        # 10. 清理测试数据
        print(f"\n清理测试数据:")
        db.delete(leaf_node)
        db.delete(sequence_node)
        db.delete(version)
        db.commit()
        print(f"  ✅ 清理完成")
        
        print("\n" + "=" * 60)
        print("✅ 所有 ModelNode 关联测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_model_node_orientation()
    sys.exit(0 if success else 1)
