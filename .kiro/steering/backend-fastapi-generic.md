# FastAPI + SQLAlchemy 通用规范

## 路由规范

- 禁止重复定义相同路由
- **具体路径必须在通配路径之前**（如 `/clear-all` 在 `/{id}` 前）
- FastAPI 按定义顺序匹配，`/{id}` 会匹配所有路径
- 422 错误通常是路径参数类型验证失败

### API路径结构
- 路由注册时使用prefix：`app.include_router(router, prefix="/api/v1/xxx")`
- 完整路径：`BASE_URL/api/v1/{prefix}/{endpoint}`
- 测试时确认完整路径，避免404错误

## 模型关系

### 双向关系配置
添加新模型时必须同时配置双向关系（`relationship` + `back_populates`）

### 模型导入顺序
在 `models/__init__.py` 中按依赖顺序导入，避免循环依赖

## 文件路径处理

- 跨平台兼容：数据库存储使用 `/`，文件操作使用 `Path` 对象
- Windows 避免使用 `Path.relative_to(Path.cwd())`，改用字符串拼接

## 文件导出

### 中文文件名
HTTP 头使用 URL 编码：`filename*=UTF-8''{quote(filename)}`

### Excel (openpyxl)
- 列宽单位：字符数（中文约占2个字符）
- 数字格式：`'#,##0.00'`（千分位）、`'0.00%'`（百分比）
- Decimal 类型必须转换为 float 或 str

### ZIP 打包
使用 `zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)`

### StreamingResponse
- Excel: `media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"`
- ZIP: `media_type="application/zip"`
- PDF: `media_type="application/pdf"`

### PDF生成 (ReportLab)
- **字体选择**：Windows使用`C:/Windows/Fonts/simsun.ttc`（宋体），Linux需安装中文字体包
- **避免WeasyPrint**：Windows上需GTK等外部依赖，优先使用纯Python的ReportLab
- **表格自动换行**：单元格内容必须包装为Paragraph对象才能自动换行，直接使用字符串不会换行
- **表格宽度控制**：计算可用宽度（页面宽度-边距），根据列数平均分配列宽
- **HTML转义**：单元格内容需转义HTML特殊字符（`<`、`>`、`&`），避免解析错误
- **换行符处理**：将`<br>`标签转为`\n`，转义后再转为`<br/>`（自闭合标签）
- **Markdown表格**：解析Markdown表格语法，跳过分隔符行，用Table组件渲染

## JOIN 查询

### 避免笛卡尔积
JOIN 多版本表时必须限定版本，使用 `DISTINCT` 或明确关联条件

## 错误处理

- 404: 不存在 | 403: 无权限 | 400: 参数错误 | 500: 服务器错误
- 错误信息明确具体

### 全局异常处理器
- 添加 `RequestValidationError` 处理器捕获请求验证错误
- 添加 `ValidationError` 处理器捕获 Pydantic 验证错误
- 添加通用 `Exception` 处理器捕获所有未处理异常
- 返回详细错误信息：错误类型、位置、消息、堆栈跟踪
- 生产环境可选择性隐藏堆栈信息

### 调试日志
- 在关键 API 端点添加详细日志（请求参数、执行结果）
- 使用 `logging` 模块而非 `print()`
- 日志级别：DEBUG（开发）、INFO（生产）
- uvicorn 启动时添加 `--log-level debug` 启用详细日志

## API 响应规范

### 字段命名一致性
- Schema 字段名必须与前端类型定义一致
- 避免后端使用复数前端期望单数（或反之）
- 简化响应结构时需同步更新前端类型定义
- 注意区分：`id`（数据库主键）vs `task_id`（业务UUID）

### 关联字段预加载
- 列表API应预加载常用关联字段（如外键对应的名称）
- 避免前端通过ID查找或额外API调用
- 在循环中为每个对象设置预加载字段

### 多租户上下文
- 使用 `X-Hospital-ID` 请求头传递当前医疗机构
- 中间件自动提取并存储到ContextVar
- API通过 `get_current_hospital_id()` 获取
- 测试脚本必须在请求头中包含此字段

## 关联查询与筛选

### 层级关系查询
- 查询子资源时，应包含所有符合父资源条件的子资源
- 使用 `sa.or_` 组合多个筛选条件，避免遗漏关联数据
- 示例：查询版本的任务时，包括该版本所有流程的任务和直接关联该版本的任务

## 分页参数

