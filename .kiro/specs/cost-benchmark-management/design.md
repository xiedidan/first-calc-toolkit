# 设计文档 - 成本基准管理

## 概述

成本基准管理功能为医院提供科室级别的成本参考标准管理能力。该功能允许管理员为不同科室在特定模型版本的各个维度下设置成本基准值，用于成本控制和绩效评估。

系统采用前后端分离架构，后端使用FastAPI + SQLAlchemy，前端使用Vue 3 + Element Plus，确保与现有模块的风格和技术栈保持一致。

## 架构

### 系统层次

```
前端层 (Vue 3 + Element Plus)
    ↓
API层 (FastAPI Router)
    ↓
服务层 (可选，简单CRUD可直接在API层实现)
    ↓
数据访问层 (SQLAlchemy ORM)
    ↓
数据库层 (PostgreSQL)
```

### 多租户架构

所有成本基准数据通过 `hospital_id` 字段实现多租户隔离：
- 查询时自动过滤当前医疗机构的数据
- 创建时自动关联当前医疗机构ID
- 更新/删除时验证数据所属权

## 组件和接口

### 数据库模型

#### CostBenchmark 模型

```python
class CostBenchmark(Base):
    """成本基准模型"""
    __tablename__ = "cost_benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), 
                        nullable=False, index=True, comment="所属医疗机构ID")
    department_code = Column(String(50), nullable=False, index=True, comment="科室代码")
    department_name = Column(String(100), nullable=False, comment="科室名称")
    version_id = Column(Integer, ForeignKey("model_versions.id", ondelete="CASCADE"), 
                       nullable=False, index=True, comment="模型版本ID")
    version_name = Column(String(100), nullable=False, comment="模型版本名称")
    dimension_code = Column(String(100), nullable=False, index=True, comment="维度代码")
    dimension_name = Column(String(200), nullable=False, comment="维度名称")
    benchmark_value = Column(Numeric(15, 2), nullable=False, comment="基准值")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    hospital = relationship("Hospital", back_populates="cost_benchmarks")
    version = relationship("ModelVersion", back_populates="cost_benchmarks")
    
    # 唯一约束：同一医疗机构内，科室+版本+维度组合唯一
    __table_args__ = (
        UniqueConstraint('hospital_id', 'department_code', 'version_id', 'dimension_code',
                        name='uq_cost_benchmark_dept_version_dimension'),
    )
```

### API端点

#### 基础路径
`/api/v1/cost-benchmarks`

#### 端点列表

1. **GET /cost-benchmarks** - 获取成本基准列表
   - 查询参数：
     - `page`: 页码（默认1）
     - `size`: 每页数量（默认20）
     - `version_id`: 模型版本ID（可选）
     - `department_code`: 科室代码（可选）
     - `dimension_code`: 维度代码（可选）
     - `keyword`: 搜索关键词（可选，搜索科室名称和维度名称）
   - 响应：分页的成本基准列表

2. **POST /cost-benchmarks** - 创建成本基准
   - 请求体：CostBenchmarkCreate schema
   - 响应：创建的成本基准对象

3. **GET /cost-benchmarks/{id}** - 获取成本基准详情
   - 路径参数：`id` - 成本基准ID
   - 响应：成本基准对象

4. **PUT /cost-benchmarks/{id}** - 更新成本基准
   - 路径参数：`id` - 成本基准ID
   - 请求体：CostBenchmarkUpdate schema
   - 响应：更新后的成本基准对象

5. **DELETE /cost-benchmarks/{id}** - 删除成本基准
   - 路径参数：`id` - 成本基准ID
   - 响应：成功消息

6. **GET /cost-benchmarks/export** - 导出成本基准到Excel
   - 查询参数：与列表接口相同的筛选参数
   - 响应：Excel文件流

### Pydantic Schemas

