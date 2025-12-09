# 医技智能分类分级 - 设计文档

## 概述

医技智能分类分级模块是医院科室业务价值评估系统的AI辅助功能，通过集成DeepSeek（OpenAI Compatible API）实现医技收费项目的自动分类。该模块采用异步处理架构，支持大批量项目的智能分类、断点续传、预案管理和批量提交功能。

### 核心功能
- AI接口配置管理（API端点、密钥加密、提示词模板）
- 医技项目分类任务创建和管理
- 异步AI分类处理（Celery后台任务）
- 断点续传和实时进度跟踪
- 分类预案查看、调整和保存
- 提交前预览（新增/覆盖分析）
- 批量提交到维度目录
- API使用统计和限流控制

### 技术栈
- 后端：FastAPI + SQLAlchemy + Celery + Redis
- AI集成：OpenAI Compatible API（DeepSeek）
- 加密：cryptography（Fernet对称加密）
- 前端：Vue 3 + Element Plus + TypeScript
- 实时通信：HTTP轮询（可扩展为WebSocket）

## 架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                            │
├─────────────────────────────────────────────────────────────────┤
│  AI接口配置  │  分类任务管理  │  预案查看调整  │  提交预览      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API 层 (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/ai-config                                               │
│  /api/v1/classification-tasks                                   │
│  /api/v1/classification-plans                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     服务层 (Services)                            │
├─────────────────────────────────────────────────────────────────┤
│  AIConfigService  │  ClassificationService  │  PlanService       │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│   Celery 异步任务层        │   │   AI 接口层              │
├───────────────────────────┤   ├──────────────────────────┤
│  classify_items_task      │──▶│  OpenAI Client           │
│  continue_classification  │   │  (DeepSeek Compatible)   │
└───────────────────────────┘   └──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    数据层 (SQLAlchemy)                           │
├─────────────────────────────────────────────────────────────────┤
│  AIConfig  │  ClassificationTask  │  ClassificationPlan  │       │
│  PlanItem  │  TaskProgress        │                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   数据库层 (PostgreSQL + Redis)                  │
└─────────────────────────────────────────────────────────────────┘
```


### 数据流

#### 1. 配置流程
```
管理员 → AI接口配置页面 → 输入API端点/密钥/提示词 → 
加密存储 → 数据库
```

#### 2. 分类任务创建流程
```
管理员 → 选择收费类别+模型版本 → 创建任务 → 
查询医技项目 → 启动Celery任务 → 异步处理
```

#### 3. AI分类处理流程
```
Celery任务 → 读取AI配置 → 逐个处理项目 →
调用AI接口 → 解析响应 → 保存结果 → 更新进度 →
完成后生成预案
```

#### 4. 预案调整流程
```
管理员 → 查看预案 → 筛选/排序项目 → 
调整维度 → 保存预案 → 更新状态
```

#### 5. 提交流程
```
管理员 → 点击提交 → 生成预览（分析新增/覆盖）→
确认提交 → 批量插入/更新维度项目 → 
更新预案状态 → 完成
```

## 组件和接口

### 数据模型

#### AIConfig（AI接口配置）

```python
class AIConfig(Base):
    __tablename__ = "ai_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    api_endpoint = Column(String(500), nullable=False, comment="API访问端点")
    api_key_encrypted = Column(Text, nullable=False, comment="加密的API密钥")
    prompt_template = Column(Text, nullable=False, comment="提示词模板")
    call_delay = Column(Float, default=1.0, comment="调用延迟（秒）")
    daily_limit = Column(Integer, default=10000, comment="每日调用限额")
    batch_size = Column(Integer, default=100, comment="批次大小")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="ai_configs")
    
    # 唯一约束：每个医疗机构只有一个AI配置
    __table_args__ = (
        UniqueConstraint('hospital_id', name='uq_ai_config_hospital'),
    )
```

#### ClassificationTask（分类任务）

```python
class ClassificationTask(Base):
    __tablename__ = "classification_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    task_name = Column(String(100), nullable=False, comment="任务名称")
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False, comment="模型版本ID")
    charge_categories = Column(JSON, nullable=False, comment="收费类别列表")
    status = Column(Enum('pending', 'processing', 'completed', 'failed', 'paused'), 
                   default='pending', comment="任务状态")
    total_items = Column(Integer, default=0, comment="总项目数")
    processed_items = Column(Integer, default=0, comment="已处理项目数")
    failed_items = Column(Integer, default=0, comment="失败项目数")
    celery_task_id = Column(String(255), comment="Celery任务ID")
    error_message = Column(Text, comment="错误信息")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="classification_tasks")
    model_version = relationship("ModelVersion", back_populates="classification_tasks")
    creator = relationship("User")
    plan = relationship("ClassificationPlan", back_populates="task", uselist=False)
    progress_records = relationship("TaskProgress", back_populates="task", cascade="all, delete-orphan")
