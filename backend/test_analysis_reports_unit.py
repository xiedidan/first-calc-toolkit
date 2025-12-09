"""
科室运营分析报告单元测试

测试 Schema 验证和模型定义
"""
import sys
from datetime import datetime
from decimal import Decimal

# 测试 Schema 验证
def test_schema_validation():
    """测试 Schema 验证"""
    from app.schemas.analysis_report import (
        AnalysisReportBase,
        AnalysisReportCreate,
        AnalysisReportUpdate,
        AnalysisReport,
        ValueDistributionItem,
        BusinessContentItem,
    )
    from pydantic import ValidationError
    
    print("=" * 60)
    print("Schema 验证测试")
    print("=" * 60)
    
    errors = []
    
    # 测试 1: 有效的年月格式
    print("\n1. 测试有效的年月格式...")
    try:
        report = AnalysisReportCreate(
            department_id=1,
            period="2025-12",
            current_issues="测试问题",
            future_plans="测试计划"
        )
        print(f"   ✓ 有效格式 '2025-12' 通过验证")
    except ValidationError as e:
        print(f"   ✗ 有效格式验证失败: {e}")
        errors.append("有效年月格式验证失败")
    
    # 测试 2: 无效的年月格式
    print("\n2. 测试无效的年月格式...")
    try:
        report = AnalysisReportCreate(
            department_id=1,
            period="2025-1",  # 无效格式
            current_issues="测试问题"
        )
        print(f"   ✗ 无效格式 '2025-1' 应该被拒绝")
        errors.append("无效年月格式未被拒绝")
    except ValidationError as e:
        print(f"   ✓ 无效格式 '2025-1' 被正确拒绝")
    
    # 测试 3: 内容长度验证 - 正好 2000 字符
    print("\n3. 测试内容长度验证 (2000字符)...")
    try:
        content_2000 = "x" * 2000
        report = AnalysisReportCreate(
            department_id=1,
            period="2025-12",
            current_issues=content_2000
        )
        print(f"   ✓ 2000字符内容通过验证")
    except ValidationError as e:
        print(f"   ✗ 2000字符内容验证失败: {e}")
        errors.append("2000字符内容验证失败")
    
    # 测试 4: 内容长度验证 - 超过 2000 字符
    print("\n4. 测试内容长度验证 (2001字符)...")
    try:
        content_2001 = "x" * 2001
        report = AnalysisReportCreate(
            department_id=1,
            period="2025-12",
            current_issues=content_2001
        )
        print(f"   ✗ 2001字符内容应该被拒绝")
        errors.append("超长内容未被拒绝")
    except ValidationError as e:
        print(f"   ✓ 2001字符内容被正确拒绝")
    
    # 测试 5: 更新 Schema 验证
    print("\n5. 测试更新 Schema 验证...")
    try:
        update = AnalysisReportUpdate(
            current_issues="更新的问题",
            future_plans="更新的计划"
        )
        print(f"   ✓ 更新 Schema 验证通过")
    except ValidationError as e:
        print(f"   ✗ 更新 Schema 验证失败: {e}")
        errors.append("更新 Schema 验证失败")
    
    # 测试 6: ValueDistributionItem 验证
    print("\n6. 测试 ValueDistributionItem 验证...")
    try:
        item = ValueDistributionItem(
            rank=1,
            dimension_name="测试维度",
            value=Decimal("1000.50"),
            ratio=Decimal("25.50")
        )
        print(f"   ✓ ValueDistributionItem 验证通过")
    except ValidationError as e:
        print(f"   ✗ ValueDistributionItem 验证失败: {e}")
        errors.append("ValueDistributionItem 验证失败")
    
    # 测试 7: BusinessContentItem 验证
    print("\n7. 测试 BusinessContentItem 验证...")
    try:
        item = BusinessContentItem(
            rank=1,
            dimension_name="测试维度",
            item_code="ITEM001",
            item_name="测试项目",
            value=Decimal("500.00")
        )
        print(f"   ✓ BusinessContentItem 验证通过")
    except ValidationError as e:
        print(f"   ✗ BusinessContentItem 验证失败: {e}")
        errors.append("BusinessContentItem 验证失败")
    
    # 测试 8: 可选字段为 None
    print("\n8. 测试可选字段为 None...")
    try:
        report = AnalysisReportCreate(
            department_id=1,
            period="2025-12",
            current_issues=None,
            future_plans=None
        )
        print(f"   ✓ 可选字段为 None 验证通过")
    except ValidationError as e:
        print(f"   ✗ 可选字段为 None 验证失败: {e}")
        errors.append("可选字段为 None 验证失败")
    
    return errors


