# AI分类数据库迁移总结

## 迁移文件

**文件**: `backend/alembic/versions/20251126_add_ai_classification_tables.py`
**Revision ID**: `20251126_ai_classification`
**依赖**: `20251126_orientation_ids`

## 创建的数据库对象

### 枚举类型

1. **task_status** - 任务状态
   - `pending`: 待处理
   - `processing`: 处理中
   - `completed`: 已完成
   - `failed`: 失败
   - `paused`: 已暂停

2. **plan_status** - 预案状态
   - `draft`: 草稿
   - `submitted`: 已提交

3. **processing_status** - 处理状态
   - `pending`: 待处理
   - `processing`: 处理中
   - `completed`: 已完成
   - `failed`: 失败

4. **progress_status** - 进度状态
   - `pending`: 待处理
   - `processing`: 处理中
   - `completed`: 已完成
   - `failed`: 失败

### 数据表

#### 1. ai_configs（AI接口配置表）

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，CASCADE删除）
- `api_endpoint`: API访问端点（VARCHAR(500)）
- `api_key_encrypted`: 加密的API密钥（TEXT）
- `prompt_template`: 提示词模板（TEXT）
- `call_delay`: 调用延迟（FLOAT，默认1.0）
- `daily_limit`: 每日调用限额（INTEGER，默认10000）
- `batch_size`: 批次大小（INTEGER，默认100）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**约束**:
- 主键: `id`
- 外键: `hospital_id` → `hospitals.id` (CASCADE)
- 唯一约束: `hospital_id` (每个医疗机构只有一个配置)

**索引**:
- `ix_ai_configs_id`
- `ix_ai_configs_hospital_id`

#### 2. classification_tasks（分类任务表）

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，CASCADE删除）
- `task_name`: 任务名称（VARCHAR(100)）
- `model_version_id`: 模型版本ID（外键，CASCADE删除）
- `charge_categories`: 收费类别列表（JSON）
- `status`: 任务状态（task_status枚举，默认pending）
- `total_items`: 总项目数（INTEGER，默认0）
- `processed_items`: 已处理项目数（INTEGER，默认0）
- `failed_items`: 失败项目数（INTEGER，默认0）
- `celery_task_id`: Celery任务ID（VARCHAR(255)）
- `error_message`: 错误信息（TEXT）
- `started_at`: 开始时间
- `completed_at`: 完成时间
- `created_by`: 创建人ID（外键）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**约束**:
- 主键: `id`
- 外键: 
  - `hospital_id` → `hospitals.id` (CASCADE)
  - `model_version_id` → `model_versions.id` (CASCADE)
  - `created_by` → `users.id`

**索引**:
- `ix_classification_tasks_id`
- `ix_classification_tasks_hospital_id`

#### 3. classification_plans（分类预案表）

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，CASCADE删除）
- `task_id`: 分类任务ID（外键，CASCADE删除）
- `plan_name`: 预案名称（VARCHAR(100)）
- `status`: 预案状态（plan_status枚举，默认draft）
- `submitted_at`: 提交时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

**约束**:
- 主键: `id`
- 外键:
  - `hospital_id` → `hospitals.id` (CASCADE)
  - `task_id` → `classification_tasks.id` (CASCADE)
- 唯一约束: `task_id` (每个任务只有一个预案)

**索引**:
- `ix_classification_plans_id`
- `ix_classification_plans_hospital_id`

#### 4. plan_items（预案项目表）

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，CASCADE删除）
- `plan_id`: 预案ID（外键，CASCADE删除）
- `charge_item_id`: 收费项目ID（外键，CASCADE删除）
- `charge_item_name`: 收费项目名称（VARCHAR(200)）
- `ai_suggested_dimension_id`: AI建议维度ID（外键，SET NULL）
- `ai_confidence`: AI确信度（NUMERIC(5,4)，范围0-1）
- `user_set_dimension_id`: 用户设置维度ID（外键，SET NULL）
- `is_adjusted`: 是否已调整（BOOLEAN，默认false）
- `processing_status`: 处理状态（processing_status枚举，默认pending）
- `error_message`: 错误信息（TEXT）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**约束**:
- 主键: `id`
- 外键:
  - `hospital_id` → `hospitals.id` (CASCADE)
  - `plan_id` → `classification_plans.id` (CASCADE)
  - `charge_item_id` → `charge_items.id` (CASCADE)
  - `ai_suggested_dimension_id` → `model_nodes.id` (SET NULL)
  - `user_set_dimension_id` → `model_nodes.id` (SET NULL)
- 唯一约束: (`plan_id`, `charge_item_id`) (同一预案中每个收费项目唯一)

**索引**:
- `ix_plan_items_id`
- `ix_plan_items_hospital_id`
- `ix_plan_items_plan_id`

#### 5. task_progress（任务进度记录表）