```


#### ClassificationPlan（分类预案）

```python
class ClassificationPlan(Base):
    __tablename__ = "classification_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("classification_tasks.id"), nullable=False, unique=True)
    plan_name = Column(String(100), comment="预案名称")
    status = Column(Enum('draft', 'submitted'), default='draft', comment="预案状态")
    submitted_at = Column(DateTime, comment="提交时间")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital", back_populates="classification_plans")
    task = relationship("ClassificationTask", back_populates="plan")
    items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")
```

#### PlanItem（预案项目）

```python
class PlanItem(Base):
    __tablename__ = "plan_items"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("classification_plans.id"), nullable=False, index=True)
    charge_item_id = Column(Integer, ForeignKey("charge_items.id"), nullable=False, comment="收费项目ID")
    charge_item_name = Column(String(200), nullable=False, comment="收费项目名称")
    ai_suggested_dimension_id = Column(Integer, ForeignKey("model_nodes.id"), comment="AI建议维度ID")
    ai_confidence = Column(Numeric(5, 4), comment="AI确信度（0-1）")
    user_set_dimension_id = Column(Integer, ForeignKey("model_nodes.id"), comment="用户设置维度ID")
    is_adjusted = Column(Boolean, default=False, comment="是否已调整")
    processing_status = Column(Enum('pending', 'processing', 'completed', 'failed'), 
                               default='pending', comment="处理状态")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    hospital = relationship("Hospital")
    plan = relationship("ClassificationPlan", back_populates="items")
    charge_item = relationship("ChargeItem")
    ai_suggested_dimension = relationship("ModelNode", foreign_keys=[ai_suggested_dimension_id])
    user_set_dimension = relationship("ModelNode", foreign_keys=[user_set_dimension_id])
    
    # 唯一约束：同一预案中每个收费项目只能出现一次
    __table_args__ = (
        UniqueConstraint('plan_id', 'charge_item_id', name='uq_plan_item'),
    )
```

#### TaskProgress（任务进度记录）

```python
class TaskProgress(Base):
    __tablename__ = "task_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("classification_tasks.id"), nullable=False, index=True)
    charge_item_id = Column(Integer, ForeignKey("charge_items.id"), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'failed'), 
                   default='pending', comment="处理状态")
    error_message = Column(Text, comment="错误信息")
    processed_at = Column(DateTime, comment="处理时间")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    task = relationship("ClassificationTask", back_populates="progress_records")
    charge_item = relationship("ChargeItem")
    
    # 唯一约束：同一任务中每个项目只记录一次
    __table_args__ = (
        UniqueConstraint('task_id', 'charge_item_id', name='uq_task_progress'),
    )
```

#### APIUsageLog（API使用日志）

```python
class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("classification_tasks.id"), nullable=False, index=True)
    charge_item_id = Column(Integer, ForeignKey("charge_items.id"), nullable=False)
    request_data = Column(JSON, comment="请求数据")
    response_data = Column(JSON, comment="响应数据")
    status_code = Column(Integer, comment="HTTP状态码")
    error_message = Column(Text, comment="错误信息")
    call_duration = Column(Float, comment="调用耗时（秒）")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    hospital = relationship("Hospital")
    task = relationship("ClassificationTask")
    charge_item = relationship("ChargeItem")
```


### API 端点

#### AI配置 API

```
GET    /api/v1/ai-config                    # 获取AI配置（密钥掩码）
POST   /api/v1/ai-config                    # 创建/更新AI配置
POST   /api/v1/ai-config/test               # 测试AI配置
GET    /api/v1/ai-config/usage-stats        # 获取API使用统计
```

#### 分类任务 API

```
GET    /api/v1/classification-tasks                      # 获取任务列表
POST   /api/v1/classification-tasks                      # 创建分类任务
GET    /api/v1/classification-tasks/{id}                 # 获取任务详情
DELETE /api/v1/classification-tasks/{id}                 # 删除任务
POST   /api/v1/classification-tasks/{id}/continue        # 继续处理任务
GET    /api/v1/classification-tasks/{id}/progress        # 获取实时进度
GET    /api/v1/classification-tasks/{id}/logs            # 获取处理日志
```

#### 分类预案 API

```
GET    /api/v1/classification-plans                      # 获取预案列表
GET    /api/v1/classification-plans/{id}                 # 获取预案详情
PUT    /api/v1/classification-plans/{id}                 # 更新预案（名称、状态）
DELETE /api/v1/classification-plans/{id}                 # 删除预案
GET    /api/v1/classification-plans/{id}/items           # 获取预案项目列表
PUT    /api/v1/classification-plans/{id}/items/{item_id} # 调整项目维度
POST   /api/v1/classification-plans/{id}/preview         # 生成提交预览
POST   /api/v1/classification-plans/{id}/submit          # 提交预案
```

### 前端路由

```typescript
{
  path: '/system-settings',
  children: [
    {
      path: 'ai-config',
      name: 'AIConfig',
      component: () => import('@/views/system/AIConfig.vue'),
      meta: { title: 'AI接口管理', requiresAdmin: true }
    }
  ]
},
{
  path: '/intelligent-classification',
  children: [
    {
      path: 'tasks',
      name: 'ClassificationTasks',
      component: () => import('@/views/classification/Tasks.vue'),
      meta: { title: '分类任务管理' }
    },
    {
      path: 'plans',
      name: 'ClassificationPlans',
      component: () => import('@/views/classification/Plans.vue'),
      meta: { title: '分类预案管理' }
    },
    {
      path: 'plans/:id',
      name: 'PlanDetail',
      component: () => import('@/views/classification/PlanDetail.vue'),
      meta: { title: '预案详情' }
    }
  ]
}
```

### 前端组件结构

```
views/
├── system/
│   └── AIConfig.vue                    # AI接口配置页面
└── classification/
    ├── Tasks.vue                       # 分类任务列表
    ├── Plans.vue                       # 分类预案列表
    └── PlanDetail.vue                  # 预案详情和调整

