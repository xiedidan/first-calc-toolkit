"""
测试导向规则导出功能
"""
import sys
import os
from datetime import datetime, timedelta

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.models.orientation_benchmark import OrientationBenchmark, BenchmarkType
from app.models.orientation_ladder import OrientationLadder
from app.services.orientation_rule_service import OrientationRuleService
from app.middleware.hospital_context import set_current_hospital_id

# 数据库连接
DATABASE_URL = "postgresql://admin:admin123@localhost:5432/hospital_value"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def test_export_benchmark_ladder_rule():
    """测试导出基准阶梯类别的导向规则"""
    print("\n=== 测试导出基准阶梯类别的导向规则 ===")
    
    db = SessionLocal()
    try:
        # 设置当前医疗机构ID
        set_current_hospital_id(1)
        
        # 创建测试导向规则
        rule = OrientationRule(
            hospital_id=1,
            name="测试导出基准阶梯",
            category=OrientationCategory.benchmark_ladder,
            description="这是一个用于测试导出功能的基准阶梯导向规则"
        )
        db.add(rule)
        db.flush()
        
        # 添加导向基准
        benchmark1 = OrientationBenchmark(
            hospital_id=1,
            rule_id=rule.id,
            department_code="D001",
            department_name="内科",
            benchmark_type=BenchmarkType.average,
            control_intensity=0.8500,
            stat_start_date=datetime(2024, 1, 1),
            stat_end_date=datetime(2024, 12, 31),
            benchmark_value=1000.5000
        )
        db.add(benchmark1)
        
        benchmark2 = OrientationBenchmark(
            hospital_id=1,
            rule_id=rule.id,
            department_code="D002",
            department_name="外科",
            benchmark_type=BenchmarkType.median,
            control_intensity=0.9000,
            stat_start_date=datetime(2024, 1, 1),
            stat_end_date=datetime(2024, 12, 31),
            benchmark_value=1200.7500
        )
        db.add(benchmark2)
        
        # 添加导向阶梯
        ladder1 = OrientationLadder(
            hospital_id=1,
            rule_id=rule.id,
            ladder_order=1,
            lower_limit=None,  # 负无穷
            upper_limit=0.8000,
            adjustment_intensity=0.5000
        )
        db.add(ladder1)
        
        ladder2 = OrientationLadder(
            hospital_id=1,
            rule_id=rule.id,
            ladder_order=2,
            lower_limit=0.8000,
            upper_limit=1.2000,
            adjustment_intensity=1.0000
        )
        db.add(ladder2)
        
        ladder3 = OrientationLadder(
            hospital_id=1,
            rule_id=rule.id,
            ladder_order=3,
            lower_limit=1.2000,
            upper_limit=None,  # 正无穷
            adjustment_intensity=1.5000
        )
        db.add(ladder3)
        
        db.commit()
        db.refresh(rule)
        
        print(f"✓ 创建测试导向规则: ID={rule.id}, 名称={rule.name}")
        print(f"  - 基准数量: {len(rule.benchmarks)}")
        print(f"  - 阶梯数量: {len(rule.ladders)}")
        
        # 导出规则
        buffer, filename = OrientationRuleService.export_rule(db, rule.id, 1)
        
        print(f"✓ 导出成功")
        print(f"  - 文件名: {filename}")
        
        # 读取并显示内容
        content = buffer.read().decode('utf-8')
        print(f"  - 内容长度: {len(content)} 字符")
        print("\n--- Markdown 内容预览 ---")
        print(content[:500])
        print("...")
        
        # 验证内容
        assert rule.name in content, "内容应包含导向名称"
        assert "基准阶梯" in content, "内容应包含导向类别"
        assert rule.description in content, "内容应包含描述"
        assert "导向基准" in content, "内容应包含基准表格"
        assert "导向阶梯" in content, "内容应包含阶梯表格"
        assert "内科" in content, "内容应包含科室名称"
        assert "平均值" in content, "内容应包含基准类别"
        assert "-∞" in content, "内容应包含负无穷符号"
        assert "+∞" in content, "内容应包含正无穷符号"
        
        print("\n✓ 所有验证通过")
        
        # 清理测试数据
        db.delete(rule)
        db.commit()
        print("✓ 清理测试数据完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def test_export_direct_ladder_rule():
    """测试导出直接阶梯类别的导向规则"""
    print("\n=== 测试导出直接阶梯类别的导向规则 ===")
    
    db = SessionLocal()
    try:
        # 设置当前医疗机构ID
        set_current_hospital_id(1)
        
        # 创建测试导向规则
        rule = OrientationRule(
            hospital_id=1,
            name="测试导出直接阶梯",
            category=OrientationCategory.direct_ladder,
            description="这是一个用于测试导出功能的直接阶梯导向规则"
        )
        db.add(rule)
        db.flush()
        
        # 添加导向阶梯
        ladder1 = OrientationLadder(
            hospital_id=1,
            rule_id=rule.id,
            ladder_order=1,
            lower_limit=0.0000,
            upper_limit=50.0000,
            adjustment_intensity=0.8000
        )
        db.add(ladder1)
        
        ladder2 = OrientationLadder(
            hospital_id=1,
            rule_id=rule.id,
            ladder_order=2,
            lower_limit=50.0000,
            upper_limit=100.0000,
            adjustment_intensity=1.0000
        )
        db.add(ladder2)
        
        db.commit()
        db.refresh(rule)
        
        print(f"✓ 创建测试导向规则: ID={rule.id}, 名称={rule.name}")
        print(f"  - 阶梯数量: {len(rule.ladders)}")
        
        # 导出规则
        buffer, filename = OrientationRuleService.export_rule(db, rule.id, 1)
        
        print(f"✓ 导出成功")
        print(f"  - 文件名: {filename}")
        
        # 读取并显示内容
        content = buffer.read().decode('utf-8')
        print(f"  - 内容长度: {len(content)} 字符")
        print("\n--- Markdown 内容预览 ---")
        print(content)
        
        # 验证内容
        assert rule.name in content, "内容应包含导向名称"
        assert "直接阶梯" in content, "内容应包含导向类别"
        assert "导向阶梯" in content, "内容应包含阶梯表格"
        assert "导向基准" not in content, "内容不应包含基准表格"
        
        print("\n✓ 所有验证通过")
        
        # 清理测试数据
        db.delete(rule)
        db.commit()
        print("✓ 清理测试数据完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def test_export_other_rule():
    """测试导出其他类别的导向规则"""
    print("\n=== 测试导出其他类别的导向规则 ===")
    
    db = SessionLocal()
    try:
        # 设置当前医疗机构ID
        set_current_hospital_id(1)
        
        # 创建测试导向规则
        rule = OrientationRule(
            hospital_id=1,
            name="测试导出其他类别",
            category=OrientationCategory.other,
            description="这是一个用于测试导出功能的其他类别导向规则"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        print(f"✓ 创建测试导向规则: ID={rule.id}, 名称={rule.name}")
        
        # 导出规则
        buffer, filename = OrientationRuleService.export_rule(db, rule.id, 1)
        
        print(f"✓ 导出成功")
        print(f"  - 文件名: {filename}")
        
        # 读取并显示内容
        content = buffer.read().decode('utf-8')
        print(f"  - 内容长度: {len(content)} 字符")
        print("\n--- Markdown 内容 ---")
        print(content)
        
        # 验证内容
        assert rule.name in content, "内容应包含导向名称"
        assert "其他" in content, "内容应包含导向类别"
        assert "导向基准" not in content, "内容不应包含基准表格"
        assert "导向阶梯" not in content, "内容不应包含阶梯表格"
        
        print("\n✓ 所有验证通过")
        
        # 清理测试数据
        db.delete(rule)
        db.commit()
        print("✓ 清理测试数据完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def test_export_filename_format():
    """测试导出文件名格式"""
    print("\n=== 测试导出文件名格式 ===")
    
    db = SessionLocal()
    try:
        # 设置当前医疗机构ID
        set_current_hospital_id(1)
        
        # 创建测试导向规则（包含中文名称）
        rule = OrientationRule(
            hospital_id=1,
            name="测试中文文件名导出",
            category=OrientationCategory.other,
            description="测试文件名格式"
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        print(f"✓ 创建测试导向规则: ID={rule.id}, 名称={rule.name}")
        
        # 导出规则
        buffer, filename = OrientationRuleService.export_rule(db, rule.id, 1)
        
        print(f"✓ 导出成功")
        print(f"  - 文件名: {filename}")
        
        # 验证文件名格式
        assert filename.startswith(rule.name), "文件名应以导向名称开头"
        assert filename.endswith(".md"), "文件名应以.md结尾"
        assert "_" in filename, "文件名应包含时间戳分隔符"
        
        # 验证时间戳格式（YYYYMMDD_HHMMSS）
        parts = filename.replace(".md", "").split("_")
        assert len(parts) >= 3, "文件名应包含时间戳"
        
        print("✓ 文件名格式验证通过")
        
        # 清理测试数据
        db.delete(rule)
        db.commit()
        print("✓ 清理测试数据完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("开始测试导向规则导出功能...")
    
    test_export_benchmark_ladder_rule()
    test_export_direct_ladder_rule()
    test_export_other_rule()
    test_export_filename_format()
    
    print("\n" + "="*50)
    print("所有测试完成！")