def test_model_definition():
    """测试模型定义"""
    from app.models.analysis_report import AnalysisReport
    
    print("\n" + "=" * 60)
    print("模型定义测试")
    print("=" * 60)
    
    errors = []
    
    # 测试 1: 检查表名
    print("\n1. 检查表名...")
    if AnalysisReport.__tablename__ == "analysis_reports":
        print(f"   ✓ 表名正确: {AnalysisReport.__tablename__}")
    else:
        print(f"   ✗ 表名错误: {AnalysisReport.__tablename__}")
        errors.append("表名错误")
    
    # 测试 2: 检查必要字段
    print("\n2. 检查必要字段...")
    required_columns = ['id', 'hospital_id', 'department_id', 'period', 
                       'current_issues', 'future_plans', 'created_at', 
                       'updated_at', 'created_by']
    
    model_columns = [c.name for c in AnalysisReport.__table__.columns]
    
    for col in required_columns:
        if col in model_columns:
            print(f"   ✓ 字段 '{col}' 存在")
        else:
            print(f"   ✗ 字段 '{col}' 缺失")
            errors.append(f"字段 '{col}' 缺失")
    
    # 测试 3: 检查关系定义
    print("\n3. 检查关系定义...")
    relationships = ['hospital', 'department', 'creator']
    
    for rel in relationships:
        if hasattr(AnalysisReport, rel):
            print(f"   ✓ 关系 '{rel}' 已定义")
        else:
            print(f"   ✗ 关系 '{rel}' 未定义")
            errors.append(f"关系 '{rel}' 未定义")
    
    return errors


def test_api_router():
    """测试 API 路由定义"""
    from app.api.analysis_reports import router
    
    print("\n" + "=" * 60)
    print("API 路由测试")
    print("=" * 60)
    
    errors = []
    
    # 检查路由数量
    print(f"\n路由总数: {len(router.routes)}")
    
    # 预期的路由
    expected_routes = [
        ("GET", ""),
        ("GET", "/{report_id}"),
        ("POST", ""),
        ("PUT", "/{report_id}"),
        ("DELETE", "/{report_id}"),
        ("GET", "/{report_id}/value-distribution"),
        ("GET", "/{report_id}/business-content"),
    ]
    
    # 获取实际路由
    actual_routes = []
    for route in router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                if method != "HEAD":  # 忽略 HEAD 方法
                    actual_routes.append((method, route.path))
    
    print("\n实际路由:")
    for method, path in actual_routes:
        print(f"   {method} {path}")
    
    # 检查预期路由是否存在
    print("\n检查预期路由:")
    for method, path in expected_routes:
        if (method, path) in actual_routes:
            print(f"   ✓ {method} {path}")
        else:
            print(f"   ✗ {method} {path} 缺失")
            errors.append(f"路由 {method} {path} 缺失")
    
    return errors


def main():
    """主测试函数"""
    print("=" * 60)
    print("科室运营分析报告单元测试")
    print("=" * 60)
    
    all_errors = []
    
    # 运行 Schema 验证测试
    errors = test_schema_validation()
    all_errors.extend(errors)
    
    # 运行模型定义测试
    errors = test_model_definition()
    all_errors.extend(errors)
    
    # 运行 API 路由测试
    errors = test_api_router()
    all_errors.extend(errors)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if all_errors:
        print(f"\n发现 {len(all_errors)} 个错误:")
        for error in all_errors:
            print(f"   - {error}")
        sys.exit(1)
    else:
        print("\n✓ 所有测试通过!")
        sys.exit(0)


if __name__ == "__main__":
    main()