components/
├── CreateTaskDialog.vue                # 创建任务对话框
├── PlanItemTable.vue                   # 预案项目表格
├── SubmitPreviewDialog.vue             # 提交预览对话框
└── ProgressIndicator.vue               # 进度指示器
```

## 数据模型

### 实体关系图

```
┌─────────────────┐
│    Hospital     │
└────────┬────────┘
         │ 1
         │
    ┌────┴────────────────────┐
    │ *                       │ *
┌───┴──────────┐      ┌───────┴──────────┐
│  AIConfig    │      │ ClassificationTask│
└──────────────┘      └───────┬───────────┘
                              │ 1
                              │
                              │ 1
                      ┌───────┴──────────┐
                      │ClassificationPlan│
                      └───────┬───────────┘
                              │ 1
                              │
                              │ *
                      ┌───────┴──────────┐
                      │    PlanItem      │
                      └───────┬───────────┘
                              │
                    ┌─────────┴─────────┐
                    │ *                 │ *
            ┌───────┴────┐      ┌──────┴─────┐
            │ ChargeItem │      │ ModelNode  │
            └────────────┘      └────────────┘
```


### 枚举类型

#### TaskStatus（任务状态）
- `pending`: 待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败
- `paused`: 已暂停

#### PlanStatus（预案状态）
- `draft`: 草稿
- `submitted`: 已提交

#### ProcessingStatus（处理状态）
- `pending`: 待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

### 数据约束

1. **AI配置**
   - 每个医疗机构只能有一个AI配置
   - API端点必须是有效的URL
   - API密钥必须加密存储
   - 调用延迟范围：0.1-10秒
   - 每日限额：1-100000次

2. **分类任务**
   - 任务名称不为空，长度不超过100字符
   - 收费类别至少选择一个
   - 模型版本必须存在且激活
   - 进度计数器：0 <= processed_items <= total_items

3. **分类预案**
   - 每个任务只能有一个预案
   - 预案名称长度不超过100字符
   - 提交后状态不可回退为草稿

4. **预案项目**
   - 同一预案中每个收费项目唯一
   - AI确信度范围：0-1
   - 最终维度 = user_set_dimension_id ?? ai_suggested_dimension_id
   - 用户设置维度后，is_adjusted = true

5. **任务进度**
   - 同一任务中每个项目只记录一次
   - 状态转换：pending → processing → completed/failed

## 正确性属性

*属性是系统在所有有效执行中应保持为真的特征或行为——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1：URL格式验证
*对于任何*API端点输入，如果格式不是有效的URL，系统应拒绝保存
**验证：需求 1.2**

### 属性 2：API密钥加密存储
*对于任何*API密钥，保存到数据库后，存储的值应与原始值不同且可通过解密恢复原始值
**验证：需求 1.4**

### 属性 3：API密钥掩码显示
*对于任何*已保存的API配置，查询时返回的密钥字段应被掩码处理（如"****"），不包含原始明文
**验证：需求 1.5**

### 属性 4：API密钥更新覆盖
*对于任何*已存在的AI配置，更新密钥后，解密存储的密钥应等于新输入的密钥
**验证：需求 1.6**

### 属性 5：提示词模板保存一致性
*对于任何*多行文本提示词，保存后读取的内容应与输入完全一致（包括换行符）
**验证：需求 1.7**

### 属性 6：AI配置必填字段验证
*对于任何*AI配置保存请求，如果缺少API端点、API密钥或提示词模板，系统应拒绝保存
**验证：需求 1.8**

### 属性 7：收费类别多选保存
*对于任何*分类任务，选择的收费类别列表应完整保存到数据库，且顺序和内容一致
**验证：需求 2.3**

### 属性 8：模型版本末级维度加载
*对于任何*模型版本，系统应返回该版本下所有is_leaf=true的维度节点
**验证：需求 2.4**

### 属性 9：任务名称长度验证
*对于任何*任务名称，如果为空或长度超过100字符，系统应拒绝创建任务
**验证：需求 2.5**

### 属性 10：任务创建启动异步处理
*对于任何*创建的分类任务，系统应生成celery_task_id并将任务状态设置为processing
**验证：需求 2.6**

### 属性 11：任务元数据完整性
*对于任何*分类任务，创建后应包含收费类别、模型版本ID、创建时间和创建人字段
**验证：需求 2.7**

### 属性 12：异步任务启动验证
*对于任何*创建的分类任务，应能在Celery队列中找到对应的celery_task_id任务
**验证：需求 3.1**

### 属性 13：AI接口调用参数正确性
*对于任何*医技项目，调用AI接口时应传递项目名称和目标模型版本的末级维度列表
**验证：需求 3.2**

### 属性 14：AI响应解析正确性
*对于任何*有效的AI JSON响应，系统应正确提取dimension_id和confidence字段
**验证：需求 3.3**

### 属性 15：进度计数器递增
*对于任何*分类任务，每处理一个项目后，processed_items应增加1
**验证：需求 3.4**

### 属性 16：部分失败继续处理
*对于任何*分类任务，如果某个项目处理失败，系统应记录错误但继续处理下一个项目
**验证：需求 3.5**

### 属性 17：任务完成状态更新
*对于任何*分类任务，当processed_items等于total_items时，状态应更新为completed
**验证：需求 3.6**

### 属性 18：断点进度保存
*对于任何*中断的分类任务，系统应保存已完成项目的处理状态为completed
**验证：需求 3.7**

### 属性 19：任务列表进度显示
*对于任何*分类任务，列表中显示的进度应为processed_items/total_items
**验证：需求 4.1**

### 属性 20：实时进度更新
*对于任何*处理中的任务，轮询进度接口应返回最新的processed_items值
**验证：需求 4.2**

### 属性 21：中断位置记录
*对于任何*中断的任务，系统应记录最后一个status=completed的项目位置
**验证：需求 4.3**

### 属性 22：续传跳过已完成项目
*对于任何*继续处理的任务，系统应仅处理status=pending或failed的项目
**验证：需求 4.4, 4.5**

### 属性 23：项目处理状态管理
*对于任何*预案项目，其processing_status应在pending、processing、completed、failed之间正确转换
**验证：需求 4.6**

### 属性 24：任务完成生成预案
*对于任何*状态为completed的任务，系统应创建对应的ClassificationPlan记录
**验证：需求 5.1**

### 属性 25：预案项目字段完整性
*对于任何*预案项目，应包含项目名称、AI建议维度、确信度和用户设置维度字段
**验证：需求 5.3**

### 属性 26：未调整项目默认维度
*对于任何*is_adjusted=false的预案项目，最终维度应等于ai_suggested_dimension_id
**验证：需求 5.4**

### 属性 27：调整项目维度保存
*对于任何*预案项目，修改user_set_dimension_id后，is_adjusted应设置为true
**验证：需求 5.6**

### 属性 28：确信度排序正确性
*对于任何*预案项目列表，按确信度升序排序后，每个项目的confidence应大于等于前一个项目
**验证：需求 5.7**

### 属性 29：确信度范围筛选
*对于任何*确信度阈值，筛选后的项目列表中所有项目的confidence应满足筛选条件
**验证：需求 5.8**

### 属性 30：预案名称长度验证
*对于任何*预案名称，如果为空或长度超过100字符，系统应拒绝保存
**验证：需求 6.2**

### 属性 31：预案保存字段完整性
*对于任何*保存的预案，应包含预案名称、状态和最后修改时间字段
**验证：需求 6.3**

### 属性 32：预案保留任务元数据
*对于任何*预案，应能通过task关系访问原始任务的收费类别和模型版本ID
**验证：需求 6.4**

### 属性 33：预案列表查询完整性
*对于任何*医疗机构，查询预案列表应返回该机构的所有预案及其元数据
**验证：需求 6.5**

### 属性 34：预案加载数据完整性
*对于任何*预案ID，加载预案应返回所有关联的预案项目和调整记录
**验证：需求 6.6**

### 属性 35：预案编辑更新成功
*对于任何*已保存的预案，修改项目维度后再次保存，更新应成功且updated_at字段更新
**验证：需求 6.7**

### 属性 36：提交预览分析正确性
*对于任何*预案，生成预览时应正确识别每个项目在目标维度中是否已存在
**验证：需求 7.2**

### 属性 37：新增项目标记
*对于任何*在目标维度中不存在的项目，预览应标记为"新增"
**验证：需求 7.3**

### 属性 38：覆盖项目标记和原维度显示
*对于任何*在目标维度中已存在的项目，预览应标记为"覆盖"并显示原有维度名称
**验证：需求 7.4**

### 属性 39：预览统计数字正确性
*对于任何*预览结果，新增数量+覆盖数量应等于预案项目总数
**验证：需求 7.5**

### 属性 40：批量提交插入正确性
*对于任何*预案提交，所有标记为"新增"的项目应在对应维度中创建新的维度项目记录
**验证：需求 8.2, 8.3**

### 属性 41：批量提交更新正确性
*对于任何*预案提交，所有标记为"覆盖"的项目应更新现有维度项目记录的维度归属
**验证：需求 8.2, 8.4**

### 属性 42：提交完成状态更新
*对于任何*成功提交的预案，状态应从draft更新为submitted，且submitted_at字段设置为当前时间
**验证：需求 8.5**

### 属性 43：提交失败事务回滚
*对于任何*提交失败的预案，数据库中不应存在本次提交创建或修改的维度项目记录
**验证：需求 8.6**

### 属性 44：提示词占位符替换
*对于任何*包含{item_name}和{dimensions}占位符的提示词模板，调用AI时应替换为实际的项目名称和维度列表JSON
**验证：需求 9.1, 9.2**

### 属性 45：维度列表字段完整性
*对于任何*构建的维度列表，每个维度应包含id、name和path字段
**验证：需求 9.3**

### 属性 46：AI请求JSON格式要求
*对于任何*发送给AI的提示词，应明确要求返回包含dimension_id和confidence字段的JSON格式
**验证：需求 9.4**

### 属性 47：非JSON响应错误处理
*对于任何*AI返回的非JSON格式响应，系统应记录错误日志且不崩溃
**验证：需求 9.5**

### 属性 48：多租户任务创建隔离
*对于任何*创建的分类任务，hospital_id应自动设置为当前医疗机构ID
**验证：需求 10.1**

### 属性 49：多租户任务查询隔离
*对于任何*医疗机构，查询任务或预案应仅返回hospital_id等于该机构ID的记录
**验证：需求 10.2**

### 属性 50：多租户提交操作隔离
*对于任何*预案提交，仅操作hospital_id等于当前机构ID的模型版本和维度数据
**验证：需求 10.3**

### 属性 51：机构切换数据刷新
*对于任何*医疗机构切换操作，前端应重新加载任务和预案列表，显示新机构的数据
**验证：需求 10.4**

### 属性 52：多租户AI配置隔离
*对于任何*AI接口调用，应使用hospital_id等于当前机构ID的AI配置
**验证：需求 10.5**

### 属性 53：API调用失败日志记录
*对于任何*失败的AI接口调用，系统应记录HTTP状态码和错误消息到APIUsageLog
**验证：需求 11.1**

### 属性 54：响应解析错误日志记录
*对于任何*AI响应解析失败，系统应记录原始响应内容和解析错误到日志
**验证：需求 11.2**

### 属性 55：失败项目列表显示
*对于任何*包含失败项目的任务，任务详情应显示所有processing_status=failed的项目及其错误原因
**验证：需求 11.3**

### 属性 56：任务处理日志完整性
*对于任何*完成的任务，任务详情应显示开始时间、结束时间、成功数和失败数
**验证：需求 11.4**

### 属性 57：日志字段完整性
*对于任何*系统日志记录，应包含时间戳、操作类型、用户ID和详细信息字段
**验证：需求 11.5**

### 属性 58：API调用延迟控制
*对于任何*连续的AI接口调用，两次调用之间的时间间隔应大于等于配置的call_delay值
**验证：需求 12.1**

### 属性 59：调用延迟配置验证
*对于任何*调用延迟配置值，如果不在0.1-10秒范围内，系统应拒绝保存
**验证：需求 12.2**

### 属性 60：批次大小处理控制
*对于任何*批量处理任务，每处理batch_size个项目后应暂停，然后继续下一批
**验证：需求 12.3**

### 属性 61：每日限额控制
*对于任何*医疗机构，当日API调用次数达到daily_limit时，新的调用应被拒绝
**验证：需求 12.4**

### 属性 62：API使用统计准确性
*对于任何*医疗机构，当日调用次数应等于APIUsageLog中hospital_id匹配且created_at为当日的记录数
**验证：需求 12.5**


## 错误处理

### 错误类型

1. **验证错误（400 Bad Request）**
   - 必填字段缺失
   - 字段长度超限
   - URL格式无效
   - 数值范围无效
   - 收费类别为空

2. **认证错误（401 Unauthorized）**
   - API密钥无效
   - AI接口认证失败

3. **权限错误（403 Forbidden）**
   - 非管理员访问AI配置
   - 跨医疗机构访问数据

4. **资源不存在（404 Not Found）**
   - 任务ID不存在
   - 预案ID不存在
   - 模型版本不存在

5. **冲突错误（409 Conflict）**
   - 任务名称重复
   - 预案已提交不可修改

6. **限流错误（429 Too Many Requests）**
   - 达到每日调用限额
   - 调用频率过高

7. **外部服务错误（502 Bad Gateway）**
   - AI接口不可达
   - AI接口超时
   - AI接口返回错误

8. **服务器错误（500 Internal Server Error）**
   - 数据库连接失败
   - Celery任务启动失败
   - 加密/解密失败

### 错误响应格式

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "field": "字段名（如果适用）",
  "retry_after": 3600
}
```

