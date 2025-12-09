"""
简单测试导向规则API - 直接使用数据库
"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.models.hospital import Hospital

def test_orientation_rule_crud():
    """测试导向规则CRUD操作"""
    db: Session = SessionLocal()
    
    try:
        # 确保有一个医疗机构
        hospital = db.query(Hospital).first()
        if not hospital:
            print("错误：数据库中没有医疗机构")
            return
        
        print(f"使用医疗机构: {hospital.name} (ID: {hospital.id})")
        
        # 1. 创建导向规则
        print("\n=== 测试创建导向规则 ===")
        rule = OrientationRule(
            hospital_id=hospital.id,
            name="测试导向规则-API",
            category=OrientationCategory.benchmark_ladder,
            description="这是一个通过API测试创建的导向规则"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        print(f"✓ 创建成功: ID={rule.id}, 名称={rule.name}, 类别={rule.category.value}")
        
        # 2. 查询导向规则
        print("\n=== 测试查询导向规则 ===")
        found_rule = db.query(OrientationRule).filter(
            OrientationRule.id == rule.id,
            OrientationRule.hospital_id == hospital.id
        ).first()
        if found_rule:
            print(f"✓ 查询成功: {found_rule.name}")
        else:
            print("✗ 查询失败")
        
        # 3. 更新导向规则
        print("\n=== 测试更新导向规则 ===")
        rule.description = "更新后的描述"
        db.commit()
        db.refresh(rule)
        print(f"✓ 更新成功: {rule.description}")
        
        # 4. 列表查询
        print("\n=== 测试列表查询 ===")
        rules = db.query(OrientationRule).filter(
            OrientationRule.hospital_id == hospital.id
        ).all()
        print(f"✓ 找到 {len(rules)} 条导向规则")
        for r in rules:
            print(f"  - {r.name} ({r.category.value})")
        
        # 5. 删除导向规则
        print("\n=== 测试删除导向规则 ===")
        db.delete(rule)
        db.commit()
        print("✓ 删除成功")
        
        # 验证删除
        deleted_rule = db.query(OrientationRule).filter(
            OrientationRule.id == rule.id
        ).first()
        if deleted_rule is None:
            print("✓ 验证删除成功")
        else:
            print("✗ 删除验证失败")
        
        print("\n所有测试通过！")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_orientation_rule_crud()
