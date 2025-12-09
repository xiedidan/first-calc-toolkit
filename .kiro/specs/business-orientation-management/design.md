# 业务导向管理 - 设计文档

## 概述

业务导向管理模块是医院科室业务价值评估系统的核心配置模块之一，用于定义和管理业务导向规则、基准值和阶梯配置。该模块通过结构化的数据模型替代原有的文本描述方式，实现了导向规则的标准化管理和复用。

### 核心功能
- 导向规则的 CRUD 操作
- 导向规则的复制（包括关联数据）
- 导向规则的导出（Markdown 格式）
- 导向基准的配置和管理
- 导向阶梯的配置和管理
- 模型节点与导向规则的关联

### 技术栈
- 后端：FastAPI + SQLAlchemy + PostgreSQL
- 前端：Vue 3 + Element Plus + TypeScript
- 导出：Python Markdown 生成

## 架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                        │
├─────────────────────────────────────────────────────────────┤
│  导向规则管理  │  导向基准管理  │  导向阶梯管理  │  模型节点  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 层 (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  /api/v1/orientation-rules                                  │
│  /api/v1/orientation-benchmarks                             │
│  /api/v1/orientation-ladders                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     服务层 (Services)                        │
├─────────────────────────────────────────────────────────────┤
│  OrientationRuleService                                      │
│  OrientationBenchmarkService                                 │
│  OrientationLadderService                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据层 (SQLAlchemy)                       │
├─────────────────────────────────────────────────────────────┤
│  OrientationRule  │  OrientationBenchmark  │  OrientationLadder │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   数据库层 (PostgreSQL)                      │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

1. **查询流程**：前端 → API → Service → Model → Database
2. **创建/更新流程**：前端 → API（验证）→ Service（业务逻辑）→ Model → Database
3. **复制流程**：前端 → API → Service（事务处理）→ Model（批量创建）→ Database
4. **导出流程**：前端 → API → Service（数据聚合）→ Markdown 生成 → 文件下载

## 组件和接口

### 数据模型

#### OrientationRule（导向规则）

```python
class OrientationRule(Base):
    __tablename__ = "orientation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, comment="导向名称")
    category = Column(Enum('benchmark_ladder', 'direct_ladder', 'other'), nullable=False, comment="导向类别")
    description = Column(String(1024), comment="导向规则描述")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="orientation_rules")
    benchmarks = relationship("OrientationBenchmark", back_populates="rule", cascade="all, delete-orphan")
    ladders = relationship("OrientationLadder", back_populates="rule", cascade="all, delete-orphan")
    model_nodes = relationship("ModelNode", back_populates="orientation_rule")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('hospital_id', 'name', name='uq_orientation_rule_name'),
    )
```

#### OrientationBenchmark（导向基准）

```python
class OrientationBenchmark(Base):
    __tablename__ = "orientation_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    department_code = Column(String(50), nullable=False, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    benchmark_type = Column(Enum('average', 'median', 'max', 'min', 'other'), nullable=False, comment="基准类别")
    control_intensity = Column(Numeric(10, 4), nullable=False, comment="管控力度")
    stat_start_date = Column(DateTime, nullable=False, comment="统计开始时间")
    stat_end_date = Column(DateTime, nullable=False, comment="统计结束时间")
    benchmark_value = Column(Numeric(10, 4), nullable=False, comment="基准值")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="orientation_benchmarks")
    rule = relationship("OrientationRule", back_populates="benchmarks")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('hospital_id', 'rule_id', 'department_code', name='uq_benchmark_dept'),
    )
```

#### OrientationLadder（导向阶梯）

```python
class OrientationLadder(Base):
    __tablename__ = "orientation_ladders"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("orientation_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    ladder_order = Column(Integer, nullable=False, comment="阶梯次序")
    upper_limit = Column(Numeric(10, 4), comment="阶梯上限（NULL表示正无穷）")
    lower_limit = Column(Numeric(10, 4), comment="阶梯下限（NULL表示负无穷）")
    adjustment_intensity = Column(Numeric(10, 4), nullable=False, comment="调整力度")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="orientation_ladders")
    rule = relationship("OrientationLadder", back_populates="ladders")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('hospital_id', 'rule_id', 'ladder_order', name='uq_ladder_order'),
    )
```

#### ModelNode 扩展

```python
# 在 ModelNode 中添加字段
orientation_rule_id = Column(Integer, ForeignKey("orientation_rules.id"), nullable=True, comment="关联导向规则ID")

# 添加关系
orientation_rule = relationship("OrientationRule", back_populates="model_nodes")
```

### API 端点

#### 导向规则 API

```
GET    /api/v1/orientation-rules              # 获取导向规则列表
POST   /api/v1/orientation-rules              # 创建导向规则
GET    /api/v1/orientation-rules/{id}         # 获取导向规则详情
PUT    /api/v1/orientation-rules/{id}         # 更新导向规则
DELETE /api/v1/orientation-rules/{id}         # 删除导向规则
POST   /api/v1/orientation-rules/{id}/copy    # 复制导向规则
GET    /api/v1/orientation-rules/{id}/export  # 导出导向规则
```

#### 导向基准 API

```
GET    /api/v1/orientation-benchmarks                    # 获取导向基准列表
POST   /api/v1/orientation-benchmarks                    # 创建导向基准
GET    /api/v1/orientation-benchmarks/{id}               # 获取导向基准详情
PUT    /api/v1/orientation-benchmarks/{id}               # 更新导向基准
DELETE /api/v1/orientation-benchmarks/{id}               # 删除导向基准
GET    /api/v1/orientation-benchmarks?rule_id={rule_id} # 按导向筛选
```

#### 导向阶梯 API

```
GET    /api/v1/orientation-ladders                    # 获取导向阶梯列表
POST   /api/v1/orientation-ladders                    # 创建导向阶梯
GET    /api/v1/orientation-ladders/{id}               # 获取导向阶梯详情
PUT    /api/v1/orientation-ladders/{id}               # 更新导向阶梯
DELETE /api/v1/orientation-ladders/{id}               # 删除导向阶梯
GET    /api/v1/orientation-ladders?rule_id={rule_id} # 按导向筛选
```

### 前端路由

```typescript
{
  path: '/orientation-rules',
  name: 'OrientationRules',
  component: () => import('@/views/OrientationRules.vue'),
  meta: { title: '导向规则管理' }
},
{
  path: '/orientation-benchmarks',
  name: 'OrientationBenchmarks',
  component: () => import('@/views/OrientationBenchmarks.vue'),
  meta: { title: '导向基准管理' }
},
{
  path: '/orientation-ladders',
  name: 'OrientationLadders',
  component: () => import('@/views/OrientationLadders.vue'),
  meta: { title: '导向阶梯管理' }
}
```

### 前端组件结构

```
views/
├── OrientationRules.vue          # 导向规则管理页面
├── OrientationBenchmarks.vue     # 导向基准管理页面
└── OrientationLadders.vue        # 导向阶梯管理页面

components/
├── OrientationRuleDialog.vue     # 导向规则编辑对话框
├── OrientationBenchmarkDialog.vue # 导向基准编辑对话框
└── OrientationLadderDialog.vue   # 导向阶梯编辑对话框
```

## 数据模型

### 实体关系图

```
┌─────────────────┐
│    Hospital     │
└────────┬────────┘
         │ 1
         │
         │ *
┌────────┴────────────────┐
│   OrientationRule       │
│  ─────────────────────  │
│  + id                   │
│  + hospital_id          │
│  + name                 │
│  + category             │
│  + description          │
└────────┬────────────────┘
         │ 1
         │
    ┌────┴────┐
    │ *       │ *
┌───┴──────┐  │  ┌──────────┐
│Benchmark │  │  │  Ladder  │
└──────────┘  │  └──────────┘
              │
              │ *
         ┌────┴────────┐
         │  ModelNode  │
         └─────────────┘
```

### 枚举类型

#### OrientationCategory（导向类别）
- `benchmark_ladder`: 基准阶梯
- `direct_ladder`: 直接阶梯
- `other`: 其他

#### BenchmarkType（基准类别）
- `average`: 平均值
- `median`: 中位数
- `max`: 最大值
- `min`: 最小值
- `other`: 其他

### 数据约束

1. **导向规则**
   - 同一医疗机构内导向名称唯一
   - 导向类别必须为枚举值之一
   - 描述长度不超过 1024 字符

2. **导向基准**
   - 仅"基准阶梯"类别的导向可以创建基准
   - 同一导向下，同一科室只能有一个基准
   - 统计开始时间必须早于统计结束时间
   - 数值字段保留 4 位小数

3. **导向阶梯**
   - "基准阶梯"和"直接阶梯"类别的导向可以创建阶梯
   - 同一导向下，阶梯次序唯一
   - 阶梯下限必须小于阶梯上限（除非使用无穷值）
   - 数值字段保留 4 位小数

## 正确性属性

*属性是系统在所有有效执行中应保持为真的特征或行为——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 属性 1：导向规则列表完整性
*对于任何*医疗机构，查询导向规则列表应返回该机构的所有导向规则，且每条记录包含ID、导向名称、导向类别和导向规则描述字段
**验证：需求 1.1**

### 属性 2：导向规则输入验证
*对于任何*导向规则创建请求，如果缺少必填字段（导向名称或导向类别）或描述超过1024字符，系统应拒绝该请求
**验证：需求 1.2**

### 属性 3：导向规则更新保持完整性
*对于任何*现有导向规则，更新其字段后，该导向规则的其他未修改字段和关联数据应保持不变
**验证：需求 1.3**

### 属性 4：导向规则删除约束
*对于任何*导向规则，如果存在模型节点关联该规则，删除操作应被拒绝并返回错误消息
**验证：需求 1.4**

### 属性 5：导向规则复制基本行为
*对于任何*导向规则，复制操作应创建新记录，且新记录的名称为原名称加"（副本）"后缀
**验证：需求 2.1**

### 属性 6：基准阶梯导向复制基准
*对于任何*"基准阶梯"类别的导向规则，复制操作应同时复制所有关联的导向基准记录，且基准数量和内容一致
**验证：需求 2.2**

### 属性 7：阶梯类别导向复制阶梯
*对于任何*"基准阶梯"或"直接阶梯"类别的导向规则，复制操作应同时复制所有关联的导向阶梯记录，且阶梯数量和内容一致
**验证：需求 2.3**

### 属性 8：复制操作事务完整性
*对于任何*导向规则复制操作，如果过程中发生错误，系统应回滚所有已创建的记录，不留下部分数据
**验证：需求 2.5**

### 属性 9：导向规则导出包含完整信息
*对于任何*导向规则，导出的Markdown文件应包含该规则的所有详细信息（名称、类别、描述）
**验证：需求 3.1**

### 属性 10：基准阶梯导向导出包含基准
*对于任何*"基准阶梯"类别的导向规则，导出的Markdown文件应包含所有关联的导向基准数据
**验证：需求 3.2**

### 属性 11：阶梯类别导向导出包含阶梯
*对于任何*"基准阶梯"或"直接阶梯"类别的导向规则，导出的Markdown文件应包含所有关联的导向阶梯数据
**验证：需求 3.3**

### 属性 12：导出文件命名规则
*对于任何*导向规则导出操作，生成的文件名应包含导向名称和时间戳，格式为"{导向名称}_{时间戳}.md"
**验证：需求 3.4**

### 属性 13：导向基准列表完整性
*对于任何*医疗机构，查询导向基准列表应返回该机构的所有导向基准，且每条记录包含所属导向名称、科室名称、基准类别、管控力度、统计时间范围和基准值字段
**验证：需求 4.1**

### 属性 14：导向基准类别验证
*对于任何*导向基准创建请求，如果所属导向不是"基准阶梯"类别，系统应拒绝该请求
**验证：需求 4.2**

### 属性 15：基准数值格式化
*对于任何*导向基准的管控力度或基准值输入，系统应自动格式化为小数点后4位并存储
**验证：需求 4.3**

### 属性 16：导向基准按导向筛选
*对于任何*导向ID，按该导向筛选基准列表应仅返回rule_id等于该导向ID的基准记录
**验证：需求 4.5**

### 属性 17：导向阶梯列表完整性
*对于任何*医疗机构，查询导向阶梯列表应返回该机构的所有导向阶梯，且每条记录包含所属导向名称、阶梯次序、阶梯上限、阶梯下限和调整力度字段
**验证：需求 5.1**

### 属性 18：导向阶梯类别验证
*对于任何*导向阶梯创建请求，如果所属导向不是"基准阶梯"或"直接阶梯"类别，系统应拒绝该请求
**验证：需求 5.2**

### 属性 19：阶梯数值格式化
*对于任何*导向阶梯的上限、下限或调整力度输入，系统应自动格式化为小数点后4位并存储
**验证：需求 5.3**

### 属性 20：导向阶梯按导向筛选并排序
*对于任何*导向ID，按该导向筛选阶梯列表应仅返回rule_id等于该导向ID的阶梯记录，且按ladder_order升序排序
**验证：需求 5.6**

### 属性 21：导向阶梯次序唯一性
*对于任何*导向规则，同一导向下不能存在两个相同ladder_order的阶梯记录
**验证：需求 5.8**

### 属性 22：模型节点关联导向规则
*对于任何*模型末级节点，更新其orientation_rule_id字段后，该节点应正确关联到指定的导向规则
**验证：需求 6.2**

### 属性 23：模型节点详情包含导向名称
*对于任何*关联了导向规则的模型节点，查询节点详情应返回关联的导向规则名称
**验证：需求 6.3**

### 属性 24：多租户创建隔离
*对于任何*导向规则、导向基准或导向阶梯的创建操作，系统应自动设置hospital_id为当前医疗机构ID
**验证：需求 7.1**

### 属性 25：多租户查询隔离
*对于任何*医疗机构，查询导向数据应仅返回hospital_id等于该医疗机构ID的记录
**验证：需求 7.2**

### 属性 26：多租户操作隔离
*对于任何*复制或导出操作，系统应仅操作当前医疗机构的数据，不跨医疗机构访问
**验证：需求 7.3**

### 属性 27：导向基准日期范围验证
*对于任何*导向基准创建请求，如果统计开始时间晚于或等于统计结束时间，系统应拒绝该请求
**验证：需求 8.1**

### 属性 28：导向阶梯范围验证
*对于任何*导向阶梯创建请求，如果阶梯下限大于或等于阶梯上限（且两者都不为NULL），系统应拒绝该请求
**验证：需求 8.2**

### 属性 29：导向规则删除级联检查
*对于任何*导向规则，如果存在关联的基准、阶梯或模型节点，删除操作应被拒绝或执行级联删除
**验证：需求 8.3**

### 属性 30：导向类别修改一致性验证
*对于任何*导向规则，如果修改类别为"其他"且存在关联的基准或阶梯，系统应拒绝该修改
**验证：需求 8.4**

### 属性 31：数值字段格式验证
*对于任何*数值字段输入，系统应验证格式正确（可解析为数字），并自动四舍五入到小数点后4位
**验证：需求 8.5**

## 错误处理

### 错误类型

1. **验证错误（400 Bad Request）**
   - 必填字段缺失
   - 字段长度超限
   - 数值格式错误
   - 日期范围无效
   - 业务规则冲突

2. **权限错误（403 Forbidden）**
   - 非管理员用户尝试操作
   - 跨医疗机构访问数据

3. **资源不存在（404 Not Found）**
   - 导向规则ID不存在
   - 导向基准ID不存在
   - 导向阶梯ID不存在

4. **冲突错误（409 Conflict）**
   - 导向名称重复
   - 阶梯次序重复
   - 科室基准重复

5. **服务器错误（500 Internal Server Error）**
   - 数据库连接失败
   - 事务回滚失败
   - 文件生成失败

### 错误响应格式

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "field": "字段名（如果适用）"
}
```

### 错误处理策略

1. **输入验证**：在 Pydantic Schema 层进行基本验证
2. **业务规则验证**：在 Service 层进行复杂业务逻辑验证
3. **数据库约束**：依赖数据库唯一约束和外键约束
4. **事务管理**：复制等复杂操作使用数据库事务确保原子性
5. **日志记录**：所有错误都应记录到日志系统

## 测试策略

### 单元测试

1. **模型测试**
   - 测试模型字段定义
   - 测试模型关系
   - 测试模型约束

2. **Schema 测试**
   - 测试输入验证
   - 测试数据序列化
   - 测试数据反序列化

3. **Service 测试**
   - 测试 CRUD 操作
   - 测试复制逻辑
   - 测试导出逻辑
   - 测试多租户隔离

### 属性测试

本项目使用 **Hypothesis** 作为属性测试库。每个属性测试应运行至少 **100 次迭代**。

#### 属性测试标记格式
每个属性测试必须使用以下格式标记：
```python
# Feature: business-orientation-management, Property 1: 导向规则列表完整性
```

#### 属性测试覆盖

1. **属性 1-4**：导向规则基本操作
   - 生成随机导向规则数据
   - 测试列表、创建、更新、删除操作
   - 验证数据完整性和约束

2. **属性 5-8**：导向规则复制
   - 生成随机导向规则及关联数据
   - 测试复制操作的完整性
   - 验证事务回滚

3. **属性 9-12**：导向规则导出
   - 生成随机导向规则及关联数据
   - 测试导出Markdown格式
   - 验证文件命名和内容完整性

4. **属性 13-16**：导向基准操作
   - 生成随机导向基准数据
   - 测试类别验证和数值格式化
   - 验证筛选功能

5. **属性 17-21**：导向阶梯操作
   - 生成随机导向阶梯数据
   - 测试类别验证和数值格式化
   - 验证筛选、排序和唯一性

6. **属性 22-23**：模型节点关联
   - 生成随机模型节点和导向规则
   - 测试关联操作
   - 验证预加载字段

7. **属性 24-26**：多租户隔离
   - 生成多个医疗机构的数据
   - 测试创建、查询、操作的隔离性
   - 验证跨租户访问被阻止

8. **属性 27-31**：数据完整性验证
   - 生成各种有效和无效输入
   - 测试验证规则
   - 验证错误处理

### 集成测试

1. **API 端到端测试**
   - 测试完整的 CRUD 流程
   - 测试复制和导出流程
   - 测试多租户场景

2. **前端集成测试**
   - 测试页面渲染
   - 测试表单提交
   - 测试路由跳转

### 测试数据生成

使用 Hypothesis 的 strategies 生成测试数据：

```python
from hypothesis import strategies as st