```python
class CostBenchmarkBase(BaseModel):
    department_code: str
    department_name: str
    version_id: int
    version_name: str
    dimension_code: str
    dimension_name: str
    benchmark_value: Decimal

class CostBenchmarkCreate(CostBenchmarkBase):
    pass

class CostBenchmarkUpdate(BaseModel):
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    version_id: Optional[int] = None
    version_name: Optional[str] = None
    dimension_code: Optional[str] = None
    dimension_name: Optional[str] = None
    benchmark_value: Optional[Decimal] = None

class CostBenchmark(CostBenchmarkBase):
    id: int
    hospital_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CostBenchmarkList(BaseModel):
    total: int
    items: List[CostBenchmark]
```

### 前端组件

#### 主组件：CostBenchmarks.vue

**组件结构：**
```
<template>
  <div class="cost-benchmarks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成本基准管理</span>
          <div>
            <el-button type="success" @click="handleExport">导出Excel</el-button>
            <el-button type="primary" @click="handleAdd">添加成本基准</el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="模型版本">
          <el-select v-model="searchForm.versionId" />
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="searchForm.departmentCode" />
        </el-form-item>
        <el-form-item label="维度">
          <el-select v-model="searchForm.dimensionCode" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="department_name" label="科室名称" />
        <el-table-column prop="version_name" label="模型版本" />
        <el-table-column prop="dimension_name" label="维度名称" />
        <el-table-column prop="benchmark_value" label="基准值" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column prop="updated_at" label="更新时间" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination />
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" append-to-body>
      <el-form :model="formData" label-width="120px">
        <el-form-item label="科室" required>
          <el-select v-model="formData.departmentCode" />
        </el-form-item>
        <el-form-item label="模型版本" required>
          <el-select v-model="formData.versionId" />
        </el-form-item>
        <el-form-item label="维度" required>
          <el-select v-model="formData.dimensionCode" />
        </el-form-item>
        <el-form-item label="基准值" required>
          <el-input-number v-model="formData.benchmarkValue" :min="0" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
```

#### API服务：cost-benchmarks.ts

```typescript
import request from '@/utils/request'

export interface CostBenchmark {
  id: number
  hospital_id: number
  department_code: string
  department_name: string
  version_id: number
  version_name: string
  dimension_code: string
  dimension_name: string
  benchmark_value: number
  created_at: string
  updated_at: string
}

export interface CostBenchmarkCreate {
  department_code: string
  department_name: string
  version_id: number
  version_name: string
  dimension_code: string
  dimension_name: string
  benchmark_value: number
}

export interface CostBenchmarkList {
  total: number
  items: CostBenchmark[]
}

export const getCostBenchmarks = (params: any) => {
  return request.get<CostBenchmarkList>('/cost-benchmarks', { params })
}

export const createCostBenchmark = (data: CostBenchmarkCreate) => {
  return request.post<CostBenchmark>('/cost-benchmarks', data)
}

export const updateCostBenchmark = (id: number, data: Partial<CostBenchmarkCreate>) => {
  return request.put<CostBenchmark>(`/cost-benchmarks/${id}`, data)
}

export const deleteCostBenchmark = (id: number) => {
  return request.delete(`/cost-benchmarks/${id}`)
}

export const exportCostBenchmarks = (params: any) => {
  return request.get('/cost-benchmarks/export', {
    params,
    responseType: 'blob'
  })
}
```

## 数据模型

### 实体关系

```
Hospital (医疗机构)
    ↓ 1:N
CostBenchmark (成本基准)
    ↓ N:1
ModelVersion (模型版本)

CostBenchmark (成本基准)
    ↓ 引用
Department (科室) - 通过 department_code
ModelNode (维度节点) - 通过 dimension_code
```

