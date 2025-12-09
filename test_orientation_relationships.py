"""
测试业务导向管理模型的关系是否正确工作
"""
import sys
sys.path.insert(0, 'backend')

from app.models import (
    OrientationRule, OrientationCategory,
    OrientationBenchmark, BenchmarkType,
    OrientationLadder,
    Hospital,
    ModelNode,
    ModelVersion
)
from app.database import SessionLocal, engine, Base
from datetime import datetime


def test_relationships():
    """测试模型关系"""
    print("=" * 60)
    print("测试业务导向管理模型关系")
    print("=" * 60)
    
    # 创建测试会话
    db = SessionLocal()
    
    try:
        # 1. 查找或创建测试医疗机构
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
            print(f"✅ 创建测试医疗机构: {hospital.name} (ID: {hospital.id})")
        else:
            print(f"✅ 使用现有测试医疗机构: {hospital.name} (ID: {hospital.id})")
        
        # 2. 创建导向规则
        rule = OrientationRule(
            hospital_id=hospital.id,
            name="测试导向规则",
            category=OrientationCategory.benchmark_ladder,
            description="这是一个测试导向规则"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        print(f"✅ 创建导向规则: {rule.name} (ID: {rule.id})")
        
        # 验证 OrientationRule -> Hospital 关系
        assert rule.hospital is not None
        assert rule.hospital.id == hospital.id
        print(f"  ✅ OrientationRule.hospital 关系正常")
        
        # 验证 Hospital -> OrientationRule 反向关系
        db.refresh(hospital)
        assert any(r.id == rule.id for r in hospital.orientation_rules)
        print(f"  ✅ Hospital.orientation_rules 反向关系正常")
        
        # 3. 创建导向基准
        benchmark = OrientationBenchmark(
            hospital_id=hospital.id,
            rule_id=rule.id,
            department_code="TEST_DEPT",
            department_name="测试科室",
            benchmark_type=BenchmarkType.average,
            control_intensity=1.2000,
            stat_start_date=datetime(2024, 1, 1),
            stat_end_date=datetime(2024, 12, 31),
            benchmark_value=100.5000
        )
        db.add(benchmark)
        db.commit()
        db.refresh(benchmark)
        print(f"✅ 创建导向基准 (ID: {benchmark.id})")
        
        # 验证 OrientationBenchmark -> OrientationRule 关系
        assert benchmark.rule is not None
        assert benchmark.rule.id == rule.id
        print(f"  ✅ OrientationBenchmark.rule 关系正常")
        
        # 验证 OrientationRule -> OrientationBenchmark 反向关系
        db.refresh(rule)
        assert any(b.id == benchmark.id for b in rule.benchmarks)
        print(f"  ✅ OrientationRule.benchmarks 反向关系正常")
        
        # 4. 创建导向阶梯
        ladder = OrientationLadder(
            hospital_id=hospital.id,
            rule_id=rule.id,
            ladder_order=1,
            upper_limit=100.0000,
            lower_limit=0.0000,
            adjustment_intensity=1.5000
        )
        db.add(ladder)
        db.commit()
        db.refresh(ladder)
        print(f"✅ 创建导向阶梯 (ID: {ladder.id})")
        
        # 验证 OrientationLadder -> OrientationRule 关系
        assert ladder.rule is not None
        assert ladder.rule.id == rule.id
        print(f"  ✅ OrientationLadder.rule 关系正常")
        
        # 验证 OrientationRule -> OrientationLadder 反向关系
        db.refresh(rule)
        assert any(l.id == ladder.id for l in rule.ladders)
        print(f"  ✅ OrientationRule.ladders 反向关系正常")
        
        # 5. 测试 ModelNode 关联（如果存在模型版本）
        version = db.query(ModelVersion).filter(
            ModelVersion.hospital_id == hospital.id
        ).first()
        
        if version:
            # 查找末级节点
            leaf_node = db.query(ModelNode).filter(
                ModelNode.version_id == version.id,
                ModelNode.is_leaf == True
            ).first()
            
            if leaf_node:
                # 关联导向规则
                leaf_node.orientation_rule_id = rule.id
                db.commit()
                db.refresh(leaf_node)
                print(f"✅ 关联模型节点到导向规则")
                
                # 验证 ModelNode -> OrientationRule 关系
                assert leaf_node.orientation_rule is not None
                assert leaf_node.orientation_rule.id == rule.id
                print(f"  ✅ ModelNode.orientation_rule 关系正常")
                
                # 验证 OrientationRule -> ModelNode 反向关系
                db.refresh(rule)
                assert any(n.id == leaf_node.id for n in rule.model_nodes)
                print(f"  ✅ OrientationRule.model_nodes 反向关系正常")
            else:
                print(f"ℹ️  未找到末级节点，跳过 ModelNode 关联测试")
        else:
            print(f"ℹ️  未找到模型版本，跳过 ModelNode 关联测试")
        
        # 6. 测试级联删除
        print(f"\n测试级联删除:")
        benchmark_id = benchmark.id
        ladder_id = ladder.id
        
        # 删除导向规则应该级联删除基准和阶梯
        db.delete(rule)
        db.commit()
        print(f"✅ 删除导向规则")
        
        # 验证基准和阶梯已被删除
        deleted_benchmark = db.query(OrientationBenchmark).filter(
            OrientationBenchmark.id == benchmark_id
        ).first()
        deleted_ladder = db.query(OrientationLadder).filter(
            OrientationLadder.id == ladder_id
        ).first()
        
        assert deleted_benchmark is None
        assert deleted_ladder is None
        print(f"  ✅ 级联删除正常工作（基准和阶梯已删除）")
        
        print("\n" + "=" * 60)
        print("✅ 所有关系测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_relationships()
    sys.exit(0 if success else 1)
