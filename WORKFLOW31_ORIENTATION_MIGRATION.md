# 计算流程31业务导向调整功能移植总结

## 概述

成功将计算流程30的"业务导向调整"和"业务价值汇总"两个步骤移植到计算流程31，使流程31也支持业务导向调整功能。

## 移植内容

### 源步骤（流程30）
- **步骤111**: 业务导向调整 (sort_order: 3.00, SQL长度: 8219字符)
- **步骤116**: 业务价值汇总 (sort_order: 5.00, SQL长度: 5837字符)

### 目标步骤（流程31）
- **步骤120**: 业务导向调整 (sort_order: 4.00)
- **步骤121**: 业务价值汇总 (sort_order: 5.00)

## 流程31最终步骤结构

| 步骤 | 名称 | sort_order | SQL长度 | 说明 |
|------|------|------------|---------|------|
| 117 | 医生业务价值计算 | 1.00 | 11242 | 统计医生序列各维度的工作量和业务价值 |
| 118 | 护理业务价值计算 | 2.00 | 13397 | 统计护理序列各维度的工作量和业务价值 |
| 119 | 医技业务价值计算 | 3.00 | 21288 | 统计医技序列各维度的工作量和业务价值 |
| 120 | 业务导向调整 | 4.00 | 8219 | 根据导向规则调整维度的学科业务价值 |
| 121 | 业务价值汇总 | 5.00 | 5837 | 自下而上汇总各科室的业务价值 |

## 兼容性分析

### ✅ 完全兼容，无需修改

两个步骤的SQL模板可以直接使用，原因如下：

#### 1. 数据表结构一致
- 两个流程都使用 `calculation_results` 表存储计算结果
- 表结构包含所有必需字段：`task_id`, `node_id`, `department_id`, `node_type`, `workload`, `weight`, `original_weight`, `value`

#### 2. 数据流向一致
**流程30**:
```
Step 2: 维度统计 → calculation_results (叶子维度)
Step 3: 业务导向调整 → 更新 calculation_results.weight
Step 4: 业务价值汇总 → calculation_results (序列节点)
```

**流程31**:
```
Step 1-3: 医生/护理/医技计算 → calculation_results (叶子维度)
Step 4: 业务导向调整 → 更新 calculation_results.weight
Step 5: 业务价值汇总 → calculation_results (序列节点)
```

#### 3. 占位符使用一致
两个步骤使用的占位符：
- `{task_id}` - 计算任务ID
- `{version_id}` - 模型版本ID
- `{year_month}` - 计算年月

这些占位符在流程31中同样适用。

#### 4. 树形结构处理一致
- 步骤4(业务导向调整)：只更新叶子维度节点的 `weight` 字段
- 步骤5(业务价值汇总)：
  - 从 `calculation_results` 读取叶子维度数据
  - 使用调整后的 `weight` 字段
  - 递归汇总到序列节点
  - 补充所有中间层级节点

## 关键技术点

### 1. 业务导向调整算法

```sql
-- 计算导向比例
导向比例 = 当月实际值 / 基准值

-- 查找管控力度
从阶梯表中找到比例所在的区间 → 获取adjustment_intensity

-- 调整权重
调整后weight = 原始weight × 管控力度

-- 更新calculation_results
UPDATE calculation_results 
SET weight = 调整后weight
WHERE 配置了导向规则的维度节点
```

### 2. 业务价值汇总算法

```sql
-- 加载模型结构（递归CTE）
获取所有节点的层级关系

-- 加载维度结果
从calculation_results读取叶子维度数据（使用调整后的weight）

-- 计算维度得分
得分 = 工作量 × 权重

-- 构建节点层级关系（递归CTE）
从叶子节点向上递归到所有祖先节点

-- 汇总得分
每个节点的得分 = 所有子孙节点得分之和

-- 插入序列节点
将非叶子节点（序列+中间维度）插入calculation_results
```

### 3. 关键字段说明

| 字段 | 说明 | 来源 |
|------|------|------|
| `weight` | 科室业务价值（可被调整） | Step 1-3插入，Step 4调整 |
| `original_weight` | 原始权重（不变） | Step 1-3插入时保存 |
| `workload` | 工作量 | Step 1-3统计 |
| `value` | 业务价值得分 | Step 5计算（workload × weight） |
| `node_type` | 节点类型 | 'dimension' 或 'sequence' |
| `parent_id` | 父节点ID | 用于构建树形结构 |

## 数据依赖

### 步骤4（业务导向调整）依赖

1. **导向配置数据**:
   - `orientation_rules`: 导向规则定义
   - `orientation_values`: 科室导向实际值（按年月）
   - `orientation_benchmarks`: 科室导向基准值
   - `orientation_ladders`: 导向阶梯（比例区间→管控力度）

2. **模型配置**:
   - `model_nodes.orientation_rule_ids`: 维度节点关联的导向规则ID数组

3. **计算结果**:
   - `calculation_results`: Step 1-3插入的叶子维度数据

4. **科室信息**:
   - `departments.accounting_unit_code`: 科室核算编码（用于匹配导向数据）

### 步骤5（业务价值汇总）依赖

1. **模型结构**:
   - `model_nodes`: 完整的树形结构（包含所有层级节点）

2. **计算结果**:
   - `calculation_results`: Step 1-3插入的叶子维度数据（Step 4已调整weight）

## 执行流程

### 完整计算流程

