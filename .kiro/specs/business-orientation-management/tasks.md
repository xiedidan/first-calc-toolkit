# 业务导向管理 - 实施任务列表

## 阶段 1：数据库和模型（后端基础）

- [x] 1. 创建数据库迁移和模型定义









  - 创建 Alembic 迁移文件，定义三个新表：orientation_rules、orientation_benchmarks、orientation_ladders
  - 定义枚举类型：OrientationCategory（benchmark_ladder、direct_ladder、other）和 BenchmarkType（average、median、max、min、other）
  - 为 model_nodes 表添加 orientation_rule_id 外键字段
  - 设置多租户唯一约束和索引
  - _需求：1.1, 1.2, 4.1, 5.1, 6.1, 7.1_

- [x] 2. 实现 SQLAlchemy 模型类





  - 创建 OrientationRule 模型，包含字段和关系定义
  - 创建 OrientationBenchmark 模型，包含字段和关系定义
  - 创建 OrientationLadder 模型，包含字段和关系定义
  - 更新 ModelNode 模型，添加 orientation_rule 关系
  - 更新 Hospital 模型，添加反向关系
  - _需求：1.1, 4.1, 5.1, 6.2_

- [x] 3. 创建 Pydantic Schema




  - 创建导向规则的 Schema（Create、Update、Response）
  - 创建导向基准的 Schema（Create、Update、Response）
  - 创建导向阶梯的 Schema（Create、Update、Response）
  - 添加输入验证规则（字段长度、数值格式、枚举值）
  - _需求：1.2, 4.2, 5.2, 8.5_


## 阶段 2：导向规则 API 实现

- [x] 4. 实现导向规则基础 CRUD API





  - 创建 orientation_rules.py API 路由文件
  - 实现 GET /api/v1/orientation-rules（列表查询，支持分页）
  - 实现 POST /api/v1/orientation-rules（创建导向规则）
  - 实现 GET /api/v1/orientation-rules/{id}（获取详情）
  - 实现 PUT /api/v1/orientation-rules/{id}（更新导向规则）
  - 实现 DELETE /api/v1/orientation-rules/{id}（删除导向规则，检查关联）
  - 添加多租户隔离逻辑
  - _需求：1.1, 1.2, 1.3, 1.4, 7.1, 7.2_

- [ ]* 4.1 编写导向规则 CRUD 的属性测试
  - **属性 1：导向规则列表完整性**
  - **属性 2：导向规则输入验证**
  - **属性 3：导向规则更新保持完整性**
  - **属性 4：导向规则删除约束**
  - **验证：需求 1.1, 1.2, 1.3, 1.4**

- [x] 5. 实现导向规则复制功能




  - 实现 POST /api/v1/orientation-rules/{id}/copy
  - 创建 OrientationRuleService.copy_rule() 方法
  - 使用数据库事务确保原子性
  - 复制导向规则本身（名称添加"（副本）"）
  - 根据类别复制关联的基准和阶梯
  - 处理复制失败的回滚逻辑
  - _需求：2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 5.1 编写导向规则复制的属性测试
  - **属性 5：导向规则复制基本行为**
  - **属性 6：基准阶梯导向复制基准**
  - **属性 7：阶梯类别导向复制阶梯**
  - **属性 8：复制操作事务完整性**
  - **验证：需求 2.1, 2.2, 2.3, 2.5**

- [x] 6. 实现导向规则导出功能





  - 实现 GET /api/v1/orientation-rules/{id}/export
  - 创建 OrientationRuleService.export_rule() 方法
  - 生成 Markdown 格式内容（包含规则详情）
  - 根据类别包含关联的基准和阶梯数据
  - 使用导向名称和时间戳生成文件名
  - 正确处理中文文件名（URL编码）
  - 返回 StreamingResponse 供下载
  - _需求：3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 6.1 编写导向规则导出的属性测试
  - **属性 9：导向规则导出包含完整信息**
  - **属性 10：基准阶梯导向导出包含基准**
  - **属性 11：阶梯类别导向导出包含阶梯**
  - **属性 12：导出文件命名规则**
  - **验证：需求 3.1, 3.2, 3.3, 3.4**


## 阶段 3：导向基准 API 实现

- [x] 7. 实现导向基准 CRUD API





  - 创建 orientation_benchmarks.py API 路由文件
  - 实现 GET /api/v1/orientation-benchmarks（列表查询，支持按 rule_id 筛选）
  - 实现 POST /api/v1/orientation-benchmarks（创建基准，验证导向类别）
  - 实现 GET /api/v1/orientation-benchmarks/{id}（获取详情）
  - 实现 PUT /api/v1/orientation-benchmarks/{id}（更新基准）
  - 实现 DELETE /api/v1/orientation-benchmarks/{id}（删除基准）
  - 添加多租户隔离逻辑
  - 预加载 rule.name 和 department 信息
  - 自动格式化数值字段为 4 位小数
  - _需求：4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2_

