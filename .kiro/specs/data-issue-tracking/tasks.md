# Implementation Plan - 数据问题记录功能

## 任务列表

- [x] 1. 创建数据库模型和Schema


  - 创建DataIssue模型类，包含所有必需字段和关系映射
  - 创建ProcessingStage枚举类
  - 创建Pydantic Schema类（DataIssueBase, DataIssueCreate, DataIssueUpdate, DataIssue）
  - 在models/__init__.py中注册新模型
  - _Requirements: 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_



- [x] 2. 创建数据库迁移脚本

  - 使用Alembic创建data_issues表的迁移脚本
  - 包含所有字段定义、外键约束和索引
  - 验证迁移脚本可以正确执行


  - _Requirements: 1.4, 4.1, 8.1_

- [ ] 3. 实现后端API路由
  - [x] 3.1 实现GET /api/data-issues接口（列表查询）

    - 实现分页功能（page, size参数）
    - 实现关键词搜索（keyword参数，搜索标题和描述）


    - 实现处理阶段筛选（processing_stage参数）
    - 实现多租户数据隔离（基于hospital_id）
    - 返回符合Schema的JSON响应
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 3.2 实现POST /api/data-issues接口（创建问题）


    - 验证必填字段（title, description, reporter）
    - 自动设置hospital_id为当前用户所属医疗机构
    - 自动设置created_at为当前时间
    - 默认processing_stage为"not_started"
    - 返回创建的问题记录


    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1_

  - [x] 3.3 实现GET /api/data-issues/{id}接口（获取详情）

    - 根据ID查询问题记录
    - 验证问题记录存在性
    - 验证用户有权访问该问题（hospital_id匹配）


    - 返回完整的问题详情
    - _Requirements: 9.3_

  - [x] 3.4 实现PUT /api/data-issues/{id}接口（更新问题）


    - 验证问题记录存在性和访问权限
    - 支持部分字段更新
    - 当processing_stage更新为"resolved"时，自动设置resolved_at


    - 验证processing_stage为"resolved"时resolution必填
    - 自动更新updated_at
    - _Requirements: 6.2, 6.3, 6.4, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 10.1, 10.2_



  - [x] 3.5 实现DELETE /api/data-issues/{id}接口（删除问题）

    - 验证问题记录存在性和访问权限
    - 执行物理删除
    - 返回204 No Content
    - _Requirements: 10.3, 10.4, 10.5_



  - [x] 3.6 在api/__init__.py中注册data_issues路由

    - 导入data_issues模块
    - 在__all__中添加data_issues
    - _Requirements: 1.1_

  - [x] 3.7 在main.py中注册API路由

    - 使用app.include_router注册/api/data-issues路由


    - 设置tags为["data-issues"]
    - _Requirements: 1.1_

- [x] 4. 创建前端API客户端

  - 创建dataIssue.ts文件定义API接口

  - 定义DataIssue TypeScript接口
  - 实现getDataIssueList、createDataIssue、getDataIssue、updateDataIssue、deleteDataIssue函数
  - 使用统一的request实例发送HTTP请求
  - _Requirements: 1.1, 1.2, 1.3, 9.1, 10.1, 10.3_

- [x] 5. 实现用户选择器组件

  - [x] 5.1 创建UserSelector.vue组件

    - 使用el-autocomplete实现自动完成功能
    - 支持v-model双向绑定显示值
    - 支持userId prop和update:userId事件
    - 实现用户搜索功能（调用getUserList API）
    - 支持手动输入文本
    - 支持清除选择
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5_


