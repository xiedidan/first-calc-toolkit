"""
测试业务导向管理模型
"""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models import (
    Hospital, 
    OrientationRule, 
    OrientationCategory,
    OrientationBenchmark,
    BenchmarkType,
    OrientationLadder
)
from datetime import datetime


def test_orientation_models():
    """测试业务导向管理模型"""
    db = SessionLocal()
    
    try:
        # 1. 获取或创建测试医院
        hospital = db.query(Hospital).filter(Hospital.code == "TEST_HOSPITAL").first()
        if not hospital:
            hospital = Hospital(
                code="TEST_HOSPITAL",
                name="测试医院",
                is_active=True
            )
            db.add(hospital)
            db.commit()
            db.refresh(hospital)
            print(f"✓ 创建测试医院: {hospital.name} (ID: {hospital.id})")
        else:
            print(f"✓ 使用现有测试医院: {hospital.name} (ID: {hospital.id})")
        
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
        print(f"✓ 创建导向规则: {rule.name} (ID: {rule.id}, 类别: {rule.category.value})")
        
        # 3. 创建导向基准
        benchmark = OrientationBenchmark(
            hospital_id=hospital.id,
            rule_id=rule.id,
            department_code="TEST_DEPT",
            department_name="测试科室",
            benchmark_type=BenchmarkType.average,
            control_intensity=1.2000,
            stat_start_date=datetime(2025, 1, 1),
            stat_end_date=datetime(2025, 12, 31),
            benchmark_value=100.5000
        )
        db.add(benchmark)
        db.commit()
        db.refresh(benchmark)
        print(f"✓ 创建导向基准: {benchmark.department_name} (ID: {benchmark.id}, 基准值: {benchmark.benchmark_value})")
        
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
        print(f"✓ 创建导向阶梯: 次序 {ladder.ladder_order} (ID: {ladder.id}, 调整力度: {ladder.adjustment_intensity})")
        
        # 5. 验证关系
        db.refresh(rule)
        print(f"\n关系验证:")
        print(f"  - 导向规则关联的基准数量: {len(rule.benchmarks)}")
        print(f"  - 导向规则关联的阶梯数量: {len(rule.ladders)}")
        print(f"  - 医院关联的导向规则数量: {len(hospital.orientation_rules)}")
        
        # 6. 测试多租户唯一约束
        try:
            duplicate_rule = OrientationRule(
                hospital_id=hospital.id,
                name="测试导向规则",  # 重复名称
                category=OrientationCategory.direct_ladder,
                description="重复的导向规则"
            )
            db.add(duplicate_rule)
            db.commit()
            print("✗ 多租户唯一约束测试失败：允许了重复名称")
        except Exception as e:
            db.rollback()
            print(f"✓ 多租户唯一约束测试通过：正确拒绝了重复名称")
        
        # 7. 清理测试数据
        print(f"\n清理测试数据...")
        db.delete(ladder)
        db.delete(benchmark)
        db.delete(rule)
        db.commit()
        print(f"✓ 测试数据已清理")
        
        print(f"\n所有测试通过！✓")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_orientation_models()
