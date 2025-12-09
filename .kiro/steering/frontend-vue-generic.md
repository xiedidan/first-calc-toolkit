# Vue 3 + Element Plus 通用规范

## Vue 响应式陷阱

### 模板中避免直接调用方法
模板中直接调用 `array.join()` 等方法会导致无限递归，应使用 computed 属性

### Computed 返回函数问题
`computed(() => (param) => {...})` 每次访问创建新函数引用触发无限更新，改用普通函数

### 空值安全
- 使用可选链：`obj?.prop?.method()`
- 提供默认值：`array?.join(', ') || ''`

## Pinia Store

### 状态初始化
- localStorage 恢复状态使用 try-catch
- 初始化失败时清理无效数据

### 避免循环触发
- 检查状态是否已存在再执行操作
- 避免自动激活逻辑中触发页面重载
- 使用导航代替 `router.go(0)`

## Element Plus 组件

### Dropdown
- disabled 项中避免复杂计算
- 使用计算属性缓存显示内容

### 分页陷阱
`@current-change` 会传递页码作为参数，需使用专门处理函数：
- 翻页：不重置页码
- 搜索/筛选/改变每页数量：重置 `currentPage = 1`

### 树形表格
- 必需属性：`row-key`、`:tree-props="{ children: 'children' }"`
- 数据结构：叶子节点不含 `children` 字段，父节点含 `children` 数组

### 对话框（el-dialog）
- 必须添加 `append-to-body` 属性，确保对话框插入到 body 下，避免页面滚动时定位异常
- 页面滚动后打开对话框可能导致对话框定位到视口外，需在全局样式中设置 `.el-overlay` 和 `.el-overlay-dialog` 为 `position: fixed`
- 避免在 `body.el-popup-parent--hidden` 上使用 `position: fixed`，会导致关闭对话框后需点击才能滚动

### 页面滚动焦点丢失
- 树形表格等复杂组件可能导致滚动焦点丢失
- 全局设置 `html { overflow-y: scroll }` 强制显示滚动条，确保始终可滚动
- 避免使用 `position: fixed` 锁定 body，改用 `overflow: hidden`

## 性能优化

- 模板中复杂逻辑提取为 computed
- 避免模板中数据转换
- 大列表使用虚拟滚动
- 合理使用 v-memo、v-once

## Vite 构建

### 避免循环依赖
使用动态分包函数 `manualChunks(id)` 而非静态配置对象

## 跨页多选

使用 `@select` 和 `@select-all` 而非 `@selection-change`，配合 `:reserve-selection="true"` 和 `row-key`

## 列表操作按钮

上移下移按钮需检查全局位置而非当前页索引

## 文件处理

### 上传
- 单文件：`:limit="1"` + `:auto-upload="false"`
- 多文件：`multiple` + `:file-list` + `:on-change` + `:on-remove`
- 待上传文件存储在 `ref<File | null>` 或 `ref<File[]>`

### 下载
- 设置 `responseType: 'blob'`
- 使用 `URL.createObjectURL()` 创建链接
- 下载后释放：`URL.revokeObjectURL(url)`
- **从响应头获取文件名**：前端不应硬编码文件名，应从`Content-Disposition`响应头中提取后端返回的文件名
- **Axios拦截器与blob**：响应拦截器返回`response.data`会丢失headers，blob类型响应需返回完整response对象

### Markdown 渲染
使用 `marked` 库，用 `:deep()` 修改渲染后 HTML 样式

## 路由导航参数传递

### 跨页面状态传递
- 页面跳转时必须传递完整的上下文参数（如 ID、版本号、时间等）
- 目标页面从 `route.query` 初始化状态时需类型转换（`Number()`）
- 避免依赖全局状态或假设默认值能满足跳转场景

### 参数优先级
- URL 参数 > 默认值（如激活版本）
- 初始化时先检查 URL 参数是否存在再应用默认逻辑

### URL参数初始化模式
- 从URL参数初始化时，先加载参数对应的完整对象
- 从对象中提取所有相关筛选条件，确保状态一致
- 初始化失败时清除无效参数，回退到默认逻辑

## API 响应处理

检查 Axios 拦截器是否已返回 `response.data`，避免重复解构

### 传递完整上下文数据
- 关键操作（如导入执行）应传递完整数据，不依赖后端会话
- 避免仅传递 ID 依赖后端查询（后端重启会丢失会话）
- 预览数据应在执行时一并传递

### 后端预加载字段优先使用
- 后端API已在响应中预加载关联字段时，直接使用而非前端再次查找
- 避免依赖前端本地数据源（如需额外API调用的数组）
- 减少不必要的数据加载和查找操作

## 选择器与下拉框

### 关联字段显示
- 关联对象名称优先使用后端预加载字段
- 为空值提供默认显示文本

## 前后端数据契约

### 字段名称一致性
- 前端类型定义必须与后端 API 响应字段完全匹配
- 单复数形式必须一致（`role` vs `roles`）
- Store 中的访问逻辑必须与类型定义匹配

### 权限判断
- 检查后端返回的角色字段格式（字符串/数组/枚举）
- Store 方法需适配实际数据结构
- 条件渲染（`v-if`）依赖的计算属性需验证数据源

## 变量命名一致性

### 重构后的变量名检查
- 变量名从单数改为复数（或反之）时，全局搜索所有引用
- 特别注意回调函数、事件处理器中的引用
- 使用 IDE 的重命名功能而非手动查找替换
- 测试所有相关功能确保无遗漏
