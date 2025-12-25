# 实现计划

## 第一阶段：数据库模型和迁移

- [x] 1. 创建数据库模型和迁移文件
  - [x] 1.1 创建AI接口模型 (`ai_interfaces` 表)
    - 已创建 `backend/app/models/ai_interface.py`
    - 字段：id, hospital_id, name, api_endpoint, model_name, api_key_encrypted, call_delay, daily_limit, is_active, created_at, updated_at
    - _需求: 10.1, 10.2_
  - [x] 1.2 创建AI提示词模块模型 (`ai_prompt_modules` 表)
    - 已创建 `backend/app/models/ai_prompt_module.py`
    - 字段：id, hospital_id, module_code, module_name, description, ai_interface_id, temperature, placeholders, system_prompt, user_prompt, created_at, updated_at
    - _需求: 11.1, 11.2_
  - [x] 1.3 创建对话分组模型 (`conversation_groups` 表)
    - 已创建 `backend/app/models/conversation_group.py`
    - 字段：id, hospital_id, name, sort_order, is_collapsed, created_at
    - _需求: 2.1_
  - [x] 1.4 创建对话模型 (`conversations` 表)
    - 已创建 `backend/app/models/conversation.py`
    - 字段：id, hospital_id, group_id, title, description, conversation_type, created_at, updated_at
    - _需求: 1.1_
  - [x] 1.5 创建对话消息模型 (`conversation_messages` 表)
    - 已创建 `backend/app/models/conversation_message.py`
    - 字段：id, conversation_id, role, content, content_type, metadata, created_at
    - _需求: 6.1, 6.2_
  - [x] 1.6 创建指标项目模型 (`metric_projects` 表)
    - 已创建 `backend/app/models/metric_project.py`
    - 字段：id, hospital_id, name, description, sort_order, created_at, updated_at
    - _需求: 7.2_
  - [x] 1.7 创建指标主题模型 (`metric_topics` 表)
    - 已创建 `backend/app/models/metric_topic.py`
    - 字段：id, project_id, name, description, sort_order, created_at, updated_at
    - _需求: 7.3_
  - [x] 1.8 创建指标模型 (`metrics` 表)
    - 已创建 `backend/app/models/metric.py`
    - 字段：id, topic_id, name_cn, name_en, metric_type, metric_level, business_caliber, technical_caliber, source_table, dimension_tables, dimensions, data_source_id, sort_order, created_at, updated_at
    - _需求: 8.2, 8.3_
  - [x] 1.9 创建指标关联模型 (`metric_relations` 表)
    - 已创建 `backend/app/models/metric_relation.py`
    - 字段：id, source_metric_id, target_metric_id, relation_type, created_at
    - _需求: 9.1_
  - [x] 1.10 创建Alembic迁移文件
    - 已创建 `backend/alembic/versions/20251217_add_intelligent_query_system.py`
    - 包含所有新表的创建语句
  - [x] 1.11 更新模型导出
    - 已更新 `backend/app/models/__init__.py`
    - 导出所有新模型
  - [ ]* 1.12 编写属性测试：对话创建后列表长度增加
    - **属性1：对话创建后列表长度增加**
    - **验证：需求 1.1**

- [x] 2. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

## 第二阶段：AI接口配置功能

- [x] 3. 实现AI接口配置后端
  - [x] 3.1 创建AI接口Schema
    - 已创建 `backend/app/schemas/ai_interface.py`
    - 包含：AIInterfaceCreate, AIInterfaceUpdate, AIInterfaceResponse, AIInterfaceListResponse
    - _需求: 10.1, 10.2, 10.3_
  - [x] 3.2 创建AI接口API路由
    - 已创建 `backend/app/api/ai_interfaces.py`
    - 实现：GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}, POST /{id}/test
    - _需求: 10.1, 10.2, 10.3, 10.4, 10.5_
  - [x] 3.3 注册AI接口路由
    - 已在 `backend/app/main.py` 中注册路由
    - 路径：`/api/v1/ai-interfaces`
  - [ ]* 3.4 编写属性测试：AI接口删除引用检查
    - **属性14：AI接口删除引用检查**
    - **验证：需求 10.4**