**字段**:
- `id`: 主键
- `task_id`: 分类任务ID（外键，CASCADE删除）
- `charge_item_id`: 收费项目ID（外键，CASCADE删除）
- `status`: 处理状态（progress_status枚举，默认pending）
- `error_message`: 错误信息（TEXT）
- `processed_at`: 处理时间
- `created_at`: 创建时间

**约束**:
- 主键: `id`
- 外键:
  - `task_id` → `classification_tasks.id` (CASCADE)
  - `charge_item_id` → `charge_items.id` (CASCADE)
- 唯一约束: (`task_id`, `charge_item_id`) (同一任务中每个项目只记录一次)

**索引**:
- `ix_task_progress_id`
- `ix_task_progress_task_id`

#### 6. api_usage_logs（API使用日志表）

**字段**:
- `id`: 主键
- `hospital_id`: 医疗机构ID（外键，CASCADE删除）
- `task_id`: 分类任务ID（外键，CASCADE删除）
- `charge_item_id`: 收费项目ID（外键，CASCADE删除）
- `request_data`: 请求数据（JSON）
- `response_data`: 响应数据（JSON）
- `status_code`: HTTP状态码（INTEGER）
- `error_message`: 错误信息（TEXT）
- `call_duration`: 调用耗时（FLOAT，秒）
- `created_at`: 创建时间

**约束**:
- 主键: `id`
- 外键:
  - `hospital_id` → `hospitals.id` (CASCADE)
  - `task_id` → `classification_tasks.id` (CASCADE)
  - `charge_item_id` → `charge_items.id` (CASCADE)

**索引**:
- `ix_api_usage_logs_id`
- `ix_api_usage_logs_hospital_id`
- `ix_api_usage_logs_task_id`
- `ix_api_usage_logs_created_at` (用于日期范围查询)

## 数据完整性

### 级联删除策略

1. **医疗机构删除** → 级联删除所有相关的AI配置、任务、预案、日志
2. **任务删除** → 级联删除相关的预案、进度记录、日志
3. **预案删除** → 级联删除所有预案项目
4. **维度删除** → 预案项目中的维度引用设为NULL（不影响历史记录）

### 唯一性约束

1. **AI配置**: 每个医疗机构只能有一个AI配置
2. **预案**: 每个任务只能有一个预案
3. **预案项目**: 同一预案中每个收费项目只能出现一次
4. **进度记录**: 同一任务中每个项目只记录一次

## 迁移执行

### 升级（upgrade）

```bash
alembic upgrade head
```

执行内容：
1. 创建4个枚举类型（使用DO块确保幂等性）
2. 创建6个数据表
3. 创建所有索引
4. 添加表注释

### 降级（downgrade）

```bash
alembic downgrade -1
```

执行内容：
1. 删除所有索引
2. 删除6个数据表（按依赖顺序逆序删除）
3. 删除4个枚举类型

## 性能优化

### 索引策略

1. **主键索引**: 所有表的id字段
2. **外键索引**: 所有外键字段（hospital_id, task_id, plan_id等）
3. **查询优化索引**: created_at（用于日志查询和统计）

### 查询优化建议

1. **多租户查询**: 始终包含hospital_id过滤
2. **任务查询**: 使用task_id索引
3. **日志统计**: 使用created_at索引进行日期范围查询
4. **预案项目**: 使用plan_id索引进行批量查询

## 数据类型说明

1. **JSON字段**: 使用PostgreSQL的JSON类型存储结构化数据
2. **NUMERIC(5,4)**: 用于存储确信度（0.0000-1.0000）
3. **FLOAT**: 用于存储延迟时间和调用耗时
4. **TEXT**: 用于存储长文本（提示词、错误信息等）
5. **ENUM**: 使用PostgreSQL枚举类型确保数据一致性

## 兼容性

- **PostgreSQL版本**: 9.6+（支持JSON和ENUM类型）
- **Alembic版本**: 1.7+
- **SQLAlchemy版本**: 1.4+

## 注意事项

1. **枚举类型**: 使用DO块创建，确保重复执行不会报错
2. **外键约束**: 所有外键都指定了ondelete行为
3. **默认值**: 使用server_default确保数据库层面的默认值
4. **时间戳**: 使用PostgreSQL的now()函数
5. **索引命名**: 遵循ix_{table}_{column}的命名规范

## 验证

迁移执行后，可以通过以下SQL验证：

```sql
-- 检查表是否创建
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE '%classification%' OR table_name LIKE 'ai_%';

-- 检查枚举类型
SELECT typname FROM pg_type 
WHERE typname IN ('task_status', 'plan_status', 'processing_status', 'progress_status');

-- 检查索引
SELECT indexname FROM pg_indexes 
WHERE tablename LIKE '%classification%' OR tablename LIKE 'ai_%';

-- 检查外键约束
SELECT conname, conrelid::regclass, confrelid::regclass 
FROM pg_constraint 
WHERE contype = 'f' 
AND conrelid::regclass::text LIKE '%classification%';
```

---

**迁移状态**: ✅ 已完成并测试
**创建时间**: 2025-11-26
**最后验证**: 2025-11-27
