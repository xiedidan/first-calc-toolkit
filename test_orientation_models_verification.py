"""
验证业务导向管理模型的完整性和关系
"""
import sys
sys.path.insert(0, 'backend')

from app.models import (
    OrientationRule, OrientationCategory,
    OrientationBenchmark, BenchmarkType,
    OrientationLadder,
    Hospital,
    ModelNode
)
from sqlalchemy import inspect


def verify_model_fields(model_class, expected_fields):
    """验证模型字段"""
    mapper = inspect(model_class)
    actual_fields = {col.key for col in mapper.columns}
    
    print(f"\n检查 {model_class.__name__} 模型:")
    print(f"  预期字段: {expected_fields}")
    print(f"  实际字段: {actual_fields}")
    
    missing = expected_fields - actual_fields
    extra = actual_fields - expected_fields
    
    if missing:
        print(f"  ❌ 缺少字段: {missing}")
        return False
    if extra:
        print(f"  ℹ️  额外字段: {extra}")
    
    print(f"  ✅ 所有必需字段都存在")
    return True


def verify_relationships(model_class, expected_relationships):
    """验证模型关系"""
    mapper = inspect(model_class)
    actual_relationships = {rel.key for rel in mapper.relationships}
    
    print(f"\n检查 {model_class.__name__} 关系:")
    print(f"  预期关系: {expected_relationships}")
    print(f"  实际关系: {actual_relationships}")
    
    missing = expected_relationships - actual_relationships
    
    if missing:
        print(f"  ❌ 缺少关系: {missing}")
        return False
    
    print(f"  ✅ 所有必需关系都存在")
    return True


def verify_enums():
    """验证枚举类型"""
    print("\n检查枚举类型:")
    
    # OrientationCategory
    expected_categories = {'benchmark_ladder', 'direct_ladder', 'other'}
    actual_categories = {e.value for e in OrientationCategory}
    print(f"  OrientationCategory: {actual_categories}")
    if expected_categories == actual_categories:
        print(f"  ✅ OrientationCategory 正确")
    else:
        print(f"  ❌ OrientationCategory 不匹配")
        return False
    
    # BenchmarkType
    expected_benchmark_types = {'average', 'median', 'max', 'min', 'other'}
    actual_benchmark_types = {e.value for e in BenchmarkType}
    print(f"  BenchmarkType: {actual_benchmark_types}")
    if expected_benchmark_types == actual_benchmark_types:
        print(f"  ✅ BenchmarkType 正确")
    else:
        print(f"  ❌ BenchmarkType 不匹配")
        return False
    
    return True


def main():
    """主验证函数"""
    print("=" * 60)
    print("业务导向管理模型验证")
    print("=" * 60)
    
    all_passed = True
    
    # 验证枚举
    if not verify_enums():
        all_passed = False
    
    # 验证 OrientationRule
    orientation_rule_fields = {
        'id', 'hospital_id', 'name', 'category', 'description',
        'created_at', 'updated_at'
    }
    orientation_rule_relationships = {
        'hospital', 'benchmarks', 'ladders', 'model_nodes'
    }
    
    if not verify_model_fields(OrientationRule, orientation_rule_fields):
        all_passed = False
    if not verify_relationships(OrientationRule, orientation_rule_relationships):
        all_passed = False
    
    # 验证 OrientationBenchmark
    orientation_benchmark_fields = {
        'id', 'hospital_id', 'rule_id', 'department_code', 'department_name',
        'benchmark_type', 'control_intensity', 'stat_start_date', 'stat_end_date',
        'benchmark_value', 'created_at', 'updated_at'
    }
    orientation_benchmark_relationships = {
        'hospital', 'rule'
    }
    
    if not verify_model_fields(OrientationBenchmark, orientation_benchmark_fields):
        all_passed = False
    if not verify_relationships(OrientationBenchmark, orientation_benchmark_relationships):
        all_passed = False
    
    # 验证 OrientationLadder
    orientation_ladder_fields = {
        'id', 'hospital_id', 'rule_id', 'ladder_order',
        'upper_limit', 'lower_limit', 'adjustment_intensity',
        'created_at', 'updated_at'
    }
    orientation_ladder_relationships = {
        'hospital', 'rule'
    }
    
    if not verify_model_fields(OrientationLadder, orientation_ladder_fields):
        all_passed = False
    if not verify_relationships(OrientationLadder, orientation_ladder_relationships):
        all_passed = False
    
    # 验证 Hospital 的反向关系
    hospital_orientation_relationships = {
        'orientation_rules', 'orientation_benchmarks', 'orientation_ladders'
    }
    print(f"\n检查 Hospital 模型的导向管理关系:")
    mapper = inspect(Hospital)
    actual_relationships = {rel.key for rel in mapper.relationships}
    
    missing = hospital_orientation_relationships - actual_relationships
    if missing:
        print(f"  ❌ Hospital 缺少关系: {missing}")
        all_passed = False
    else:
        print(f"  ✅ Hospital 包含所有导向管理关系")
    
    # 验证 ModelNode 的关系
    print(f"\n检查 ModelNode 模型的导向规则关系:")
    mapper = inspect(ModelNode)
    actual_fields = {col.key for col in mapper.columns}
    actual_relationships = {rel.key for rel in mapper.relationships}
    
    if 'orientation_rule_id' not in actual_fields:
        print(f"  ❌ ModelNode 缺少字段: orientation_rule_id")
        all_passed = False
    else:
        print(f"  ✅ ModelNode 包含 orientation_rule_id 字段")
    
    if 'orientation_rule' not in actual_relationships:
        print(f"  ❌ ModelNode 缺少关系: orientation_rule")
        all_passed = False
    else:
        print(f"  ✅ ModelNode 包含 orientation_rule 关系")
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有模型验证通过！")
        print("=" * 60)
        return 0
    else:
        print("❌ 部分验证失败，请检查上述错误")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
