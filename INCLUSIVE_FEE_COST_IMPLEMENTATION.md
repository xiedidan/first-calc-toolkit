# 内含式收费成本计算步骤实现

## 功能概述

在工作流39中添加了"内含式收费成本计算"步骤，用于将内含式收费项目的成本累加到科室的"不收费卫生材料费"维度。

## 前端管理页面

新增"内含收费管理"页面，位于"评估模型管理"菜单下，成本基准管理之后。

- 路由：`/inclusive-fees`
- 功能：对 `dim_inclusive_fees` 表进行 CRUD 操作
- 支持按项目代码/名称搜索

## 数据流

```
dim_inclusive_fees (内含式收费项目表)
        ↓
    item_code + cost
        ↓
charge_details (收费明细表)
        ↓
    按科室汇总 (quantity * cost)
        ↓
cost_values (成本值表)
    → 更新 dim-*-cost-mat 维度
```

## 表结构

### dim_inclusive_fees
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 主键 |
| item_code | varchar(255) | 收费项目代码 |
| item_name | varchar(255) | 收费项目名称 |
| cost | numeric(10,2) | 单位成本 |

### 关联逻辑
- `dim_inclusive_fees.item_code` → `charge_details.item_code`
- `charge_details.prescribing_dept_code` → `departments.his_code`
- `departments.accounting_unit_code` → `cost_values.dept_code`

## 计算步骤

| 序号 | 步骤ID | 名称 |
|------|--------|------|
| 0.50 | 174 | 生成核算明细 |
| 1.00 | 175 | 医生业务价值计算 |
| 2.00 | 176 | 护理业务价值计算 |
| 3.00 | 177 | 医技业务价值计算 |
| **3.50** | **182** | **内含式收费成本计算** |
| 4.00 | 178 | 成本直接扣减 |
| 5.00 | 179 | 业务导向调整 |
| 6.00 | 180 | 学科规则调整 |
| 7.00 | 181 | 业务价值汇总 |

## SQL 逻辑

1. 从 `dim_inclusive_fees` 获取内含式收费项目及其单位成本
2. 关联 `charge_details` 中的收费记录
3. 按科室汇总：`SUM(quantity * cost)`
4. 根据科室的核算序列，更新对应的 cost_values：
   - 医生序列 → `dim-doc-cost-mat`
   - 护理序列 → `dim-nur-cost-mat`
   - 医技序列 → `dim-tech-cost-mat`

## 使用方法

### 1. 添加内含式收费项目
```sql
INSERT INTO dim_inclusive_fees (item_code, item_name, cost)
VALUES ('128100138', '三棱镜检查', 5.00);
```

### 2. 运行计算任务
通过工作流39执行计算任务，内含式收费成本会自动累加到对应科室的材料费维度。

## 注意事项

1. `dim_inclusive_fees` 表为全局表，不区分医院
2. 成本累加是增量操作，会在原有 cost_values 基础上增加
3. 只有 `is_active = true` 且有 `accounting_unit_code` 的科室才会被计算
