# 医技业务价值计算 - 快速指南

## 快速开始

### 1. 添加步骤到工作流

```bash
python add_medical_tech_step.py
```

### 2. 测试计算

```bash
python test_medical_tech_workflow.py
```

## 工作流信息

- **工作流ID**: 31
- **工作流名称**: 业务价值计算流程
- **模型版本**: 26

## 步骤顺序

1. 医生业务价值计算（步骤117）
2. 护理业务价值计算（步骤118）
3. **医技业务价值计算（步骤119）** ← 新增

## 覆盖维度

### 检查（7个）
- 量表检查、眼科检查、CT检查、超声检查、内窥镜检查、X线检查、其他检查

### 化验（7个）
- 临床免疫学检验、临床血液学检验、临床化学检验、临床体液检验
- 分子病理学技术与诊断、其他化验、临床微生物与寄生虫学检验

### 麻醉（4个）
- 全身麻醉、部位麻醉、麻醉中监测、其他麻醉

## 数据来源

```
charge_details (收费明细)
  → dimension_item_mappings (维度映射)
  → model_nodes (模型节点)
  → departments (科室对照)
  → calculation_results (计算结果)
```

## 计算公式

```
工作量 = SUM(收费金额)
业务价值 = 工作量 × 权重
```

## 验证SQL

```sql
-- 查看医技维度统计
SELECT 
    SUBSTRING(node_code FROM 'dim-tech-([^-]+)') as category,
    COUNT(*) as count,
    SUM(workload) as total_workload,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'your-task-id'
  AND node_code LIKE 'dim-tech%'
GROUP BY SUBSTRING(node_code FROM 'dim-tech-([^-]+)');

-- 查看各维度明细
SELECT 
    node_code,
    node_name,
    COUNT(*) as dept_count,
    SUM(workload) as total_workload,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'your-task-id'
  AND node_code LIKE 'dim-tech%'
GROUP BY node_code, node_name
ORDER BY node_code;
```

## 未映射项目

1个项目需要添加到维度目录：
- 激光费（128000007）→ 建议映射到"其他检查"

## 常见问题

**Q: 某个维度没有数据？**
A: 检查是否有对应的维度映射和收费明细数据

**Q: 科室数据不对？**
A: 确认departments表中的his_code与charge_details中的prescribing_dept_code匹配

**Q: 权重为0？**
A: 检查model_nodes表中对应维度的weight字段是否已设置

## 相关文件

- `add_medical_tech_step.py` - 添加步骤脚本
- `test_medical_tech_workflow.py` - 测试脚本
- `unmapped_medical_tech_items.csv` - 未映射项目
- `MEDICAL_TECH_WORKFLOW_IMPLEMENTATION.md` - 详细文档
