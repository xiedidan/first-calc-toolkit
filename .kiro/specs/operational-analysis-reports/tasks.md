# 实现计划

- [x] 1. 创建数据库模型和迁移





  - [x] 1.1 创建 AnalysisReport 数据模型


    - 在 `backend/app/models/` 目录下创建 `analysis_report.py`
    - 定义字段：id, hospital_id, department_id, period, current_issues, future_plans, created_at, updated_at, created_by
    - 添加与 Hospital、Department、User 的关系
    - _需求: 8.1, 8.2_
  - [x] 1.2 创建 Alembic 数据库迁移文件


    - 创建 `analysis_reports` 表
    - 添加唯一约束 (hospital_id, department_id, period)
    - 创建索引
    - _需求: 5.1, 7.7_
  - [x] 1.3 更新 models/__init__.py 导出新模型


    - _需求: 1.1_




- [x] 2. 创建后端 Schema 和 API
  - [x] 2.1 创建 Schema 定义

    - 在 `backend/app/schemas/` 目录下创建 `analysis_report.py`
    - 定义 AnalysisReportBase, AnalysisReportCreate, AnalysisReportUpdate, AnalysisReport
    - 定义 ValueDistributionItem, BusinessContentItem
    - 添加字段验证（Markdown内容长度限制2000字符）
    - _需求: 6.5, 6.6_
  - [ ]* 2.2 编写属性测试：Markdown内容长度验证
    - **属性 6: Markdown内容长度验证**
    - **验证需求: 6.5, 6.6**

  - [x] 2.3 创建 API 路由

    - 在 `backend/app/api/` 目录下创建 `analysis_reports.py`
    - 实现 GET /analysis-reports（列表，支持分页、排序、筛选）
    - 实现 GET /analysis-reports/{id}（详情）
    - 实现 POST /analysis-reports（创建）
    - 实现 PUT /analysis-reports/{id}（更新）
    - 实现 DELETE /analysis-reports/{id}（删除）
    - _需求: 2.1, 5.1, 5.2, 5.3, 5.4, 5.5_
  - [ ]* 2.4 编写属性测试：多租户医疗机构隔离
    - **属性 1: 多租户医疗机构隔离**
    - **验证需求: 8.1, 8.2, 8.3, 8.4**
  - [ ]* 2.5 编写属性测试：报告唯一性约束
    - **属性 7: 报告唯一性约束**
    - **验证需求: 5.1**

  - [x] 2.6 实现科室用户访问控制
    - 科室用户只能查看自己科室的报告
    - 管理员可以查看所有报告
    - _需求: 3.1, 3.2, 3.3_
  - [ ]* 2.7 编写属性测试：科室用户访问控制
    - **属性 2: 科室用户访问控制**

    - **验证需求: 3.1, 3.2, 3.3**
  - [x] 2.8 注册 API 路由到主应用


    - 在 `backend/app/main.py` 中注册路由
    - _需求: 1.1_

-

- [x] 3. 检查点 - 确保所有测试通过



  - 确保所有测试通过，如有问题请询问用户。
-

- [x] 4. 实现价值分布和业务内涵查询



  - [x] 4.1 实现科室主业价值分布查询 API

    - 实现 GET /analysis-reports/{id}/value-distribution
    - 从 calculation_results 表提取 Top 10 维度
    - 计算占比
    - _需求: 4.3, 7.1, 7.4_
  - [ ]* 4.2 编写属性测试：价值分布数据提取
    - **属性 4: 价值分布数据提取**
    - **验证需求: 4.3, 7.1, 7.4**

  - [x] 4.3 实现科室业务内涵查询 API

    - 实现 GET /analysis-reports/{id}/business-content
    - 从 charge_details 表提取 Top 20 业务项目
    - 关联 Top 10 维度
    - _需求: 4.4, 7.2, 7.5_
  - [ ]* 4.4 编写属性测试：业务内涵数据提取
    - **属性 5: 业务内涵数据提取**
    - **验证需求: 4.4, 7.2, 7.5**

- [x] 5. 检查点 - 确保所有测试通过





  - 确保所有测试通过，如有问题请询问用户。

- [x] 6. 创建前端 API 模块





  - [x] 6.1 创建前端 API 接口定义

    - 在 `frontend/src/api/` 目录下创建 `analysis-reports.ts`
    - 定义 TypeScript 接口
    - 实现 API 调用函数
    - _需求: 2.1, 4.1_

- [x] 7. 创建前端页面组件







  - [x] 7.1 配置菜单和路由


    - 在 `frontend/src/config/menus.ts` 添加运营分析报告菜单
    - 添加两个子菜单：分析报告查看、分析报告管理
    - 配置路由
    - _需求: 1.1, 1.2, 1.3, 1.4_

  - [x] 7.2 创建分析报告查看页面 (ReportView.vue)

    - 实现报告列表展示
    - 实现排序、筛选、搜索功能
    - 实现分页
    - 实现科室用户数据过滤（前端配合后端）
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 9.1, 9.2, 9.3, 9.4_
  - [ ]* 7.3 编写属性测试：列表查询操作
    - **属性 3: 列表查询操作**
    - **验证需求: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**
  - [ ]* 7.4 编写属性测试：分页行为
    - **属性 8: 分页行为**
    - **验证需求: 9.1, 9.2, 9.3, 9.4**

  - [x] 7.5 创建报告详情模态框 (ReportDetailModal.vue)








    - 展示科室主业价值分布（Top 10维度列表）
    - 展示科室业务内涵（Top 20业务项目列表）
    - 展示当前存在问题（Markdown渲染）
    - 展示未来发展计划（Markdown渲染）
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

-

- [x] 8. 创建分析报告管理页面




  - [x] 8.1 创建分析报告管理页面 (ReportManagement.vue)

    - 实现报告列表展示（与查看页面类似）
    - 添加编辑和删除操作按钮
    - 实现删除确认对话框
    - _需求: 5.1, 5.2, 5.4, 5.5_
  - [ ]* 8.2 编写属性测试：报告删除一致性
    - **属性 9: 报告删除一致性**
    - **验证需求: 5.5**

  - [x] 8.3 安装 Markdown 编辑器依赖

    - 安装 md-editor-v3 包
    - _需求: 6.3, 6.4_

  - [x] 8.4 创建报告编辑模态框 (ReportEditModal.vue)

    - 展示科室主业价值分布（只读）
    - 展示科室业务内涵（只读）
    - 集成 Markdown 编辑器编辑当前存在问题
    - 集成 Markdown 编辑器编辑未来发展计划
    - 实现字符数限制（2000字符）
    - 实现保存功能
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 9. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 10. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。
