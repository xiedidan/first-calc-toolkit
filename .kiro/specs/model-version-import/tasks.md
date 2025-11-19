# 模型版本导入功能 - 实现任务清单

## 设计概述

### 功能目标
实现模型版本导入功能，允许用户从系统中其他医疗机构的模型版本中导入结构和配置，提高模型复用性。

### 核心设计要点

#### 1. 数据模型设计
- **model_version_imports** 表：记录导入历史（仅记录，不提供查询功能）
  - id: 主键
  - target_version_id: 目标版本ID（导入后创建的新版本）
  - source_version_id: 源版本ID
  - source_hospital_id: 源医疗机构ID
  - import_type: 导入类型（structure_only/with_workflows）
  - imported_by: 导入用户ID
  - import_time: 导入时间
  - statistics: 导入统计信息（JSON格式）
  
**注意**：导入后的模型版本与本地创建的版本完全相同，不做区分

#### 2. API设计
- `GET /api/v1/model-versions/importable` - 获取可导入的版本列表
- `GET /api/v1/model-versions/{id}/preview` - 预览版本详情
- `POST /api/v1/model-versions/import` - 执行导入操作
- `GET /api/v1/model-versions/{id}/import-info` - 获取版本导入信息

#### 3. 导入流程设计
1. **查询阶段**：查询其他医疗机构的模型版本（排除当前医疗机构）
2. **预览阶段**：展示源版本的结构、流程、映射统计
3. **配置阶段**：用户选择导入选项和新版本信息
4. **执行阶段**：
   - 创建新版本记录（hospital_id为当前医疗机构）
   - 复制模型节点（递归复制整个树结构）
   - 可选：复制计算流程和步骤
   - 记录导入历史
5. **结果阶段**：返回导入统计和警告信息

#### 4. 数据冲突处理
- **数据源不存在**：将data_source_id设为NULL，记录警告
- **版本号冲突**：前端验证，后端再次验证并返回错误

#### 5. 权限控制
- 仅"模型设计师"和"系统管理员"可执行导入
- 只能导入到当前用户所属的医疗机构

### 技术栈
- 后端：FastAPI + SQLAlchemy
- 前端：Vue 3 + Element Plus
- 数据库：PostgreSQL

---

## 实现任务

- [x] 1. 数据库设计和迁移

  - 创建model_version_imports表用于记录导入历史
  - 添加必要的索引和外键约束
  - _需求: 需求8_

- [x] 1.1 创建数据库迁移脚本


  - 使用Alembic创建迁移文件
  - 定义model_version_imports表结构
  - 添加外键关联到model_versions、hospitals、users表
  - _需求: 需求8_


- [x] 1.2 创建ModelVersionImport模型类

  - 在backend/app/models/创建model_version_import.py
  - 定义SQLAlchemy模型类
  - 添加关系映射（version、hospital、user）
  - _需求: 需求8_


- [ ] 2. 后端API实现 - 查询可导入版本
  - 实现GET /api/v1/model-versions/importable接口
  - 查询所有其他医疗机构的模型版本
  - 支持搜索和分页
  - 返回版本基本信息和所属医疗机构名称
  - _需求: 需求1_

- [x] 2.1 实现可导入版本列表查询


  - 在backend/app/api/model_versions.py添加get_importable_versions端点
  - 使用hospital_filter排除当前医疗机构的版本
  - 实现搜索功能（版本号、名称、医疗机构名称）
  - 实现分页功能
  - _需求: 需求1_


- [x] 2.2 创建响应Schema

  - 在backend/app/schemas/model_version.py添加ImportableVersionResponse
  - 包含版本信息和医疗机构信息
  - _需求: 需求1_

- [ ] 3. 后端API实现 - 预览版本详情
  - 实现GET /api/v1/model-versions/{id}/preview接口
  - 返回模型结构树（节点统计）
  - 返回计算流程数量
  - _需求: 需求2_


- [ ] 3.1 实现版本预览端点
  - 在backend/app/api/model_versions.py添加preview_version端点
  - 查询并统计模型节点数量
  - 查询并统计计算流程和步骤数量
  - _需求: 需求2_

- [x] 3.2 创建预览响应Schema

  - 在backend/app/schemas/model_version.py添加VersionPreviewResponse
  - 包含统计信息和结构概览
  - _需求: 需求2_

- [ ] 4. 后端API实现 - 执行导入
  - 实现POST /api/v1/model-versions/import接口
  - 验证版本号唯一性
  - 创建新版本记录
  - 复制模型节点（递归）
  - 可选复制计算流程和步骤
  - 可选复制维度目录映射
  - 记录导入历史
  - 返回导入结果和统计
  - _需求: 需求3, 需求4, 需求5, 需求6_

- [x] 4.1 创建导入请求Schema

  - 在backend/app/schemas/model_version.py添加ModelVersionImportRequest
  - 包含source_version_id、import_type、新版本信息
  - _需求: 需求3_


- [x] 4.2 实现导入服务类

  - 在backend/app/services/创建model_version_import_service.py
  - 实现import_model_version方法
  - 处理事务和回滚
  - _需求: 需求4_


- [ ] 4.3 实现节点复制逻辑
  - 在import_service中实现_copy_nodes_recursive方法
  - 递归复制整个节点树
  - 保持父子关系和排序
  - _需求: 需求4_


- [ ] 4.4 实现计算流程复制逻辑
  - 在import_service中实现_copy_workflows方法
  - 复制计算流程和所有步骤
  - 处理数据源引用（不存在时设为NULL）
  - 记录警告信息

  - _需求: 需求4, 需求6_

- [ ] 4.6 实现导入历史记录
  - 在import_service中实现_record_import_history方法
  - 创建ModelVersionImport记录
  - 保存导入统计和警告信息
  - _需求: 需求8_


