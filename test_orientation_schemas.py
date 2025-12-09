"""
测试导向管理模块的Pydantic Schema验证
"""
import sys
sys.path.insert(0, 'backend')

from datetime import datetime
from decimal import Decimal
from app.schemas.orientation_rule import OrientationRuleCreate, OrientationRuleUpdate
from app.schemas.orientation_benchmark import OrientationBenchmarkCreate, OrientationBenchmarkUpdate
from app.schemas.orientation_ladder import OrientationLadderCreate, OrientationLadderUpdate
from app.models.orientation_rule import OrientationCategory
from app.models.orientation_benchmark import BenchmarkType


def test_orientation_rule_validation():
    """测试导向规则验证"""
    print("测试导向规则验证...")
    
    # 测试有效数据
    valid_rule = OrientationRuleCreate(
        name="测试导向",
        category=OrientationCategory.benchmark_ladder,
        description="这是一个测试导向"
    )
    print(f"✓ 有效导向规则创建成功: {valid_rule.name}")
    
    # 测试名称长度限制
    try:
        invalid_rule = OrientationRuleCreate(
            name="a" * 101,  # 超过100字符
            category=OrientationCategory.benchmark_ladder
        )
        print("✗ 应该拒绝超长名称")
    except ValueError as e:
        print(f"✓ 正确拒绝超长名称: {e}")
    
    # 测试空名称
    try:
        invalid_rule = OrientationRuleCreate(
            name="   ",  # 空白字符
            category=OrientationCategory.benchmark_ladder
        )
        print("✗ 应该拒绝空白名称")
    except ValueError as e:
        print(f"✓ 正确拒绝空白名称: {e}")
    
    # 测试描述长度限制
    try:
        invalid_rule = OrientationRuleCreate(
            name="测试",
            category=OrientationCategory.benchmark_ladder,
            description="a" * 1025  # 超过1024字符
        )
        print("✗ 应该拒绝超长描述")
    except ValueError as e:
        print(f"✓ 正确拒绝超长描述: {e}")
    
    print()


def test_orientation_benchmark_validation():
    """测试导向基准验证"""
    print("测试导向基准验证...")
    
    # 测试有效数据
    valid_benchmark = OrientationBenchmarkCreate(
        rule_id=1,
        department_code="001",
        department_name="内科",
        benchmark_type=BenchmarkType.average,
        control_intensity=Decimal("1.2345"),
        stat_start_date=datetime(2024, 1, 1),
        stat_end_date=datetime(2024, 12, 31),
        benchmark_value=Decimal("100.5678")
    )
    print(f"✓ 有效导向基准创建成功")
    print(f"  管控力度: {valid_benchmark.control_intensity} (应为4位小数)")
    print(f"  基准值: {valid_benchmark.benchmark_value} (应为4位小数)")
    
    # 测试数值精度自动格式化
    benchmark_with_precision = OrientationBenchmarkCreate(
        rule_id=1,
        department_code="001",
        department_name="内科",
        benchmark_type=BenchmarkType.average,
        control_intensity=Decimal("1.23456789"),  # 超过4位小数
        stat_start_date=datetime(2024, 1, 1),
        stat_end_date=datetime(2024, 12, 31),
        benchmark_value=Decimal("100.56789")  # 超过4位小数
    )
    print(f"✓ 数值自动格式化为4位小数:")
    print(f"  管控力度: {benchmark_with_precision.control_intensity}")
    print(f"  基准值: {benchmark_with_precision.benchmark_value}")
    
    # 测试日期范围验证
    try:
        invalid_benchmark = OrientationBenchmarkCreate(
            rule_id=1,
            department_code="001",
            department_name="内科",
            benchmark_type=BenchmarkType.average,
            control_intensity=Decimal("1.2345"),
            stat_start_date=datetime(2024, 12, 31),
            stat_end_date=datetime(2024, 1, 1),  # 结束时间早于开始时间
            benchmark_value=Decimal("100.5678")
        )
        print("✗ 应该拒绝无效日期范围")
    except ValueError as e:
        print(f"✓ 正确拒绝无效日期范围: {e}")
    
    # 测试空字符串验证
    try:
        invalid_benchmark = OrientationBenchmarkCreate(
            rule_id=1,
            department_code="   ",  # 空白字符
            department_name="内科",
            benchmark_type=BenchmarkType.average,
            control_intensity=Decimal("1.2345"),
            stat_start_date=datetime(2024, 1, 1),
            stat_end_date=datetime(2024, 12, 31),
            benchmark_value=Decimal("100.5678")
        )
        print("✗ 应该拒绝空白科室代码")
    except ValueError as e:
        print(f"✓ 正确拒绝空白科室代码: {e}")
    
    print()


def test_orientation_ladder_validation():
    """测试导向阶梯验证"""
    print("测试导向阶梯验证...")
    
    # 测试有效数据
    valid_ladder = OrientationLadderCreate(
        rule_id=1,
        ladder_order=1,
        upper_limit=Decimal("100.5678"),
        lower_limit=Decimal("0.1234"),
        adjustment_intensity=Decimal("1.2345")
    )
    print(f"✓ 有效导向阶梯创建成功")
    print(f"  上限: {valid_ladder.upper_limit} (应为4位小数)")
    print(f"  下限: {valid_ladder.lower_limit} (应为4位小数)")
    print(f"  调整力度: {valid_ladder.adjustment_intensity} (应为4位小数)")
    
    # 测试无穷值（NULL）
    ladder_with_infinity = OrientationLadderCreate(
        rule_id=1,
        ladder_order=2,
        upper_limit=None,  # 正无穷
        lower_limit=Decimal("100.0"),
        adjustment_intensity=Decimal("2.0")
    )
    print(f"✓ 支持无穷值: 上限={ladder_with_infinity.upper_limit}")
    
    # 测试范围验证
    try:
        invalid_ladder = OrientationLadderCreate(
            rule_id=1,
            ladder_order=1,
            upper_limit=Decimal("10.0"),
            lower_limit=Decimal("20.0"),  # 下限大于上限
            adjustment_intensity=Decimal("1.0")
        )
        print("✗ 应该拒绝无效范围")
    except ValueError as e:
        print(f"✓ 正确拒绝无效范围: {e}")
    
    # 测试阶梯次序验证
    try:
        invalid_ladder = OrientationLadderCreate(
            rule_id=1,
            ladder_order=0,  # 必须为正整数
            upper_limit=Decimal("100.0"),
            lower_limit=Decimal("0.0"),
            adjustment_intensity=Decimal("1.0")
        )
        print("✗ 应该拒绝无效阶梯次序")
    except ValueError as e:
        print(f"✓ 正确拒绝无效阶梯次序: {e}")
    
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("导向管理模块 Schema 验证测试")
    print("=" * 60)
    print()
    
    test_orientation_rule_validation()
    test_orientation_benchmark_validation()
    test_orientation_ladder_validation()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)
