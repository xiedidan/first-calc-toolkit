# 数据模型管理模块 - 实现任务清单

## 设计概述

### 数据库设计

**data_templates 表**
```sql
CREATE TABLE data_templates (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,           -- 表名（如 TB_CIS_JJBJL）
    table_name_cn VARCHAR(200) NOT NULL,        -- 中文名（如 交接班记录）
    description TEXT,                            -- 表说明
    is_core BOOLEAN DEFAULT FALSE,               -- 是否核心表
    sort_order NUMERIC(10, 2) NOT NULL,         -- 排序序号
    definition_file_path TEXT,                   -- 表定义文档存储路径
    definition_file_name VARCHAR(255),           -- 表定义文档原始文件名
    sql_file_path TEXT,                          -- SQL建表代码存储路径
    sql_file_name VARCHAR(255),                  -- SQL建表代码原始文件名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hospital_id, table_name)              -- 同一医疗机构内表名唯一
);

CREATE INDEX idx_data_templates_hospital ON data_templates(hospital_id);
CREATE INDEX idx_data_templates_sort ON data_templates(hospital_id, sort_order);
CREATE INDEX idx_data_templates_core ON data_templates(hospital_id, is_core);
```

### 文件存储设计

**存储路径结构**:
```
uploads/
  data-templates/
    {hospital_id}/
      definitions/
        {uuid}_{original_filename}.md
      sql/
        {uuid}_{original_filename}.sql
```

**文件命名规则**:
- 使用UUID前缀避免文件名冲突
- 保留原始文件名用于下载时显示
- 按医疗机构ID分目录存储，便于管理和清理

### API设计

**基础路径**: `/api/v1/data-templates`

**端点列表**:
- `GET /data-templates` - 获取数据模板列表
- `POST /data-templates` - 创建数据模板
- `GET /data-templates/{id}` - 获取数据模板详情
- `PUT /data-templates/{id}` - 更新数据模板
- `DELETE /data-templates/{id}` - 删除数据模板
- `POST /data-templates/{id}/upload-definition` - 上传表定义文档
- `POST /data-templates/{id}/upload-sql` - 上传SQL建表代码
- `GET /data-templates/{id}/download-definition` - 下载表定义文档
- `GET /data-templates/{id}/download-sql` - 下载SQL建表代码
- `POST /data-templates/batch-upload` - 批量上传文件
- `POST /data-templates/{id}/move-up` - 上移
- `POST /data-templates/{id}/move-down` - 下移
- `PUT /data-templates/{id}/toggle-core` - 切换核心标志
- `GET /data-templates/hospitals` - 获取其他医疗机构列表（用于复制）
- `POST /data-templates/copy` - 从其他医疗机构复制数据模板

### 前端设计

**页面结构**: `DataTemplates.vue`

**主要组件**:
1. 工具栏：新建、批量上传、从其他医院复制
2. 搜索筛选栏：关键词搜索、核心表筛选、文档状态筛选
3. 数据表格：显示表名、中文名、核心标志、文档状态、操作按钮
4. 编辑对话框：表单 + 文件上传区域
5. 批量上传对话框：文件选择 + 匹配预览 + 确认导入
6. 复制对话框：医疗机构选择 + 数据模板选择 + 确认复制

## 实现任务

- [ ] 1. 数据库模型和迁移脚本
  - 创建 DataTemplate 模型类
  - 定义字段、关系和约束
  - 创建数据库迁移脚本
  - _需求: 1, 6_

- [x] 1.1 创建 DataTemplate 模型


  - 文件路径: `backend/app/models/data_template.py`
  - 参考 ChargeItem 模型的结构
  - 包含 hospital_id 外键和唯一约束
  - 添加文件路径字段和排序字段
  - _需求: 1, 6, 10_

- [x] 1.2 创建数据库迁移脚本


  - 使用 Alembic 创建迁移脚本
  - 包含表创建和索引创建
  - 测试迁移的正向和回滚
  - _需求: 1_

- [ ] 2. Pydantic Schema 定义
  - 创建请求和响应的数据模型
  - 包含验证规则
  - _需求: 1, 9_

- [x] 2.1 创建 Schema 类


  - 文件路径: `backend/app/schemas/data_template.py`
  - DataTemplateBase: 基础字段
  - DataTemplateCreate: 创建请求
  - DataTemplateUpdate: 更新请求
  - DataTemplate: 响应模型
  - DataTemplateList: 列表响应
  - BatchUploadResult: 批量上传结果
  - CopyResult: 复制结果
  - _需求: 1, 3, 7, 9_