```
1. 创建计算任务
   ↓
2. Step 1: 医生业务价值计算
   → 插入医生序列的叶子维度到calculation_results
   ↓
3. Step 2: 护理业务价值计算
   → 插入护理序列的叶子维度到calculation_results
   ↓
4. Step 3: 医技业务价值计算
   → 插入医技序列的叶子维度到calculation_results
   ↓
5. Step 4: 业务导向调整
   → 根据导向规则更新calculation_results.weight
   → 记录调整明细到orientation_adjustment_details
   ↓
6. Step 5: 业务价值汇总
   → 从calculation_results读取叶子维度（使用调整后的weight）
   → 递归汇总到序列节点
   → 补充所有中间层级和序列节点到calculation_results
   ↓
7. 计算完成
   → calculation_results包含完整的树形结构数据
   → 可用于报表查询和导出
```

## 验证要点

### 1. 步骤4验证

```sql
-- 检查是否有维度被调整
SELECT COUNT(*) 
FROM orientation_adjustment_details 
WHERE task_id = '{task_id}' AND is_adjusted = TRUE;

-- 检查调整明细
SELECT 
    department_name,
    node_name,
    orientation_rule_name,
    orientation_ratio,
    adjustment_intensity,
    original_weight,
    adjusted_weight
FROM orientation_adjustment_details
WHERE task_id = '{task_id}' AND is_adjusted = TRUE;

-- 验证weight已更新
SELECT 
    cr.node_name,
    cr.weight as adjusted_weight,
    cr.original_weight,
    mn.weight as model_weight
FROM calculation_results cr
JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = '{task_id}'
  AND cr.node_type = 'dimension'
  AND cr.weight != cr.original_weight;
```

### 2. 步骤5验证

```sql
-- 检查序列节点是否插入
SELECT COUNT(*) 
FROM calculation_results 
WHERE task_id = '{task_id}' AND node_type = 'sequence';

-- 检查树形结构完整性
WITH RECURSIVE tree AS (
    SELECT node_id, parent_id, node_name, node_type, 1 as level
    FROM calculation_results
    WHERE task_id = '{task_id}' AND parent_id IS NULL
    
    UNION ALL
    
    SELECT cr.node_id, cr.parent_id, cr.node_name, cr.node_type, t.level + 1
    FROM calculation_results cr
    JOIN tree t ON cr.parent_id = t.node_id
    WHERE cr.task_id = '{task_id}'
)
SELECT node_type, COUNT(*) as count, MAX(level) as max_level
FROM tree
GROUP BY node_type;

-- 检查价值汇总是否正确
SELECT 
    node_name,
    node_type,
    SUM(value) as total_value,
    COUNT(*) as dept_count
FROM calculation_results
WHERE task_id = '{task_id}' AND node_type = 'sequence'
GROUP BY node_name, node_type
ORDER BY total_value DESC;
```

## 与流程30的差异

| 维度 | 流程30 | 流程31 |
|------|--------|--------|
| **步骤数量** | 6个步骤 | 5个步骤 |
| **维度插入** | Step 2统一插入 | Step 1-3分序列插入 |
| **调整时机** | Step 3 (sort_order 3.00) | Step 4 (sort_order 4.00) |
| **汇总时机** | Step 4 (sort_order 5.00) | Step 5 (sort_order 5.00) |
| **数据来源** | charge_details统一处理 | 按序列分别处理 |
| **业务类型** | 不区分 | 区分医生/护理/医技 |
| **SQL模板** | 通用模板 | 序列专用模板 |

## 注意事项

### 1. 导向规则配置

- 确保 `model_nodes.orientation_rule_ids` 字段已配置
- 导向规则ID必须存在于 `orientation_rules` 表
- 科室必须有对应的导向实际值和基准值

### 2. 科室核算编码

- `departments.accounting_unit_code` 必须与导向数据中的 `department_code` 匹配
- 缺少核算编码的科室不会被调整

### 3. 树形结构完整性

- Step 5会补充所有中间层级节点
- 确保 `model_nodes` 表包含完整的树形结构
- 验证 `parent_id` 关系链的完整性

### 4. 占位符替换

- 确保Celery任务正确替换所有占位符
- 特别注意 `{year_month}` 格式必须为 'YYYY-MM'

## 测试建议

### 1. 单元测试

```python
# 测试步骤4
def test_orientation_adjustment():
    # 准备导向数据
    # 执行步骤4
    # 验证weight已更新
    # 验证明细记录已插入

# 测试步骤5
def test_value_aggregation():
    # 准备维度数据
    # 执行步骤5
    # 验证序列节点已插入
    # 验证价值汇总正确
```

### 2. 集成测试

```python
# 测试完整流程
def test_workflow31_with_orientation():
    # 创建任务
    # 执行Step 1-3
    # 执行Step 4（导向调整）
    # 执行Step 5（价值汇总）
    # 验证最终结果
```

### 3. 数据验证

- 对比有无导向调整的结果差异
- 验证调整比例是否符合预期
- 检查树形结构的完整性
- 验证价值汇总的准确性

## 总结

✅ **移植成功**: 两个步骤的SQL模板完全兼容，无需修改即可在流程31中使用

✅ **数据流一致**: 流程31的数据流向与流程30完全一致，只是步骤编号不同

✅ **功能完整**: 支持完整的业务导向调整功能，包括导向比例计算、阶梯匹配、权重调整、明细记录

✅ **树形结构**: 正确处理树形数据的分步插入和汇总，确保结构完整性

## 相关文件

- `add_orientation_to_workflow31.py`: 移植脚本
- `WORKFLOW31_ORIENTATION_MIGRATION.md`: 本文档
- 流程30步骤111: 业务导向调整SQL模板
- 流程30步骤116: 业务价值汇总SQL模板
