# 修复说明

## 问题1: Step 3 计算结果全为0

### 根本原因
Steps 1和2只执行SELECT查询，没有将结果INSERT到`calculation_results`表中。Step 3期望从`calculation_results`读取数据进行汇总，但找不到数据，导致结果全为0。

### 修复方案
修改了三个SQL文件，使数据正确流转：

1. **step1_dimension_catalog.sql**
   - 改为INSERT INTO calculation_results
   - 保存维度工作量数据（dimension类型）
   - 最后返回插入记录数

2. **step2_indicator_calculation.sql**
   - 改为INSERT INTO calculation_results
   - 保存指标工作量数据（dimension类型）
   - 最后返回插入记录数

3. **step3_value_aggregation.sql**
   - 从calculation_results读取数据
   - 按层级汇总计算
   - INSERT INTO calculation_summaries
   - 更新占比字段
   - 最后返回插入记录数

### 数据流
```
Step 1 → calculation_results (维度数据)
Step 2 → calculation_results (指标数据)
Step 3 → 读取 calculation_results → 汇总 → calculation_summaries
```

## 问题2: 计算任务列表中"计算流程"列显示为"-"

### 根本原因
- CalculationTaskResponse schema缺少workflow_name字段
- API返回时没有加载workflow关系数据

### 修复方案

1. **backend/app/schemas/calculation_task.py**
   - 在CalculationTaskResponse中添加workflow_name字段

2. **backend/app/api/calculation_tasks.py**
   - 在get_calculation_tasks中加载workflow_name
   - 遍历tasks，从workflow关系中获取name

## 问题3: 多SQL语句执行和提交问题

### 根本原因
SQL文件包含多个语句（INSERT + SELECT），SQLAlchemy的execute()可能无法正确处理多语句和事务提交。

### 修复方案

**backend/app/tasks/calculation_tasks.py**
- 修改execute_calculation_step函数
- 将SQL按分号分割成多个语句
- 逐个执行每个语句
- 累计影响行数
- 最后统一commit
- 返回最后一个语句的结果（通常是SELECT）

**backend/app/api/calculation_steps.py**
- 修改test_step_code函数（测试已保存的步骤）
- 修改test_code_without_save函数（测试未保存的代码）
- 同样实现多语句分割和执行
- **关键修复**：无论最后是否返回行，都执行commit()
- 之前的bug：如果最后是SELECT，就不commit，导致INSERT被回滚

## 测试步骤

1. 删除旧的workflow (例如workflow_id=14):
```bash
cd backend/standard_workflow_templates
bash delete_workflow.sh 14
```

2. 重新导入修复后的workflow:
```bash
bash import_standard_workflow.sh
```

3. 在前端创建新的计算任务，选择"标准计算流程"

4. 查看计算结果:
   - 计算任务列表应显示"标准计算流程"
   - Step 1、2、3都应该有插入记录
   - calculation_summaries应该有汇总数据（非全0）

## 相关文件

### 修改的文件
- backend/standard_workflow_templates/step1_dimension_catalog.sql
- backend/standard_workflow_templates/step2_indicator_calculation.sql
- backend/standard_workflow_templates/step3_value_aggregation.sql
- backend/app/schemas/calculation_task.py
- backend/app/api/calculation_tasks.py
- backend/app/tasks/calculation_tasks.py
- backend/standard_workflow_templates/cleanup_failed_import.sh

### 新增的文件
- backend/standard_workflow_templates/delete_workflow.sh (灵活删除指定workflow)


## 2025-11-20: 计算结果字段缺失修复

### 问题
计算任务执行后，`calculation_results` 表中的记录缺少关键字段：
- `node_code` - 节点编码（空）
- `parent_id` - 父节点ID（空）

导致报表无法正确显示树形结构。

### 根本原因
标准工作流模板的SQL语句中，INSERT语句没有包含 `node_code` 和 `parent_id` 字段。

### 修复内容

1. **step1_dimension_catalog.sql**
   - 添加 `node_code` 和 `parent_id` 到INSERT字段列表
   - 从 `model_nodes` 表获取这些字段
   - 更新 GROUP BY 子句包含新字段

2. **step2_indicator_calculation.sql**
   - 护理床日数INSERT：添加 `node_code` 和 `parent_id`
   - 会诊INSERT：添加 `node_code` 和 `parent_id`
   - 更新两个INSERT的GROUP BY子句

### 验证步骤

1. 重新导入工作流模板
2. 创建新的计算任务
3. 检查 `calculation_results` 表中的 `node_code` 和 `parent_id` 字段应该有值
4. 报表应该能正确显示树形结构

### 修复现有数据

如果已有旧数据，可以运行：
```bash
psql -U admin -d hospital_value -f fix-existing-results.sql
```

### 相关文档
- CALCULATION_RESULTS_FIELDS_FIX.md - 详细说明
- fix-existing-results.sql - 修复现有数据的SQL脚本