- [x] 4. 实现提示词模块配置后端
  - [x] 4.1 创建提示词模块Schema
    - 已创建 `backend/app/schemas/ai_prompt_module.py`
    - 包含：AIPromptModuleUpdate, AIPromptModuleResponse, AIPromptModuleListResponse
    - _需求: 11.1, 11.2_
  - [x] 4.2 创建提示词模块API路由
    - 已创建 `backend/app/api/ai_prompt_modules.py`
    - 实现：GET /, GET /{module_code}, PUT /{module_code}
    - _需求: 11.1, 11.2, 11.3, 11.4_
  - [x] 4.3 创建提示词模块初始化服务
    - 已创建 `backend/app/services/ai_prompt_module_service.py`
    - 初始化6个模块的默认配置
    - _需求: 11.1_
  - [x] 4.4 注册提示词模块路由
    - 已在 `backend/app/main.py` 中注册路由
    - 路径：`/api/v1/ai-prompt-modules`
  - [ ]* 4.5 编写属性测试：提示词模块配置完整性
    - **属性15：提示词模块配置完整性**
    - **验证：需求 11.2**
  - [ ]* 4.6 编写属性测试：未配置AI接口时阻止功能
    - **属性16：未配置AI接口时阻止功能**
    - **验证：需求 11.5**

- [x] 5. 实现AI配置前端





  - [x] 5.1 创建AI接口配置前端API
    - 已创建 `frontend/src/api/ai-interfaces.ts`
    - _需求: 10.1, 10.2, 10.3, 10.4, 10.5_
  - [x] 5.2 创建提示词模块配置前端API
    - 已创建 `frontend/src/api/ai-prompt-modules.ts`
    - _需求: 11.1, 11.2, 11.3, 11.4_

  - [x] 5.3 升级AI配置页面
    - 已重构 `frontend/src/views/AIConfig.vue`
    - 添加AI接口列表管理（CRUD、测试连接、引用模块显示）
    - 添加提示词模块配置（按功能模块分类：智能分类分级、业务价值报表、智能问数系统）
    - 添加模型温度设置（滑块控件，0-2范围）
    - 左右分栏布局：左侧模块列表，右侧配置详情
    - _需求: 10.1, 10.2, 10.3, 10.4, 10.5, 11.1, 11.2, 11.3, 11.4_
  - [x] 5.4 创建提示词编辑模态框组件
    - 已创建 `frontend/src/components/PromptEditModal.vue`
    - 供Maintainer用户在功能模块中快速编辑提示词
    - 支持占位符点击插入、温度调节、系统/用户提示词编辑
    - _需求: 11.6_

- [ ] 6. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

## 第三阶段：指标资产管理功能