- [ ] 3. 文件存储服务
  - 实现文件上传、下载、删除功能
  - 管理文件存储路径
  - _需求: 2, 10_

- [x] 3.1 创建文件存储服务


  - 文件路径: `backend/app/services/data_template_file_service.py`
  - save_definition_file(): 保存表定义文档
  - save_sql_file(): 保存SQL建表代码
  - get_file_path(): 获取文件完整路径
  - delete_file(): 删除文件
  - ensure_directory(): 确保目录存在
  - generate_unique_filename(): 生成唯一文件名
  - _需求: 2, 10_

- [ ] 4. 批量上传解析服务
  - 解析文件名提取表名和中文名
  - 匹配表定义文档和SQL文件
  - _需求: 3_

- [x] 4.1 创建批量上传服务


  - 文件路径: `backend/app/services/data_template_batch_service.py`
  - parse_definition_filename(): 解析表定义文档文件名（中文名(表名).md）
  - parse_sql_filename(): 解析SQL文件名（表名.sql）
  - match_files(): 根据表名匹配文档和SQL文件
  - create_or_update_templates(): 批量创建或更新数据模板
  - _需求: 3_

- [ ] 5. 数据模板基础API
  - 实现CRUD操作
  - 应用医疗机构隔离
  - _需求: 1, 6_

- [x] 5.1 创建数据模板API路由


  - 文件路径: `backend/app/api/data_templates.py`
  - GET /data-templates: 获取列表（支持搜索、筛选、排序、分页）
  - POST /data-templates: 创建数据模板
  - GET /data-templates/{id}: 获取详情
  - PUT /data-templates/{id}: 更新数据模板
  - DELETE /data-templates/{id}: 删除数据模板（级联删除文件）
  - 使用 apply_hospital_filter 应用医疗机构隔离
  - _需求: 1, 6, 8, 9_

- [ ] 6. 文件上传和下载API
  - 实现单个文件上传和下载
  - _需求: 2_

- [ ] 6.1 实现文件上传API
  - POST /data-templates/{id}/upload-definition: 上传表定义文档
  - POST /data-templates/{id}/upload-sql: 上传SQL建表代码
  - 验证文件格式（.md 和 .sql）
  - 验证文件大小（最大10MB）
  - 如果已有文件则删除旧文件
  - 更新数据库记录
  - _需求: 2, 9_

- [ ] 6.2 实现文件下载API
  - GET /data-templates/{id}/download-definition: 下载表定义文档
  - GET /data-templates/{id}/download-sql: 下载SQL建表代码
  - 使用 FileResponse 返回文件流
  - 设置正确的 Content-Disposition 头
  - _需求: 2_

- [ ] 7. 批量上传API
  - 实现批量文件上传和解析
  - _需求: 3_

- [ ] 7.1 实现批量上传API
  - POST /data-templates/batch-upload: 批量上传
  - 接收多个文件（表定义文档和SQL文件）
  - 调用批量上传服务解析和匹配文件
  - 返回匹配结果预览
  - 支持确认后批量创建或更新
  - 返回导入结果报告
  - _需求: 3_

- [ ] 8. 排序管理API
  - 实现上移、下移功能
  - _需求: 4_

- [ ] 8.1 实现排序API
  - POST /data-templates/{id}/move-up: 上移
  - POST /data-templates/{id}/move-down: 下移
  - 交换相邻两条记录的 sort_order
  - 验证是否已经是第一条或最后一条
  - _需求: 4_

- [ ] 9. 核心标志切换API
  - 实现核心标志切换
  - _需求: 5_

- [ ] 9.1 实现核心标志切换API
  - PUT /data-templates/{id}/toggle-core: 切换核心标志
  - 切换 is_core 字段的布尔值
  - 返回更新后的状态
  - _需求: 5_

- [ ] 10. 跨医疗机构复制API
  - 实现从其他医疗机构复制数据模板
  - _需求: 7_

- [ ] 10.1 实现复制相关API
  - GET /data-templates/hospitals: 获取其他医疗机构列表
  - POST /data-templates/copy: 复制数据模板
  - 复制数据模板记录
  - 复制关联的文件
  - 处理表名冲突（覆盖或跳过）
  - 返回复制结果报告
  - _需求: 7_

