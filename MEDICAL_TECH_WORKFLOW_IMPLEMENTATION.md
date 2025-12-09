# 医技业务价值计算步骤实施文档

## 概述

为"业务价值计算流程"（ID: 31）添加了第三个步骤"医技业务价值计算"，用于统计医技序列各末级维度的工作量和业务价值。

## 实施内容

### 1. 计算步骤信息

- **步骤ID**: 119
- **工作流ID**: 31（业务价值计算流程）
- **步骤名称**: 医技业务价值计算
- **排序顺序**: 3.00
- **代码类型**: SQL

### 2. 覆盖的维度

医技序列（agn-tech）包含3个一级维度，共18个末级维度：

#### 检查维度（dim-tech-exam）
1. dim-tech-exam-scale - 量表检查
2. dim-tech-exam-ophth - 眼科检查
3. dim-tech-exam-ct - CT检查
4. dim-tech-exam-us - 超声检查
5. dim-tech-exam-endo - 内窥镜检查
6. dim-tech-exam-xray - X线检查
7. dim-tech-exam-other - 其他检查

#### 化验维度（dim-tech-lab）
8. dim-tech-lab-immu - 临床免疫学检验
9. dim-tech-lab-blood - 临床血液学检验
10. dim-tech-lab-chem - 临床化学检验
11. dim-tech-lab-fluid - 临床体液检验
12. dim-tech-lab-molecular - 分子病理学技术与诊断
13. dim-tech-lab-other - 其他化验
14. dim-tech-lab-micro - 临床微生物与寄生虫学检验

#### 麻醉维度（dim-tech-ana）
15. dim-tech-ana-general - 全身麻醉
16. dim-tech-ana-regional - 部位麻醉
17. dim-tech-ana-mon - 麻醉中监测
18. dim-tech-ana-other - 其他麻醉

### 3. 计算逻辑

每个末级维度的计算逻辑：

```sql
-- 从收费明细表统计工作量
SELECT
    mn.id as node_id,
    d.id as department_id,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,           -- 工作量 = 收费金额
    mn.weight,                             -- 权重（从模型节点）
    mn.weight as original_weight,          -- 原始权重
    SUM(cd.amount) * mn.weight as value,   -- 业务价值 = 工作量 × 权重
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim 
    ON cd.item_code = dim.item_code 
    AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn 
    ON dim.dimension_code = mn.code 
    AND mn.version_id = {version_id}
INNER JOIN departments d 
    ON cd.prescribing_dept_code = d.his_code 
    AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-xxx-xxx'  -- 具体维度编码
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight
```

### 4. 数据流

```
charge_details (收费明细)
    ↓ (通过 item_code 关联)
dimension_item_mappings (维度项目映射)
    ↓ (通过 dimension_code 关联)
model_nodes (模型节点 - 获取权重)
    ↓ (通过 prescribing_dept_code 关联)
departments (科室表 - HIS科室转核算单元)
    ↓
calculation_results (计算结果)
```

### 5. 参数说明

步骤使用以下参数（由任务执行时替换）：

- `{task_id}` - 计算任务ID
- `{current_year_month}` - 当期年月（格式：YYYY-MM）
- `{hospital_id}` - 医疗机构ID
- `{version_id}` - 模型版本ID

### 6. 维度映射覆盖情况

当前医疗机构（hospital_id=1）的维度映射统计：

| 维度编码 | 维度名称 | 映射项目数 |
|---------|---------|-----------|
| dim-tech-exam-scale | 量表检查 | 0 |
| dim-tech-exam-ophth | 眼科检查 | 98 |
| dim-tech-exam-ct | CT检查 | 5 |
| dim-tech-exam-us | 超声检查 | 20 |
| dim-tech-exam-endo | 内窥镜检查 | 1 |
| dim-tech-exam-xray | X线检查 | 1 |
| dim-tech-exam-other | 其他检查 | 9 |
| dim-tech-lab-immu | 临床免疫学检验 | 79 |
| dim-tech-lab-blood | 临床血液学检验 | 23 |
| dim-tech-lab-chem | 临床化学检验 | 70 |
| dim-tech-lab-fluid | 临床体液检验 | 13 |
| dim-tech-lab-molecular | 分子病理学技术与诊断 | 21 |
| dim-tech-lab-other | 其他化验 | 1 |
| dim-tech-lab-micro | 临床微生物与寄生虫学检验 | 19 |
| dim-tech-ana-general | 全身麻醉 | 6 |
| dim-tech-ana-regional | 部位麻醉 | 5 |
| dim-tech-ana-mon | 麻醉中监测 | 4 |
| dim-tech-ana-other | 其他麻醉 | 1 |

**总计**: 376个项目已映射

### 7. 未映射项目

发现1个未映射的医技相关项目，已记录在 `unmapped_medical_tech_items.csv`：

| 项目编码 | 项目名称 | 项目类别 | 建议维度 |
|---------|---------|---------|---------|
| 128000007 | 激光费 | 激光费 | dim-tech-exam-other |

**建议**: 将此项目添加到维度目录的"其他检查"维度中。

## 使用方法

### 1. 通过API创建任务

```bash
curl -X POST "http://localhost:8000/api/v1/calculation-tasks" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "version_id": 26,
    "workflow_id": 31,
    "period": "2025-10",
    "description": "测试医技业务价值计算"
  }'
```

### 2. 运行测试脚本

```bash
python test_medical_tech_workflow.py
```

测试脚本会：
1. 登录系统
2. 创建计算任务
3. 等待任务完成
4. 检查并展示计算结果统计

## 验证要点

1. **步骤执行**: 确认步骤119在工作流中正确执行
2. **数据插入**: 检查calculation_results表中是否有医技维度的记录
3. **维度覆盖**: 确认18个末级维度都有数据（如果有对应的收费明细）
4. **科室分布**: 验证各科室的医技工作量是否合理
5. **权重应用**: 确认weight字段正确应用到value计算中

## 相关文件

- `add_medical_tech_step.py` - 添加步骤的脚本
- `test_medical_tech_workflow.py` - 测试脚本
- `unmapped_medical_tech_items.csv` - 未映射项目清单

## 后续工作

1. 将未映射的"激光费"项目添加到维度目录
2. 补充中间层级节点（检查、化验、麻醉三个一级维度）
3. 补充医技序列节点（agn-tech）
4. 测试完整的树形结构查询

## 注意事项

1. **科室对照**: charge_details中的prescribing_dept_code是HIS科室编码，通过departments表的his_code字段关联到核算单元
2. **时间筛选**: 使用TO_CHAR(cd.charge_time, 'YYYY-MM')进行月份筛选
3. **多租户隔离**: 所有查询都包含hospital_id过滤
4. **叶子节点**: 只统计is_leaf=TRUE的末级维度
5. **活跃科室**: 只统计is_active=TRUE的科室

## 数据库变更

无需数据库迁移，仅在calculation_steps表中新增一条记录。

## 版本信息

- 创建日期: 2025-12-06
- 工作流版本: 26
- 步骤ID: 119
- 排序顺序: 3.00
