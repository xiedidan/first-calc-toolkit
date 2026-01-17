# 项目前端规范

## 样式规范

### CSS 约束
禁止使用 SCSS/SASS，统一使用 scoped CSS

### 标准布局
参考 ChargeItems/Departments：
- 页面容器：`padding: 0`（滚动由 Layout.vue 的 `.layout-main` 统一处理）
- 卡片 header 使用 `card-header` 类
- 搜索栏使用 `search-form` 类，margin-bottom: `20px`
- 表格使用 `border stripe v-loading`

### 页面滚动机制
- 滚动由 Layout.vue 的 `.layout-main` 统一处理（`overflow-y: auto; height: calc(100vh - 60px)`）
- 页面容器不要设置 `height: 100%` 或 `overflow`，否则会导致双重滚动或间距异常
- 如果页面无法滚动，检查 Layout.vue 的 `.layout-main` 样式是否正确

### 表格滚轮事件穿透（重要）
Element Plus 表格默认会捕获滚轮事件用于水平滚动，导致鼠标在表格上时页面无法垂直滚动。App.vue 已添加全局修复：

**方案一：CSS 修复（基础表格）**
```css
/* 保留横向滚动，禁用纵向滚动（让页面滚动） */
.el-table .el-table__body-wrapper {
  overflow-x: auto !important;
  overflow-y: visible !important;
}
.el-table__inner-wrapper {
  overflow-x: auto !important;
  overflow-y: visible !important;
}
.el-table .el-scrollbar__wrap {
  overflow-x: auto !important;
  overflow-y: visible !important;
}

/* 固定列事件穿透 */
.el-table__fixed, .el-table__fixed-right { pointer-events: none; }
.el-table__fixed *, .el-table__fixed-right * { pointer-events: auto; }
```

**方案二：JavaScript 修复（固定列表格）**
对于有 `fixed` 列的表格，CSS 方案可能不够，需要 JavaScript 全局滚轮事件处理：
```typescript
// App.vue 中监听 wheel 事件
// 检测事件来自表格时，手动滚动 .layout-main 容器
document.addEventListener('wheel', handleTableWheel, { passive: true })
```

注意事项：
- 使用 `overflow-x: auto` 保留横向滚动（宽表格可拖拽）
- 使用 `overflow-y: visible` 让垂直滚轮事件穿透到页面
- 固定列使用 `pointer-events` 穿透，子元素恢复事件响应
- 有 `max-height` 的表格需要内部滚动，JS 方案会检测边界情况

### 对话框
- 单步：width `600px`
- 多步：width `800px`，使用 `el-steps`
- 表单 label-width: `120px`
- 所有对话框必须添加 `append-to-body` 属性
- App.vue 已配置全局对话框样式修复（fixed 定位、滚动支持）

### 下拉选择器自定义选项
当 `el-option` 使用自定义多行内容时，需要：
1. 给 `el-select` 添加 `popper-class="xxx-select-popper"` 属性
2. 在非 scoped 的 `<style>` 块中定义选项高度：
```css
<style>
.xxx-select-popper .el-select-dropdown__item {
  height: auto !important;
  min-height: 50px;
  padding: 8px 20px;
  line-height: 1.5;
}
</style>
```
- 原因：下拉菜单渲染到 body 下，scoped 样式和 `:deep()` 无法生效

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
