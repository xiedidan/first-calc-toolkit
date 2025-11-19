# 科室业务价值标准计算流程 - 需求文档

## 简介

### 文档概述

本文档定义"科室业务价值标准计算流程"的需求规范。该流程基于《科室业务价值评估数据集.md》中定义的数据表(收费明细表、工作量统计表)以及系统内的表、功能和参数定义,建立一套标准化的计算流程。

### 术语表

- **System**: 科室业务价值评估系统
- **Calculation Workflow**: 计算流程,包含多个按顺序执行的计算步骤
- **Calculation Step**: 计算步骤,执行特定的SQL或Python代码以提取或计算数据
- **Data Source**: 数据源,指向外部数据库(如HIS系统、数据仓库)的连接配置
- **Charge Detail Table**: 收费明细表,记录医院所有收费业务的明细信息
- **Workload Statistics Table**: 工作量统计表,记录护理、会诊、MDT等非收费类业务指标
- **Department**: 科室,医院的组织单元
- **Dimension**: 维度,评估模型中的具体指标项
- **Business Value**: 业务价值,科室在特定周期内的评估得分
- **Current Year Month**: 当期年月,系统全局设置的计算周期

## 需求

### 需求 1: 标准计算流程定义

**用户故事:** 作为模型设计师,我希望系统提供一套标准的计算流程模板,以便快速建立符合数据集规范的业务价值计算流程

#### 验收标准

1. WHEN 用户创建新的计算流程时, THE System SHALL 提供"标准计算流程"模板选项
2. WHEN 用户选择"标准计算流程"模板时, THE System SHALL 自动创建包含以下步骤的计算流程:
   - 维度目录统计步骤
   - 指标计算步骤
   - 业务价值汇总步骤
3. THE System SHALL 为每个步骤提供标准的SQL代码模板
4. THE System SHALL 支持用户根据实际数据库结构调整SQL代码
5. THE System SHALL 验证步骤之间的依赖关系和执行顺序

### 需求 2: 维度目录统计

**用户故事:** 作为模型设计师,我希望系统能够根据维度-收费项目映射关系统计各维度的工作量,以便计算目录统计型维度的业务价值

#### 验收标准

1. WHEN 执行维度目录统计步骤时, THE System SHALL 读取dimension_item_mappings表获取维度-收费项目映射关系
2. THE System SHALL 关联收费明细数据,按维度和科室汇总金额和数量
3. THE System SHALL 处理一个收费项目可能属于多个维度的情况
4. THE System SHALL 计算每个维度在每个科室的工作量(金额、数量、人次等)
5. THE System SHALL 将统计结果存储到calculation_results表

### 需求 3: 指标计算

**用户故事:** 作为模型设计师,我希望系统能够执行自定义的指标计算逻辑,以便计算指标计算型维度的业务价值

#### 验收标准

1. WHEN 执行指标计算步骤时, THE System SHALL 读取计算步骤中配置的SQL或Python代码
2. THE System SHALL 替换代码中的占位符(如{current_year_month}、{department_id})
3. THE System SHALL 执行代码并获取返回结果
4. THE System SHALL 验证返回结果的格式(必须包含科室ID和数值字段)
5. IF 代码执行失败, THEN THE System SHALL 记录错误信息并继续执行其他步骤
6. THE System SHALL 将计算结果存储到calculation_results表

### 需求 4: 业务价值汇总

**用户故事:** 作为数据分析师,我希望系统能够根据模型结构和权重自动汇总各科室的业务价值,以便生成最终的评估结果

#### 验收标准

1. WHEN 所有维度计算完成后, THE System SHALL 执行业务价值汇总步骤
2. THE System SHALL 读取模型结构(model_nodes表)获取层级关系和权重
3. THE System SHALL 对每个科室,按照模型结构自下而上汇总得分
4. THE System SHALL 根据权重类型(百分比或固定值)计算维度得分
5. THE System SHALL 计算各序列(医生、护理、医技)的总价值
6. THE System SHALL 计算科室总价值
7. THE System SHALL 将汇总结果存储到calculation_summaries表
8. THE System SHALL 记录计算任务的完成状态和统计信息

### 需求 5: 占位符替换

**用户故事:** 作为模型设计师,我希望在SQL和Python代码中使用占位符,以便动态传递参数

#### 验收标准

1. THE System SHALL 支持以下占位符:
   - {current_year_month}: 当期年月(格式: YYYY-MM)
   - {department_id}: 科室ID
   - {department_code}: 科室编码
   - {start_date}: 开始日期(当月第一天)
   - {end_date}: 结束日期(当月最后一天)
   - {hospital_id}: 医疗机构ID
2. WHEN 执行计算步骤时, THE System SHALL 在执行代码前替换所有占位符
3. THE System SHALL 根据当期年月自动计算start_date和end_date
4. THE System SHALL 记录替换后的实际SQL代码到执行日志