设置合理上限防止恶意请求：`size: int = Query(10, ge=1, le=1000)`

## 文件上传

### 文件名解析
支持中英文括号，先去除扩展名：`Path(filename).stem`

### 批量上传预览
前后端使用相同正则表达式，标记状态：matched/partial/unmatched

## 会话数据管理

### 内存会话的局限性
- 类变量存储会话数据在服务重启后丢失
- 多实例部署时会话数据不共享
- 生产环境使用 Redis 或数据库存储会话

### 避免会话依赖
- 关键操作（如导入执行）应接收完整数据，不依赖会话
- 前端传递必要的上下文数据（如预览结果）
- 会话仅用于临时存储（如文件上传、多步骤向导）

## 数据类型兼容性

### Pydantic 模型与字典互操作
- 创建辅助函数统一处理：`hasattr()` 检测模型，`isinstance()` 检测字典
- 使用 `getattr(obj, field, default)` 访问模型属性
- 使用 `dict.get(field, default)` 访问字典值
- 避免假设数据类型，始终做兼容性处理

### list.index() 错误处理
- `list.index(value)` 在值不存在时抛出 `ValueError`
- 使用 try-except 捕获并提供详细错误信息
- 错误信息应包含：查找的值、可用值列表
- 或使用 `value in list` 先检查再调用 `index()`

## 树形数据 API

### Schema 一致性
- 叶子节点不含 `children` 字段
- 父节点含 `children` 数组
- 使用 `Optional[List[Model]]` 定义可选子节点

### 查询逻辑与数据依赖
- 递归查询依赖 `parent_id` 关系链完整
- 查询前验证：根节点存在且 `parent_id` 指向正确
- 若查询结果为空，检查数据表是否包含所有层级节点
- 常见问题：只插入叶子节点，缺少中间层级导致递归中断

## Alembic 迁移

### 创建前检查
`grep "^revision = " alembic/versions/*.py | tail -5`

### down_revision 引用
- 必须引用实际存在的 revision ID
- 避免多个 head，形成链式结构
- 命名：`YYYYMMDD_feature_name`

### 幂等性迁移
修改约束/索引时检查是否已存在，避免重复执行失败

### PostgreSQL 枚举类型
创建枚举类型时使用 DO 块处理重复：
```sql
DO $ BEGIN
    CREATE TYPE enumname AS ENUM ('value1', 'value2');
EXCEPTION
    WHEN duplicate_object THEN null;
END $;
```

### 外键约束幂等性
使用 DO 块检查约束是否存在：
```sql
DO $ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_name') THEN
        ALTER TABLE table_name ADD CONSTRAINT fk_name FOREIGN KEY ...;
    END IF;
END $;
```

## 数据库部署

### 表导入顺序
先导入被依赖的表，后导入依赖其他表的表

### 序列重置
导入数据后必须重置自增序列：`SELECT setval('table_id_seq', (SELECT MAX(id) FROM table))`

### 外键约束
- `ON DELETE CASCADE`: 级联删除
- `ON DELETE SET NULL`: 设为空（需字段允许 NULL）

## SQL 执行与事务管理

### 多语句执行
- 按分号分割SQL时，过滤空语句和纯注释块
- 避免多行注释 `/* */`，统一使用单行注释 `--`
- 逐个执行语句，累计影响行数
- **关键**：无论最后是SELECT还是INSERT，都必须显式 `commit()`

### 直接SQL插入
- Python模型的 `default=datetime.now` 不会在SQL INSERT时生效
- 必须在SQL中显式指定：`created_at = NOW()`
- 确保所有必填字段都在INSERT语句中

### 测试数据隔离
- 测试功能生成唯一task_id：`test-task-{timestamp}-{uuid}`
- 避免测试数据相互覆盖
- 便于批量清理：`WHERE task_id LIKE 'test-task-%'`

## Celery 异步任务

### 模块导入完整性
- 任务模块必须导入所有使用的模型类
- 检查 `NameError: name 'XXX' is not defined` 错误
- 任务函数中使用的所有类都需要在文件顶部导入

### 参数传递与占位符替换
- 批量处理模式下，必须从上下文获取必需参数（如 `hospital_id`）
- 占位符替换时使用实际数值，避免字符串 `"NULL"`
- 可选参数为 `None` 时，从关联对象获取必需值
- **关键**：确保所有SQL模板中使用的占位符都有对应的替换逻辑
- 常见占位符：`{task_id}`, `{version_id}`, `{period}`, `{year_month}`, `{hospital_id}`
- 占位符未替换会导致SQL查询失败（字面值匹配）