- [ ] 6. 实现数据问题记录页面
  - [x] 6.1 创建DataIssues.vue基础结构

    - 创建页面组件框架
    - 使用el-card包裹页面内容
    - 添加卡片头部（标题 + 新建按钮）

    - 参照Users.vue的样式保持一致性
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 6.2 实现搜索和筛选功能

    - 创建搜索表单（关键词、处理阶段筛选）
    - 实现搜索按钮点击事件
    - 实现重置按钮功能
    - 搜索时重置页码为1
    - _Requirements: 9.4, 9.5_

  - [x] 6.3 实现问题列表表格

    - 使用el-table显示问题列表
    - 显示ID、标题、记录人、负责人、处理阶段、记录时间列
    - 负责人为空时显示"待定"
    - 处理阶段使用el-tag显示，不同阶段不同颜色
    - 添加操作列（编辑、删除按钮）
    - 实现loading状态
    - _Requirements: 9.1, 9.2, 9.3, 5.6_


  - [x] 6.4 实现分页功能

    - 使用el-pagination组件
    - 支持页码和每页数量切换
    - 显示总记录数
    - 样式与Users.vue保持一致
    - _Requirements: 9.5_


  - [x] 6.5 实现新增/编辑对话框

    - 创建el-dialog组件
    - 创建表单（标题、问题描述、记录人、负责人、处理阶段、解决方案）
    - 标题和问题描述为必填字段
    - 记录人使用UserSelector组件（必填）
    - 负责人使用UserSelector组件（可选）
    - 处理阶段使用el-select下拉选择

    - 在处理阶段下方显示提示信息（使用el-alert）
    - 解决方案使用el-input type="textarea"
    - 对话框宽度600px，label-width 120px
    - _Requirements: 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3, 7.1_

  - [x] 6.6 实现表单验证

    - 标题必填验证（1-200字符）


    - 问题描述必填验证
    - 记录人必填验证
    - processing_stage为"resolved"时resolution必填验证
    - 使用Element Plus的表单验证规则


    - 显示友好的错误提示
    - _Requirements: 2.3, 3.6, 7.2, 7.3_

  - [x] 6.7 实现新增功能

    - 点击新建按钮打开对话框


    - 重置表单数据
    - 提交时调用createDataIssue API
    - 成功后关闭对话框并刷新列表
    - 显示成功提示
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 6.8 实现编辑功能

    - 点击编辑按钮打开对话框
    - 预填充现有数据
    - 提交时调用updateDataIssue API
    - 成功后关闭对话框并刷新列表
    - 显示成功提示
    - _Requirements: 10.1, 10.2, 6.4, 7.4, 7.5_

  - [x] 6.9 实现删除功能

    - 点击删除按钮显示确认对话框
    - 确认后调用deleteDataIssue API
    - 成功后刷新列表
    - 显示成功提示
    - _Requirements: 10.3, 10.4, 10.5_

- [ ] 7. 集成到系统菜单
  - [x] 7.1 添加前端路由

    - 在router/index.ts中添加/data-issues路由
    - 设置路由名称为DataIssues
    - 设置meta.title为"数据问题记录"
    - _Requirements: 1.1, 1.2_

  - [x] 7.2 修改Layout菜单结构

    - 将"数据质量报告"从单个菜单项改为子菜单（el-sub-menu）
    - 在子菜单下添加"数据问题记录"菜单项
    - 设置正确的index和路由跳转
    - 保持菜单样式与其他模块一致
    - _Requirements: 1.1, 1.2_

- [x] 8. 错误处理和用户体验优化


  - 实现API错误的统一处理和友好提示
  - 实现表单提交时的loading状态
  - 实现删除操作的二次确认
  - 优化用户选择器的搜索体验（防抖）
  - 确保所有操作都有明确的成功/失败反馈
  - _Requirements: 2.3, 3.6, 7.2, 7.3, 10.3, 10.4_

- [ ]* 9. 编写后端测试
  - [ ]* 9.1 编写模型测试
    - 测试DataIssue模型的创建
    - 测试字段验证
    - 测试关系映射
    - _Requirements: 1.4, 4.1, 8.1_

  - [ ]* 9.2 编写API测试
    - 测试GET /api/data-issues（列表、分页、筛选）
    - 测试POST /api/data-issues（创建、验证）
    - 测试GET /api/data-issues/{id}（详情）
    - 测试PUT /api/data-issues/{id}（更新、验证）
    - 测试DELETE /api/data-issues/{id}（删除）
    - 测试多租户数据隔离
    - 测试processing_stage和resolution的联动验证
    - 测试resolved_at的自动设置
    - _Requirements: 所有需求_

- [ ]* 10. 编写前端测试
  - [ ]* 10.1 编写UserSelector组件测试
    - 测试手动输入
    - 测试用户搜索
    - 测试用户选择
    - 测试v-model绑定
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 10.2 编写DataIssues页面测试
    - 测试列表渲染
    - 测试搜索和筛选
    - 测试新增对话框
    - 测试编辑对话框
    - 测试表单验证
    - 测试删除确认
    - _Requirements: 所有需求_

- [ ]* 11. 手动测试和验证
  - 执行完整的用户流程测试
  - 验证所有必填字段验证
  - 验证处理阶段和解决方案的联动
  - 验证多租户数据隔离
  - 验证UI样式与其他模块的一致性
  - 验证所有错误提示的友好性
  - _Requirements: 所有需求_
