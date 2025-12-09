# 业务导向调整明细表设计文档

## 概述

`orientation_adjustment_details` 表用于记录业务导向调整的完整计算过程，便于追溯、验证和展示每个维度节点的调整细节。

## 表结构设计

### 1. 基础信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键 |
| `task_id` | String(50) | 计算任务ID |
| `hospital_id` | Integer | 医疗机构ID |
| `year_month` | String(7) | 计算年月（格式：YYYY-MM） |

### 2. 科室信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `department_id` | Integer | 科室ID（外键） |
| `department_code` | String(50) | 科室代码 |
| `department_name` | String(100) | 科室名称 |

### 3. 维度信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `node_id` | Integer | 模型节点ID（外键） |
| `node_code` | String(50) | 维度代码 |
| `node_name` | String(200) | 维度名称 |

### 4. 导向规则信息字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `orientation_rule_id` | Integer | 导向规则ID（外键） |
| `orientation_rule_name` | String(100) | 导向规则名称 |
| `orientation_type` | String(20) | 导向类型（benchmark_ladder/fixed_benchmark） |

### 5. 计算过程 - 输入值

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `actual_value` | Numeric(15,4) | 导向实际值（来自 orientation_values 表） |
| `benchmark_value` | Numeric(15,4) | 导向基准值（来自 orientation_benchmarks 表） |

### 6. 计算过程 - 中间结果

| 字段名 | 类型 | 说明 | 计算公式 |
|--------|------|------|----------|
| `orientation_ratio` | Numeric(10,6) | 导向比例 | `actual_value / benchmark_value` |

### 7. 计算过程 - 阶梯匹配（仅基准阶梯型）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `ladder_id` | Integer | 匹配的阶梯ID（来自 orientation_ladders 表） |
| `ladder_lower_limit` | Numeric(10,6) | 阶梯下限 |
| `ladder_upper_limit` | Numeric(10,6) | 阶梯上限 |
| `adjustment_intensity` | Numeric(10,6) | 调整力度/管控力度 |

**阶梯匹配规则**：
- 左闭右开区间：`[lower_limit, upper_limit)`
- 下限为 NULL 表示负无穷
- 上限为 NULL 表示正无穷

### 8. 计算过程 - 权重调整

| 字段名 | 类型 | 说明 | 计算公式 |
|--------|------|------|----------|
| `original_weight` | Numeric(15,4) | 原始权重（全院业务价值） | 来自 model_nodes.weight |
| `adjusted_weight` | Numeric(15,4) | 调整后权重 | `original_weight × adjustment_intensity` |

### 9. 调整状态字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `is_adjusted` | Boolean | 是否实际调整（TRUE=已调整，FALSE=未调整） |
| `adjustment_reason` | String(200) | 未调整原因（仅当 is_adjusted=FALSE 时有值） |

**未调整原因示例**：
- "缺少导向实际值"
- "缺少导向基准值"
- "基准值为0"
- "未匹配到阶梯"

### 10. 时间戳

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `created_at` | DateTime | 创建时间 |

## 完整计算流程示例

### 示例1：成功调整的记录

```
科室：内科（his_code='NK001'）
维度：门诊人次（code='MZRC'）
导向规则：门诊量导向（benchmark_ladder 类型）

输入值：
- actual_value = 5000（当月门诊人次）
- benchmark_value = 4000（基准门诊人次）

中间计算：
- orientation_ratio = 5000 / 4000 = 1.25

阶梯匹配：
- ladder_lower_limit = 1.2
- ladder_upper_limit = 1.5
- adjustment_intensity = 1.1（管控力度）

权重调整：
- original_weight = 100（全院业务价值）
- adjusted_weight = 100 × 1.1 = 110

结果：
- is_adjusted = TRUE
- adjustment_reason = NULL
```

### 示例2：未调整的记录（缺少实际值）

```
科室：外科（his_code='WK001'）
维度：手术台次（code='SSTC'）
导向规则：手术量导向

输入值：
- actual_value = NULL（未录入当月数据）
- benchmark_value = 200

中间计算：
- orientation_ratio = NULL

阶梯匹配：
- 无法匹配

权重调整：
- original_weight = 150
- adjusted_weight = NULL

结果：
- is_adjusted = FALSE
- adjustment_reason = "缺少导向实际值"
```

## 数据流向

```
配置数据（用户输入）
├── orientation_rules（导向规则）
├── orientation_benchmarks（基准值）
└── orientation_ladders（阶梯）

实际数据（业务数据）
└── orientation_values（实际值）

计算过程（自动生成）
└── orientation_adjustment_details（调整明细）
    ├── 记录完整计算过程
    └── 标记是否成功调整

最终结果（更新）
└── calculation_results.weight（更新权重）
```

## SQL 使用

### 新版 SQL 文件

使用 `step3a_orientation_adjustment_with_details.sql` 替代原来的 `step3a_orientation_adjustment.sql`