- [ ]* 7.1 编写导向基准的属性测试
  - **属性 13：导向基准列表完整性**
  - **属性 14：导向基准类别验证**
  - **属性 15：基准数值格式化**
  - **属性 16：导向基准按导向筛选**
  - **验证：需求 4.1, 4.2, 4.3, 4.5**

- [ ]* 7.2 编写导向基准日期验证的属性测试
  - **属性 27：导向基准日期范围验证**
  - **验证：需求 8.1**


## 阶段 4：导向阶梯 API 实现

- [x] 8. 实现导向阶梯 CRUD API





  - 创建 orientation_ladders.py API 路由文件
  - 实现 GET /api/v1/orientation-ladders（列表查询，支持按 rule_id 筛选，按 ladder_order 排序）
  - 实现 POST /api/v1/orientation-ladders（创建阶梯，验证导向类别和次序唯一性）
  - 实现 GET /api/v1/orientation-ladders/{id}（获取详情）
  - 实现 PUT /api/v1/orientation-ladders/{id}（更新阶梯）
  - 实现 DELETE /api/v1/orientation-ladders/{id}（删除阶梯）
  - 添加多租户隔离逻辑
  - 预加载 rule.name
  - 自动格式化数值字段为 4 位小数
  - 处理无穷值（NULL 表示正/负无穷）
  - _需求：5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 7.1, 7.2_

- [ ]* 8.1 编写导向阶梯的属性测试
  - **属性 17：导向阶梯列表完整性**
  - **属性 18：导向阶梯类别验证**
  - **属性 19：阶梯数值格式化**
  - **属性 20：导向阶梯按导向筛选并排序**
  - **属性 21：导向阶梯次序唯一性**
  - **验证：需求 5.1, 5.2, 5.3, 5.6, 5.8**

- [ ]* 8.2 编写导向阶梯范围验证的属性测试
  - **属性 28：导向阶梯范围验证**
  - **验证：需求 8.2**


## 阶段 5：模型节点关联更新

- [x] 9. 更新模型节点 API 支持导向规则关联





  - 更新 ModelNode 的 Schema，添加 orientation_rule_id 和 orientation_rule_name 字段
  - 更新 ModelNodeUpdate Schema 支持更新 orientation_rule_id
  - 更新 PUT /api/v1/model-nodes/{id} 支持更新 orientation_rule_id
  - 在 GET /api/v1/model-nodes/{id} 中预加载 orientation_rule.name
  - 在 GET /api/v1/model-nodes 列表中预加载 orientation_rule.name
  - 验证仅末级节点可以关联导向规则
  - _需求：6.1, 6.2, 6.3, 6.5_

- [ ]* 9.1 编写模型节点关联的属性测试
  - **属性 22：模型节点关联导向规则**
  - **属性 23：模型节点详情包含导向名称**
  - **验证：需求 6.2, 6.3**


## 阶段 6：前端 - 导向规则管理

- [x] 10. 创建导向规则管理页面和对话框





  - 创建 frontend/src/views/OrientationRules.vue
  - 实现导向规则列表展示（表格，包含ID、名称、类别、描述）
  - 实现搜索和筛选功能（按名称、类别）
  - 实现分页功能
  - 添加"新增"、"编辑"、"删除"、"复制"、"导出"按钮
  - 根据导向类别显示"设置基准"和"设置阶梯"按钮
  - 创建 frontend/src/components/OrientationRuleDialog.vue
  - 实现表单（导向名称、导向类别、导向规则描述）
  - 添加表单验证（必填、长度限制）
  - 支持创建和编辑模式
  - 描述字段使用 textarea，限制 1024 字符
  - _需求：1.1, 1.2, 1.3, 1.5, 1.6_

- [x] 11. 实现导向规则复制和导出功能





  - 在 OrientationRules.vue 中实现复制按钮点击处理
  - 调用复制 API，显示成功/失败消息
  - 在 OrientationRules.vue 中实现导出按钮点击处理
  - 调用导出 API，触发文件下载
  - 处理中文文件名
  - _需求：2.1, 2.4, 3.4, 3.5_

- [x] 12. 实现导向规则页面跳转功能




  - 实现"设置基准"按钮，跳转到导向基准管理页面并传递 rule_id
  - 实现"设置阶梯"按钮，跳转到导向阶梯管理页面并传递 rule_id
  - 根据导向类别控制按钮显示
  - _需求：4.6, 5.7_


## 阶段 7：前端 - 导向基准管理