- [ ] 7. 实现指标资产管理后端
  - [x] 7.1 创建指标相关Schema





    - 创建 `backend/app/schemas/metric.py`
    - 包含：MetricCreate, MetricUpdate, MetricResponse, MetricTreeResponse
    - 创建 `backend/app/schemas/metric_project.py`
    - 创建 `backend/app/schemas/metric_topic.py`
    - 创建 `backend/app/schemas/metric_relation.py`
    - _需求: 7.1, 8.1, 8.2, 8.3, 9.1_


  - [x] 7.2 创建指标项目API路由



    - 创建 `backend/app/api/metric_projects.py`
    - 实现：GET /, POST /, PUT /{id}, DELETE /{id}, PUT /reorder

    - _需求: 7.2, 7.4, 7.5_


  - [x] 7.3 创建指标主题API路由


    - 创建 `backend/app/api/metric_topics.py`
    - 实现：GET /, POST /, PUT /{id}, DELETE /{id}, PUT /reorder
    - _需求: 7.3, 7.4, 7.5_


  - [x] 7.4 创建指标API路由



    - 创建 `backend/app/api/metrics.py`
    - 实现：GET /tree, GET /{id}, POST /, PUT /{id}, DELETE /{id}
    - 实现：GET /{id}/relations, POST /{id}/relations, DELETE /{id}/relations/{related_id}
    - 实现：GET /{id}/affected
    - _需求: 7.1, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4_





  - [x] 7.5 注册指标相关路由





    - 修改 `backend/app/main.py`
    - 注册 metric_projects, metric_topics, metrics 路由
  - [ ]* 7.6 编写属性测试：指标树结构正确性
    - **属性8：指标树结构正确性**
    - **验证：需求 7.1**
  - [ ]* 7.7 编写属性测试：节点排序持久化
    - **属性9：节点排序持久化**
    - **验证：需求 7.4**
  - [ ]* 7.8 编写属性测试：节点删除级联子节点
    - **属性10：节点删除级联子节点**
    - **验证：需求 7.5**
  - [ ]* 7.9 编写属性测试：指标必填字段验证
    - **属性11：指标必填字段验证**
    - **验证：需求 8.4**
  - [ ]* 7.10 编写属性测试：指标关联双向查询
    - **属性12：指标关联双向查询**
    - **验证：需求 9.1, 9.2**
  - [ ]* 7.11 编写属性测试：指标删除前检查关联
    - **属性13：指标删除前检查关联**
    - **验证：需求 9.4**

- [ ] 8. 实现指标资产管理前端
  - [x] 8.1 创建指标相关前端API





    - 创建 `frontend/src/api/metrics.ts`
    - 创建 `frontend/src/api/metric-projects.ts`
    - 创建 `frontend/src/api/metric-topics.ts`
    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4_



  - [x] 8.2 创建指标资产管理页面


    - 创建 `frontend/src/views/MetricAssets.vue`
    - 左侧：指标树（项目→主题→指标）
    - 右侧：指标详情面板
    - 支持拖拽排序

    - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 8.3 创建指标编辑对话框组件



    - 创建 `frontend/src/components/MetricEditDialog.vue`
    - 包含业务属性和技术属性编辑
    - _需求: 8.2, 8.3, 8.4_



  - [x] 8.4 创建指标关联管理组件


    - 创建 `frontend/src/components/MetricRelationManager.vue`
    - 支持添加、查看、删除关联
    - 删除时显示受影响指标列表
    - _需求: 9.1, 9.2, 9.3, 9.4_

- [ ] 9. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

## 第四阶段：智能数据问答功能

- [ ] 10. 实现对话管理后端
  - [x] 10.1 创建对话相关Schema





    - 创建 `backend/app/schemas/conversation.py`
    - 包含：ConversationCreate, ConversationUpdate, ConversationResponse, ConversationListResponse
    - 创建 `backend/app/schemas/conversation_group.py`
    - 创建 `backend/app/schemas/conversation_message.py`



    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 6.1, 6.2_
  - [x] 10.2 创建对话分组API路由


    - 创建 `backend/app/api/conversation_groups.py`
    - 实现：GET /, POST /, PUT /{id}, DELETE /{id}, PUT /{id}/conversations


    - _需求: 2.1, 2.2, 2.5_
  - [x] 10.3 创建对话API路由




    - 创建 `backend/app/api/conversations.py`
    - 实现：GET /, POST /, GET /{id}, PUT /{id}, DELETE /{id}, POST /{id}/messages
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.5_

  - [x] 10.4 注册对话相关路由





    - 修改 `backend/app/main.py`
    - 注册 conversations, conversation_groups 路由
  - [ ]* 10.5 编写属性测试：对话搜索结果包含关键词
    - **属性2：对话搜索结果包含关键词**
    - **验证：需求 1.2**
  - [ ]* 10.6 编写属性测试：对话标题更新持久化
    - **属性3：对话标题更新持久化**
    - **验证：需求 1.4**
  - [ ]* 10.7 编写属性测试：对话删除级联消息
    - **属性4：对话删除级联消息**
    - **验证：需求 1.5**
  - [ ]* 10.8 编写属性测试：分组删除后对话移至未分组
    - **属性5：分组删除后对话移至未分组**
    - **验证：需求 2.5**
  - [ ]* 10.9 编写属性测试：消息发送后持久化
    - **属性7：消息发送后持久化**
    - **验证：需求 6.1**

