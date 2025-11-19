# 维度统计测试数据生成模块 - 需求文档

## 简介

本文档定义了维度统计测试数据生成模块的需求。该模块是医院科室业务价值评估工具的辅助功能，用于根据约束条件（全院总收入、科室总额、维度比例等）直接生成指定年月每个科室每个末级维度的统计数据，写入维度统计表（dws_adv_dimension_points），为业务价值报表提供高仿真的演示数据。生成的维度统计数据将通过现有的计算流程进行维度收入加成计算，最终写入计算结果表，支持科室业务价值汇总和科室明细（结构表）的展示。

## 术语表

- **TestDataGenerationModule**: 维度统计测试数据生成模块，负责生成符合约束条件的维度统计数据
- **DimensionStatisticsTable**: 维度统计表（dws_adv_dimension_points），存储生成的维度统计数据（按科室和维度聚合）
- **CalculationResultsTable**: 计算结果表（calculation_results），存储经过计算流程处理后的业务价值数据
- **LeafDimensionNode**: 末级维度节点，模型结构中的叶子节点，代表具体的业务维度
- **DepartmentRevenueConstraint**: 科室收入约束，指定某个科室的总收入额度
- **DimensionRevenueAmount**: 维度收入金额，指定某个维度的收入金额
- **DimensionRevenueRatio**: 维度收入比例，指定某个维度在科室总收入中的占比
- **HospitalTotalRevenue**: 全院总收入，所有科室收入的总和
- **TargetYearMonth**: 目标年月，数据生成的目标时间周期（格式：YYYYMM）

## 需求

### 需求 1: 生成任务配置

**用户故事**: 作为数据分析师，我希望能够配置维度统计数据生成的约束条件，以便生成符合业务场景的测试数据

#### 验收标准

1. WHEN 用户创建数据生成任务时，THE TestDataGenerationModule SHALL 允许用户指定目标年月（TargetYearMonth）
2. WHEN 用户配置约束条件时，THE TestDataGenerationModule SHALL 允许用户指定全院总收入（HospitalTotalRevenue）
3. WHEN 用户配置约束条件时，THE TestDataGenerationModule SHALL 允许用户选择模型版本，以确定维度结构
4. WHEN 用户配置科室约束时，THE TestDataGenerationModule SHALL 允许用户为每个科室指定总收入额度（DepartmentRevenueConstraint）
5. WHEN 用户配置维度金额时，THE TestDataGenerationModule SHALL 允许用户为每个科室的每个末级维度指定收入金额（DimensionRevenueAmount）或收入占比（DimensionRevenueRatio）
6. WHERE 用户未指定科室总额时，THE TestDataGenerationModule SHALL 根据全院总收入和参与评估的科室数量自动平均分配科室总额

### 需求 2: 维度统计数据生成算法

**用户故事**: 作为系统开发者，我希望系统能够根据约束条件智能生成维度统计数据，以便确保生成的数据符合业务逻辑

#### 验收标准

1. WHEN 执行数据生成任务时，THE TestDataGenerationModule SHALL 根据选定的模型版本加载所有末级维度节点（LeafDimensionNode）
2. WHEN 计算维度收入时，THE TestDataGenerationModule SHALL 根据科室总额和维度收入比例计算每个维度的收入金额
3. WHERE 用户未指定维度比例时，THE TestDataGenerationModule SHALL 根据维度权重自动计算维度比例
4. WHEN 生成维度统计数据时，THE TestDataGenerationModule SHALL 确保科室所有维度的收入总和等于科室总额（误差小于1元）
5. WHEN 生成维度统计数据时，THE TestDataGenerationModule SHALL 为每个科室的每个末级维度生成一条统计记录

### 需求 3: 维度统计表数据写入

**用户故事**: 作为数据分析师，我希望生成的维度统计数据能够写入维度统计表，以便后续通过计算流程生成业务价值报表

#### 验收标准

