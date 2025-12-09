# 护理业务价值计算步骤实现文档

## 概述

为"医生业务价值计算流程"(ID=31)添加了第二个步骤"护理业务价值计算"，用于统计护理序列各末级维度的工作量和业务价值。

## 步骤信息

- **步骤ID**: 118
- **步骤名称**: 护理业务价值计算
- **所属流程**: 医生业务价值计算流程 (ID: 31)
- **模型版本**: 26 (2025年迭代版-宁波眼科v1.7)
- **排序**: 2.00
- **数据源**: 系统数据源 (ID: 3)

## 数据来源

步骤分为两部分，使用不同的数据源：

### Part 1: 从charge_details统计 (6个维度)

通过收费明细表和维度项目映射表统计：

1. **基础护理** (dim-nur-base) - 权重: 0.35
   - 映射项目数: 31
   - 统计方式: 收费金额汇总

2. **医护协同治疗** (dim-nur-collab) - 权重: 0.05
   - 映射项目数: 13
   - 统计方式: 收费金额汇总

3. **甲级护理治疗** (dim-nur-tr-a) - 权重: 0.08
   - 映射项目数: 5
   - 统计方式: 收费金额汇总

4. **乙级护理治疗** (dim-nur-tr-b) - 权重: 0.05
   - 映射项目数: 52
   - 统计方式: 收费金额汇总

5. **丙级护理治疗** (dim-nur-tr-c) - 权重: 0.03
   - 映射项目数: 82
   - 统计方式: 收费金额汇总

6. **其他护理** (dim-nur-other) - 权重: 0.03
   - 映射项目数: 2
   - 统计方式: 收费金额汇总

### Part 2: 从workload_statistics统计 (6个维度)

通过工作量统计表获取数据：

7. **甲级床日护理** (dim-nur-bed-3) - 权重: 50.00
   - 统计方式: 直接从workload_statistics读取

8. **乙级床日护理** (dim-nur-bed-4) - 权重: 35.00
   - 统计方式: 直接从workload_statistics读取

9. **丙级床日护理** (dim-nur-bed-5) - 权重: 10.00
   - 统计方式: 直接从workload_statistics读取

10. **普通入院护理** (dim-nur-trans-in) - 权重: 20.00
    - 统计方式: 直接从workload_statistics读取

11. **日间护理** (dim-nur-trans-intraday) - 权重: 15.00
    - 统计方式: 直接从workload_statistics读取

12. **普通出院护理** (dim-nur-trans-out) - 权重: 5.00
    - 统计方式: 直接从workload_statistics读取

## 关键技术点

### 1. 科室对照关系

- **charge_details**: 使用HIS科室代码 (`prescribing_dept_code`)
- **workload_statistics**: 使用核算单元代码 (`department_code`)
- **departments表**: 通过 `his_code` 和 `accounting_unit_code` 建立对照关系

```sql
-- charge_details关联
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code

-- workload_statistics关联
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
```

### 2. 参数替换

SQL模板使用以下占位符：

- `{task_id}` - 计算任务ID
- `{current_year_month}` - 当期年月 (格式: YYYY-MM)
- `{hospital_id}` - 医疗机构ID
- `{version_id}` - 模型版本ID

### 3. 数据写入

所有维度统计结果写入 `calculation_results` 表，包含字段：

- `task_id` - 任务ID
- `node_id` - 模型节点ID
- `department_id` - 科室ID
- `node_type` - 节点类型 (dimension)
- `node_name` - 节点名称
- `node_code` - 节点代码
- `parent_id` - 父节点ID
- `workload` - 工作量
- `weight` - 权重
- `original_weight` - 原始权重
- `value` - 业务价值 (workload × weight)

## 未覆盖的维度

当前有8个护理维度未在步骤中覆盖，原因是workload_statistics表中暂无对应数据：

| 代码 | 名称 | 权重 | 父维度 |
|------|------|------|--------|
| dim-nur-mon | 监测护理 | 0.05 | agn-nur |
| dim-nur-op-3 | 乙级手术管理 | 0.05 | dim-nur-op |
| dim-nur-op-4 | 甲级手术管理 | 0.08 | dim-nur-op |
| dim-nur-op-acad | 学科手术管理 | 0.10 | dim-nur-op |
| dim-nur-op-other | 其他级别手术管理 | 0.03 | dim-nur-op |
| dim-nur-or-large | 大手术护理 | 350.00 | dim-nur-or |
| dim-nur-or-mid | 中手术护理 | 180.00 | dim-nur-or |
| dim-nur-or-tiny | 小手术护理 | 15.00 | dim-nur-or |

详细信息已保存在 `nursing_uncovered_dimensions.csv` 文件中。

**建议**: 
- 如果这些维度需要统计，需要在workload_statistics表中补充对应的stat_type数据
- 或者为这些维度建立dimension_item_mappings映射，从charge_details统计

## 数据可用性

基于2023-10周期的测试数据：

- **charge_details中的护理数据**:
  - 项目数: 23
  - 记录数: 4,966
  - 总金额: 110,622.80元

- **workload_statistics中的护理数据**:
  - 记录数: 4
  - 总工作量: 3,510

- **可用科室数**: 37个 (有核算单元代码)

## 测试方法

### 方法1: 使用前端界面

1. 进入「计算流程管理」
2. 找到"医生业务价值计算流程"
3. 点击「测试」或「执行」按钮
4. 选择计算周期（如：2023-10）
5. 查看执行结果

### 方法2: 使用测试脚本

```bash
python test_nursing_workflow.py
```

## 相关文件

- `add_nursing_workflow_step.py` - 添加步骤的脚本
- `check_nursing_coverage.py` - 检查维度覆盖情况的脚本
- `test_nursing_workflow.py` - 测试步骤的脚本
- `nursing_uncovered_dimensions.csv` - 未覆盖维度的详细信息

## 下一步工作

1. **补充未覆盖维度的数据**:
   - 在workload_statistics中添加手术管理和手术室相关数据
   - 或为这些维度建立收费项目映射

2. **添加汇总步骤**:
   - 创建步骤3，汇总护理序列的非叶子节点
   - 计算床日、手术管理、手术室、出入转院等父维度的合计值

3. **完善整个计算流程**:
   - 添加其他序列的计算步骤（如药剂、医技等）
   - 添加最终汇总步骤

## 总结

护理业务价值计算步骤已成功添加到工作流31中，覆盖了12个护理维度（占总数的60%）。步骤采用双数据源策略，既利用了收费明细数据，也整合了工作量统计数据，为护理序列的业务价值评估提供了完整的计算基础。
