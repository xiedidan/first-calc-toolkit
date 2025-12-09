# 项目前端规范

## 样式规范

### CSS 约束
禁止使用 SCSS/SASS，统一使用 scoped CSS

### 标准布局
参考 ChargeItems/Departments：
- 容器 padding: `20px`
- 卡片 header 使用 `card-header` 类
- 搜索栏使用 `search-form` 类，margin-bottom: `20px`
- 表格使用 `border stripe v-loading`

### 对话框
- 单步：width `600px`
- 多步：width `800px`，使用 `el-steps`
- 表单 label-width: `120px`
- 所有对话框必须添加 `append-to-body` 属性
- App.vue 已配置全局对话框样式修复（fixed 定位、滚动支持）

## 多租户集成

### HTTP 拦截器
- 自动添加 `X-Hospital-ID` 请求头（从 localStorage）
- 处理 400（未激活）、403（无权限）错误

### 状态管理
- 当前激活医疗机构存储在 Pinia store + localStorage
- 单个医疗机构自动激活，多个需用户选择

### 菜单权限
- 未激活时禁用业务菜单（保留系统设置和数据源管理）
- 使用 `:disabled` 而非 `v-if`
- 二级菜单缩进：`padding-left: 50px`

## 批量操作 UI

### 清空/删除逻辑
- 不选择 = 全部
- 选择单个 = 该项
- 选择多个 = 提示错误

## 树形表格样式

- 维度名称加粗：`font-weight: 600`
- 占比信息格式："名称（占比%）"
- 列标题明确：如"维度名称（业务价值占比）"

## API 调用约定

响应拦截器已返回 `response.data`，组件中直接使用：`const res = await apiFunc()`

## 用户权限系统

### 角色字段
- 后端返回单个 `role` 字段：`'admin' | 'user'`
- Store 的 `hasRole()` 方法使用相等判断而非数组包含
- 角色显示需映射为中文：admin→管理员，user→普通用户

## 选择器标签规范

### 计算任务选择器
- 格式：`任务ID前缀... (流程名称 - 创建时间)`
- 流程名称使用后端预加载的 `workflow_name` 字段
- 无流程时显示"默认流程"