# 导向类别策略
orientation_category = st.sampled_from(['benchmark_ladder', 'direct_ladder', 'other'])

# 基准类别策略
benchmark_type = st.sampled_from(['average', 'median', 'max', 'min', 'other'])

# 导向规则策略
orientation_rule = st.builds(
    dict,
    name=st.text(min_size=1, max_size=100),
    category=orientation_category,
    description=st.text(max_size=1024)
)

# 数值策略（4位小数）
decimal_4 = st.decimals(min_value=-9999.9999, max_value=9999.9999, places=4)

# 日期范围策略
date_range = st.tuples(
    st.datetimes(min_value=datetime(2020, 1, 1)),
    st.datetimes(min_value=datetime(2020, 1, 1))
).filter(lambda x: x[0] < x[1])
```

## 实现计划

### 阶段 1：数据库和模型（后端基础）

1. 创建数据库迁移文件
2. 定义 SQLAlchemy 模型
3. 更新 ModelNode 模型添加 orientation_rule_id 字段
4. 创建 Pydantic Schema

### 阶段 2：API 实现（后端服务）

1. 实现导向规则 API
2. 实现导向基准 API
3. 实现导向阶梯 API
4. 实现复制和导出功能
5. 更新模型节点 API

### 阶段 3：前端实现

1. 创建导向规则管理页面
2. 创建导向基准管理页面
3. 创建导向阶梯管理页面
4. 更新模型节点编辑页面
5. 实现路由和菜单

### 阶段 4：测试

1. 编写单元测试
2. 编写属性测试
3. 编写集成测试
4. 执行测试并修复问题

### 阶段 5：文档和部署

1. 更新 API 文档
2. 更新用户手册
3. 数据迁移脚本
4. 部署到测试环境
5. 部署到生产环境

## 依赖关系

### 外部依赖
- FastAPI：Web 框架
- SQLAlchemy：ORM
- Pydantic：数据验证
- PostgreSQL：数据库
- Vue 3：前端框架
- Element Plus：UI 组件库
- Hypothesis：属性测试库

### 内部依赖
- Hospital 模型：多租户支持
- ModelNode 模型：业务导向关联
- Department 模型：科室信息

## 性能考虑

1. **数据库索引**
   - hospital_id：多租户查询优化
   - rule_id：关联查询优化
   - category：类别筛选优化

2. **查询优化**
   - 使用 joinedload 预加载关联数据
   - 分页查询避免大数据量
   - 缓存常用查询结果

3. **导出优化**
   - 异步生成大文件
   - 流式写入避免内存溢出
   - 压缩文件减少传输时间

## 安全考虑

1. **权限控制**
   - 仅管理员可以操作导向管理
   - 多租户数据严格隔离
   - API 层验证用户权限

2. **输入验证**
   - 所有输入进行严格验证
   - 防止 SQL 注入
   - 防止 XSS 攻击

3. **数据保护**
   - 敏感操作记录审计日志
   - 删除操作需要确认
   - 导出数据加密传输

## 可扩展性

1. **新增导向类别**
   - 枚举类型易于扩展
   - 业务逻辑集中在 Service 层

2. **新增基准类别**
   - 枚举类型易于扩展
   - 统计逻辑可插拔

3. **导出格式扩展**
   - 支持多种导出格式（PDF、Excel）
   - 模板化导出内容

4. **批量操作**
   - 批量导入导向规则
   - 批量复制和导出
