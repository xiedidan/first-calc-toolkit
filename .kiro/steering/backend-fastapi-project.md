# 项目后端规范

## 多租户隔离

### 唯一约束设计
多租户表的唯一字段必须包含 `hospital_id`：`UNIQUE(hospital_id, version)`

### 基本原则
所有带 `hospital_id` 字段的模型必须在 API 层强制隔离：
- 查询时过滤：`query.filter(Model.hospital_id == hospital_id)`
- 创建时设置：`Model(hospital_id=hospital_id, ...)`
- JOIN 时也要隔离关联表

### 检查清单
1. 所有 `query.filter()` 是否包含 `hospital_id`
2. 所有 `JOIN` 是否在关联表上也过滤 `hospital_id`
3. 创建操作是否设置 `hospital_id`
4. 更新/删除是否验证所属医院
5. 服务层方法是否接收并使用 `hospital_id` 参数
6. 会话数据中的查询是否按 `hospital_id` 过滤

### 服务层隔离
- 服务类方法必须接收 `hospital_id` 参数
- 所有数据库查询都添加 `hospital_id` 过滤
- 避免在服务层使用全局查询（如 `Model.query.all()`）
- API 层通过 `get_current_hospital_id_or_raise()` 获取并传递

## 批量操作路由

- 单个资源清空：`DELETE /{resource}/{id}/clear-all`
- 全部资源清空：`DELETE /{resource}/clear-all`
- 条件清空：`DELETE /{resource}/orphans/clear-all`

## 时区处理

- 数据库：UTC（`datetime.utcnow()`）
- API 响应：UTC（前端转换）
- 导出文件：UTC+8

## SQL 参数替换

必须在两处替换：任务执行 + 测试功能

## PostgreSQL 语法

- 注释：单独的 `COMMENT ON COLUMN table.col IS '注释'`
- 递归 CTE：递归部分不能用聚合函数，先递归再聚合

## 测试数据生成

### 数据生成策略
- 使用系统实际配置（科室、收费项目、映射）
- 80% 使用映射数据，20% 随机
- 提供调试 SQL 逐步检查关联

### 源表数据生成
- 生成到TB_MZ_SFMXB和TB_ZY_SFMXB而非直接生成charge_details
- 门诊/住院比例：70%/30%
- 字段映射：MXXMSSJE（实收金额）→ amount，KDKSBM → prescribing_dept_code
- 每次生成前清空指定周期的旧数据（按FYFSSJ过滤）

## 字段命名

- 检查模型定义与 SQL 字段名一致性
- 字符串字段存储数字需类型转换：`float(item.unit_price) if item.unit_price else 0`

## 数据库部署

### 表导入顺序
明确定义 `TABLE_IMPORT_ORDER`，按外键依赖层级排序

### 初始化脚本
- 检查数据是否已存在
- 使用 `ON CONFLICT DO NOTHING` 或先查询再插入

## 计算流程设计

### 数据流架构
- **源表层**：TB_MZ_SFMXB（门诊）、TB_ZY_SFMXB（住院）- HIS系统原始数据
- **统一层**：charge_details - 由Step 1从源表转换生成
- **计算层**：calculation_results - 存储计算结果
- 数据流向：源表 → 统一表 → 计算结果

### 数据表职责
- `calculation_results`: 存储所有节点数据（叶子+非叶子，维度+序列）
- `calculation_summaries`: 已废弃，不再使用

### 步骤间数据传递
- Step 1: 数据准备 - 从源表生成统一的charge_details表
- Step 2: 维度统计 - 从charge_details统计维度工作量，设置`original_weight = weight`
- Step 3: 导向调整 - 更新`weight`字段，保持`original_weight`不变
- Step 4: 指标计算 - 从其他统计表计算指标
- Step 5: 价值汇总 - **必须使用`calculation_results.weight`（调整后）而非`model_nodes.weight`（原始）**
- 避免使用临时表，直接写入持久化表
- 每个步骤的SQL末尾返回插入记录数用于验证

### 权重字段使用规则
- `model_nodes.weight`: 全院业务价值（原始，不变）
- `calculation_results.weight`: 科室业务价值（可被Step 3调整）
- `calculation_results.original_weight`: 保存原始值，用于对比
- **汇总步骤必须从`calculation_results`读取`weight`，确保使用调整后的值**
- 非叶子节点的`original_weight`应为NULL（值是汇总来的）

### 树形结构完整性
- **关键原则**: 报表查询依赖完整的树形结构，必须插入所有层级节点
- Step 1/2 插入叶子节点后，Step 3 必须补充所有祖先节点（中间维度+序列）
- 所有节点的 `parent_id` 必须正确指向父节点，形成连续的层级关系
- 检查方法：从序列节点开始，通过 `parent_id` 应能递归找到所有子孙节点

### 数据源配置
- 数据源表无 `hospital_id`，为全局共享资源
- 导入脚本支持 `--data-source-id` 参数自动关联
- 步骤必须指定 `data_source_id`，否则无法执行

