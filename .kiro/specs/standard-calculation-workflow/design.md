# 科室业务价值标准计算流程 - 设计文档

## 概述

本文档描述"科室业务价值标准计算流程"的设计方案。该标准流程基于《科室业务价值评估数据集.md》定义的数据模型,为用户提供一套**可直接使用的SQL代码示例**和**自动导入脚本**,用于快速建立符合规范的业务价值评估计算流程。

### 核心交付物

1. **SQL代码文件**: 包含3个标准计算步骤的SQL代码模板
2. **导入脚本**: 自动将SQL代码导入到计算流程管理模块的Shell脚本  
3. **使用文档**: 详细的使用说明和参数配置指南(README.md)

### 设计目标

1. **开箱即用**: 用户无需编写代码,直接使用提供的SQL模板
2. **一键导入**: 通过脚本自动创建标准计算流程
3. **易于调整**: SQL代码清晰易懂,用户可根据实际情况修改
4. **符合规范**: 严格遵循数据集文档定义的表结构和字段

## 交付物设计

### 1. 文件结构

```
backend/standard_workflow_templates/
├── README.md                           # 使用说明文档
├── step1_dimension_catalog.sql         # 步骤1: 维度目录统计
├── step2_indicator_calculation.sql     # 步骤2: 指标计算(示例)
├── step3_value_aggregation.sql         # 步骤3: 业务价值汇总
└── import_standard_workflow.sh         # 自动导入脚本
```

### 2. 使用流程

```
用户操作流程:
1. 进入backend/standard_workflow_templates目录
2. (可选)根据实际数据库结构调整SQL代码
3. 执行: bash import_standard_workflow.sh --version-id <版本ID> --db-password <密码>
4. 在前端"计算流程管理"页面查看导入的标准流程
5. 创建计算任务时选择该标准流程
```


## SQL代码文件设计

### 文件1: step1_dimension_catalog.sql

**功能**: 维度目录统计 - 根据维度-收费项目映射统计各维度的工作量

**输入参数**(通过占位符):
- `{current_year_month}`: 当期年月 (如: 2025-10)
- `{hospital_id}`: 医疗机构ID
- `{start_date}`: 开始日期 (当月第一天)
- `{end_date}`: 结束日期 (当月最后一天)

**输出字段**:
- `dimension_id`: 维度ID
- `department_id`: 科室ID
- `workload_amount`: 工作量金额
- `workload_quantity`: 工作量数量
- `workload_patient_count`: 患者人次

**数据来源**:
- `dimension_item_mappings`: 维度-收费项目映射表(系统表)
- `charge_details`: 收费明细表(外部数据源)
- `departments`: 科室表(系统表)
- `model_nodes`: 模型节点表(系统表)

**SQL代码结构**:
```sql
-- 第1步: 获取维度-收费项目映射关系
WITH dimension_mappings AS (...)

-- 第2步: 获取收费明细数据并汇总
, charge_data AS (...)

-- 第3步: 关联映射和收费数据,按维度和科室汇总
SELECT 
    dm.dimension_id,
    d.id as department_id,
    SUM(cd.total_amount) as workload_amount,
    SUM(cd.total_quantity) as workload_quantity,
    SUM(cd.patient_count) as workload_patient_count
FROM dimension_mappings dm
INNER JOIN charge_data cd ON dm.item_code = cd.item_code
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code
WHERE d.hospital_id = {hospital_id}
GROUP BY dm.dimension_id, d.id;
```

### 文件2: step2_indicator_calculation.sql

**功能**: 指标计算 - 计算指标型维度的工作量(示例: 护理床日数)

**输入参数**:
- `{current_year_month}`: 当期年月
- `{hospital_id}`: 医疗机构ID
- `{dimension_id}`: 维度ID (需要用户根据实际维度ID替换)

**输出字段**:
- `dimension_id`: 维度ID
- `department_id`: 科室ID
- `workload_value`: 工作量数值

**数据来源**:
- `workload_statistics`: 工作量统计表(外部数据源)
- `departments`: 科室表(系统表)

**SQL代码结构**:
```sql
-- 示例: 护理床日数统计
SELECT 
    {dimension_id} as dimension_id,
    d.id as department_id,
    ws.level1_nursing_days + ws.level2_nursing_days + ws.level3_nursing_days as workload_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE ws.year_month = '{current_year_month}'
  AND d.hospital_id = {hospital_id}
  AND d.is_active = TRUE;
```

**说明**: 
- 此文件提供护理床日数统计示例
- 用户需要根据实际维度创建多个类似的步骤
- 可以复制此步骤并修改维度ID和计算逻辑

### 文件3: step3_value_aggregation.sql

**功能**: 业务价值汇总 - 根据模型结构和权重汇总各科室的业务价值

**输入参数**:
- `{task_id}`: 计算任务ID
- `{version_id}`: 模型版本ID

