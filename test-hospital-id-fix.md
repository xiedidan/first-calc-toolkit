# Hospital ID 参数修复验证

## 问题描述

执行标准计算流程时报错：
```
psycopg2.errors.SyntaxError: syntax error at or near "{"
LINE 35:     WHERE mv.hospital_id = {hospital_id}
```

## 问题原因

在 `backend/app/tasks/calculation_tasks.py` 的 `execute_calculation_step` 函数中，SQL 参数替换逻辑缺少了 `{hospital_id}` 的处理。

## 修复内容

### 1. 任务执行代码修复

在 `backend/app/tasks/calculation_tasks.py` 中添加了 `{hospital_id}` 参数的替换逻辑：

```python
# 科室相关参数
if department:
    # 指定了科室：使用具体科室的信息
    code = code.replace("{hospital_id}", str(department.hospital_id))  # ✅ 新增
    code = code.replace("{department_id}", str(department.id))
    # ... 其他参数
else:
    # 未指定科室：使用空值或特殊标记
    code = code.replace("{hospital_id}", "NULL")  # ✅ 新增
    code = code.replace("{department_id}", "NULL")
    # ... 其他参数
```

### 2. 测试功能修复

在 `backend/app/api/calculation_steps.py` 中添加了参数替换功能：

```python
def _replace_sql_parameters(code: str, test_params: Optional[dict] = None) -> str:
    """替换 SQL 中的参数占位符"""
    # 使用默认测试参数
    defaults = {
        "hospital_id": "1",
        "department_id": "1",
        "department_code": "TEST",
        "period": "2025-10",
        # ... 其他参数
    }
    
    # 替换所有参数
    for key, value in params.items():
        placeholder = "{" + key + "}"
        code = code.replace(placeholder, str(value))
    
    return code
```

现在测试功能会自动替换 SQL 中的所有参数占位符。

### 3. 文档更新

更新了 `SQL_PARAMETERS_GUIDE.md`，在参数列表中添加了 `{hospital_id}` 的说明：

| 参数 | 说明 | 示例值 | 批量模式值 | 用途 |
|------|------|--------|-----------|------|
| `{hospital_id}` | 医疗机构ID | `1` | `NULL` | 关联医疗机构表 |

### 4. 模板文件更新

更新了标准流程模板文件的注释：
- `backend/standard_workflow_templates/step1_dimension_catalog.sql`
- `backend/standard_workflow_templates/step2_indicator_calculation.sql`

明确说明 `{hospital_id}` 参数是从科室信息中获取的。

## 验证步骤

### 方法 1：使用测试功能（推荐）

1. **重启后端服务**（如果正在运行）
   ```bash
   # 停止 Celery worker
   # 重启 FastAPI 服务
   ```

2. **在步骤编辑页面测试**
   - 打开计算流程管理
   - 选择标准计算流程
   - 点击某个步骤的"编辑"
   - 点击"测试运行"按钮
   - 查看测试结果，确认 SQL 执行成功

3. **检查参数替换**
   - 测试功能会自动使用默认参数值
   - `{hospital_id}` 会被替换为 `1`
   - `{department_code}` 会被替换为 `TEST`
   - 等等...

### 方法 2：创建实际计算任务

1. **创建测试计算任务**
   - 选择一个科室
   - 选择标准计算流程
   - 选择计算周期（如 2025-10）
   - 提交任务

2. **检查执行结果**
   - 查看任务状态是否为"已完成"
   - 查看步骤日志，确认 SQL 执行成功
   - 检查 `{hospital_id}` 是否被正确替换为实际的医疗机构 ID

## 支持的参数列表

现在系统支持以下参数：

### 时间周期参数
- `{current_year_month}` / `{period}` - 计算周期
- `{year}` / `{month}` - 年份和月份
- `{start_date}` / `{end_date}` - 月份起止日期

### 科室相关参数
- `{hospital_id}` ✅ **新增** - 医疗机构ID
- `{department_id}` - 科室ID
- `{department_code}` - HIS科室代码
- `{department_name}` - HIS科室名称
- `{cost_center_code}` - 成本中心代码
- `{cost_center_name}` - 成本中心名称
- `{accounting_unit_code}` - 核算单元代码
- `{accounting_unit_name}` - 核算单元名称

### 任务相关参数
- `{task_id}` - 计算任务ID

## 注意事项

