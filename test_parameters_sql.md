# 计算步骤参数测试 SQL

这是一套完整的测试 SQL，用于验证计算步骤中的参数替换功能。

---

## 步骤 1：创建测试表

**步骤名称：** 01-创建测试表  
**代码类型：** SQL  
**排序：** 1.00

```sql
-- 创建参数测试表
CREATE TABLE IF NOT EXISTS test_calculation_params (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100),
    department_id INTEGER,
    department_code VARCHAR(50),
    department_name VARCHAR(100),
    cost_center_code VARCHAR(50),
    cost_center_name VARCHAR(100),
    accounting_unit_code VARCHAR(50),
    accounting_unit_name VARCHAR(100),
    period VARCHAR(20),
    year VARCHAR(4),
    month VARCHAR(2),
    start_date DATE,
    end_date DATE,
    test_time TIMESTAMP DEFAULT NOW(),
    CONSTRAINT test_calc_params_unique UNIQUE (task_id, department_id)
);

-- 添加注释
COMMENT ON TABLE test_calculation_params IS '计算参数测试表';
COMMENT ON COLUMN test_calculation_params.task_id IS '任务ID';
COMMENT ON COLUMN test_calculation_params.department_id IS '科室ID';
COMMENT ON COLUMN test_calculation_params.period IS '计算周期';
```

---

## 步骤 2：插入参数测试数据

**步骤名称：** 02-插入参数数据  
**代码类型：** SQL  
**排序：** 2.00

```sql
-- 插入当前任务的参数值
INSERT INTO test_calculation_params (
    task_id,
    department_id,
    department_code,
    department_name,
    cost_center_code,
    cost_center_name,
    accounting_unit_code,
    accounting_unit_name,
    period,
    year,
    month,
    start_date,
    end_date
) VALUES (
    '{task_id}',
    {department_id},
    '{department_code}',
    '{department_name}',
    '{cost_center_code}',
    '{cost_center_name}',
    '{accounting_unit_code}',
    '{accounting_unit_name}',
    '{period}',
    '{year}',
    '{month}',
    '{start_date}'::DATE,
    '{end_date}'::DATE
)
ON CONFLICT (task_id, department_id) 
DO UPDATE SET
    department_code = EXCLUDED.department_code,
    department_name = EXCLUDED.department_name,
    cost_center_code = EXCLUDED.cost_center_code,
    cost_center_name = EXCLUDED.cost_center_name,
    accounting_unit_code = EXCLUDED.accounting_unit_code,
    accounting_unit_name = EXCLUDED.accounting_unit_name,
    period = EXCLUDED.period,
    year = EXCLUDED.year,
    month = EXCLUDED.month,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    test_time = NOW();
```

---

## 步骤 3：查询参数验证

**步骤名称：** 03-查询参数验证  
**代码类型：** SQL  
**排序：** 3.00

```sql
-- 查询并验证参数值
SELECT 
    task_id,
    department_id,
    department_code,
    department_name,
    cost_center_code,
    cost_center_name,
    accounting_unit_code,
    accounting_unit_name,
    period,
    year,
    month,
    start_date,
    end_date,
    test_time,
    -- 验证日期计算是否正确
    EXTRACT(YEAR FROM start_date) as start_year,
    EXTRACT(MONTH FROM start_date) as start_month,
    EXTRACT(DAY FROM start_date) as start_day,
    EXTRACT(DAY FROM end_date) as end_day,
    -- 验证日期范围
    (end_date - start_date + 1) as days_in_month
FROM test_calculation_params
WHERE task_id = '{task_id}'
  AND department_id = {department_id}
ORDER BY test_time DESC
LIMIT 1;
```

---

## 步骤 4：统计测试结果

**步骤名称：** 04-统计测试结果  
**代码类型：** SQL  
**排序：** 4.00

