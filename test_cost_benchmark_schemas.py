"""
测试成本基准Schemas
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# 添加backend目录到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.schemas.cost_benchmark import (
    CostBenchmarkBase,
    CostBenchmarkCreate,
    CostBenchmarkUpdate,
    CostBenchmark,
    CostBenchmarkList,
)


def test_cost_benchmark_create():
    """测试创建Schema"""
    print("测试 CostBenchmarkCreate...")
    
    # 有效数据
    data = {
        "department_code": "DEPT001",
        "department_name": "内科",
        "version_id": 1,
        "version_name": "2024版本",
        "dimension_code": "DIM001",
        "dimension_name": "医疗服务",
        "benchmark_value": Decimal("1000.50")
    }
    
    schema = CostBenchmarkCreate(**data)
    print(f"✓ 创建成功: {schema.department_name}, 基准值: {schema.benchmark_value}")
    
    # 验证基准值格式化为2位小数
    assert schema.benchmark_value == Decimal("1000.50")
    
    # 测试基准值必须大于0
    try:
        invalid_data = data.copy()
        invalid_data["benchmark_value"] = Decimal("0")
        CostBenchmarkCreate(**invalid_data)
        print("✗ 应该拒绝基准值为0")
        return False
    except ValueError as e:
        print(f"✓ 正确拒绝基准值为0: {e}")
    
    # 测试基准值必须大于0（负数）
    try:
        invalid_data = data.copy()
        invalid_data["benchmark_value"] = Decimal("-100")
        CostBenchmarkCreate(**invalid_data)
        print("✗ 应该拒绝负数基准值")
        return False
    except ValueError as e:
        print(f"✓ 正确拒绝负数基准值: {e}")
    
    # 测试必填字段不能为空
    try:
        invalid_data = data.copy()
        invalid_data["department_name"] = "  "
        CostBenchmarkCreate(**invalid_data)
        print("✗ 应该拒绝空字符串")
        return False
    except ValueError as e:
        print(f"✓ 正确拒绝空字符串: {e}")
    
    print("✓ CostBenchmarkCreate 测试通过\n")
    return True


def test_cost_benchmark_update():
    """测试更新Schema"""
    print("测试 CostBenchmarkUpdate...")
    
    # 部分更新
    data = {
        "benchmark_value": Decimal("2000.75")
    }
    
    schema = CostBenchmarkUpdate(**data)
    print(f"✓ 部分更新成功: 基准值: {schema.benchmark_value}")
    
    # 验证基准值格式化为2位小数
    assert schema.benchmark_value == Decimal("2000.75")
    
    # 测试基准值必须大于0
    try:
        invalid_data = {"benchmark_value": Decimal("-50")}
        CostBenchmarkUpdate(**invalid_data)
        print("✗ 应该拒绝负数基准值")
        return False
    except ValueError as e:
        print(f"✓ 正确拒绝负数基准值: {e}")
    
    # 测试可选字段可以为None
    schema = CostBenchmarkUpdate(department_name=None)
    assert schema.department_name is None
    print("✓ 可选字段可以为None")
    
    print("✓ CostBenchmarkUpdate 测试通过\n")
    return True


def test_cost_benchmark_response():
    """测试响应Schema"""
    print("测试 CostBenchmark 响应模型...")
    
    data = {
        "id": 1,
        "hospital_id": 1,
        "department_code": "DEPT001",
        "department_name": "内科",
        "version_id": 1,
        "version_name": "2024版本",
        "dimension_code": "DIM001",
        "dimension_name": "医疗服务",
        "benchmark_value": Decimal("1000.50"),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    schema = CostBenchmark(**data)
    print(f"✓ 响应模型创建成功: ID={schema.id}, 科室={schema.department_name}")
    
    print("✓ CostBenchmark 响应模型测试通过\n")
    return True


def test_cost_benchmark_list():
    """测试列表Schema"""
    print("测试 CostBenchmarkList...")
    
    items = [
        {
            "id": 1,
            "hospital_id": 1,
            "department_code": "DEPT001",
            "department_name": "内科",
            "version_id": 1,
            "version_name": "2024版本",
            "dimension_code": "DIM001",
            "dimension_name": "医疗服务",
            "benchmark_value": Decimal("1000.50"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "id": 2,
            "hospital_id": 1,
            "department_code": "DEPT002",
            "department_name": "外科",
            "version_id": 1,
            "version_name": "2024版本",
            "dimension_code": "DIM001",
            "dimension_name": "医疗服务",
            "benchmark_value": Decimal("1500.00"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    schema = CostBenchmarkList(total=2, items=items)
    print(f"✓ 列表模型创建成功: 总数={schema.total}, 项目数={len(schema.items)}")
    
    print("✓ CostBenchmarkList 测试通过\n")
    return True


def test_decimal_precision():
    """测试小数精度处理"""
    print("测试小数精度处理...")
    
    # 测试多位小数会被四舍五入到2位
    data = {
        "department_code": "DEPT001",
        "department_name": "内科",
        "version_id": 1,
        "version_name": "2024版本",
        "dimension_code": "DIM001",
        "dimension_name": "医疗服务",
        "benchmark_value": Decimal("1000.567")  # 3位小数
    }
    
    schema = CostBenchmarkCreate(**data)
    print(f"✓ 输入: 1000.567, 输出: {schema.benchmark_value}")
    assert schema.benchmark_value == Decimal("1000.57"), f"期望 1000.57, 实际 {schema.benchmark_value}"
    
    # 测试四舍五入
    data["benchmark_value"] = Decimal("1000.564")
    schema = CostBenchmarkCreate(**data)
    print(f"✓ 输入: 1000.564, 输出: {schema.benchmark_value}")
    assert schema.benchmark_value == Decimal("1000.56"), f"期望 1000.56, 实际 {schema.benchmark_value}"
    
    print("✓ 小数精度处理测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("成本基准 Schemas 测试")
    print("=" * 60 + "\n")
    
    tests = [
        test_cost_benchmark_create,
        test_cost_benchmark_update,
        test_cost_benchmark_response,
        test_cost_benchmark_list,
        test_decimal_precision,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ 测试失败: {e}\n")
            results.append(False)
    
    print("=" * 60)
    if all(results):
        print("✓ 所有测试通过!")
    else:
        print(f"✗ {results.count(False)} 个测试失败")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
