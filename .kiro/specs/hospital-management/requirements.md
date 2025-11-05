# 医疗机构管理功能 - 需求文档

## 简介

本功能旨在为系统添加多租户支持,允许系统管理多个医疗机构的数据。每个医疗机构拥有独立的数据空间,用户可以在不同医疗机构之间切换,系统根据当前激活的医疗机构来展示和操作相应的数据。

## 术语表

- **医疗机构(Hospital)**: 系统中的租户单位,代表一个独立的医院或医疗机构
- **医疗机构编码(Hospital Code)**: 医疗机构的唯一标识符,使用拼音或英文缩写
- **激活医疗机构(Active Hospital)**: 用户当前正在操作的医疗机构
- **机构绑定用户(Hospital-Bound User)**: 只能访问特定医疗机构数据的用户
- **超级用户(Super User)**: 不绑定任何机构,可以访问所有机构数据的用户
- **数据隔离(Data Isolation)**: 确保不同医疗机构的数据相互独立,互不干扰

## 需求

### 需求 1: 医疗机构基础管理

**用户故事**: 作为系统管理员,我希望能够管理医疗机构信息,以便系统支持多个医院的数据管理。

#### 验收标准

1. WHEN 系统管理员访问医疗机构管理页面, THE System SHALL 显示所有已配置的医疗机构列表
2. WHEN 系统管理员创建新医疗机构, THE System SHALL 要求输入医疗机构编码和医疗机构名称
3. WHEN 系统管理员输入的医疗机构编码已存在, THE System SHALL 拒绝创建并提示编码重复
4. WHEN 系统管理员编辑医疗机构信息, THE System SHALL 允许修改医疗机构名称但不允许修改医疗机构编码
5. WHEN 系统管理员删除医疗机构, THE System SHALL 检查该机构是否有关联数据,如有则拒绝删除并提示

### 需求 2: 医疗机构激活与切换

**用户故事**: 作为系统用户,我希望能够激活某个医疗机构,以便对该机构的数据进行操作。

#### 验收标准

1. WHEN 用户登录系统且未激活任何医疗机构, THE System SHALL 仅允许访问系统设置和数据源管理菜单
2. WHEN 用户登录系统且未激活任何医疗机构, THE System SHALL 禁用其他所有一级菜单
3. WHEN 用户选择激活某个医疗机构, THE System SHALL 验证用户是否有权访问该机构
4. WHEN 用户成功激活医疗机构, THE System SHALL 在页面顶部标题栏显示该机构名称
5. WHEN 用户成功激活医疗机构, THE System SHALL 将标题更新为"XX医院科室业务价值评估工具"格式
6. WHEN 用户激活医疗机构后, THE System SHALL 启用所有一级菜单供用户访问
7. WHEN 用户切换到不同医疗机构, THE System SHALL 重新加载页面数据以显示新机构的数据

### 需求 3: 用户与医疗机构绑定

**用户故事**: 作为系统管理员,我希望能够将用户绑定到特定医疗机构,以便实现数据访问权限控制。

#### 验收标准

1. WHEN 系统管理员创建或编辑用户, THE System SHALL 提供所属医疗机构选择字段
2. WHEN 系统管理员为用户选择所属医疗机构, THE System SHALL 将该用户绑定到指定机构
3. WHEN 系统管理员不为用户选择所属医疗机构, THE System SHALL 将该用户标记为超级用户
4. WHEN 机构绑定用户登录系统, THE System SHALL 仅允许该用户访问其所属机构的数据
5. WHEN 机构绑定用户尝试激活非所属机构, THE System SHALL 拒绝激活并提示权限不足
6. WHEN 超级用户登录系统, THE System SHALL 允许该用户访问所有医疗机构的数据
7. WHEN 超级用户激活任意医疗机构, THE System SHALL 允许激活并显示该机构数据

### 需求 4: 数据库数据迁移

**用户故事**: 作为系统管理员,我希望现有数据能够平滑迁移到新的多租户架构,以便保证系统升级不影响现有功能。

#### 验收标准