### 数据字段说明

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | Integer | 主键 | PK, Auto Increment |
| hospital_id | Integer | 医疗机构ID | FK, NOT NULL, Indexed |
| department_code | String(50) | 科室代码 | NOT NULL, Indexed |
| department_name | String(100) | 科室名称 | NOT NULL |
| version_id | Integer | 模型版本ID | FK, NOT NULL, Indexed |
| version_name | String(100) | 模型版本名称 | NOT NULL |
| dimension_code | String(100) | 维度代码 | NOT NULL, Indexed |
| dimension_name | String(200) | 维度名称 | NOT NULL |
| benchmark_value | Numeric(15,2) | 基准值 | NOT NULL, > 0 |
| created_at | DateTime | 创建时间 | NOT NULL, Default: now() |
| updated_at | DateTime | 更新时间 | NOT NULL, Default: now() |

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1：多租户数据隔离
*对于任意* 医疗机构和查询条件，查询返回的所有成本基准记录的 hospital_id 应该等于当前医疗机构ID
**验证需求：6.1, 6.4**

### 属性 2：创建时自动关联医疗机构
*对于任意* 有效的成本基准创建请求，创建后的记录的 hospital_id 应该等于当前医疗机构ID
**验证需求：6.2**

### 属性 3：跨租户访问控制
*对于任意* 编辑或删除操作，如果目标记录的 hospital_id 不等于当前医疗机构ID，则操作应该失败
**验证需求：6.3**

### 属性 4：版本筛选正确性
*对于任意* 模型版本ID，使用该版本ID筛选后返回的所有记录的 version_id 应该等于该版本ID
**验证需求：1.2**

### 属性 5：科室筛选正确性
*对于任意* 科室代码，使用该科室代码筛选后返回的所有记录的 department_code 应该等于该科室代码
**验证需求：1.3**

### 属性 6：维度筛选正确性
*对于任意* 维度代码，使用该维度代码筛选后返回的所有记录的 dimension_code 应该等于该维度代码
**验证需求：1.4**

### 属性 7：关键词搜索正确性
*对于任意* 关键词，搜索返回的所有记录的 department_name 或 dimension_name 应该包含该关键词
**验证需求：1.5**

### 属性 8：唯一性约束
*对于任意* 医疗机构、科室代码、版本ID和维度代码的组合，如果该组合的记录已存在，则创建相同组合的新记录应该失败
**验证需求：2.5**

### 属性 9：更新唯一性约束
*对于任意* 成本基准记录，如果更新后的科室代码、版本ID和维度代码组合与其他记录冲突，则更新应该失败
**验证需求：3.4**

### 属性 10：基准值范围验证
*对于任意* 基准值，如果该值小于等于0或不是有效数字，则创建或更新操作应该失败
**验证需求：2.3, 3.2, 8.2**

### 属性 11：删除操作正确性
*对于任意* 存在的成本基准记录，删除操作成功后，该记录应该不再存在于数据库中
**验证需求：4.2**

### 属性 12：导出数据一致性
*对于任意* 筛选条件，导出的Excel文件中的数据应该与使用相同筛选条件查询列表返回的数据一致
**验证需求：5.1**

### 属性 13：导出字段完整性
*对于任意* 导出的Excel文件，应该包含以下列：科室代码、科室名称、模型版本名称、维度代码、维度名称、基准值、创建时间、更新时间
**验证需求：5.2**

### 属性 14：必填字段验证
*对于任意* 创建或更新请求，如果任何必填字段（科室代码、科室名称、版本ID、版本名称、维度代码、维度名称、基准值）为空，则操作应该失败
**验证需求：8.1**

### 属性 15：外键引用验证
*对于任意* 创建或更新请求，如果 version_id 引用的模型版本不存在，则操作应该失败
**验证需求：2.2**



## 错误处理

### API层错误处理

1. **404 Not Found**
   - 场景：查询、更新或删除不存在的成本基准记录
   - 响应：`{"detail": "成本基准不存在"}`

2. **400 Bad Request**
   - 场景：
     - 创建重复的成本基准（相同科室+版本+维度）
     - 基准值无效（≤0或非数字）
     - 必填字段缺失
     - 外键引用无效（版本不存在）
   - 响应：`{"detail": "具体错误描述"}`