### 错误处理策略

1. **输入验证**：在 Pydantic Schema 层进行基本验证
2. **业务规则验证**：在 Service 层进行复杂业务逻辑验证
3. **外部服务容错**：AI接口调用失败时记录错误但继续处理
4. **事务管理**：提交预案等关键操作使用数据库事务确保原子性
5. **重试机制**：AI接口调用失败时自动重试（最多3次）
6. **日志记录**：所有错误都应记录到日志系统和APIUsageLog表

## 测试策略

### 单元测试

1. **加密解密测试**
   - 测试API密钥加密存储
   - 测试密钥解密恢复
   - 测试密钥掩码显示

2. **模板渲染测试**
   - 测试占位符替换
   - 测试维度列表构建
   - 测试JSON格式生成

3. **进度管理测试**
   - 测试进度计数器更新
   - 测试断点记录
   - 测试续传逻辑

4. **预览分析测试**
   - 测试新增/覆盖识别
   - 测试统计数字计算
   - 测试原维度查询

### 属性测试

本项目使用 **Hypothesis** 作为属性测试库。每个属性测试应运行至少 **100 次迭代**。

#### 属性测试标记格式
每个属性测试必须使用以下格式标记：
```python
# Feature: ai-medical-tech-classification, Property 1: URL格式验证
```