```sql
-- 统计当前任务的测试数据
SELECT 
    '{task_id}' as current_task_id,
    '{period}' as current_period,
    COUNT(*) as total_departments,
    COUNT(DISTINCT department_code) as unique_dept_codes,
    COUNT(DISTINCT period) as unique_periods,
    MIN(test_time) as first_test_time,
    MAX(test_time) as last_test_time,
    -- 检查是否有空值
    COUNT(*) FILTER (WHERE department_code IS NULL OR department_code = '') as empty_dept_codes,
    COUNT(*) FILTER (WHERE cost_center_code IS NULL OR cost_center_code = '') as empty_cost_centers,
    COUNT(*) FILTER (WHERE accounting_unit_code IS NULL OR accounting_unit_code = '') as empty_accounting_units
FROM test_calculation_params
WHERE task_id = '{task_id}';
```

---

## 步骤 5：测试日期范围查询

**步骤名称：** 05-测试日期范围  
**代码类型：** SQL  
**排序：** 5.00

```sql
-- 模拟实际业务查询：使用日期范围参数
SELECT 
    '{department_code}' as dept_code,
    '{department_name}' as dept_name,
    '{start_date}' as query_start_date,
    '{end_date}' as query_end_date,
    -- 生成测试日期序列
    generate_series(
        '{start_date}'::DATE,
        '{end_date}'::DATE,
        '1 day'::INTERVAL
    )::DATE as date_in_range,
    -- 验证日期是否在范围内
    CASE 
        WHEN generate_series('{start_date}'::DATE, '{end_date}'::DATE, '1 day'::INTERVAL)::DATE 
             BETWEEN '{start_date}'::DATE AND '{end_date}'::DATE 
        THEN 'YES' 
        ELSE 'NO' 
    END as is_in_range
LIMIT 5;
```

---

## 步骤 6：测试年月参数

**步骤名称：** 06-测试年月参数  
**代码类型：** SQL  
**排序：** 6.00

```sql
-- 测试年月参数的使用
SELECT 
    '{period}' as period_param,
    '{current_year_month}' as current_year_month_param,
    '{year}' as year_param,
    '{month}' as month_param,
    -- 验证参数一致性
    CASE 
        WHEN '{period}' = '{current_year_month}' THEN 'MATCH'
        ELSE 'MISMATCH'
    END as period_consistency,
    CASE 
        WHEN '{period}' = '{year}' || '-' || '{month}' THEN 'MATCH'
        ELSE 'MISMATCH'
    END as year_month_consistency,
    -- 测试在 WHERE 条件中使用
    COUNT(*) as matching_records
FROM test_calculation_params
WHERE period = '{period}'
  AND year = '{year}'
  AND month = '{month}';
```

---

## 步骤 7：清理测试数据（可选）

**步骤名称：** 07-清理测试数据  
**代码类型：** SQL  
**排序：** 7.00  
**是否启用：** 否（默认禁用，需要时手动启用）

```sql
-- 清理当前任务的测试数据
DELETE FROM test_calculation_params
WHERE task_id = '{task_id}';

-- 或者清理所有测试数据
-- DELETE FROM test_calculation_params;

-- 或者删除整个测试表
-- DROP TABLE IF EXISTS test_calculation_params;
```

---

## 步骤 8：完整参数展示

**步骤名称：** 08-完整参数展示  
**代码类型：** SQL  
**排序：** 8.00

```sql
-- 展示所有参数的实际值
SELECT 
    '参数测试报告' as report_title,
    '{task_id}' as task_id,
    {department_id} as department_id,
    '{department_code}' as department_code,
    '{department_name}' as department_name,
    '{cost_center_code}' as cost_center_code,
    '{cost_center_name}' as cost_center_name,
    '{accounting_unit_code}' as accounting_unit_code,
    '{accounting_unit_name}' as accounting_unit_name,
    '{period}' as period,
    '{current_year_month}' as current_year_month,
    '{year}' as year,
    '{month}' as month,
    '{start_date}' as start_date,
    '{end_date}' as end_date,
    NOW() as test_timestamp;
```

---

## 使用说明

### 1. 创建计算流程

1. 进入"计算流程管理"页面
2. 点击"创建计算流程"
3. 填写流程信息：
   - 流程名称：`参数测试流程`
   - 流程描述：`用于测试计算步骤中的参数替换功能`
   - 关联模型版本：选择任意版本

### 2. 添加计算步骤

按照上面的步骤顺序，依次创建 8 个计算步骤：

