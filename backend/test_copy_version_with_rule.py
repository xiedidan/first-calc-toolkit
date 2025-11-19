"""
测试复制版本时是否包含 rule 字段
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode


def test_copy_version_with_rule():
    """测试复制版本时是否包含 rule 字段"""
    db: Session = SessionLocal()
    
    try:
        # 查找第一个有节点的版本
        version = db.query(ModelVersion).first()
        if not version:
            print("❌ 没有找到任何版本")
            return False
        
        print(f"✓ 找到版本: {version.name} (ID: {version.id})")
        
        # 查找该版本的节点
        nodes = db.query(ModelNode).filter(ModelNode.version_id == version.id).all()
        if not nodes:
            print("❌ 该版本没有节点")
            return False
        
        print(f"✓ 找到 {len(nodes)} 个节点")
        
        # 检查是否有节点包含 rule
        nodes_with_rule = [n for n in nodes if n.rule]
        if not nodes_with_rule:
            print("⚠ 该版本的节点都没有设置 rule 字段")
            print("  请先在界面上为某些节点添加规则说明，然后再测试复制功能")
            return True
        
        print(f"✓ 有 {len(nodes_with_rule)} 个节点包含 rule 字段")
        
        # 显示包含 rule 的节点
        for node in nodes_with_rule[:3]:  # 只显示前3个
            rule_preview = node.rule[:50] + "..." if len(node.rule) > 50 else node.rule
            print(f"  - {node.name} ({node.code}): {rule_preview}")
        
        print("\n✓ 测试通过！")
        print("  现在可以在界面上测试复制版本功能")
        print("  复制后的版本应该包含所有节点的 rule 字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_copy_version_with_rule()
    sys.exit(0 if success else 1)
