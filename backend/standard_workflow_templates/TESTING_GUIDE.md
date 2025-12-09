# 标准计算流程测试指南

## 测试步骤概述

标准计算流程包含 3 个步骤，它们之间有依赖关系：

| 步骤 | 名称 | 输入 | 输出 | 是否可单独测试 |
|------|------|------|------|---------------|
| Step1 | 维度目录统计 | 外部数据源（收费明细） | 维度工作量 | ✅ 可以 |
| Step2 | 指标工作量统计 | 外部数据源（工作量统计） | 指标工作量 | ✅ 可以 |
| Step3 | 业务价值汇总 | calculation_results 表 | 科室业务价值 | ❌ 不可以 |

## 单步测试

### Step1 测试

**前置条件**：
1. ✅ 外部数据源中有 `charge_details` 表
2. ✅ 表中有测试数据
3. ✅ 系统中有维度-收费项目映射
4. ✅ 收费明细的 `item_code` 和映射表的 `item_code` 匹配

**测试方法**：
1. 在计算流程管理页面，找到标准流程
2. 点击 Step1 的"测试"按钮
3. 查看返回结果

**预期结果**：
```
返回 N 行数据，每行包含：
- dimension_id: 维度ID
- department_id: 科室ID
- workload_amount: 工作量金额
- workload_quantity: 工作量数量
- workload_patient_count: 患者人次
```

**如果返回 0 行**：
- 检查维度映射和收费项目的 `item_code` 是否匹配
- 运行 `debug_step1.sql` 排查问题

### Step2 测试

**前置条件**：
1. ✅ 外部数据源中有 `workload_statistics` 表
2. ✅ 表中有测试数据
3. ✅ 系统中有指标型维度（名称包含"护理"或"会诊"）

**测试方法**：
1. 在计算流程管理页面，找到标准流程
2. 点击 Step2 的"测试"按钮
3. 查看返回结果

**预期结果**：
```
返回 N 行数据，每行包含：
- dimension_id: 维度ID
- department_id: 科室ID
- workload_value: 工作量数值
```

**如果返回 0 行**：
- 检查是否有名称包含"护理"或"会诊"的维度
- 检查 `workload_statistics` 表中是否有对应的数据

### Step3 测试

**Step3 不能单独测试**，原因：
1. Step3 从 `calculation_results` 表读取数据
2. 这个表只有在运行完整计算任务后才会有数据
3. 需要一个真实的 `task_id`

**如何测试 Step3**：
必须运行完整的计算任务（见下文"完整流程测试"）

## 完整流程测试

### 准备工作

1. **生成测试数据**：
```bash
python backend/standard_workflow_templates/generate_test_data.py \
  --hospital-id 1 \
  --period 2025-10 \
  --data-source-id 2
```

2. **确认数据生成成功**：
```sql
-- 检查收费明细
SELECT COUNT(*) FROM charge_details 
WHERE charge_time >= '2025-10-01' AND charge_time <= '2025-10-31';

-- 检查工作量统计
SELECT COUNT(*) FROM workload_statistics 
WHERE stat_month = '2025-10';
```

3. **确认维度映射配置**：
- 在前端"维度-收费项目映射"页面检查
- 确保有映射数据

### 运行完整任务

1. **在前端创建计算任务**：
   - 进入"计算任务"页面
   - 点击"新建任务"
   - 选择模型版本
   - 选择标准计算流程
   - 选择周期：2025-10
   - 选择科室（或不选，批量模式）
   - 提交任务

2. **查看任务执行**：
   - 任务状态应该变为"运行中"
   - 等待任务完成（通常几秒到几分钟）
   - 状态变为"已完成"

3. **查看执行日志**：
   - 点击任务的"查看日志"
   - 检查每个步骤的执行情况
   - Step1、Step2、Step3 都应该显示"成功"

4. **查看计算结果**：
   - 点击任务的"查看结果"
   - 应该能看到各科室的业务价值

### 验证结果

```sql
-- 1. 检查 calculation_results 表
SELECT 
    node_type,
    COUNT(*) as count,
    SUM(workload) as total_workload,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'your-task-id'
GROUP BY node_type;

-- 2. 检查 calculation_summaries 表
SELECT 
    department_id,
    doctor_value,
    nurse_value,
    tech_value,
    total_value
FROM calculation_summaries
WHERE task_id = 'your-task-id';
```

## 常见问题

### Q1: Step1 返回 0 行

**原因**：维度映射的 `item_code` 和收费明细的 `item_code` 不匹配

**解决方法**：
1. 运行 `debug_step1.sql` 排查
2. 检查维度映射配置
3. 重新生成测试数据，确保使用匹配的 `item_code`

### Q2: Step2 返回 0 行

**原因**：
- 没有指标型维度（名称包含"护理"或"会诊"）
- `workload_statistics` 表中没有数据

**解决方法**：
1. 检查模型中是否有指标型维度
2. 运行测试数据生成脚本
3. 调整 Step2 的维度匹配规则

### Q3: Step3 测试报错

**原因**：Step3 不能单独测试

**解决方法**：运行完整的计算任务

### Q4: 完整任务执行失败

**排查步骤**：
1. 查看任务执行日志，找到失败的步骤
2. 查看步骤的错误信息
3. 根据错误信息修复问题
4. 重新运行任务

**常见错误**：
- 参数未替换：检查后端是否重启
- 表不存在：检查外部数据源配置
- 数据为空：检查测试数据是否生成成功

### Q5: 计算结果不正确

**检查清单**：
1. ✅ 维度-收费项目映射是否正确
2. ✅ 模型结构和权重是否正确
3. ✅ 测试数据是否合理
4. ✅ SQL 逻辑是否符合业务需求

## 调试技巧

### 1. 查看步骤执行日志

```sql
SELECT 
    step_id,
    status,
    duration_ms,
    execution_info,
    result_data
FROM calculation_step_logs
WHERE task_id = 'your-task-id'
ORDER BY start_time;
```

### 2. 查看中间结果

Step2 会创建临时表 `dimension_workload_temp`，但这个表在会话结束后会被删除。如果需要查看中间结果，可以修改 Step2，将结果插入到持久化表。

### 3. 手动执行 SQL

将步骤的 SQL 复制出来，手动替换参数，在数据库中执行，查看详细的错误信息。

## 性能优化

### 大数据量测试

如果需要测试大数据量场景：

```bash
# 生成 10000 条收费记录
python backend/standard_workflow_templates/generate_test_data.py \
  --hospital-id 1 \
  --period 2025-10 \
  --record-count 10000 \
  --patient-count 1000 \
  --data-source-id 2
```

### 批量模式 vs 单科室模式

- **批量模式**（不选科室）：流程只执行一次，适合大规模计算
- **单科室模式**（选择科室）：对每个科室循环执行，适合小规模测试

建议：
- 测试时使用单科室模式，选择 1-2 个科室
- 生产环境使用批量模式

## 相关文档

- [标准流程 README](README.md)
- [SQL 参数指南](../SQL_PARAMETERS_GUIDE.md)
- [测试数据生成指南](GENERATE_TEST_DATA.md)
- [问题修复文档](../test-hospital-id-fix.md)