**输出字段**:
- `task_id`: 任务ID
- `department_id`: 科室ID
- `doctor_value`: 医生序列价值
- `nursing_value`: 护理序列价值
- `medical_tech_value`: 医技序列价值
- `total_value`: 科室总价值

**数据来源**:
- `model_nodes`: 模型节点表(系统表)
- `calculation_results`: 计算结果表(系统表)

**SQL代码结构**:
```sql
-- 第1步: 加载模型结构和权重
WITH model_structure AS (...)

-- 第2步: 加载维度计算结果
, dimension_results AS (...)

-- 第3步: 计算维度得分(根据权重类型)
, dimension_scores AS (...)

-- 第4步: 自下而上汇总(递归CTE)
, aggregated_scores AS (...)

-- 第5步: 提取序列得分并计算科室总价值
SELECT 
    '{task_id}' as task_id,
    department_id,
    MAX(CASE WHEN sequence_name = 'doctor' THEN score END) as doctor_value,
    MAX(CASE WHEN sequence_name = 'nursing' THEN score END) as nursing_value,
    MAX(CASE WHEN sequence_name = 'medical_tech' THEN score END) as medical_tech_value,
    SUM(score) as total_value
FROM aggregated_scores
WHERE node_level = 1  -- 序列级别
GROUP BY department_id;
```

**说明**:
- 此SQL实现自下而上的汇总算法
- 根据权重类型(百分比/固定值)计算得分
- 使用递归CTE实现层级汇总


## 导入脚本设计

### 脚本参数

```bash
#!/bin/bash
# import_standard_workflow.sh
# 功能: 将标准计算流程SQL代码导入到系统
# 配置来源: 自动读取backend/.env文件获取数据库连接信息

# 必填参数:
#   --version-id: 模型版本ID

# 可选参数:
#   --workflow-name: 流程名称 (默认: "标准计算流程")

# 数据库连接参数(自动从backend/.env读取):
#   DATABASE_HOST: 数据库主机
#   DATABASE_PORT: 数据库端口
#   DATABASE_NAME: 数据库名称
#   DATABASE_USER: 数据库用户
#   DATABASE_PASSWORD: 数据库密码

# 使用示例:
# bash import_standard_workflow.sh --version-id 123
# bash import_standard_workflow.sh --version-id 123 --workflow-name "标准计算流程-2025"
```

**设计说明**:
- 脚本自动读取`backend/.env`文件中的数据库配置
- 保证与系统配置的一致性,避免手动输入错误
- 简化用户操作,只需提供版本ID即可

### 脚本执行流程

```
1. 读取backend/.env配置文件
   - 解析DATABASE_HOST, DATABASE_PORT, DATABASE_NAME等变量
   - 如果.env文件不存在,输出错误信息并退出

2. 解析命令行参数
   - 验证必填参数(version-id)
   - 设置默认值(workflow-name)

3. 测试数据库连接
   - 使用psql和.env中的配置测试连接
   - 如果失败,输出错误信息并退出

4. 验证模型版本
   - 查询model_versions表确认版本存在
   - 如果不存在,输出错误信息并退出

5. 读取SQL代码文件
   - step1_dimension_catalog.sql
   - step2_indicator_calculation.sql
   - step3_value_aggregation.sql

6. 创建计算流程记录
   - INSERT INTO calculation_workflows
   - 获取生成的workflow_id

7. 创建计算步骤记录(3个)
   - INSERT INTO calculation_steps (步骤1)
   - INSERT INTO calculation_steps (步骤2)
   - INSERT INTO calculation_steps (步骤3)

8. 输出导入结果
   - 流程ID
   - 流程名称
   - 步骤数量
   - 前端访问URL
```

### 脚本输出示例

```
========================================
标准计算流程导入成功!
========================================
流程ID: 456
流程名称: 标准计算流程-2025
模型版本ID: 123
步骤数量: 3

步骤详情:
  1. 维度目录统计 (SQL, 排序: 1.00)
  2. 指标计算-护理床日数 (SQL, 排序: 2.00)
  3. 业务价值汇总 (SQL, 排序: 3.00)

前端访问:
  http://localhost/calculation-workflows/456

下一步操作:
  1. 在前端查看和编辑计算流程
  2. 根据实际维度添加更多指标计算步骤
  3. 创建计算任务并选择此流程
========================================
```

## README文档设计

### README.md内容结构

```markdown
# 科室业务价值标准计算流程

## 简介

本目录包含科室业务价值评估的标准计算流程SQL代码和导入脚本。

## 文件说明

- `step1_dimension_catalog.sql`: 维度目录统计
- `step2_indicator_calculation.sql`: 指标计算示例(护理床日数)
- `step3_value_aggregation.sql`: 业务价值汇总
- `import_standard_workflow.sh`: 自动导入脚本

## 快速开始

### 1. 准备工作

确保已完成以下准备:
- 系统已部署并运行
- 已创建模型版本
- 已配置数据源(指向HIS系统或数据仓库)
- 已导入科室信息和收费项目

### 2. 导入标准流程

```bash
cd backend/standard_workflow_templates
bash import_standard_workflow.sh --version-id <你的模型版本ID>