#### 属性测试覆盖

1. **属性 1-8**：AI配置管理
   - 生成随机URL、密钥、提示词
   - 测试验证、加密、掩码逻辑
   - 验证保存和读取一致性

2. **属性 9-11**：任务创建
   - 生成随机任务配置
   - 测试验证和元数据保存
   - 验证异步任务启动

3. **属性 12-23**：异步处理和断点续传
   - 生成随机项目列表
   - 模拟AI接口响应
   - 测试进度更新和续传逻辑

4. **属性 24-29**：预案查看和调整
   - 生成随机预案数据
   - 测试默认维度、调整、排序、筛选
   - 验证数据完整性

5. **属性 30-35**：预案保存和加载
   - 生成随机预案名称和修改
   - 测试保存、查询、更新逻辑
   - 验证元数据保留

6. **属性 36-39**：提交预览
   - 生成已存在和不存在的项目
   - 测试新增/覆盖识别
   - 验证统计准确性

7. **属性 40-43**：批量提交
   - 生成混合项目（新增+覆盖）
   - 测试批量插入和更新
   - 验证事务回滚

8. **属性 44-47**：提示词模板
   - 生成随机模板和数据
   - 测试占位符替换
   - 验证JSON格式要求

9. **属性 48-52**：多租户隔离
   - 生成多个医疗机构的数据
   - 测试创建、查询、操作的隔离性
   - 验证跨租户访问被阻止

