# SQL 计算步骤参数使用指南

在计算步骤的 SQL 代码中，可以使用以下占位符参数。系统会在执行时自动替换为实际值。

## 📅 时间周期参数

| 参数 | 说明 | 示例值 | 用途 |
|------|------|--------|------|
| `{current_year_month}` | 当前计算周期（年-月） | `2025-10` | 主要的周期参数 |
| `{period}` | 同 `{current_year_month}` | `2025-10` | 别名，更简短 |
| `{year}` | 年份 | `2025` | 单独使用年份 |
| `{month}` | 月份（两位数） | `10` | 单独使用月份 |
| `{start_date}` | 月份第一天 | `2025-10-01` | 日期范围查询 |
| `{end_date}` | 月份最后一天 | `2025-10-31` | 日期范围查询 |

## 🏥 科室相关参数

| 参数 | 说明 | 示例值 | 批量模式值 | 用途 |
|------|------|--------|-----------|------|
| `{department_id}` | 科室ID（系统内部） | `123` | `NULL` | 关联系统内部表 |
| `{department_code}` | HIS科室代码 | `NK` | `""` (空字符串) | 关联HIS业务表 |
| `{department_name}` | HIS科室名称 | `内科` | `""` (空字符串) | 显示或过滤 |
| `{cost_center_code}` | 成本中心代码 | `CC001` | `""` (空字符串) | 成本核算 |
| `{cost_center_name}` | 成本中心名称 | `内科成本中心` | `""` (空字符串) | 成本核算 |
| `{accounting_unit_code}` | 核算单元代码 | `AU001` | `""` (空字符串) | 财务核算 |
| `{accounting_unit_name}` | 核算单元名称 | `内科核算单元` | `""` (空字符串) | 财务核算 |

> **批量模式说明**：当创建计算任务时不选择科室时，系统进入批量模式，流程只执行一次，科室相关参数会被替换为空值或 NULL。

## 🔧 任务相关参数

| 参数 | 说明 | 示例值 | 用途 |
|------|------|--------|------|
| `{task_id}` | 当前计算任务ID | `abc123...` | 关联任务结果 |

---

## 🔄 执行模式

系统支持两种执行模式：

### 1. 单科室模式（循环执行）
- **触发条件**：创建计算任务时选择了一个或多个科室
- **执行方式**：对每个科室循环执行一次完整的计算流程
- **参数值**：科室参数使用具体科室的实际值
- **进度显示**：按科室数量显示进度（如 3/10）
- **适用场景**：需要针对每个科室单独处理的计算

### 2. 批量模式（单次执行）
- **触发条件**：创建计算任务时不选择科室（留空）
- **执行方式**：整个流程只执行一次
- **参数值**：科室参数为空值或 NULL
- **进度显示**：0% → 100%（一次性完成）
- **适用场景**：SQL 自己处理所有科室的批量计算

---

## 📝 使用示例

### 示例 1：查询科室门诊量

```sql
SELECT 
    COUNT(*) as visit_count,
    SUM(total_fee) as total_revenue
FROM outpatient_visits
WHERE department_code = '{department_code}'
  AND visit_date >= '{start_date}'
  AND visit_date <= '{end_date}'
```

**执行时替换为：**
```sql
SELECT 
    COUNT(*) as visit_count,
    SUM(total_fee) as total_revenue
FROM outpatient_visits
WHERE department_code = 'NK'
  AND visit_date >= '2025-10-01'
  AND visit_date <= '2025-10-31'
```

### 示例 2：查询科室住院手术量

```sql
SELECT 
    COUNT(DISTINCT operation_id) as operation_count,
    SUM(operation_fee) as operation_revenue
FROM inpatient_operations
WHERE dept_code = '{department_code}'
  AND operation_date BETWEEN '{start_date}' AND '{end_date}'
  AND status = 'completed'
```

### 示例 3：按年月统计

```sql
SELECT 
    '{period}' as period,
    department_code,
    COUNT(*) as patient_count
FROM patient_records
WHERE department_code = '{department_code}'
  AND EXTRACT(YEAR FROM record_date) = {year}
  AND EXTRACT(MONTH FROM record_date) = {month}
GROUP BY department_code
```

### 示例 4：插入计算结果到中间表