- [ ] 11. 实现AI对话服务
  - [x] 11.1 创建指标口径查询服务





    - 创建 `backend/app/services/metric_caliber_service.py`
    - 实现指标搜索和口径查询逻辑



    - _需求: 3.1, 3.2, 3.4_
  - [x] 11.2 创建数据智能查询服务

    - 创建 `backend/app/services/data_query_service.py`
    - 实现自然语言转SQL、执行查询、图表建议
    - _需求: 4.1, 4.2, 4.5_


  - [x] 11.3 创建SQL代码生成服务



    - 创建 `backend/app/services/sql_generation_service.py`
    - 实现基于指标定义生成SQL
    - _需求: 5.1, 5.2_
  - [ ]* 11.4 编写属性测试：指标口径查询结果包含必需字段
    - **属性6：指标口径查询结果包含必需字段**
    - **验证：需求 3.2**

- [x] 12. 实现智能数据问答前端



  - [x] 12.1 创建对话相关前端API


    - 创建 `frontend/src/api/conversations.ts`
    - 创建 `frontend/src/api/conversation-groups.ts`


    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.5, 6.1, 6.2_

  - [x] 12.2 创建智能数据问答页面

    - 创建 `frontend/src/views/SmartDataQA.vue`
    - 左侧：对话列表（支持搜索、分组、拖拽）
    - 右侧：对话主界面（标题、消息、类型选择、输入框）
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_


  - [x] 12.3 创建对话消息组件






    - 创建 `frontend/src/components/ConversationMessage.vue`
    - 支持表格、代码块、图表等多种内容类型渲染
    - _需求: 3.2, 4.2, 5.3, 6.2_





  - [x] 12.4 创建图表渲染组件


    - 创建 `frontend/src/components/ChartRenderer.vue`
    - 支持折线图、柱状图、饼图等
    - _需求: 4.3_



  - [x] 12.5 集成Maintainer提示词编辑按钮


    - 在对话类型选择区域添加"修改提示词"按钮
    - 仅Maintainer用户可见
    - 点击打开提示词编辑模态框
    - _需求: 11.6_

- [ ] 13. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户

## 第五阶段：数据导出功能

- [x] 14. 实现数据导出功能




  - [x] 14.1 创建导出服务


    - 扩展 `backend/app/services/export_service.py`
    - 实现Markdown导出
    - 实现PDF导出
    - 实现Excel导出
    - 实现CSV导出
    - _需求: 12.1, 12.2, 12.3, 12.4_


  - [x] 14.2 创建导出API路由
    - 在对话API中添加导出端点
    - POST /conversations/{id}/messages/{msg_id}/export

    - _需求: 3.3, 4.4, 12.1, 12.2, 12.3, 12.4, 12.5_
  - [x] 14.3 实现前端导出功能


    - 在消息组件中添加导出按钮
    - 根据对话类型显示不同的导出选项
    - _需求: 3.3, 4.4_

- [x] 15. 检查点 - 确保所有测试通过
  - 导出服务单元测试全部通过（9/9）

## 第六阶段：菜单和路由配置

- [x] 16. 配置菜单和路由
  - [x] 16.1 更新菜单配置





    - 修改 `frontend/src/config/menus.ts`
    - 将"智能问数系统"从disabled改为启用
    - 添加子菜单：智能数据问答、指标资产管理

    - _需求: 全部_


  - [x] 16.2 配置前端路由


    - 修改 `frontend/src/router/index.ts`
    - 添加智能数据问答路由
    - 添加指标资产管理路由
    - _需求: 全部_

- [x] 17. 最终检查点 - 确保所有测试通过
  - 导出服务单元测试全部通过（9/9）
  - 后端API路由已注册
  - 前端导出功能已集成到ConversationMessage组件
  - 菜单和路由配置已完成

