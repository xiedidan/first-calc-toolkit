# 业务导向管理 Schema 使用指南

## 快速开始

### 导入 Schema

```python
from app.schemas import (
    OrientationRule,
    OrientationRuleCreate,
    OrientationRuleUpdate,
    OrientationBenchmark,
    OrientationBenchmarkCreate,
    OrientationBenchmarkUpdate,
    OrientationLadder,
    OrientationLadderCreate,
    OrientationLadderUpdate,
)
from app.models.orientation_rule import OrientationCategory
from app.models.orientation_benchmark import BenchmarkType
```

## 导向规则 Schema

### 创建导向规则

```python
# 创建请求
rule_data = OrientationRuleCreate(
    name="基准阶梯导向",
    category=OrientationCategory.benchmark_ladder,
    description="基于统计基准的阶梯调整导向"
)

# 验证会自动进行：
# - 名称长度：1-100字符
# - 名称不能为空白
# - 描述最多1024字符
# - 类别必须为有效枚举值
```

### 更新导向规则

```python
# 更新请求（所有字段可选）
update_data = OrientationRuleUpdate(
    name="更新后的导向名称",
    description="更新后的描述"
)
```

### 响应数据

```python
# API 响应
rule = OrientationRule(
    id=1,
    hospital_id=1,
    name="基准阶梯导向",
    category=OrientationCategory.benchmark_ladder,
    description="基于统计基准的阶梯调整导向",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

## 导向基准 Schema

### 创建导向基准

```python
from datetime import datetime
from decimal import Decimal

# 创建请求
benchmark_data = OrientationBenchmarkCreate(
    rule_id=1,
    department_code="001",
    department_name="内科",
    benchmark_type=BenchmarkType.average,
    control_intensity=Decimal("1.2345"),  # 自动格式化为4位小数
    stat_start_date=datetime(2024, 1, 1),
    stat_end_date=datetime(2024, 12, 31),
    benchmark_value=Decimal("100.5678")  # 自动格式化为4位小数
)

# 验证会自动进行：
# - 科室代码和名称不能为空
# - 数值自动格式化为4位小数
# - 开始时间必须早于结束时间
```

### 数值精度示例

```python
# 输入超过4位小数的值
benchmark = OrientationBenchmarkCreate(
    rule_id=1,
    department_code="001",
    department_name="内科",
    benchmark_type=BenchmarkType.average,
    control_intensity=Decimal("1.23456789"),  # 输入
    stat_start_date=datetime(2024, 1, 1),
    stat_end_date=datetime(2024, 12, 31),
    benchmark_value=Decimal("100.56789")  # 输入
)

# 自动格式化后：
# control_intensity = Decimal("1.2346")  # 四舍五入
# benchmark_value = Decimal("100.5679")  # 四舍五入
```

### 响应数据（带预加载字段）

```python
# API 响应
benchmark = OrientationBenchmark(
    id=1,
    hospital_id=1,
    rule_id=1,
    department_code="001",
    department_name="内科",
    benchmark_type=BenchmarkType.average,
    control_intensity=Decimal("1.2345"),
    stat_start_date=datetime(2024, 1, 1),
    stat_end_date=datetime(2024, 12, 31),
    benchmark_value=Decimal("100.5678"),
    created_at=datetime.now(),
    updated_at=datetime.now(),
    rule_name="基准阶梯导向"  # 预加载字段
)
```

## 导向阶梯 Schema

### 创建导向阶梯

```python
# 创建请求（有限范围）
ladder_data = OrientationLadderCreate(
    rule_id=1,
    ladder_order=1,
    upper_limit=Decimal("100.0"),
    lower_limit=Decimal("0.0"),
    adjustment_intensity=Decimal("1.5")
)

# 验证会自动进行：
# - 阶梯次序必须≥1
# - 数值自动格式化为4位小数
# - 下限必须小于上限
```

### 无穷值支持

```python
# 正无穷（上限为 NULL）
ladder_positive_infinity = OrientationLadderCreate(
    rule_id=1,
    ladder_order=3,
    upper_limit=None,  # 正无穷
    lower_limit=Decimal("100.0"),
    adjustment_intensity=Decimal("2.0")
)

# 负无穷（下限为 NULL）
ladder_negative_infinity = OrientationLadderCreate(
    rule_id=1,
    ladder_order=1,
    upper_limit=Decimal("0.0"),
    lower_limit=None,  # 负无穷
    adjustment_intensity=Decimal("0.5")
)

# 双向无穷（不推荐，但技术上可行）
ladder_full_infinity = OrientationLadderCreate(
    rule_id=1,
    ladder_order=2,
    upper_limit=None,
    lower_limit=None,
    adjustment_intensity=Decimal("1.0")
)
```

### 响应数据（带预加载字段）

```python
# API 响应
ladder = OrientationLadder(
    id=1,
    hospital_id=1,
    rule_id=1,
    ladder_order=1,
    upper_limit=Decimal("100.0"),
    lower_limit=Decimal("0.0"),
    adjustment_intensity=Decimal("1.5"),
    created_at=datetime.now(),
    updated_at=datetime.now(),
    rule_name="基准阶梯导向"  # 预加载字段
)
```

## API 端点使用示例

### FastAPI 路由定义

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_hospital_id_or_raise
from app.schemas import (
    OrientationRuleCreate,
    OrientationRuleUpdate,
    OrientationRule,
    OrientationRuleList,
)

router = APIRouter()

@router.post("/orientation-rules", response_model=OrientationRule)
def create_orientation_rule(
    rule: OrientationRuleCreate,
    db: Session = Depends(get_db),
    hospital_id: int = Depends(get_current_hospital_id_or_raise)
):
    """创建导向规则"""
    # rule 已经过验证
    # 可以直接使用 rule.name, rule.category, rule.description
    ...

@router.put("/orientation-rules/{rule_id}", response_model=OrientationRule)
def update_orientation_rule(
    rule_id: int,
    rule: OrientationRuleUpdate,
    db: Session = Depends(get_db),
    hospital_id: int = Depends(get_current_hospital_id_or_raise)
):
    """更新导向规则"""
    # rule 已经过验证
    # 只有提供的字段会被更新
    ...

@router.get("/orientation-rules", response_model=OrientationRuleList)
def list_orientation_rules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    hospital_id: int = Depends(get_current_hospital_id_or_raise)
):
    """获取导向规则列表"""
    ...
```

