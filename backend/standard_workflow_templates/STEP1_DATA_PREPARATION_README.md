# 步骤1：数据准备 - 说明文档

## 概述

新增的步骤1用于从门诊和住院收费明细源表（TB_MZ_SFMXB、TB_ZY_SFMXB）提取数据，转换并生成统一的收费明细表（charge_details）。

## 字段映射关系

### charge_details 目标表结构

| 字段名 | 类型 | 说明 | 来源 |
|--------|------|------|------|
| patient_id | VARCHAR(50) | 患者ID | BRZSY（患者主索引） |
| prescribing_dept_code | VARCHAR(50) | 开单科室代码 | KDKSBM（开单科室编码） |
| item_code | VARCHAR(100) | 收费项目编码 | MXXMBM（明细项目编码） |
| item_name | VARCHAR(200) | 收费项目名称 | MXXMMC（明细项目名称） |
| amount | DECIMAL(20,4) | 金额 | MXXMSSJE（明细项目实收金额） |
| quantity | DECIMAL(20,4) | 数量 | MXXMSL（明细项目数量） |
| charge_time | TIMESTAMP | 收费时间 | FYFSSJ（费用发生时间） |
| business_type | VARCHAR(20) | 业务类别 | 固定值：'门诊' 或 '住院' |

### TB_MZ_SFMXB（门诊收费明细表）

- **业务类别**：固定标记为 `'门诊'`
- **金额字段**：使用 `MXXMSSJE`（实收金额）而非 `MXXMYSJE`（应收金额）
- **数据过滤**：只要求必填字段不为空（BRZSY、KDKSBM、MXXMBM、FYFSSJ）
- **忽略字段**：
  - `TFBZ`（退费标志）- 不处理
  - `XGBZ`（修改标志）- 不处理

### TB_ZY_SFMXB（住院收费明细表）

- **业务类别**：固定标记为 `'住院'`
- **金额字段**：使用 `MXXMSSJE`（实收金额）而非 `MXXMYSJE`（应收金额）
- **数据过滤**：只要求必填字段不为空（BRZSY、KDKSBM、MXXMBM、FYFSSJ）
- **忽略字段**：
  - `TFBZ`（退费标志）- 不处理
  - `XGBZ`（修改标志）- 不处理

## 执行流程

1. **清空现有数据**：使用 `TRUNCATE TABLE charge_details` 清空目标表
2. **插入门诊数据**：从 TB_MZ_SFMXB 提取并插入，标记为 '门诊'
3. **插入住院数据**：从 TB_ZY_SFMXB 提取并插入，标记为 '住院'
4. **返回统计信息**：按业务类别汇总记录数、患者数、科室数、项目数、金额等

## 数据处理规则

### 金额处理
- 使用 `COALESCE(MXXMSSJE, 0)` 确保金额不为 NULL
- 不处理退费标志，所有金额按原值插入

### 数量处理
- 使用 `COALESCE(MXXMSL, 0)` 确保数量不为 NULL

### 时间范围
- **不在此步骤进行时间过滤**
- 提取所有时间段的数据
- 时间范围过滤由后续步骤（步骤2）根据 `{start_date}` 和 `{end_date}` 参数处理

### 数据验证
- 必填字段检查：BRZSY、KDKSBM、MXXMBM、FYFSSJ 不能为 NULL
- 自动添加 `created_at` 时间戳

## 输出统计

执行完成后返回以下统计信息：

```sql
SELECT 
    business_type,              -- 业务类别
    COUNT(*) as record_count,   -- 记录数
    COUNT(DISTINCT patient_id) as patient_count,  -- 患者数
    COUNT(DISTINCT prescribing_dept_code) as dept_count,  -- 科室数
    COUNT(DISTINCT item_code) as item_count,  -- 项目数
    SUM(amount) as total_amount,  -- 总金额
    SUM(quantity) as total_quantity,  -- 总数量
    MIN(charge_time) as earliest_charge,  -- 最早收费时间
    MAX(charge_time) as latest_charge   -- 最晚收费时间
FROM charge_details
GROUP BY business_type;
```

## 与后续步骤的关系

### 步骤2：维度目录统计
- 从 `charge_details` 表读取数据
- 根据 `{start_date}` 和 `{end_date}` 过滤时间范围
- 使用 `business_type` 字段进行业务类别匹配
- 通过 `prescribing_dept_code` 关联科室
- 通过 `item_code` 关联收费项目映射

### 步骤3：指标工作量统计
- 从其他工作量统计表读取数据（不依赖 charge_details）

### 步骤4：业务价值汇总
- 汇总前面步骤的计算结果

## 常见问题排查

### 记录数为0
- 检查源表（TB_MZ_SFMXB、TB_ZY_SFMXB）是否有数据
- 检查字段名是否正确（注意大小写和引号）
- 检查必填字段是否有 NULL 值

### 金额异常
- 确认使用的是 MXXMSSJE（实收金额）而非 MXXMYSJE（应收金额）
- 检查源表中的金额数据是否正常

### 科室不匹配
- 检查 `prescribing_dept_code` 与系统中 `departments.his_code` 的映射关系
- 确认科室编码格式是否一致

### 业务类别分布异常
- 检查门诊和住院数据的比例是否符合预期
- 验证源表数据的业务类型分布

## 数据源配置

此步骤需要配置外部数据源，确保：

1. 数据源包含 TB_MZ_SFMXB 和 TB_ZY_SFMXB 表
2. 数据源包含 charge_details 表（目标表）
3. 数据源连接正常且有读写权限
4. 在导入工作流时使用 `--data-source-id` 参数指定数据源

## 更新历史

- **2025-11-21**：创建步骤1，从门诊和住院源表生成统一的收费明细数据
- 原步骤1-3顺延为步骤2-4
