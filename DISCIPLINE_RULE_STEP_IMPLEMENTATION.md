# 学科规则调整步骤实现

## 概述

为计算流程ID34（业务价值计算流程）增加了学科规则调整步骤，用于根据学科规则系数调整特定科室-维度组合的业务价值。

## 流程变更

### 变更前
| 步骤 | 名称 | sort_order |
|------|------|------------|
| 1 | 医生业务价值计算 | 1.00 |
| 2 | 护理业务价值计算 | 2.00 |
| 3 | 医技业务价值计算 | 3.00 |
| 4 | 成本直接扣减 | 4.00 |
| 5 | 业务导向调整 | 5.00 |
| 6 | 业务价值汇总 | 6.00 |

### 变更后
| 步骤 | 名称 | sort_order |
|------|------|------------|
| 1 | 医生业务价值计算 | 1.00 |
| 2 | 护理业务价值计算 | 2.00 |
| 3 | 医技业务价值计算 | 3.00 |
| 4 | 成本直接扣减 | 4.00 |
| 5 | 业务导向调整 | 5.00 |
| **6** | **学科规则调整** | **6.00** |
| 7 | 业务价值汇总 | 7.00 |

## 学科规则调整步骤说明

### 功能
根据 `discipline_rules` 表中配置的规则系数，调整 `calculation_results` 表中对应科室-维度组合的 `weight` 和 `value` 字段。

### 算法
```
调整后的 weight = 原 weight × rule_coefficient
调整后的 value = 原 value × rule_coefficient
```

### 输入参数（占位符）
- `{task_id}` - 计算任务ID
- `{version_id}` - 模型版本ID
- `{hospital_id}` - 医疗机构ID

### 匹配条件
- 科室代码匹配：`discipline_rules.department_code = departments.his_code`
- 维度代码匹配：`discipline_rules.dimension_code = model_nodes.code`
- 版本匹配：`discipline_rules.version_id = {version_id}`
- 医院匹配：`discipline_rules.hospital_id = {hospital_id}`

## 相关文件

- `add_discipline_rule_step.py` - 添加步骤的脚本
- `test_discipline_rule_step.py` - 测试脚本
- `backend/app/models/discipline_rule.py` - 学科规则模型
- `backend/app/schemas/discipline_rule.py` - 学科规则Schema
- `backend/app/api/discipline_rules.py` - 学科规则API

## 使用方式

1. 在前端"学科规则管理"页面配置规则
2. 指定科室、维度和规则系数
3. 执行计算任务时，步骤6会自动应用这些规则

## 注意事项

1. 只有在 `discipline_rules` 表中配置了规则的科室-维度组合才会被调整
2. 未配置规则的科室-维度保持原值不变
3. 调整后的权重和价值会影响步骤7（业务价值汇总）的结果