10. **属性 53-57**：错误处理和日志
    - 模拟各种错误场景
    - 测试日志记录完整性
    - 验证错误不影响后续处理

11. **属性 58-62**：性能和限流
    - 测试调用延迟控制
    - 测试批次处理
    - 测试限额控制和统计

### 集成测试

1. **端到端分类流程**
   - 创建任务 → AI处理 → 生成预案 → 调整 → 提交
   - 验证完整流程数据一致性

2. **断点续传场景**
   - 模拟任务中断
   - 继续处理
   - 验证不重复处理

3. **AI接口集成**
   - 使用真实AI接口测试
   - 验证请求格式和响应解析
   - 测试错误处理

4. **前端集成测试**
   - 测试页面渲染
   - 测试表单提交
   - 测试实时进度更新

### 测试数据生成

使用 Hypothesis 的 strategies 生成测试数据：

```python
from hypothesis import strategies as st

# URL策略
valid_url = st.from_regex(r'https?://[a-z0-9.-]+\.[a-z]{2,}', fullmatch=True)
invalid_url = st.text().filter(lambda x: not x.startswith('http'))

# API密钥策略
api_key = st.text(min_size=20, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))

# 确信度策略
confidence = st.floats(min_value=0.0, max_value=1.0)

# 任务名称策略
task_name = st.text(min_size=1, max_size=100)

# 收费类别策略
charge_categories = st.lists(
    st.sampled_from(['检查费', '放射费', '化验费', '麻醉费', '手术费']),
    min_size=1,
    max_size=5,
    unique=True
)

# 提示词模板策略
prompt_template = st.text(min_size=10, max_size=1000).map(
    lambda x: x.replace('{', '{{').replace('}', '}}') + '\n{item_name}\n{dimensions}'
)
```


## 实现细节

### API密钥加密

使用 `cryptography` 库的 Fernet 对称加密：