### 任务调用方式
- 使用 `.delay()` 或 `.apply_async()` 异步执行任务
- 禁止直接调用任务函数（缺少 `self` 参数会导致错误）
- 测试时使用 `.delay()` 并轮询任务状态

### 调试日志
- 关键步骤添加 `print()` 日志（Celery worker会输出）
- 包含任务ID、参数、执行进度等信息
- 异常捕获后打印完整堆栈：`traceback.print_exc()`
- SQL执行前打印模板片段和关键特征，便于验证版本正确性

### 事务管理
- 每个步骤执行后显式 `commit()`
- 失败时先 `rollback()` 再更新状态
- 避免在 `finally` 中直接 `commit()`

## SQL 模板与数据完整性

### INSERT 语句字段完整性
- 确保 INSERT 包含所有业务必需字段
- 特别注意关系字段：`parent_id`、`code`、外键等
- GROUP BY 必须包含 SELECT 中的所有非聚合字段

### 树形数据插入
- 必须包含 `parent_id` 用于构建层级关系
- 必须包含 `node_code` 用于数据追溯
- 从关联表（如 `model_nodes`）获取这些字段

### 分步插入树形数据
- 叶子节点和非叶子节点可分步插入
- 汇总步骤需补充所有中间层级节点，确保树形结构完整
- 使用 `NOT IN (SELECT node_id FROM existing_table)` 避免重复插入
- 验证方法：检查根节点能否通过 `parent_id` 递归到所有叶子节点

### 占比字段处理
- 占比（ratio）通常在API层动态计算，不在SQL中
- 如需在SQL中计算，确保除数不为零

## Docker 部署

- 依赖安装：扩展包必须显式声明（如 `pydantic[email]`）
- 启动命令：使用 `python -m uvicorn` 避免 PATH 问题
- Alembic 配置：从环境变量读取 `DATABASE_URL`

## Windows + Conda 环境

### PowerShell 初始化
- 执行命令前先初始化 conda hook：`& 'path\to\conda-hook.ps1'`
- 然后激活环境：`conda activate env-name`
- 初始化后 conda 命令在当前 session 持续可用

### 批处理脚本
- 使用 `powershell.exe -ExecutionPolicy ByPass -NoExit -Command` 启动
- 在命令中先执行 hook 再激活环境
- 路径使用绝对路径避免查找失败

## PostgreSQL 客户端 (psql)

### 命令执行
- 禁用分页器：`-P pager=off` 避免命令阻塞
- 使用 `-c "SQL"` 执行单条语句
- 使用 `\d table_name` 查看表结构
- 未在 PATH 时使用绝对路径调用

### 密码认证
- 使用环境变量 `PGPASSWORD` 避免交互式密码输入
- PowerShell: `$env:PGPASSWORD='password'; psql ...`
- Python 脚本优先：复杂操作使用 SQLAlchemy，避免 psql 编码和认证问题

### 编码问题处理
- Windows psql 执行包含中文的SQL文件时可能出现编码错误
- 解决方案：使用Python脚本通过SQLAlchemy执行，避免编码问题
- 或使用 `-c` 参数直接执行SQL命令（适用于简单SQL）

## PostgreSQL 递归CTE

### 类型一致性要求
- 递归CTE中所有列的类型必须在递归和非递归部分保持一致
- 字符串拼接导致长度变化时，非递归部分需显式类型转换
- 使用 `CAST(column AS TEXT)` 或 `column::TEXT` 转换为可变长度类型
- 错误示例：`VARCHAR(100)` 拼接后变为 `VARCHAR` 导致类型不匹配

### 路径构建模式
- 从根节点向下递归时，使用字符串拼接构建完整路径
- 路径分隔符统一使用 `/`，便于后续 LIKE 匹配
- 初始路径使用 `CAST(root_name AS TEXT)` 确保类型正确

## PostgreSQL 表名大小写

### 引号使用规则
- 表名包含大写字母或特殊字符时必须使用双引号：`"TB_MZ_SFMXB"`
- 列名同理：`"KDKSBM"`、`"MXXMSSJE"`
- 不加引号时PostgreSQL自动转为小写
- 建议：源表保持原始命名（带引号），内部表使用小写（不带引号）