1. WHEN 系统执行数据迁移脚本, THE System SHALL 创建默认医疗机构"宁波市眼科医院"
2. WHEN 系统创建默认医疗机构, THE System SHALL 使用医疗机构编码"nbeye"
3. WHEN 系统执行数据迁移脚本, THE System SHALL 将所有现有数据关联到默认医疗机构
4. WHEN 系统执行数据迁移脚本, THE System SHALL 为所有需要机构隔离的表添加hospital_id字段
5. WHEN 系统执行数据迁移脚本, THE System SHALL 更新所有现有数据的hospital_id为默认机构ID
6. WHEN 数据迁移完成后, THE System SHALL 保持所有现有功能正常运行
7. WHEN 数据迁移完成后, THE System SHALL 允许用户继续访问原有数据

### 需求 5: 数据隔离与权限控制

**用户故事**: 作为系统架构师,我希望系统能够严格隔离不同医疗机构的数据,以便保证数据安全和隐私。

#### 验收标准

1. WHEN 用户查询任何业务数据, THE System SHALL 自动添加当前激活医疗机构的过滤条件
2. WHEN 用户创建任何业务数据, THE System SHALL 自动关联到当前激活的医疗机构
3. WHEN 用户更新任何业务数据, THE System SHALL 验证该数据属于当前激活的医疗机构
4. WHEN 用户删除任何业务数据, THE System SHALL 验证该数据属于当前激活的医疗机构
5. WHEN 机构绑定用户尝试访问其他机构数据, THE System SHALL 拒绝访问并返回空结果
6. WHEN 超级用户未激活任何机构, THE System SHALL 不返回任何业务数据
7. WHEN API接口接收到数据请求, THE System SHALL 从用户会话中获取当前激活的医疗机构ID

### 需求 6: 菜单权限控制

**用户故事**: 作为系统用户,我希望在未激活医疗机构时只能访问必要的系统功能,以便避免误操作。

#### 验收标准

1. WHEN 用户未激活任何医疗机构, THE System SHALL 仅显示系统设置菜单为可用状态
2. WHEN 用户未激活任何医疗机构, THE System SHALL 仅显示数据源管理菜单为可用状态
3. WHEN 用户未激活任何医疗机构, THE System SHALL 将模型管理菜单显示为禁用状态
4. WHEN 用户未激活任何医疗机构, THE System SHALL 将科室管理菜单显示为禁用状态
5. WHEN 用户未激活任何医疗机构, THE System SHALL 将计算任务菜单显示为禁用状态
6. WHEN 用户未激活任何医疗机构, THE System SHALL 将结果查询菜单显示为禁用状态
7. WHEN 用户激活医疗机构后, THE System SHALL 启用所有菜单供用户访问

### 需求 7: 界面展示调整

**用户故事**: 作为系统用户,我希望能够清楚地看到当前正在操作的医疗机构,以便避免数据混淆。

#### 验收标准

1. WHEN 用户激活医疗机构, THE System SHALL 在页面顶部标题栏显示医疗机构名称
2. WHEN 用户激活医疗机构, THE System SHALL 将页面标题更新为"{医疗机构名称}科室业务价值评估工具"格式
3. WHEN 用户未激活医疗机构, THE System SHALL 显示默认标题"医院科室业务价值评估工具"
4. WHEN 用户在顶部标题栏点击医疗机构名称, THE System SHALL 显示医疗机构切换下拉菜单
5. WHEN 用户在下拉菜单中选择其他医疗机构, THE System SHALL 切换到该机构并刷新页面数据
6. WHEN 机构绑定用户查看医疗机构切换菜单, THE System SHALL 仅显示该用户所属的医疗机构
7. WHEN 超级用户查看医疗机构切换菜单, THE System SHALL 显示所有医疗机构供选择

### 需求 8: 数据迁移脚本

**用户故事**: 作为数据库管理员,我希望有完整的数据迁移脚本,以便安全地升级系统到多租户架构。

#### 验收标准

1. WHEN 执行数据迁移脚本, THE System SHALL 创建hospitals表存储医疗机构信息
2. WHEN 执行数据迁移脚本, THE System SHALL 在users表添加hospital_id字段
3. WHEN 执行数据迁移脚本, THE System SHALL 为所有业务表添加hospital_id字段
4. WHEN 执行数据迁移脚本, THE System SHALL 创建默认医疗机构记录
5. WHEN 执行数据迁移脚本, THE System SHALL 更新所有现有数据的hospital_id字段
6. WHEN 执行数据迁移脚本, THE System SHALL 为hospital_id字段添加外键约束
7. WHEN 执行数据迁移脚本, THE System SHALL 为hospital_id字段添加索引以提升查询性能