```python
from cryptography.fernet import Fernet
import os

# 生成或加载加密密钥（存储在环境变量中）
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY') or Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_api_key(plain_key: str) -> str:
    """加密API密钥"""
    return cipher.encrypt(plain_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """解密API密钥"""
    return cipher.decrypt(encrypted_key.encode()).decode()

def mask_api_key(encrypted_key: str) -> str:
    """掩码显示API密钥"""
    return "****" + encrypted_key[-4:] if len(encrypted_key) > 4 else "****"
```

### AI接口调用

使用 OpenAI Python SDK（兼容DeepSeek）：

```python
from openai import OpenAI
import json

def call_ai_classification(
    api_endpoint: str,
    api_key: str,
    prompt: str,
    item_name: str,
    dimensions: list
) -> dict:
    """调用AI接口进行分类"""
    client = OpenAI(
        base_url=api_endpoint,
        api_key=api_key
    )
    
    # 构建维度列表JSON
    dimensions_json = json.dumps([
        {
            "id": d.id,
            "name": d.name,
            "path": d.get_full_path()
        }
        for d in dimensions
    ], ensure_ascii=False)
    
    # 替换占位符
    final_prompt = prompt.replace('{item_name}', item_name)
    final_prompt = final_prompt.replace('{dimensions}', dimensions_json)
    
    # 调用AI
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个医技项目分类专家。"},
            {"role": "user", "content": final_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    # 解析响应
    result = json.loads(response.choices[0].message.content)
    return {
        "dimension_id": result.get("dimension_id"),
        "confidence": float(result.get("confidence", 0.0))
    }
```

### Celery异步任务

```python
from celery import Task
from app.tasks import celery_app
import time

@celery_app.task(bind=True, max_retries=3)
def classify_items_task(self, task_id: int, hospital_id: int):
    """异步分类任务"""
    db = SessionLocal()
    try:
        # 加载任务
        task = db.query(ClassificationTask).filter_by(id=task_id).first()
        if not task:
            return
        
        # 加载AI配置
        ai_config = db.query(AIConfig).filter_by(hospital_id=hospital_id).first()
        if not ai_config:
            raise ValueError("AI配置不存在")
        
        # 解密API密钥
        api_key = decrypt_api_key(ai_config.api_key_encrypted)
        
        # 加载待处理项目
        pending_items = db.query(PlanItem).join(ClassificationPlan).filter(
            ClassificationPlan.task_id == task_id,
            PlanItem.processing_status.in_(['pending', 'failed'])
        ).all()
        
        # 加载目标维度
        dimensions = db.query(ModelNode).filter(
            ModelNode.version_id == task.model_version_id,
            ModelNode.is_leaf == True
        ).all()
        
        # 逐个处理项目
        for item in pending_items:
            try:
                # 更新状态为处理中
                item.processing_status = 'processing'
                db.commit()
                
                # 调用AI接口
                result = call_ai_classification(
                    api_endpoint=ai_config.api_endpoint,
                    api_key=api_key,
                    prompt=ai_config.prompt_template,
                    item_name=item.charge_item_name,
                    dimensions=dimensions
                )
                
                # 保存结果
                item.ai_suggested_dimension_id = result['dimension_id']
                item.ai_confidence = result['confidence']
                item.processing_status = 'completed'
                
                # 记录API使用日志
                log = APIUsageLog(
                    hospital_id=hospital_id,
                    task_id=task_id,
                    charge_item_id=item.charge_item_id,
                    request_data={"item_name": item.charge_item_name},
                    response_data=result,
                    status_code=200
                )
                db.add(log)
                
                # 更新任务进度
                task.processed_items += 1
                db.commit()
                
                # 延迟控制
                time.sleep(ai_config.call_delay)
                
            except Exception as e:
                # 记录错误
                item.processing_status = 'failed'
                item.error_message = str(e)
                task.failed_items += 1
                db.commit()
                
                # 记录错误日志
                log = APIUsageLog(
                    hospital_id=hospital_id,
                    task_id=task_id,
                    charge_item_id=item.charge_item_id,
                    error_message=str(e),
                    status_code=500
                )
                db.add(log)
                db.commit()
        
        # 更新任务状态
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        db.commit()
        raise
    finally:
        db.close()
```

### 提交预览分析

```python
def generate_submit_preview(plan_id: int, db: Session) -> dict:
    """生成提交预览"""
    plan = db.query(ClassificationPlan).filter_by(id=plan_id).first()
    if not plan:
        raise ValueError("预案不存在")
    
    items = plan.items
    new_items = []
    overwrite_items = []
    
    for item in items:
        # 确定最终维度
        final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
        
        # 检查是否已存在
        existing = db.query(DimensionItem).filter(
            DimensionItem.hospital_id == plan.hospital_id,
            DimensionItem.node_id == final_dimension_id,
            DimensionItem.charge_item_id == item.charge_item_id
        ).first()
        
        if existing:
            # 覆盖
            overwrite_items.append({
                "item_id": item.id,
                "item_name": item.charge_item_name,
                "new_dimension_id": final_dimension_id,
                "new_dimension_name": get_dimension_name(final_dimension_id, db),
                "old_dimension_id": existing.node_id,
                "old_dimension_name": get_dimension_name(existing.node_id, db)
            })
        else:
            # 新增
            new_items.append({
                "item_id": item.id,
                "item_name": item.charge_item_name,
                "dimension_id": final_dimension_id,
                "dimension_name": get_dimension_name(final_dimension_id, db)
            })
    
    return {
        "new_count": len(new_items),
        "overwrite_count": len(overwrite_items),
        "new_items": new_items,
        "overwrite_items": overwrite_items
    }
```