## 错误处理

### 验证错误示例

```python
from pydantic import ValidationError

try:
    # 尝试创建无效数据
    rule = OrientationRuleCreate(
        name="",  # 空名称
        category=OrientationCategory.benchmark_ladder
    )
except ValidationError as e:
    print(e.errors())
    # [
    #     {
    #         'type': 'value_error',
    #         'loc': ('name',),
    #         'msg': 'Value error, 导向名称不能为空',
    #         'input': '',
    #         'ctx': {'error': ValueError('导向名称不能为空')}
    #     }
    # ]
```

### FastAPI 自动错误响应

FastAPI 会自动将验证错误转换为 422 响应：

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "name"],
      "msg": "Value error, 导向名称不能为空",
      "input": ""
    }
  ]
}
```

## 最佳实践

### 1. 使用类型提示

```python
from typing import List

def process_rules(rules: List[OrientationRule]) -> None:
    for rule in rules:
        # IDE 会提供自动完成
        print(f"规则: {rule.name}, 类别: {rule.category}")
```

### 2. 数值处理

```python
from decimal import Decimal

# 推荐：使用字符串创建 Decimal
value = Decimal("1.2345")

# 避免：使用浮点数（可能有精度问题）
value = Decimal(1.2345)  # 可能不精确
```

### 3. 日期处理

```python
from datetime import datetime

# 推荐：明确指定日期时间
start_date = datetime(2024, 1, 1, 0, 0, 0)
end_date = datetime(2024, 12, 31, 23, 59, 59)

# 或使用 ISO 格式字符串（API 请求）
# "2024-01-01T00:00:00"
```

### 4. 枚举值处理

```python
# 推荐：使用枚举类型
category = OrientationCategory.benchmark_ladder

# 也可以使用字符串（会自动转换）
category = "benchmark_ladder"

# 获取枚举值
category_value = category.value  # "benchmark_ladder"
```

## 测试示例

```python
import pytest
from app.schemas import OrientationRuleCreate
from app.models.orientation_rule import OrientationCategory

def test_valid_rule_creation():
    """测试有效的导向规则创建"""
    rule = OrientationRuleCreate(
        name="测试导向",
        category=OrientationCategory.benchmark_ladder,
        description="测试描述"
    )
    assert rule.name == "测试导向"
    assert rule.category == OrientationCategory.benchmark_ladder

def test_invalid_rule_name():
    """测试无效的导向规则名称"""
    with pytest.raises(ValueError):
        OrientationRuleCreate(
            name="   ",  # 空白名称
            category=OrientationCategory.benchmark_ladder
        )

def test_decimal_precision():
    """测试数值精度自动格式化"""
    from decimal import Decimal
    from datetime import datetime
    from app.schemas import OrientationBenchmarkCreate
    from app.models.orientation_benchmark import BenchmarkType
    
    benchmark = OrientationBenchmarkCreate(
        rule_id=1,
        department_code="001",
        department_name="内科",
        benchmark_type=BenchmarkType.average,
        control_intensity=Decimal("1.23456789"),
        stat_start_date=datetime(2024, 1, 1),
        stat_end_date=datetime(2024, 12, 31),
        benchmark_value=Decimal("100.56789")
    )
    
    # 验证自动格式化为4位小数
    assert benchmark.control_intensity == Decimal("1.2346")
    assert benchmark.benchmark_value == Decimal("100.5679")
```

## 常见问题

### Q: 为什么数值要使用 Decimal 而不是 float？
A: Decimal 提供精确的十进制运算，避免浮点数的精度问题。金融和统计数据应始终使用 Decimal。

### Q: 如何处理前端传来的数值？
A: Pydantic 会自动将字符串、整数、浮点数转换为 Decimal。推荐前端发送字符串格式的数值。

### Q: 无穷值在数据库中如何存储？
A: 使用 NULL 表示无穷值。查询时需要特殊处理（如显示为"∞"或"-∞"）。

### Q: 如何在 API 中使用预加载字段？
A: 在查询数据库后，手动设置预加载字段：
```python
benchmark.rule_name = benchmark.rule.name
```

### Q: 更新时如何只更新部分字段？
A: 使用 `OrientationRuleUpdate`，只设置需要更新的字段。未设置的字段为 None，不会更新。

## 相关文档

- [设计文档](.kiro/specs/business-orientation-management/design.md)
- [需求文档](.kiro/specs/business-orientation-management/requirements.md)
- [任务列表](.kiro/specs/business-orientation-management/tasks.md)
- [实现总结](ORIENTATION_SCHEMAS_IMPLEMENTATION.md)