**主要改进**：
1. 插入完整的调整明细记录
2. 记录未调整的原因
3. 返回详细的统计信息

### 查询示例

#### 1. 查看某个任务的所有调整明细

```sql
SELECT 
    department_name,
    node_name,
    actual_value,
    benchmark_value,
    orientation_ratio,
    adjustment_intensity,
    original_weight,
    adjusted_weight,
    is_adjusted,
    adjustment_reason
FROM orientation_adjustment_details 
WHERE task_id = 'xxx'
ORDER BY department_name, node_name;
```

#### 2. 查看某个科室的调整情况

```sql
SELECT 
    node_name,
    orientation_rule_name,
    actual_value,
    benchmark_value,
    orientation_ratio,
    CONCAT('[', ladder_lower_limit, ', ', ladder_upper_limit, ')') as ladder_range,
    adjustment_intensity,
    original_weight,
    adjusted_weight
FROM orientation_adjustment_details 
WHERE task_id = 'xxx' 
  AND department_code = 'NK001'
  AND is_adjusted = TRUE;
```

#### 3. 查看未调整的记录及原因

```sql
SELECT 
    department_name,
    node_name,
    orientation_rule_name,
    adjustment_reason,
    COUNT(*) as count
FROM orientation_adjustment_details 
WHERE task_id = 'xxx' 
  AND is_adjusted = FALSE
GROUP BY department_name, node_name, orientation_rule_name, adjustment_reason
ORDER BY count DESC;
```

#### 4. 查看调整前后对比

```sql
SELECT 
    department_name,
    node_name,
    original_weight,
    adjusted_weight,
    (adjusted_weight - original_weight) as weight_change,
    ROUND((adjusted_weight - original_weight) / original_weight * 100, 2) as change_percent,
    adjustment_intensity
FROM orientation_adjustment_details 
WHERE task_id = 'xxx' 
  AND is_adjusted = TRUE
ORDER BY ABS(adjusted_weight - original_weight) DESC
LIMIT 20;
```

#### 5. 统计各导向规则的调整效果

```sql
SELECT 
    orientation_rule_name,
    COUNT(*) as total_count,
    SUM(CASE WHEN is_adjusted THEN 1 ELSE 0 END) as adjusted_count,
    ROUND(AVG(CASE WHEN is_adjusted THEN adjustment_intensity END), 4) as avg_intensity,
    ROUND(AVG(CASE WHEN is_adjusted THEN adjusted_weight - original_weight END), 2) as avg_weight_change
FROM orientation_adjustment_details 
WHERE task_id = 'xxx'
GROUP BY orientation_rule_name;
```

## 前端展示建议

### 1. 调整明细列表页

**表格列**：
- 科室名称
- 维度名称
- 导向规则
- 实际值
- 基准值
- 导向比例
- 调整力度
- 原始权重
- 调整后权重
- 权重变化
- 状态（已调整/未调整）

**筛选条件**：
- 科室
- 维度
- 导向规则
- 调整状态

### 2. 调整详情对话框

展示单条记录的完整计算过程：

```
【基础信息】
科室：内科
维度：门诊人次
导向规则：门诊量导向（基准阶梯型）

【计算过程】
步骤1：获取输入值
  - 实际值：5,000 人次
  - 基准值：4,000 人次

步骤2：计算导向比例
  - 导向比例 = 5,000 ÷ 4,000 = 1.25

步骤3：匹配阶梯
  - 匹配阶梯：[1.2, 1.5)
  - 调整力度：1.1

步骤4：计算调整后权重
  - 原始权重：100.00
  - 调整后权重 = 100.00 × 1.1 = 110.00
  - 权重变化：+10.00 (+10.00%)

【调整结果】
✓ 已成功调整
```

### 3. 统计图表

- **饼图**：调整成功率（已调整 vs 未调整）
- **柱状图**：各科室的平均调整力度
- **散点图**：导向比例 vs 调整力度
- **热力图**：科室×维度的调整效果矩阵

## 注意事项

1. **数据完整性**：确保 orientation_values 和 orientation_benchmarks 数据完整
2. **阶梯配置**：阶梯区间不能有重叠或遗漏
3. **性能优化**：task_id 上有索引，查询时优先使用
4. **数据清理**：定期清理历史任务的明细数据
5. **多租户隔离**：所有查询都要加 hospital_id 过滤

## 相关表关系

```
orientation_adjustment_details
├── hospital_id → hospitals.id
├── department_id → departments.id
├── node_id → model_nodes.id
└── orientation_rule_id → orientation_rules.id

关联查询：
├── orientation_values（实际值）
├── orientation_benchmarks（基准值）
└── orientation_ladders（阶梯）
```

## 版本历史

- **v1.0** (2025-11-28): 初始版本，支持基准阶梯型导向的完整记录