1. `{hospital_id}` 是数字类型，SQL 中不需要加引号
2. 在批量模式下（不选择科室），`{hospital_id}` 会被替换为 `NULL`
3. 如果需要在批量模式下使用 hospital_id，需要从其他地方获取（如系统配置）

## 额外修复：dimension_id 字段错误

在测试过程中发现了另一个问题：

### 问题
```
column dim.dimension_id does not exist
HINT: Perhaps you meant to reference the column "dim.dimension_code".
```

### 原因
`dimension_item_mappings` 表中存储的是 `dimension_code`（维度编码），而不是 `dimension_id`。

### 修复
修改了 `step1_dimension_catalog.sql` 中的关联逻辑：

```sql
-- 修复前（错误）
FROM dimension_item_mappings dim
INNER JOIN model_nodes mn ON dim.dimension_id = mn.id  -- ❌ dimension_id 不存在

-- 修复后（正确）
FROM dimension_item_mappings dim
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code  -- ✅ 使用 dimension_code 关联
```

同时添加了 `dim.hospital_id` 的过滤条件，确保只查询当前医疗机构的映射数据。

## 相关文件

- `backend/app/tasks/calculation_tasks.py` - 参数替换逻辑
- `backend/app/api/calculation_steps.py` - 测试功能参数替换
- `SQL_PARAMETERS_GUIDE.md` - 参数使用指南
- `backend/standard_workflow_templates/step1_dimension_catalog.sql` - 步骤1 SQL（已修复）


## 测试环境准备

### 问题：外部数据表不存在

如果测试时遇到 `relation "charge_details" does not exist` 错误，说明外部数据源中缺少所需的表。

### 解决方案

#### 方案 1：创建测试表（推荐）

使用提供的测试表创建脚本：

```bash
# 1. 连接到外部数据源数据库（配置在数据源管理中的数据库）
psql -h <host> -p <port> -U <user> -d <database>

# 2. 执行测试表创建脚本
\i backend/standard_workflow_templates/create_test_tables.sql

# 或者直接执行
psql -h <host> -p <port> -U <user> -d <database> -f backend/standard_workflow_templates/create_test_tables.sql
```

脚本会创建：
- `charge_details` 表（收费明细）
- `workload_statistics` 表（工作量统计）
- 并插入一些测试数据

#### 方案 2：修改 SQL 使用实际表名

如果你的数据库中有类似的表但名称不同，可以修改 SQL 文件：

1. 编辑 `backend/standard_workflow_templates/step1_dimension_catalog.sql`
2. 将 `charge_details` 替换为实际的表名（如 `dwd_sfmxb`）
3. 调整字段名以匹配实际表结构
4. 重新导入流程或更新步骤

#### 方案 3：只测试步骤 3

步骤 3（业务价值汇总）不依赖外部数据源，只使用系统内部表：

1. 在流程管理中禁用步骤 1 和步骤 2
2. 只启用步骤 3
3. 手动在 `calculation_results` 表中插入一些测试数据
4. 运行计算任务测试步骤 3

### 测试数据说明

`create_test_tables.sql` 包含的测试数据：

**科室数据**：
- 内科 (NK)：3个患者，5条收费记录
- 外科 (WK)：2个患者，4条收费记录
- 儿科 (EK)：2个患者，3条收费记录

**收费项目**：
- ITEM001：血常规（25元）
- ITEM002：尿常规（15元）
- ITEM003：CT检查（300元）
- ITEM004：心电图（50元）
- ITEM005：手术费（5000元）
- ITEM006：麻醉费（800元）
- ITEM007：疫苗接种（120元）

**工作量数据**：
- 护理床日数（一级、二级、三级、特级）
- 会诊工作量（发起、参与）

### 验证测试数据

创建测试表后，可以验证数据是否正确：

```sql
-- 查看收费明细汇总
SELECT 
    prescribing_dept_code,
    COUNT(*) as record_count,
    COUNT(DISTINCT patient_id) as patient_count,
    SUM(amount) as total_amount
FROM charge_details
WHERE charge_time >= '2025-10-01' AND charge_time < '2025-11-01'
GROUP BY prescribing_dept_code;

-- 查看工作量统计
SELECT 
    department_code,
    stat_type,
    SUM(stat_value) as total_value
FROM workload_statistics
WHERE stat_month = '2025-10'
GROUP BY department_code, stat_type;
```
