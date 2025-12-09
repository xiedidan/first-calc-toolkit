# 工作量维度统计功能实现

## 概述

在标准计算流程中新增了步骤3c"工作量维度统计"，用于从`workload_statistics`表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量数据。

## 实现内容

### 1. 新增SQL步骤文件

**文件**: `backend/standard_workflow_templates/step3c_workload_dimensions.sql`

**功能**: 从workload_statistics表中提取四类维度的工作量数据

**支持的维度类型**:
- `nursing_bed_days`: 护理床日
- `admission_discharge_transfer`: 出入转院
- `surgery_management`: 手术管理
- `operating_room_nursing`: 手术室护理

**数据流程**:
1. 从`workload_statistics`表读取指定月份的工作量数据
2. 根据`stat_type`字段匹配对应的维度类型
3. 通过维度的`code`字段进行模糊匹配（支持中英文）
4. 按科室汇总工作量
5. 计算价值（工作量 × 权重）
6. 插入到`calculation_results`表

### 2. 更新导入脚本

**文件**: `backend/standard_workflow_templates/import_standard_workflow.sh`

**变更**:
- 步骤数量从5个增加到6个
- 新增步骤3c的导入逻辑（sort_order=3.60）
- 更新步骤详情输出

### 3. 更新测试数据

**文件**: `backend/standard_workflow_templates/generate_test_data.py`

**新增测试数据**:
- 护理床日: 每个科室生成总计床日数
- 出入转院: 每个科室生成入院、出院、转院人次
- 手术管理: 每个科室生成手术台次
- 手术室护理: 每个科室生成护理工作量

**文件**: `backend/standard_workflow_templates/create_test_tables.sql`

**新增测试记录**:
- 为内科、外科、儿科各添加4类维度的测试数据
- 总计新增约24条测试记录

### 4. 更新文档

**文件**: `backend/standard_workflow_templates/README.md`

**变更**:
- 更新文件说明表，添加step3c说明
- 新增步骤3c的详细说明
- 说明维度匹配规则和占位符

## 使用方法

### 1. 准备工作

确保`workload_statistics`表中有对应的数据：

```sql
-- 查看现有数据
SELECT stat_type, COUNT(*) 
FROM workload_statistics 
WHERE stat_month = '2025-10'
GROUP BY stat_type;
```

### 2. 创建维度

在模型中创建对应的维度，确保`code`字段包含以下关键词之一：

- 护理床日: `nursing_bed_days` 或 `护理床日`
- 出入转院: `admission_discharge_transfer` 或 `出入转院`
- 手术管理: `surgery_management` 或 `手术管理`
- 手术室护理: `operating_room_nursing` 或 `手术室护理`

### 3. 导入标准流程

```bash
cd backend/standard_workflow_templates

# 导入标准流程（包含新步骤）
bash import_standard_workflow.sh --version-id <版本ID> --data-source-id <数据源ID>
```

### 4. 运行计算任务

在前端创建计算任务，选择导入的标准流程，系统会自动执行步骤3c。

### 5. 查看结果

```sql
-- 查看工作量维度的计算结果
SELECT 
    d.name as department_name,
    mn.name as dimension_name,
    cr.workload,
    cr.weight,
    cr.value
FROM calculation_results cr
JOIN departments d ON cr.department_id = d.id
JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = '<任务ID>'
  AND mn.code IN (
    SELECT code FROM model_nodes 
    WHERE code LIKE '%nursing_bed_days%'
       OR code LIKE '%admission_discharge_transfer%'
       OR code LIKE '%surgery_management%'
       OR code LIKE '%operating_room_nursing%'
  )
ORDER BY d.name, mn.name;
```

## 测试

### 生成测试数据

```bash
cd backend/standard_workflow_templates

# 生成测试数据（包含新维度）
python generate_test_data.py --period 2025-10 --record-count 100
```

### 运行测试脚本

```bash
# 测试工作量维度统计功能
python test_workload_dimensions.py
```

测试脚本会检查：
1. workload_statistics表中是否有数据
2. 模型节点中是否有对应的维度
3. SQL语法是否正确

## 数据结构

### workload_statistics表

| 字段 | 类型 | 说明 |
|------|------|------|
| department_code | VARCHAR(50) | 科室代码 |
| stat_month | VARCHAR(7) | 统计月份(YYYY-MM) |
| stat_type | VARCHAR(50) | 统计类型 |
| stat_level | VARCHAR(50) | 统计级别 |
| stat_value | DECIMAL(20,4) | 统计值 |

### stat_type取值

| 值 | 说明 | stat_level示例 |
|----|------|----------------|
| nursing_bed_days | 护理床日 | 总计 |
| admission_discharge_transfer | 出入转院 | 入院/出院/转院 |
| surgery_management | 手术管理 | 手术台次 |
| operating_room_nursing | 手术室护理 | 护理工作量 |
| nursing_days | 护理床日数（旧） | 一级护理/二级护理/三级护理/特级护理 |
| consultation | 会诊 | 发起/参与 |

## 注意事项

### 1. 维度匹配规则

步骤3c使用模糊匹配来关联维度：

```sql
WHERE mn.code LIKE '%nursing_bed_days%' OR mn.code LIKE '%护理床日%'
```

如果维度的`code`字段不符合这个规则，需要：
- 修改维度的`code`字段，或
- 修改SQL中的匹配条件

### 2. 与步骤3b的区别

- **步骤3b**: 处理`nursing_days`类型（按护理级别统计）
- **步骤3c**: 处理`nursing_bed_days`等类型（按维度统计）

两个步骤可以共存，处理不同类型的工作量数据。

### 3. 数据源配置

步骤3c需要访问外部数据源的`workload_statistics`表，确保：
- 数据源配置正确
- 数据源已启用
- 导入流程时指定了`--data-source-id`参数

### 4. 占位符替换

系统会自动替换以下占位符：
- `{task_id}`: 计算任务ID
- `{current_year_month}`: 当期年月
- `{hospital_id}`: 医疗机构ID
- `{version_id}`: 模型版本ID

## 扩展

### 添加新的维度类型

如需支持更多维度类型，在`step3c_workload_dimensions.sql`中添加类似的INSERT语句：

```sql
-- 示例: 添加MDT工作量统计
INSERT INTO calculation_results (...)
SELECT ...
FROM workload_statistics ws
WHERE ws.stat_type = 'mdt'
  AND (mn.code LIKE '%mdt%' OR mn.code LIKE '%MDT%')
...
```

### 自定义匹配规则

如果需要更精确的匹配，可以修改WHERE条件：

```sql
-- 精确匹配
WHERE mn.code = 'nursing_bed_days'

-- 使用正则表达式
WHERE mn.code ~ '^nursing_bed_days_.*$'

-- 使用维度类型字段（如果有）
WHERE mn.dimension_type = 'nursing_bed_days'
```

## 相关文件

- SQL步骤: `backend/standard_workflow_templates/step3c_workload_dimensions.sql`
- 导入脚本: `backend/standard_workflow_templates/import_standard_workflow.sh`
- 测试数据生成: `backend/standard_workflow_templates/generate_test_data.py`
- 测试表创建: `backend/standard_workflow_templates/create_test_tables.sql`
- 测试脚本: `test_workload_dimensions.py`
- 文档: `backend/standard_workflow_templates/README.md`

## 总结

新增的步骤3c"工作量维度统计"完善了标准计算流程，支持从workload_statistics表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量数据。该步骤与现有步骤无冲突，可以独立运行，为科室业务价值评估提供更全面的数据支持。
