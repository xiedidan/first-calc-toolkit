# 业务导向管理 SQLAlchemy 模型实现总结

## 实施日期
2024-11-26

## 任务概述
实现业务导向管理模块的 SQLAlchemy 模型类，包括导向规则、导向基准、导向阶梯三个核心模型，以及与 Hospital 和 ModelNode 的关系配置。

## 实施内容

### 1. OrientationRule（导向规则）模型
**文件**: `backend/app/models/orientation_rule.py`

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，支持多租户）
- `name`: 导向名称（最大100字符）
- `category`: 导向类别（枚举：benchmark_ladder/direct_ladder/other）
- `description`: 导向规则描述（最大1024字符）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**关系**:
- `hospital`: 关联到 Hospital 模型
- `benchmarks`: 一对多关联到 OrientationBenchmark（级联删除）
- `ladders`: 一对多关联到 OrientationLadder（级联删除）
- `model_nodes`: 一对多关联到 ModelNode

**枚举类型**:
```python
class OrientationCategory(str, enum.Enum):
    benchmark_ladder = "benchmark_ladder"  # 基准阶梯
    direct_ladder = "direct_ladder"        # 直接阶梯
    other = "other"                        # 其他
```

### 2. OrientationBenchmark（导向基准）模型
**文件**: `backend/app/models/orientation_benchmark.py`

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键）
- `rule_id`: 导向规则ID（外键，级联删除）
- `department_code`: 科室代码（最大50字符）
- `department_name`: 科室名称（最大100字符）
- `benchmark_type`: 基准类别（枚举）
- `control_intensity`: 管控力度（Numeric(10,4)）
- `stat_start_date`: 统计开始时间
- `stat_end_date`: 统计结束时间
- `benchmark_value`: 基准值（Numeric(10,4)）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**关系**:
- `hospital`: 关联到 Hospital 模型
- `rule`: 关联到 OrientationRule 模型

**枚举类型**:
```python
class BenchmarkType(str, enum.Enum):
    average = "average"  # 平均值
    median = "median"    # 中位数
    max = "max"          # 最大值
    min = "min"          # 最小值
    other = "other"      # 其他
```

### 3. OrientationLadder（导向阶梯）模型
**文件**: `backend/app/models/orientation_ladder.py`

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键）
- `rule_id`: 导向规则ID（外键，级联删除）
- `ladder_order`: 阶梯次序（整数）
- `upper_limit`: 阶梯上限（Numeric(10,4)，NULL表示正无穷）
- `lower_limit`: 阶梯下限（Numeric(10,4)，NULL表示负无穷）
- `adjustment_intensity`: 调整力度（Numeric(10,4)）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**关系**:
- `hospital`: 关联到 Hospital 模型
- `rule`: 关联到 OrientationRule 模型

### 4. Hospital 模型更新
**文件**: `backend/app/models/hospital.py`

**新增关系**:
```python
orientation_rules = relationship("OrientationRule", back_populates="hospital")
orientation_benchmarks = relationship("OrientationBenchmark", back_populates="hospital")
orientation_ladders = relationship("OrientationLadder", back_populates="hospital")
```

### 5. ModelNode 模型更新
**文件**: `backend/app/models/model_node.py`

**新增字段**:
```python
orientation_rule_id = Column(
    Integer, 
    ForeignKey("orientation_rules.id", ondelete="SET NULL"), 
    nullable=True, 
    comment="关联导向规则ID"
)
```

**新增关系**:
```python
orientation_rule = relationship("OrientationRule", back_populates="model_nodes")
```

**外键行为**: `ON DELETE SET NULL` - 删除导向规则时，关联节点的 `orientation_rule_id` 自动设为 NULL

### 6. 模型导入配置
**文件**: `backend/app/models/__init__.py`

已按正确的依赖顺序导入所有模型：
```python
from .orientation_rule import OrientationRule, OrientationCategory
from .orientation_benchmark import OrientationBenchmark, BenchmarkType
from .orientation_ladder import OrientationLadder
```

## 测试验证

### 测试1: 模型字段和关系验证
**文件**: `test_orientation_models_verification.py`

**验证内容**:
- ✅ 所有枚举类型定义正确
- ✅ OrientationRule 包含所有必需字段和关系
- ✅ OrientationBenchmark 包含所有必需字段和关系
- ✅ OrientationLadder 包含所有必需字段和关系
- ✅ Hospital 包含导向管理的反向关系
- ✅ ModelNode 包含 orientation_rule_id 字段和关系

### 测试2: 关系功能测试
**文件**: `test_orientation_relationships.py`

