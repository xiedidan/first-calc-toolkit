# 实施计划

- [x] 1. 创建标准流程模板目录结构


  - 在backend目录下创建standard_workflow_templates文件夹
  - _需求: 1.1_

- [x] 2. 编写步骤1 SQL代码: 维度目录统计


  - [x] 2.1 编写dimension_mappings CTE获取维度-收费项目映射


    - 关联dimension_item_mappings和model_nodes表
    - 筛选指定模型版本的映射关系
    - _需求: 2.1, 2.2_
  - [x] 2.2 编写charge_data CTE提取收费明细数据


    - 从charge_details表提取指定周期的数据
    - 按科室和收费项目汇总金额、数量、人次
    - 使用占位符{start_date}, {end_date}, {hospital_id}
    - _需求: 2.1, 2.2, 5.1, 5.2_
  - [x] 2.3 编写主查询关联映射和收费数据


    - 关联dimension_mappings和charge_data
    - 关联departments表获取科室ID
    - 按维度和科室汇总工作量
    - 输出dimension_id, department_id, workload_amount, workload_quantity, workload_patient_count
    - _需求: 2.2, 2.3, 2.4, 2.5_

- [x] 3. 编写步骤2 SQL代码: 指标计算示例


  - [x] 3.1 编写护理床日数统计SQL


    - 从workload_statistics表提取护理床日数
    - 关联departments表获取科室ID
    - 汇总各级护理床日数
    - 使用占位符{current_year_month}, {hospital_id}, {dimension_id}
    - 输出dimension_id, department_id, workload_value
    - _需求: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2_
  - [x] 3.2 添加SQL注释说明如何扩展更多指标


    - 说明如何复制此步骤创建新指标
    - 列举常见指标示例(会诊、MDT、出院人次)
    - _需求: 3.1_

- [x] 4. 编写步骤3 SQL代码: 业务价值汇总


  - [x] 4.1 编写model_structure CTE加载模型结构


    - 从model_nodes表加载指定版本的节点
    - 包含层级关系、权重、权重类型
    - _需求: 4.2_
  - [x] 4.2 编写dimension_results CTE加载维度计算结果


    - 从calculation_results表加载指定任务的结果
    - 关联模型节点获取权重信息
    - _需求: 4.2_
  - [x] 4.3 编写dimension_scores CTE计算维度得分


    - 根据权重类型(百分比/固定值)计算得分
    - 百分比: 得分 = 工作量 × 权重
    - 固定值: 得分 = 工作量 × 单价
    - _需求: 4.3, 4.4_
  - [x] 4.4 编写aggregated_scores递归CTE实现自下而上汇总


    - 递归计算父节点得分
    - 父节点得分 = Σ(子节点得分)
    - _需求: 4.3_
  - [x] 4.5 编写主查询提取序列得分和科室总价值


    - 提取医生、护理、医技序列得分
    - 计算科室总价值
    - 输出task_id, department_id, doctor_value, nursing_value, medical_tech_value, total_value
    - _需求: 4.5, 4.6, 4.7, 4.8_

- [x] 5. 编写导入脚本


  - [x] 5.1 实现.env文件读取功能


    - 解析backend/.env文件
    - 提取DATABASE_*变量
    - 验证必需变量存在
    - _需求: 1.1_
  - [x] 5.2 实现命令行参数解析


    - 解析--version-id参数(必填)
    - 解析--workflow-name参数(可选)
    - 验证参数有效性
    - _需求: 1.1_
  - [x] 5.3 实现数据库连接测试


    - 使用psql测试连接
    - 输出连接状态
    - 连接失败时退出
    - _需求: 1.1_
  - [x] 5.4 实现模型版本验证


    - 查询model_versions表
    - 验证版本ID存在
    - 版本不存在时退出
    - _需求: 1.1_
  - [x] 5.5 实现SQL文件读取


    - 读取3个SQL文件内容
    - 处理文件不存在的情况
    - _需求: 1.1_
  - [x] 5.6 实现计算流程创建


    - INSERT INTO calculation_workflows
    - 获取生成的workflow_id
    - _需求: 1.1, 1.2_
  - [x] 5.7 实现计算步骤创建


    - INSERT INTO calculation_steps (3条记录)
    - 设置正确的sort_order
    - 将SQL代码写入code_content字段
    - _需求: 1.1, 1.2_
  - [x] 5.8 实现导入结果输出


    - 输出流程ID、名称、步骤数量
    - 输出前端访问URL
    - 格式化输出便于阅读
    - _需求: 1.1_

- [x] 6. 编写README文档



  - [x] 6.1 编写简介和文件说明


    - 说明目录用途
    - 列出所有文件及其功能
    - _需求: 1.1_
  - [x] 6.2 编写快速开始指南


    - 准备工作清单
    - 导入步骤说明
    - 调整SQL代码指南
    - 前端查看和使用说明
    - _需求: 1.1_
  - [x] 6.3 编写SQL代码说明


    - 每个步骤的功能说明
    - 关键逻辑解释
    - 占位符说明
    - 扩展指南
    - _需求: 2.1, 3.1, 4.1, 5.1_
  - [x] 6.4 编写常见问题解答


    - 导入失败处理
    - SQL执行错误处理
    - 如何添加更多步骤
    - 占位符使用说明
    - _需求: 1.1_

- [ ] 7. 测试和验证
  - [ ] 7.1 测试SQL代码语法
    - 在测试数据库中执行SQL
    - 验证语法正确性
    - 验证占位符替换
    - _需求: 2.1, 3.1, 4.1_
  - [ ] 7.2 测试导入脚本
    - 测试.env文件读取
    - 测试参数解析
    - 测试数据库连接
    - 测试流程创建
    - _需求: 1.1_
  - [ ] 7.3 集成测试
    - 执行完整导入流程
    - 在前端查看导入的流程
    - 创建计算任务并执行
    - 验证计算结果正确性
    - _需求: 1.1, 2.1, 3.1, 4.1_
