# 模型版本导入功能 - 实现总结

## 功能概述

成功实现了模型版本导入功能，允许用户从系统中其他医疗机构的模型版本中导入结构和配置，提高模型复用性，快速复制现有知识。

## 已完成的工作

### 1. 数据库层 ✅

#### 新增表
- **model_version_imports** - 记录模型版本导入历史
  - 字段：target_version_id, source_version_id, source_hospital_id, import_type, imported_by, import_time, statistics
  - 外键：关联到model_versions, hospitals, users表
  - 索引：target_version_id, source_version_id

#### 迁移脚本
- 文件：`backend/alembic/versions/20251105_add_model_version_imports.py`
- 状态：已创建，已修复down_revision引用

### 2. 后端实现 ✅

#### 数据模型
- **ModelVersionImport** (`backend/app/models/model_version_import.py`)
  - SQLAlchemy模型类
  - 关系映射：target_version, source_version, source_hospital, importer

#### Schema定义
- **ImportableVersionResponse** - 可导入版本响应
- **VersionPreviewResponse** - 版本预览响应
- **ModelVersionImportRequest** - 导入请求
- **ModelVersionImportResponse** - 导入响应
- **ImportInfoResponse** - 导入信息响应

#### 服务层
- **ModelVersionImportService** (`backend/app/services/model_version_import_service.py`)
  - `import_model_version()` - 主导入方法
  - `_copy_nodes()` - 复制模型节点
  - `_copy_node_recursive()` - 递归复制节点
  - `_copy_workflows()` - 复制计算流程和步骤
  - `_record_import_history()` - 记录导入历史
  - 数据冲突处理：自动处理数据源引用不存在的情况

#### API端点
1. **GET /api/v1/model-versions/importable**
   - 功能：获取可导入的模型版本列表（其他医疗机构）
   - 支持：搜索、分页
   - 返回：版本信息 + 医疗机构名称

2. **GET /api/v1/model-versions/{id}/preview**
   - 功能：预览版本详情
   - 返回：节点数量、流程数量、步骤数量统计

3. **POST /api/v1/model-versions/import**
   - 功能：执行导入操作
   - 参数：source_version_id, import_type, version, name, description
   - 返回：新版本信息、统计数据、警告信息

4. **GET /api/v1/model-versions/{id}/import-info**
   - 功能：获取版本导入信息
   - 返回：是否导入、源版本、源医疗机构、导入时间等

### 3. 前端实现 ✅

#### API调用层
- 文件：`frontend/src/api/model.ts`
- 新增方法：
  - `getImportableVersions()` - 获取可导入版本列表
  - `previewVersion()` - 预览版本详情
  - `importVersion()` - 执行导入
  - `getImportInfo()` - 获取导入信息

#### 组件
- **ModelVersionImportDialog** (`frontend/src/components/ModelVersionImportDialog.vue`)
  - 4步导入向导：
    1. 选择版本（表格 + 搜索 + 分页）
    2. 预览详情（统计信息展示）
    3. 配置导入（导入类型 + 新版本信息）
    4. 显示结果（统计 + 警告信息）
  - 功能特性：
    - 版本号唯一性验证
    - 导入类型选择（仅结构/含流程）
    - 警告提示（SQL代码需调整）
    - 导入结果展示
    - 查看新版本按钮

#### 页面集成
- 文件：`frontend/src/views/ModelVersions.vue`
- 修改：
  - 添加"导入版本"按钮
  - 集成导入对话框组件
  - 导入成功后刷新列表

### 4. 核心功能特性 ✅

#### 导入模式
- **仅导入模型结构** (structure_only)
  - 复制所有模型节点（递归）
  - 保持节点层级关系和排序
  
- **导入模型结构和计算流程** (with_workflows)
  - 复制所有模型节点
  - 复制所有计算流程
  - 复制所有计算步骤
  - 处理数据源引用冲突

#### 数据冲突处理
- **数据源不存在**：将data_source_id设为NULL，记录警告
- **版本号冲突**：前端验证 + 后端验证，返回错误

#### 权限控制
- 使用现有的hospital_filter机制
- 自动应用当前用户的医疗机构ID
- 只能导入到当前用户所属的医疗机构

#### 导入历史
- 记录每次导入操作
- 保存导入统计信息（节点数、流程数、步骤数）
- 支持查询版本的导入来源

## 技术亮点

1. **递归复制算法** - 完整复制多层级节点树结构
2. **事务管理** - 导入失败自动回滚，保证数据一致性
3. **冲突处理** - 智能处理数据源引用不存在的情况
4. **用户体验** - 4步向导式交互，清晰的进度指示
5. **数据隔离** - 严格的医疗机构数据隔离
6. **可追溯性** - 完整的导入历史记录

## 使用流程

1. 用户点击"导入版本"按钮
2. 浏览其他医疗机构的模型版本列表
3. 选择要导入的版本，查看预览信息
4. 配置导入选项和新版本信息
5. 确认导入，系统执行导入操作
6. 查看导入结果和警告信息
7. 可选：跳转到新版本进行编辑

## 下一步操作

### 必需操作
1. **执行数据库迁移**
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **重启后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

3. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```

### 测试建议
1. 创建多个医疗机构和模型版本
2. 测试导入功能（仅结构模式）
3. 测试导入功能（含流程模式）
4. 验证数据源冲突处理
5. 验证版本号唯一性检查
6. 验证导入历史记录

## 文件清单

### 后端文件
- `backend/alembic/versions/20251105_add_model_version_imports.py` - 数据库迁移
- `backend/app/models/model_version_import.py` - 数据模型
- `backend/app/schemas/model_version.py` - Schema定义（新增部分）
- `backend/app/services/model_version_import_service.py` - 导入服务
- `backend/app/api/model_versions.py` - API端点（新增部分）
- `backend/app/models/__init__.py` - 模型导入（已更新）

### 前端文件
- `frontend/src/api/model.ts` - API调用（新增部分）
- `frontend/src/components/ModelVersionImportDialog.vue` - 导入对话框组件
- `frontend/src/views/ModelVersions.vue` - 版本管理页面（已更新）

## 注意事项

1. **数据源引用**：导入含流程的版本时，如果计算步骤引用的数据源在目标医疗机构不存在，会自动设为NULL（使用默认数据源），并在结果中显示警告。

2. **版本独立性**：导入后的版本与源版本完全独立，后续修改互不影响。

3. **权限要求**：导入功能需要"模型设计师"或"系统管理员"角色权限。

4. **性能考虑**：大型模型版本（200+节点）的导入可能需要几秒钟时间，前端已实现加载状态提示。

## 已知限制

1. 不支持导入维度目录映射（因为收费项目与医疗机构相关）
2. 不支持从外部文件导入
3. 导入后的版本默认为"未激活"状态

## 总结

模型版本导入功能已完整实现，包括后端API、前端UI和数据库支持。功能经过精心设计，提供了良好的用户体验和完善的错误处理机制。现在可以进行测试和部署。