3. **403 Forbidden**
   - 场景：尝试访问或操作其他医疗机构的数据
   - 响应：`{"detail": "无权访问该资源"}`

4. **500 Internal Server Error**
   - 场景：数据库连接失败、未预期的异常
   - 响应：`{"detail": "服务器内部错误"}`
   - 日志：记录完整的错误堆栈

### 前端错误处理

1. **网络错误**
   - 使用 Axios 拦截器统一处理
   - 显示用户友好的错误消息
   - 超时设置：30秒

2. **表单验证错误**
   - 使用 Element Plus 的表单验证
   - 实时验证和提交时验证
   - 显示字段级别的错误提示

3. **业务逻辑错误**
   - 解析后端返回的错误详情
   - 使用 ElMessage 显示错误消息
   - 对于唯一性约束冲突，提供明确的提示

## 测试策略

### 单元测试

#### 后端单元测试

1. **模型测试**
   - 测试 CostBenchmark 模型的创建和字段验证
   - 测试唯一性约束
   - 测试关系映射

2. **API端点测试**
   - 测试每个端点的基本功能
   - 测试参数验证
   - 测试错误响应

3. **多租户隔离测试**
   - 测试查询时的医疗机构过滤
   - 测试跨租户访问控制
   - 测试创建时的自动关联

#### 前端单元测试

1. **组件测试**
   - 测试 CostBenchmarks.vue 的渲染
   - 测试表单验证逻辑
   - 测试事件处理

2. **API服务测试**
   - 测试 API 调用的参数构造
   - 测试响应数据的处理

### 属性测试

使用 Python 的 Hypothesis 库进行属性测试：

1. **属性 1-3：多租户隔离**
   - 生成随机的医疗机构ID和成本基准数据
   - 验证查询、创建、更新、删除操作的隔离性

2. **属性 4-7：筛选和搜索**
   - 生成随机的筛选条件
   - 验证返回结果符合筛选条件

3. **属性 8-9：唯一性约束**
   - 生成随机的成本基准数据
   - 验证重复创建和更新被正确阻止

4. **属性 10：数值验证**
   - 生成随机的基准值（包括无效值）
   - 验证验证逻辑正确工作

5. **属性 11：删除操作**
   - 生成随机的成本基准记录
   - 验证删除后记录不存在

6. **属性 12-13：导出功能**
   - 生成随机的筛选条件和数据
   - 验证导出的数据和格式正确

7. **属性 14-15：字段验证**
   - 生成随机的输入数据（包括无效数据）
   - 验证验证逻辑正确工作

### 集成测试

1. **端到端流程测试**
   - 创建 → 查询 → 更新 → 删除的完整流程
   - 多条件筛选和搜索
   - 导出功能

2. **多租户场景测试**
   - 多个医疗机构的数据隔离
   - 切换医疗机构后的数据正确性

3. **并发测试**
   - 同时创建相同组合的记录
   - 验证唯一性约束在并发场景下的正确性

### 测试数据

使用 Faker 库生成测试数据：
- 科室代码和名称
- 维度代码和名称
- 基准值（正常范围和边界值）
- 时间戳

## 性能考虑

### 数据库优化

1. **索引策略**
   - `hospital_id`: 用于多租户过滤
   - `department_code`: 用于科室筛选
   - `version_id`: 用于版本筛选
   - `dimension_code`: 用于维度筛选
   - 复合索引：`(hospital_id, department_code, version_id, dimension_code)` 用于唯一性约束

2. **查询优化**
   - 使用分页避免一次加载大量数据
   - 使用 JOIN 预加载关联数据（如需要）
   - 避免 N+1 查询问题

### 前端优化

1. **列表渲染**
   - 使用虚拟滚动（如果数据量很大）
   - 合理设置分页大小（默认20条）

