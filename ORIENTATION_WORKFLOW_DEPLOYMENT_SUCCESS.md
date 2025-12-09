# 业务导向计算流程部署成功

## 部署时间
2025-11-27

## 部署内容

### 1. 数据库迁移
✅ 已执行迁移：`20251127_add_orientation_values`
- 创建 `orientation_values` 表
- 添加索引和约束
- 建立外键关系

### 2. 标准计算流程
✅ 已导入工作流ID：**25**
- 工作流名称：**标准计算流程-含业务导向**
- 模型版本：v1.3 (ID: 12) - 2025年迭代版-宁波眼科
- 数据源：系统数据源 (ID: 3)

### 3. 计算步骤（5个）

| 排序 | 步骤名称 | 步骤ID | 说明 |
|------|----------|--------|------|
| 1.00 | 数据准备 | 76 | 从门诊和住院收费明细表生成统一数据 |
| 2.00 | 维度目录统计 | 77 | 根据维度-收费项目映射统计工作量 |
| **3.00** | **业务导向调整** | **78** | **根据导向规则调整维度权重（新增）** |
| 3.50 | 指标计算-护理床日数 | 79 | 从工作量统计表提取护理床日数 |
| 5.00 | 业务价值汇总 | 80 | 根据模型结构和权重汇总业务价值 |

### 4. 测试结果
✅ 所有测试通过（3/3）
- ✓ 工作流结构正确
- ✓ orientation_values表结构完整
- ✓ 模型关系配置正确

## 前端访问
http://localhost/calculation-workflows/25

## 使用说明

### 准备工作

#### 1. 导入导向实际值数据
由ETL工程师将科室导向数据导入到 `orientation_values` 表：

```sql
INSERT INTO orientation_values (
    hospital_id, 
    year_month, 
    department_code, 
    department_name, 
    orientation_rule_id, 
    actual_value,
    created_at,
    updated_at
) VALUES (
    1,                    -- 医疗机构ID
    '2025-11',           -- 年月
    'DEPT001',           -- 科室代码
    '内科',              -- 科室名称
    1,                   -- 导向规则ID
    85.5,                -- 导向实际取值
    NOW(),
    NOW()
);
```

#### 2. 配置导向规则
在前端"业务导向管理"模块中：
1. 创建导向规则（选择"基准阶梯"类型）
2. 为各科室配置基准值
3. 配置阶梯区间和管控力度
4. 在模型节点管理中关联导向规则

#### 3. 创建计算任务
1. 进入"计算任务管理"
2. 创建新任务
3. 选择工作流：**标准计算流程-含业务导向**
4. 选择计算月份（确保该月份有导向实际值数据）
5. 执行任务

### 验证导向调整效果

执行任务后，查询调整后的权重：

```sql
SELECT 
    cr.node_id,
    mn.name as node_name,
    d.name as department_name,
    mn.weight as original_weight,
    cr.weight as adjusted_weight,
    ROUND(cr.weight / mn.weight, 4) as adjustment_ratio
FROM calculation_results cr
INNER JOIN model_nodes mn ON cr.node_id = mn.id
INNER JOIN departments d ON cr.department_id = d.id
WHERE cr.task_id = 'your-task-id'
  AND cr.node_type = 'dimension'
  AND mn.orientation_rule_id IS NOT NULL
ORDER BY d.name, mn.name;
```

## 核心算法

### 基准阶梯型导向

```
1. 计算导向比例
   导向比例 = 当月科室导向取值 / 科室导向基准

2. 查找管控力度
   根据导向比例从阶梯表中找到对应区间的管控力度
   区间匹配规则：[lower_limit, upper_limit)

3. 调整权重
   调整后的weight = 全院业务价值(model_nodes.weight) × 管控力度
```

### 执行流程

```
Step 1: 数据准备
  ↓ 生成 charge_details
Step 2: 维度目录统计
  ↓ 插入维度节点到 calculation_results（初始weight）
Step 3a: 业务导向调整 ⭐新增
  ↓ 更新 calculation_results 中的 weight 字段
Step 3b: 指标计算
  ↓ 插入指标数据
Step 5: 业务价值汇总
  ↓ 使用调整后的weight计算价值并插入序列节点
```

## 注意事项

1. **数据完整性**
   - 确保 orientation_values 表有对应月份的数据
   - 确保 orientation_benchmarks 表有对应科室的基准值
   - 确保 orientation_ladders 表有完整的阶梯配置

2. **可选性**
   - 未配置导向规则的维度不受影响
   - 没有导向实际值数据的科室保持原始权重
   - Step3a 可以禁用，系统会使用原始权重

3. **扩展性**
   - 当前仅实现"基准阶梯"型导向
   - 未来可扩展其他导向类型

## 相关文档

- 详细实施文档：`ORIENTATION_VALUE_CALCULATION_IMPLEMENTATION.md`
- 测试脚本：`test_orientation_workflow.py`
- 导入脚本：`backend/standard_workflow_templates/import_standard_workflow.sh`
- SQL模板：`backend/standard_workflow_templates/step3a_orientation_adjustment.sql`

## 技术支持

如有问题，请检查：
1. 数据库迁移是否完整执行
2. 导向数据是否正确导入
3. 导向规则配置是否完整
4. 计算任务日志中的错误信息

---

**部署状态**: ✅ 成功  
**测试状态**: ✅ 通过  
**可用状态**: ✅ 可用