**验证内容**:
- ✅ OrientationRule ↔ Hospital 双向关系
- ✅ OrientationBenchmark ↔ OrientationRule 双向关系
- ✅ OrientationBenchmark ↔ Hospital 关系
- ✅ OrientationLadder ↔ OrientationRule 双向关系
- ✅ OrientationLadder ↔ Hospital 关系
- ✅ 级联删除功能（删除规则时自动删除基准和阶梯）

### 测试3: ModelNode 关联测试
**文件**: `test_model_node_orientation.py`

**验证内容**:
- ✅ ModelNode ↔ OrientationRule 双向关系
- ✅ 关联导向规则到末级节点
- ✅ 清空节点的导向规则关联
- ✅ ON DELETE SET NULL 行为（删除规则时节点的 orientation_rule_id 自动设为 NULL）

## 关键设计决策

### 1. 多租户隔离
所有三个模型都包含 `hospital_id` 字段，确保数据按医疗机构隔离。

### 2. 级联删除策略
- **OrientationRule → OrientationBenchmark/OrientationLadder**: `CASCADE` - 删除规则时自动删除关联的基准和阶梯
- **OrientationRule → ModelNode**: `SET NULL` - 删除规则时节点的关联字段设为 NULL，保留节点本身

### 3. 数值精度
所有数值字段（管控力度、基准值、调整力度、上下限）使用 `Numeric(10, 4)`，保留4位小数。

### 4. 无穷值处理
阶梯的上下限字段允许 NULL，用于表示正无穷或负无穷。

### 5. 枚举类型
使用 Python enum 和 SQLAlchemy Enum 类型，确保类型安全和数据一致性。

## 数据库约束

以下约束在数据库迁移文件中定义：

1. **导向规则唯一约束**: `UNIQUE(hospital_id, name)` - 同一医疗机构内导向名称唯一
2. **导向基准唯一约束**: `UNIQUE(hospital_id, rule_id, department_code)` - 同一导向下每个科室只能有一个基准
3. **导向阶梯唯一约束**: `UNIQUE(hospital_id, rule_id, ladder_order)` - 同一导向下阶梯次序唯一

## 依赖关系

```
Hospital (1) ─────┬─────> (*) OrientationRule
                  │
                  ├─────> (*) OrientationBenchmark
                  │
                  └─────> (*) OrientationLadder

OrientationRule (1) ───┬─> (*) OrientationBenchmark
                       │
                       ├─> (*) OrientationLadder
                       │
                       └─> (*) ModelNode

ModelNode (*) ─────────> (0..1) OrientationRule
```

## 验证需求覆盖

### 需求 1.1: 导向规则管理
✅ OrientationRule 模型包含所有必需字段（ID、名称、类别、描述）

### 需求 4.1: 导向基准管理
✅ OrientationBenchmark 模型包含所有必需字段（所属导向、科室、基准类别、管控力度、统计时间、基准值）

### 需求 5.1: 导向阶梯管理
✅ OrientationLadder 模型包含所有必需字段（所属导向、阶梯次序、上下限、调整力度）

### 需求 6.2: 模型节点业务导向关联
✅ ModelNode 模型添加 orientation_rule_id 字段和关系

## 后续步骤

1. ✅ 数据库迁移已创建（任务1已完成）
2. ⏭️ 创建 Pydantic Schema（任务3）
3. ⏭️ 实现 API 端点（任务4-9）
4. ⏭️ 实现前端页面（任务10-18）

## 文件清单

### 模型文件
- `backend/app/models/orientation_rule.py` - 导向规则模型
- `backend/app/models/orientation_benchmark.py` - 导向基准模型
- `backend/app/models/orientation_ladder.py` - 导向阶梯模型
- `backend/app/models/hospital.py` - 更新（添加反向关系）
- `backend/app/models/model_node.py` - 更新（添加关联字段和关系）
- `backend/app/models/__init__.py` - 更新（导入新模型）

### 测试文件
- `test_orientation_models_verification.py` - 模型结构验证
- `test_orientation_relationships.py` - 关系功能测试
- `test_model_node_orientation.py` - ModelNode 关联测试

## 结论

✅ **任务2已完成**: 所有 SQLAlchemy 模型类已成功实现，包括：
- 3个核心模型（OrientationRule、OrientationBenchmark、OrientationLadder）
- 2个枚举类型（OrientationCategory、BenchmarkType）
- Hospital 和 ModelNode 的关系更新
- 完整的双向关系配置
- 正确的级联删除策略
- 所有测试通过

模型实现完全符合设计文档要求，为后续的 API 和前端开发奠定了坚实的基础。