# 或指定自定义流程名称
bash import_standard_workflow.sh \
  --version-id <你的模型版本ID> \
  --workflow-name "标准计算流程-2025"
```

**说明**: 脚本会自动读取`backend/.env`文件中的数据库配置,无需手动输入密码

### 3. 调整SQL代码(可选)

根据实际数据库结构调整SQL代码:
- 修改表名和字段名
- 调整数据筛选条件
- 添加更多指标计算步骤

### 4. 在前端查看

访问"计算流程管理"页面,查看导入的标准流程。

### 5. 创建计算任务

在"计算任务"页面创建新任务,选择标准流程并执行。

## SQL代码说明

### 步骤1: 维度目录统计

根据维度-收费项目映射关系,从收费明细表中统计各维度的工作量。

**关键逻辑**:
- 读取dimension_item_mappings表获取映射关系
- 关联charge_details表获取收费数据
- 按维度和科室汇总金额、数量、人次

**占位符**:
- {current_year_month}: 当期年月
- {hospital_id}: 医疗机构ID
- {start_date}: 开始日期
- {end_date}: 结束日期

### 步骤2: 指标计算

执行自定义的指标计算逻辑,计算指标型维度的工作量。

**示例**: 护理床日数统计

**关键逻辑**:
- 从workload_statistics表提取护理床日数
- 按科室汇总各级护理床日数

**占位符**:
- {current_year_month}: 当期年月
- {hospital_id}: 医疗机构ID
- {dimension_id}: 维度ID(需要替换为实际ID)

**扩展**: 
用户可以复制此步骤,创建更多指标计算步骤,如:
- 会诊工作量统计
- MDT工作量统计
- 出院人次统计

### 步骤3: 业务价值汇总

根据模型结构和权重,自下而上汇总各科室的业务价值。

**关键逻辑**:
- 加载模型结构和权重
- 加载维度计算结果
- 根据权重类型计算维度得分
- 自下而上汇总父节点得分
- 提取序列得分和科室总价值

**占位符**:
- {task_id}: 计算任务ID
- {version_id}: 模型版本ID

## 常见问题

### Q1: 导入失败,提示"模型版本不存在"

**A**: 请确认version-id参数是否正确,可以在前端"模型版本管理"页面查看版本ID。

### Q2: SQL执行失败,提示"表不存在"

**A**: 请检查:
1. 数据源是否正确配置
2. 表名和字段名是否与实际数据库一致
3. 是否有权限访问外部数据表

### Q3: 如何添加更多指标计算步骤?

**A**: 
1. 复制step2_indicator_calculation.sql
2. 修改维度ID和计算逻辑
3. 在前端"计算步骤管理"页面手动添加新步骤
4. 或修改导入脚本,添加更多步骤

### Q4: 占位符如何替换?

**A**: 占位符由系统在执行时自动替换,无需手动处理。

## 技术支持

如有问题,请联系系统管理员或查看系统文档。
```

## 占位符系统

### 支持的占位符

| 占位符 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| {current_year_month} | String | 当期年月 | "2025-10" |
| {department_id} | Integer | 科室ID | 123 |
| {department_code} | String | 科室编码 | "NEI01" |
| {start_date} | Date | 开始日期(当月第一天) | "2025-10-01" |
| {end_date} | Date | 结束日期(当月最后一天) | "2025-10-31" |
| {hospital_id} | Integer | 医疗机构ID | 1 |
| {dimension_id} | Integer | 维度ID | 789 |
| {task_id} | String | 计算任务ID | "task_20251113_001" |
| {version_id} | Integer | 模型版本ID | 123 |

### 占位符替换时机

占位符由系统在**执行计算步骤时**自动替换,用户无需手动处理。

### 占位符使用示例

**SQL代码**:
```sql
SELECT * FROM charge_details
WHERE charge_time >= '{start_date}'
  AND charge_time < '{end_date}'
  AND prescribing_dept_code = '{department_code}';
```

**执行时替换为**:
```sql
SELECT * FROM charge_details
WHERE charge_time >= '2025-10-01'
  AND charge_time < '2025-10-31'
  AND prescribing_dept_code = 'NEI01';
```

## 测试策略

### 单元测试

1. **SQL语法测试**
   - 验证SQL语法正确性
   - 测试占位符替换

2. **导入脚本测试**
   - 测试参数解析
   - 测试数据库连接
   - 测试流程创建

### 集成测试

1. **完整流程测试**
   - 导入标准流程
   - 执行计算任务
   - 验证结果正确性

2. **多科室测试**
   - 测试批量计算
   - 验证结果一致性

### 验收测试

1. **用户操作测试**
   - 按README文档操作
   - 验证每个步骤可执行
   - 验证最终结果符合预期

2. **错误处理测试**
   - 测试参数错误处理
   - 测试数据库连接失败处理
   - 测试SQL执行错误处理