### API响应字段加载
- 列表API需手动加载关联对象的显示字段
- 如 `task.workflow_name = task.workflow.name`
- Schema需包含对应字段定义
- 预加载字段可避免前端N+1查询和额外API调用

### SQL模板字段要求
- `calculation_results` 表INSERT必须包含：
  - `node_code` - 从 `model_nodes.code` 获取
  - `parent_id` - 从 `model_nodes.parent_id` 获取（保持模型结构）
  - `node_type` - 'dimension' 或 'sequence'
  - 其他业务字段：`workload`、`weight`、`value`
- GROUP BY 必须包含所有非聚合字段（包括 `parent_id`）
- 测试功能和实际执行使用相同的参数替换逻辑

### Celery任务执行
- 任务函数必须导入 `ModelVersion` 等所有使用的模型
- 批量模式下从 `ModelVersion` 获取 `hospital_id`
- 参数替换时使用实际数值，不使用字符串 `"NULL"`
- 添加详细日志便于问题诊断

### API测试与验证
- 测试计算流程时使用实际存在的数据月份
- 通过API创建任务而非直接调用函数
- 验证工作流ID与版本ID的对应关系
- 检查结果记录数和节点类型分布

## 离线部署

### 数据库备份恢复策略
- **优先使用 SQL 格式**：`pg_dump` 导出纯 SQL 文件，避免版本兼容性问题
- **压缩**：使用 gzip 压缩 SQL 文件
- **恢复**：使用 `psql` 而非 `pg_restore`，兼容所有版本
- **不依赖迁移**：完整备份优于 Alembic 迁移，避免多 heads 冲突

### PostgreSQL 工具配置
- 本地无工具时，优先使用运行中的 PostgreSQL 容器
- 可通过环境变量指定容器：`PG_DOCKER_CONTAINER`
- 离线环境禁止自动 pull 镜像，只使用本地资源
- 提供清晰的手动操作指南作为兜底方案

### 数据导入
- 按依赖顺序导入表
- 跳过已存在记录
- 导入完成后自动重置所有序列
- 提供独立序列修复脚本

### 常见错误
- `duplicate key violates constraint`: 序列未重置
- `column does not exist`: 迁移未完整执行
- `cannot open uvicorn`: 使用 `python -m` 方式启动
- `localhost connection refused`: Alembic 未读取环境变量
- `unsupported version in file header`: pg_restore 版本过低，改用 SQL 格式

## 开发环境配置

### Conda 环境
- 安装路径：`C:\software\anaconda3`
- Hook 脚本：`C:\software\anaconda3\shell\condabin\conda-hook.ps1`
- 环境名称：`hospital-backend`
- Python 版本：3.12

### PowerShell 使用
- 初始化：`& 'C:\software\anaconda3\shell\condabin\conda-hook.ps1'`
- 激活环境：`conda activate hospital-backend`
- 初始化后可持续使用 conda 和 python 命令

### 数据库链接
- backend/.env中的DATABASE_URL

### PostgreSQL 客户端
- 连接命令：`$env:PGPASSWORD='ssPgSql123'; & "C:\software\PostgreSQL\18\bin\psql.exe" -h 47.108.227.254 -p 50016 -U postgres -d hospital_value -P pager=off`

## 业务逻辑与数据结构设计

### 通过层级结构判断业务属性
- 避免在映射表中添加冗余字段，优先通过层级关系推导
- 使用递归CTE构建完整路径，通过路径模式匹配判断业务属性
- 路径匹配使用 LIKE 模式，支持灵活的层级结构
- 示例：通过"序列/一级维度/二级维度"路径判断业务类别

### 条件筛选的灵活性
- 支持"不区分"场景：条件为 NULL 时匹配所有值
- JOIN 条件使用 `(condition IS NULL OR condition = value)` 模式
- 确保不同业务场景下的数据正确隔离或合并

## 数据迁移最佳实践

### 字段添加流程
1. 使用 `ALTER TABLE ADD COLUMN IF NOT EXISTS` 确保幂等性
2. 创建索引提高查询性能
3. 添加字段注释说明用途
4. 更新历史数据（根据业务规则）
5. 验证数据完整性和分布

### 历史数据更新策略
- 优先使用业务规则（如就诊类型）判断
- 次选使用数据特征（如项目名称、科室类型）推断
- 测试环境可使用随机分配，生产环境需人工确认
- 分批执行避免长时间锁表

### 更新SQL代码到数据库
- 避免使用 psql 执行包含中文的SQL文件（编码问题）
- 使用Python脚本通过SQLAlchemy更新，支持UTF-8编码
- 更新前验证目标记录存在（检查workflow_id和step_id）
- 更新后验证SQL长度和内容正确性

### 工作流导入脚本
- 使用bash脚本导入标准工作流（import_standard_workflow.sh）
- 必需参数：`--version-id`，可选：`--data-source-id`、`--workflow-name`
- 步骤编号从1开始，使用sort_order控制执行顺序（1.00, 2.00, 3.00...）
- 导入前验证：版本存在、数据源存在且启用
- 所有步骤自动关联指定的data_source_id