### 批量提交

```python
def submit_classification_plan(plan_id: int, db: Session):
    """提交分类预案"""
    plan = db.query(ClassificationPlan).filter_by(id=plan_id).first()
    if not plan:
        raise ValueError("预案不存在")
    
    if plan.status == 'submitted':
        raise ValueError("预案已提交，不可重复提交")
    
    try:
        for item in plan.items:
            # 确定最终维度
            final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
            
            # 检查是否已存在
            existing = db.query(DimensionItem).filter(
                DimensionItem.hospital_id == plan.hospital_id,
                DimensionItem.node_id == final_dimension_id,
                DimensionItem.charge_item_id == item.charge_item_id
            ).first()
            
            if existing:
                # 更新维度归属
                existing.node_id = final_dimension_id
                existing.updated_at = datetime.utcnow()
            else:
                # 创建新记录
                new_item = DimensionItem(
                    hospital_id=plan.hospital_id,
                    node_id=final_dimension_id,
                    charge_item_id=item.charge_item_id,
                    charge_item_name=item.charge_item_name
                )
                db.add(new_item)
        
        # 更新预案状态
        plan.status = 'submitted'
        plan.submitted_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
```

## 性能考虑

1. **数据库索引**
   - hospital_id：多租户查询优化
   - task_id：关联查询优化
   - plan_id：预案项目查询优化
   - created_at：日志查询和统计优化

2. **查询优化**
   - 使用 joinedload 预加载关联数据
   - 分页查询避免大数据量
   - 批量插入/更新减少数据库往返

3. **异步处理优化**
   - Celery worker 数量根据负载调整
   - Redis 作为消息队列和结果存储
   - 任务优先级队列

4. **AI接口优化**
   - 调用延迟控制避免限流
   - 失败重试机制
   - 批次处理控制内存使用

5. **前端优化**
   - 进度轮询间隔动态调整（处理中1秒，完成后停止）
   - 虚拟滚动处理大量预案项目
   - 防抖和节流优化用户输入

## 安全考虑

1. **密钥安全**
   - API密钥加密存储
   - 加密密钥存储在环境变量
   - 前端不传输明文密钥
   - 查询时返回掩码

2. **权限控制**
   - AI配置仅管理员可访问
   - 多租户数据严格隔离
   - API层验证用户权限

3. **输入验证**
   - 所有输入进行严格验证
   - 防止SQL注入
   - 防止XSS攻击
   - URL白名单验证

4. **限流保护**
   - 每日调用限额
   - 调用频率控制
   - IP限流（可选）

5. **日志审计**
   - 记录所有AI接口调用
   - 记录敏感操作（配置修改、预案提交）
   - 保留日志用于审计

## 可扩展性

1. **支持多种AI模型**
   - 抽象AI接口层
   - 支持OpenAI、DeepSeek、Claude等
   - 模型选择配置化

2. **支持更多分类场景**
   - 不仅限于医技项目
   - 可扩展到药品、耗材等
   - 分类规则可配置

3. **支持批量导入**
   - Excel导入医技项目
   - 批量创建分类任务

4. **支持导出功能**
   - 导出预案为Excel
   - 导出分类报告

5. **WebSocket实时通信**
   - 替代HTTP轮询
   - 实时推送进度更新
   - 降低服务器负载

## 依赖关系

### 外部依赖
- FastAPI：Web框架
- SQLAlchemy：ORM
- Celery：异步任务队列
- Redis：消息队列和缓存
- cryptography：加密库
- openai：AI接口SDK
- Hypothesis：属性测试库

### 内部依赖
- Hospital模型：多租户支持
- ModelVersion模型：模型版本管理
- ModelNode模型：维度管理
- ChargeItem模型：收费项目
- DimensionItem模型：维度项目映射
- User模型：用户管理

## 部署注意事项

1. **环境变量配置**
   ```bash
   ENCRYPTION_KEY=<Fernet密钥>
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

2. **Celery Worker启动**
   ```bash
   celery -A app.tasks worker --loglevel=info --concurrency=4
   ```

3. **Redis配置**
   - 持久化配置（AOF或RDB）
   - 内存限制和淘汰策略
   - 主从复制（生产环境）

4. **数据库迁移**
   ```bash
   alembic revision --autogenerate -m "add_ai_classification_tables"
   alembic upgrade head
   ```

5. **监控和告警**
   - Celery任务监控（Flower）
   - API调用统计和告警
   - 错误率监控
   - 性能指标监控