- [ ] 4.7 实现导入端点
  - 在backend/app/api/model_versions.py添加import_version端点
  - 调用import_service执行导入
  - 处理异常和回滚
  - 返回导入结果
  - _需求: 需求4, 需求5_

- [ ] 5. 后端API实现 - 查询导入信息
  - 实现GET /api/v1/model-versions/{id}/import-info接口
  - 查询版本的导入历史记录
  - 返回源版本、源医疗机构、导入时间等信息
  - _需求: 需求8_


- [ ] 5.1 实现导入信息查询端点
  - 在backend/app/api/model_versions.py添加get_import_info端点
  - 查询ModelVersionImport记录
  - 关联查询源版本和医疗机构信息
  - _需求: 需求8_

- [ ] 6. 前端实现 - 导入按钮和对话框
  - 在模型版本管理页面添加"导入版本"按钮
  - 创建导入对话框组件
  - 实现多步骤导入向导
  - _需求: 需求1_

- [x] 6.1 添加导入按钮

  - 在frontend/src/views/ModelVersions.vue添加"导入版本"按钮
  - 绑定点击事件打开导入对话框
  - _需求: 需求1_


- [ ] 6.2 创建导入对话框组件
  - 创建frontend/src/components/ModelVersionImportDialog.vue
  - 实现步骤导航（选择版本 -> 预览 -> 配置 -> 确认）
  - 使用Element Plus的Steps和Dialog组件
  - _需求: 需求1, 需求2, 需求3_

- [ ] 7. 前端实现 - 可导入版本列表
  - 实现版本列表展示
  - 实现搜索功能
  - 实现分页功能
  - 实现版本选择
  - _需求: 需求1_

- [x] 7.1 实现版本列表API调用

  - 在frontend/src/api/modelVersion.ts添加getImportableVersions方法
  - 调用后端API获取可导入版本
  - _需求: 需求1_


- [ ] 7.2 实现版本列表UI
  - 在ImportDialog中实现版本列表表格
  - 显示版本号、名称、医疗机构、创建时间
  - 实现搜索框和分页组件
  - 实现单选功能
  - _需求: 需求1_

- [ ] 8. 前端实现 - 版本预览
  - 实现版本详情预览
  - 显示模型结构统计
  - 显示计算流程统计
  - 显示维度目录映射统计
  - _需求: 需求2_


- [ ] 8.1 实现预览API调用
  - 在frontend/src/api/modelVersion.ts添加previewVersion方法
  - 调用后端API获取版本预览信息
  - _需求: 需求2_

- [ ] 9. 前端实现 - 导入配置
  - 实现导入选项选择
  - 实现新版本信息输入
  - 实现版本号唯一性验证
  - 显示警告提示

  - _需求: 需求3_

- [ ] 9.1 实现导入配置表单
  - 在ImportDialog中实现配置步骤
  - 添加导入类型单选框（仅结构/含流程）
  - 添加版本号、名称、描述输入框

  - 实现表单验证
  - _需求: 需求3_

- [x] 9.2 实现版本号唯一性验证

  - 在输入版本号时调用后端验证接口
  - 显示验证结果
  - _需求: 需求3_

- [ ] 9.3 显示警告提示
  - 当选择导入计算流程时显示警告
  - 提示用户可能需要调整SQL代码
  - _需求: 需求3_

- [ ] 10. 前端实现 - 执行导入
  - 实现导入确认
  - 调用导入API
  - 显示导入进度
  - 显示导入结果
  - _需求: 需求4, 需求5_



- [ ] 10.1 实现导入API调用
  - 在frontend/src/api/modelVersion.ts添加importVersion方法
  - 调用后端API执行导入
  - _需求: 需求4_

- [x] 10.2 实现导入确认和执行

  - 在ImportDialog中实现确认步骤
  - 显示导入摘要
  - 点击确认后调用导入API
  - 显示加载状态
  - _需求: 需求4_

- [x] 10.3 实现导入结果展示

  - 显示导入成功提示
  - 显示导入统计（节点数、流程数、步骤数、映射数）
  - 显示警告信息（如果有）
  - 提供"查看新版本"按钮
  - _需求: 需求5, 需求6_

- [ ] 11.1 实现导入信息API调用
  - 在frontend/src/api/modelVersion.ts添加getImportInfo方法
  - 调用后端API获取导入信息
  - _需求: 需求8_

- [ ] 12. 权限控制
  - 实现权限检查
  - _需求: 需求7_

- [x] 12.1 实现权限检查


  - 在导入API端点添加权限装饰器
  - 检查用户角色（模型设计师或系统管理员）
  - 验证用户只能导入到自己所属的医疗机构
  - _需求: 需求7_

- [ ]* 13. 测试
  - 编写单元测试
  - 编写集成测试
  - 执行端到端测试

- [ ]* 13.1 后端单元测试
  - 测试导入服务的各个方法
  - 测试数据冲突处理逻辑
  - 测试事务回滚

- [ ]* 13.2 后端集成测试
  - 测试完整的导入流程
  - 测试不同导入类型
  - 测试权限控制

- [ ]* 13.3 前端组件测试
  - 测试导入对话框组件
  - 测试表单验证
  - 测试API调用

- [ ] 14. 文档更新

  - 更新需求文档
  - 更新API设计文档
  - 更新用户手册

- [x] 14.1 更新API设计文档



  - 在API设计文档.md中添加新的API接口说明
  - 包含请求参数、响应格式、错误码


- [x] 14.2 更新需求文档



  - 在需求文档.md中添加模型版本导入功能需求
  - 更新功能列表

- [x] 14.3 创建用户操作指南




  - 编写模型版本导入功能的使用说明
  - 包含截图和步骤说明