- 步骤 1-6：启用
- 步骤 7：禁用（清理步骤，需要时手动启用）
- 步骤 8：启用

每个步骤的配置：
- **步骤名称**：按上面的名称填写
- **代码类型**：SQL
- **数据源**：选择你的 PostgreSQL 数据源
- **代码内容**：复制对应的 SQL 代码
- **排序序号**：按顺序填写（1.00, 2.00, 3.00...）
- **是否启用**：除了步骤 7，其他都启用

### 3. 创建计算任务

1. 进入"计算任务管理"页面
2. 点击"创建计算任务"
3. 填写任务信息：
   - 模型版本：选择关联的版本
   - 计算流程：选择"参数测试流程"
   - 计算周期：选择任意月份（如 2025-10）
   - 科室范围：选择 1-2 个科室即可

### 4. 查看测试结果

任务完成后，可以通过以下方式查看结果：

#### 方式 1：查看步骤日志
```sql
SELECT 
    step_id,
    department_id,
    status,
    duration_ms,
    result_data,
    error_message
FROM calculation_step_logs
WHERE task_id = '你的任务ID'
ORDER BY step_id, department_id;
```

#### 方式 2：查看测试表数据
```sql
SELECT * FROM test_calculation_params
WHERE task_id = '你的任务ID'
ORDER BY department_id;
```

#### 方式 3：在前端查看
- 进入"计算任务管理"
- 找到测试任务
- 查看任务详情和执行日志

### 5. 验证要点

检查以下内容是否正确：

✅ **时间参数**
- `period` 和 `current_year_month` 是否一致
- `year` 和 `month` 是否正确拆分
- `start_date` 是否为月初（01 号）
- `end_date` 是否为月末（28/29/30/31 号）

✅ **科室参数**
- `department_id` 是否为数字
- `department_code` 是否为科室的 HIS 代码
- `department_name` 是否为科室名称
- 成本中心和核算单元参数是否正确（可能为空）

✅ **任务参数**
- `task_id` 是否为当前任务的 UUID

### 6. 清理测试数据

测试完成后，如果需要清理：

1. 启用步骤 7（清理测试数据）
2. 重新运行计算任务
3. 或者手动执行清理 SQL

---

## 常见问题

### Q1: 步骤执行失败怎么办？

查看 `calculation_step_logs` 表中的 `error_message` 字段，了解具体错误。

### Q2: 参数没有被替换？

检查：
1. 参数名称是否正确（区分大小写）
2. 是否使用了花括号 `{}`
3. 数据源连接是否正常

### Q3: 某些参数为空？

部分参数可能为空：
- `cost_center_code`、`cost_center_name`
- `accounting_unit_code`、`accounting_unit_name`

这是正常的，取决于科室数据是否填写了这些字段。

### Q4: 如何调试 SQL？

1. 在计算步骤编辑页面使用"测试运行"功能
2. 先用简单的 SELECT 语句测试参数
3. 逐步增加复杂度

---

## 扩展测试

如果需要测试更复杂的场景，可以添加以下步骤：

### 测试 JOIN 查询
```sql
SELECT 
    t.department_code,
    t.department_name,
    d.his_name as actual_dept_name,
    CASE 
        WHEN t.department_name = d.his_name THEN 'MATCH'
        ELSE 'MISMATCH'
    END as name_check
FROM test_calculation_params t
LEFT JOIN departments d ON d.id = t.department_id
WHERE t.task_id = '{task_id}'
  AND t.department_id = {department_id};
```

### 测试聚合查询
```sql
SELECT 
    period,
    COUNT(*) as dept_count,
    STRING_AGG(department_code, ', ') as dept_codes
FROM test_calculation_params
WHERE period = '{period}'
GROUP BY period;
```

### 测试条件查询
```sql
SELECT 
    department_code,
    department_name,
    CASE 
        WHEN cost_center_code IS NOT NULL AND cost_center_code != '' 
        THEN 'HAS_COST_CENTER'
        ELSE 'NO_COST_CENTER'
    END as cost_center_status
FROM test_calculation_params
WHERE task_id = '{task_id}'
  AND department_id = {department_id};
```