- [ ] 11. 注册API路由
  - 将数据模板API注册到主应用
  - _需求: 1_

- [x] 11.1 注册路由


  - 文件路径: `backend/app/main.py`
  - 导入 data_templates 路由
  - 使用 app.include_router 注册
  - 设置路径前缀 `/api/v1/data-templates`
  - _需求: 1_

- [ ] 12. 前端API客户端
  - 创建API调用函数
  - _需求: 1_

- [x] 12.1 创建API客户端


  - 文件路径: `frontend/src/api/data-templates.ts`
  - 定义所有API调用函数
  - 使用统一的 request 工具
  - 定义 TypeScript 类型接口
  - _需求: 1, 2, 3, 4, 5, 7, 8_

- [ ] 13. 前端数据模板管理页面
  - 创建主页面组件
  - _需求: 1, 8_

- [x] 13.1 创建页面组件


  - 文件路径: `frontend/src/views/DataTemplates.vue`
  - 页面布局：工具栏 + 搜索栏 + 数据表格
  - 工具栏按钮：新建、批量上传、从其他医院复制
  - 搜索栏：关键词输入框、核心表筛选、文档状态筛选
  - 数据表格：表名、中文名、核心标志、文档状态、操作列
  - 操作按钮：编辑、删除、上移、下移、设置核心
  - 分页组件
  - _需求: 1, 4, 5, 8_

- [ ] 14. 编辑对话框组件
  - 创建数据模板编辑对话框
  - _需求: 1, 2_

- [x] 14.1 创建编辑对话框



  - 在 DataTemplates.vue 中实现对话框
  - 表单字段：表名、中文名、说明、核心标志
  - 文件上传区域：表定义文档、SQL建表代码
  - 显示已上传文件的下载链接
  - 支持替换已有文件
  - 表单验证
  - _需求: 1, 2, 9_

- [ ] 15. 批量上传对话框组件
  - 创建批量上传对话框
  - _需求: 3_

- [x] 15.1 创建批量上传对话框


  - 在 DataTemplates.vue 中实现对话框
  - 文件选择区域（支持多选）
  - 上传并解析文件
  - 显示匹配结果预览表格
  - 表格列：表名、中文名、表定义文档、SQL文件、匹配状态
  - 确认导入按钮
  - 显示导入结果报告
  - _需求: 3_

- [ ] 16. 复制对话框组件
  - 创建从其他医院复制的对话框
  - _需求: 7_

- [x] 16.1 创建复制对话框



  - 在 DataTemplates.vue 中实现对话框
  - 第一步：选择源医疗机构
  - 第二步：显示源医疗机构的数据模板列表
  - 支持全选和单选
  - 冲突处理选项：覆盖或跳过
  - 确认复制按钮
  - 显示复制结果报告
  - _需求: 7_

- [ ] 17. 添加路由配置
  - 将数据模板管理页面添加到路由
  - _需求: 1_

- [x] 17.1 配置路由


  - 文件路径: `frontend/src/router/index.ts`
  - 添加 /data-templates 路由
  - 配置路由元信息（标题、权限等）
  - _需求: 1_

- [ ] 18. 添加导航菜单
  - 在侧边栏添加数据模板管理菜单项
  - _需求: 1_

- [x] 18.1 更新导航菜单



  - 文件路径: `frontend/src/views/Layout.vue`
  - 在适当的菜单组中添加"数据模板管理"菜单项
  - 设置图标和路由链接
  - _需求: 1_

- [ ] 19. 测试和优化
  - 测试所有功能
  - 优化性能
  - _需求: 1-10_

- [ ] 19.1 功能测试
  - 测试数据模板的增删改查
  - 测试文件上传和下载
  - 测试批量上传功能
  - 测试排序功能
  - 测试核心标志切换
  - 测试医疗机构隔离
  - 测试跨医疗机构复制
  - 测试搜索和筛选
  - 测试数据验证
  - _需求: 1-10_

- [ ] 19.2 性能优化
  - 优化列表查询性能（添加索引）
  - 优化文件上传性能（大文件处理）
  - 优化批量上传性能（异步处理）
  - _需求: 1, 2, 3_

- [ ] 19.3 错误处理和用户体验
  - 添加友好的错误提示
  - 添加加载状态指示
  - 添加操作确认对话框
  - 添加成功提示
  - _需求: 1-10_