```sql
INSERT INTO calculation_temp_results (
    task_id,
    department_id,
    period,
    metric_name,
    metric_value,
    created_at
)
SELECT 
    '{task_id}',
    {department_id},
    '{period}',
    'bed_days',
    SUM(bed_days),
    NOW()
FROM inpatient_records
WHERE department_code = '{department_code}'
  AND admission_date >= '{start_date}'
  AND discharge_date <= '{end_date}'
```

### 示例 5：使用成本中心代码

```sql
SELECT 
    SUM(cost_amount) as total_cost
FROM cost_allocation
WHERE cost_center_code = '{cost_center_code}'
  AND cost_month = '{current_year_month}'
```

### 示例 6：批量模式 - 一次性处理所有科室

```sql
-- 批量插入所有科室的计算结果
INSERT INTO calculation_results (
    task_id,
    department_id,
    period,
    metric_name,
    metric_value,
    created_at
)
SELECT 
    '{task_id}',
    d.id,
    '{period}',
    'outpatient_visits',
    COUNT(*),
    NOW()
FROM outpatient_visits ov
JOIN departments d ON d.his_code = ov.department_code
WHERE ov.visit_date >= '{start_date}'
  AND ov.visit_date <= '{end_date}'
  AND d.is_active = TRUE
GROUP BY d.id;
```

### 示例 7：兼容两种模式的 SQL

```sql
-- 使用条件判断，同时支持单科室和批量模式
INSERT INTO calculation_results (
    task_id,
    department_id,
    period,
    metric_value
)
SELECT 
    '{task_id}',
    d.id,
    '{period}',
    SUM(amount)
FROM business_data bd
JOIN departments d ON d.his_code = bd.dept_code
WHERE bd.data_date >= '{start_date}'
  AND bd.data_date <= '{end_date}'
  AND d.is_active = TRUE
  -- 如果指定了科室，只处理该科室；否则处理所有科室
  AND ('{department_code}' = '' OR d.his_code = '{department_code}')
GROUP BY d.id;
```

---

## ⚠️ 注意事项

1. **参数大小写敏感**：必须使用花括号 `{}` 包裹，且参数名称区分大小写
   - ✅ 正确：`{department_code}`
   - ❌ 错误：`{Department_Code}` 或 `{DEPARTMENT_CODE}`

2. **字符串类型参数**：大部分参数替换后是字符串，SQL 中需要加引号
   - ✅ 正确：`WHERE dept_code = '{department_code}'`
   - ❌ 错误：`WHERE dept_code = {department_code}`

3. **数字类型参数**：以下参数是数字，不需要引号
   - `{department_id}`
   - `{year}`
   - `{month}`

4. **可能为空的参数**：以下参数可能为空字符串，使用前请检查
   - `{cost_center_code}`
   - `{cost_center_name}`
   - `{accounting_unit_code}`
   - `{accounting_unit_name}`
   - 批量模式下，所有科室相关参数都为空

5. **批量模式判断**：可以通过检查 `{department_code}` 是否为空来判断执行模式
   ```sql
   -- 判断是否为批量模式
   WHERE ('{department_code}' = '' OR dept_code = '{department_code}')
   ```

5. **日期格式**：
   - `{start_date}` 和 `{end_date}` 格式为 `YYYY-MM-DD`
   - `{period}` 和 `{current_year_month}` 格式为 `YYYY-MM`

6. **测试建议**：
   - 在计算步骤编辑页面使用"测试运行"功能验证 SQL
   - 测试时会使用实际的参数值进行替换

---

## 🔍 调试技巧

如果 SQL 执行出错，可以：

1. **查看步骤日志**：在 `calculation_step_logs` 表中查看执行记录
2. **使用测试功能**：在步骤编辑页面点击"测试运行"
3. **检查参数值**：确认科室数据中相关字段是否有值
4. **简化 SQL**：先用简单的 SQL 测试参数替换是否正确

```sql
-- 测试参数替换
SELECT 
    '{department_code}' as dept_code,
    '{department_name}' as dept_name,
    '{period}' as period,
    '{start_date}' as start_date,
    '{end_date}' as end_date
```

---

## 📚 相关文档

- [计算流程管理文档](REPORT_FEATURE_IMPLEMENTATION.md)
- [数据源配置指南](需求文档.md#312-sql数据源配置)
- [计算任务执行流程](需求文档.md#45-计算流程管理)