2. **表单优化**
   - 下拉选项懒加载
   - 防抖搜索输入

3. **导出优化**
   - 大数据量导出时显示进度提示
   - 使用流式下载避免内存溢出

## 安全考虑

### 认证和授权

1. **用户认证**
   - 所有API端点需要用户登录
   - 使用 JWT token 进行身份验证

2. **医疗机构隔离**
   - 通过 `X-Hospital-ID` 请求头传递当前医疗机构
   - 后端强制验证数据所属权

### 数据验证

1. **输入验证**
   - 前端：表单验证
   - 后端：Pydantic schema 验证
   - 数据库：约束和触发器

2. **SQL注入防护**
   - 使用 SQLAlchemy ORM
   - 参数化查询
   - 避免动态SQL拼接

### 审计日志

考虑添加审计日志记录：
- 谁在什么时间创建/更新/删除了哪条记录
- 记录变更前后的值
- 用于合规性和问题追踪

## 部署考虑

### 数据库迁移

使用 Alembic 创建迁移脚本：
```python
# 迁移文件：20251127_add_cost_benchmarks.py
def upgrade():
    op.create_table(
        'cost_benchmarks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('department_code', sa.String(50), nullable=False),
        sa.Column('department_name', sa.String(100), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('version_name', sa.String(100), nullable=False),
        sa.Column('dimension_code', sa.String(100), nullable=False),
        sa.Column('dimension_name', sa.String(200), nullable=False),
        sa.Column('benchmark_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['model_versions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('hospital_id', 'department_code', 'version_id', 'dimension_code',
                           name='uq_cost_benchmark_dept_version_dimension')
    )
    op.create_index('ix_cost_benchmarks_hospital_id', 'cost_benchmarks', ['hospital_id'])
    op.create_index('ix_cost_benchmarks_department_code', 'cost_benchmarks', ['department_code'])
    op.create_index('ix_cost_benchmarks_version_id', 'cost_benchmarks', ['version_id'])
    op.create_index('ix_cost_benchmarks_dimension_code', 'cost_benchmarks', ['dimension_code'])

def downgrade():
    op.drop_table('cost_benchmarks')
```

### 前端路由配置

在 `frontend/src/router/index.ts` 中添加路由：
```typescript
{
  path: '/cost-benchmarks',
  name: 'CostBenchmarks',
  component: () => import('@/views/CostBenchmarks.vue'),
  meta: { title: '成本基准管理', requiresAuth: true }
}
```

### 菜单配置

在 `frontend/src/views/Layout.vue` 中添加菜单项：
```vue
<el-menu-item index="/cost-benchmarks">
  <el-icon><Money /></el-icon>
  <span>成本基准管理</span>
</el-menu-item>
```

## 未来扩展

### 可能的功能增强

1. **批量导入**
   - 支持从Excel批量导入成本基准
   - 提供导入模板下载
   - 导入预览和验证

2. **历史版本**
   - 记录成本基准的修改历史
   - 支持查看和回滚到历史版本

3. **基准值分析**
   - 提供成本基准的统计分析
   - 对比不同科室的基准值
   - 趋势分析和预测

4. **自动计算基准值**
   - 基于历史数据自动计算建议基准值
   - 支持多种计算方法（平均值、中位数等）

5. **预警功能**
   - 当实际成本超过基准值时发出预警
   - 支持配置预警阈值

## 依赖关系

### 后端依赖

- FastAPI
- SQLAlchemy
- Pydantic
- openpyxl（用于Excel导出）
- Hypothesis（用于属性测试）

### 前端依赖

- Vue 3
- Element Plus
- Axios
- TypeScript

### 数据库依赖

- PostgreSQL 12+
- 依赖表：
  - `hospitals`（医疗机构）
  - `model_versions`（模型版本）
  - `departments`（科室，用于验证）
  - `model_nodes`（维度节点，用于验证）