1. WHEN 数据生成完成时，THE TestDataGenerationModule SHALL 将生成的维度统计数据写入DimensionStatisticsTable（dws_adv_dimension_points表）
2. WHEN 写入维度统计数据时，THE TestDataGenerationModule SHALL 包含必需字段：年月（year_month）、科室ID（department_id）、维度ID（dimension_id）、收入金额（revenue_amount）
3. WHEN 写入数据前，THE TestDataGenerationModule SHALL 检查目标年月是否已存在测试数据
4. WHERE 目标年月已存在测试数据时，THE TestDataGenerationModule SHALL 提示用户选择覆盖或取消操作
5. WHEN 数据写入失败时，THE TestDataGenerationModule SHALL 回滚所有已写入的数据，保持数据一致性
6. WHEN 写入维度统计数据时，THE TestDataGenerationModule SHALL 为每条记录添加测试数据标识（is_test_data字段），以便后续追踪和删除

### 需求 4: 生成数据质量验证

**用户故事**: 作为数据分析师，我希望系统能够验证生成的维度统计数据质量，以便确保数据的准确性和完整性

#### 验收标准

1. WHEN 数据生成完成时，THE TestDataGenerationModule SHALL 验证全院总收入是否等于所有科室收入之和（误差小于科室数量）
2. WHEN 验证科室数据时，THE TestDataGenerationModule SHALL 验证每个科室的总收入是否等于所有维度收入之和（误差小于1元）
3. WHEN 验证维度数据时，THE TestDataGenerationModule SHALL 验证每个维度的收入金额是否符合配置的约束条件
4. WHEN 验证完成时，THE TestDataGenerationModule SHALL 生成验证报告，包含总收入、科室数量、维度数量、统计记录数量
5. IF 验证失败，THEN THE TestDataGenerationModule SHALL 记录详细的错误信息并阻止数据写入

### 需求 5: 生成任务管理

**用户故事**: 作为数据分析师，我希望能够管理维度统计数据生成任务，以便跟踪任务状态和查看生成结果

#### 验收标准

1. WHEN 用户创建数据生成任务时，THE TestDataGenerationModule SHALL 创建任务记录并返回任务ID
2. WHEN 任务执行时，THE TestDataGenerationModule SHALL 更新任务状态（排队中、运行中、已完成、失败）
3. WHEN 任务执行过程中，THE TestDataGenerationModule SHALL 记录执行日志，包含每个步骤的开始时间、结束时间、处理数量
4. WHEN 任务完成时，THE TestDataGenerationModule SHALL 记录生成的数据统计信息（科室数量、维度数量、统计记录数量、总金额）
5. WHEN 任务失败时，THE TestDataGenerationModule SHALL 记录详细的错误信息和堆栈跟踪
6. THE TestDataGenerationModule SHALL 支持取消正在运行的数据生成任务

### 需求 6: 数据生成用户界面

**用户故事**: 作为数据分析师，我希望有一个友好的界面来配置和执行维度统计数据生成任务，以便快速生成测试数据

#### 验收标准

1. THE TestDataGenerationModule SHALL 提供数据生成任务创建页面，包含约束条件配置表单
2. WHEN 用户选择模型版本时，THE TestDataGenerationModule SHALL 自动加载该版本的所有参与评估的科室和末级维度
3. WHEN 用户配置科室总额时，THE TestDataGenerationModule SHALL 实时显示已分配总额和剩余总额
4. WHEN 用户配置维度金额或比例时，THE TestDataGenerationModule SHALL 实时显示科室的维度比例总和（应等于100%）
5. THE TestDataGenerationModule SHALL 提供任务列表页面，显示所有历史任务的状态和统计信息
6. THE TestDataGenerationModule SHALL 在任务列表页面提供查看详细日志和验证报告的功能

### 需求 7: 数据生成高级功能

**用户故事**: 作为数据分析师，我希望系统提供高级功能，以便生成更加真实和多样化的测试数据

#### 验收标准

1. WHERE 用户启用随机波动功能时，THE TestDataGenerationModule SHALL 在维度收入基础上增加随机波动（±5%）
2. WHERE 用户启用多月生成功能时，THE TestDataGenerationModule SHALL 支持一次生成连续多个月的维度统计数据
3. WHERE 用户启用模板功能时，THE TestDataGenerationModule SHALL 支持保存和加载约束条件模板
4. WHERE 用户启用导入功能时，THE TestDataGenerationModule SHALL 支持从Excel导入约束条件配置
5. WHERE 用户启用导出功能时，THE TestDataGenerationModule SHALL 支持将约束条件配置导出为Excel文件