- [x] 13. 创建导向基准管理页面和对话框






  - 创建 frontend/src/views/OrientationBenchmarks.vue
  - 实现导向基准列表展示（表格，包含所属导向、科室、基准类别、管控力度、统计时间、基准值）
  - 实现按导向筛选功能（下拉选择器，仅显示"基准阶梯"类别的导向）
  - 从 URL 参数读取 rule_id 并自动筛选
  - 实现分页功能
  - 添加"新增"、"编辑"、"删除"按钮
  - 创建 frontend/src/components/OrientationBenchmarkDialog.vue
  - 实现表单（所属导向、科室、基准类别、管控力度、统计时间范围、基准值）
  - 所属导向使用下拉选择器，仅显示"基准阶梯"类别
  - 科室使用下拉选择器，自动填充代码和名称
  - 数值字段自动格式化为 4 位小数
  - 统计时间使用日期范围选择器
  - 添加表单验证（必填、日期范围、数值格式）
  - _需求：4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 8.1_


## 阶段 8：前端 - 导向阶梯管理

- [x] 14. 创建导向阶梯管理页面和对话框





  - 创建 frontend/src/views/OrientationLadders.vue
  - 实现导向阶梯列表展示（表格，包含所属导向、阶梯次序、上限、下限、调整力度）
  - 实现按导向筛选功能（下拉选择器，仅显示"基准阶梯"和"直接阶梯"类别的导向）
  - 从 URL 参数读取 rule_id 并自动筛选
  - 按阶梯次序排序显示
  - 实现分页功能
  - 添加"新增"、"编辑"、"删除"按钮
  - 显示无穷值（NULL 显示为"∞"或"-∞"）
  - 创建 frontend/src/components/OrientationLadderDialog.vue
  - 实现表单（所属导向、阶梯次序、上限、下限、调整力度）
  - 所属导向使用下拉选择器，仅显示"基准阶梯"和"直接阶梯"类别
  - 数值字段自动格式化为 4 位小数
  - 上限和下限字段旁添加"正无穷"/"负无穷"复选框
  - 勾选无穷时禁用对应数值输入，发送 NULL
  - 添加表单验证（必填、次序唯一性、范围有效性）
  - _需求：5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 8.2_


## 阶段 9：前端 - 模型节点关联更新

- [x] 15. 更新模型节点编辑页面





  - 在 frontend/src/views/ModelNodes.vue 中更新节点编辑表单
  - 将"业务导向"字段从文本输入改为下拉选择器
  - 下拉选择器显示所有导向规则（名称）
  - 仅在末级节点显示该字段
  - 支持清空选择（设置为 NULL）
  - 在节点详情和列表中显示关联的导向规则名称
  - 添加 API 调用获取导向规则列表
  - _需求：6.1, 6.2, 6.3, 6.5_


## 阶段 10：路由和菜单集成

- [x] 16. 添加前端路由配置和侧边栏菜单




  - 在 frontend/src/router/index.ts 中添加三个新路由
  - /orientation-rules → OrientationRules.vue
  - /orientation-benchmarks → OrientationBenchmarks.vue
  - /orientation-ladders → OrientationLadders.vue
  - 配置路由元信息（标题、权限）
  - 在 frontend/src/views/Layout.vue 中添加"业务导向管理"一级菜单
  - 放置在"评估模型管理"之后
  - 添加三个二级菜单：导向规则管理、导向基准管理、导向阶梯管理
  - 配置菜单图标和权限（仅管理员可见）
  - _需求：1.1, 4.1, 5.1_


## 阶段 11：数据完整性验证（可选增强）

- [ ]* 11.1 实现额外的数据完整性验证
  - 在 Service 层添加业务规则验证
  - 验证导向类别与关联数据的一致性
  - 验证删除操作的级联检查
  - 验证导向类别修改的兼容性
  - 添加数值格式验证和自动格式化
  - _需求：8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 11.2 编写多租户隔离的属性测试
  - **属性 24：多租户创建隔离**
  - **属性 25：多租户查询隔离**
  - **属性 26：多租户操作隔离**
  - **验证：需求 7.1, 7.2, 7.3**

- [ ]* 11.3 编写数据完整性的属性测试
  - **属性 29：导向规则删除级联检查**
  - **属性 30：导向类别修改一致性验证**
  - **属性 31：数值字段格式验证**
  - **验证：需求 8.3, 8.4, 8.5**


## 阶段 12：测试和验证

- [ ] 17. 端到端功能测试




  - 测试导向规则的完整 CRUD 流程
  - 测试导向规则的复制功能（包括关联数据）
  - 测试导向规则的导出功能
  - 测试导向基准的 CRUD 和筛选
  - 测试导向阶梯的 CRUD 和筛选
  - 测试模型节点关联导向规则
  - 测试页面跳转和参数传递
  - 测试多租户隔离
  - _需求：所有_

- [ ] 18. 最终检查点 - 确保所有功能正常



  - 确保所有核心功能正常工作，如有问题请向用户询问

