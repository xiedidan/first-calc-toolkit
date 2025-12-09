# 实现计划

- [x] 1. 后端API增强

  - 为计算任务列表API添加period参数筛选支持
  - 为汇总数据API添加task_id参数支持
  - 添加数据库索引优化查询性能
  - _需求: 1.2, 1.3, 3.1, 3.2, 3.3, 3.4_

- [x] 1.1 修改任务列表API支持period筛选


  - 在`backend/app/api/calculation_tasks.py`的`get_calculation_tasks`函数中添加period参数
  - 添加period筛选逻辑到查询条件
  - 确保医疗机构隔离过滤正常工作
  - _需求: 3.1, 3.4_

- [x] 1.2 修改汇总数据API支持task_id参数


  - 在`backend/app/api/calculation_tasks.py`的`get_results_summary`函数中添加task_id参数
  - 实现参数优先级逻辑：task_id优先于period+model_version_id
  - 添加参数冲突验证
  - _需求: 1.4, 3.1_

- [x] 1.3 添加数据库索引


  - 创建Alembic迁移文件
  - 添加索引：`idx_calculation_tasks_period_status`
  - 测试索引创建的幂等性
  - _需求: 3.3_

- [x] 2. 前端报表页面任务选择器

  - 添加任务选择器UI组件
  - 实现任务列表加载逻辑
  - 实现任务选择变化处理
  - 集成URL参数初始化
  - _需求: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.1 添加任务选择器UI


  - 在`frontend/src/views/Results.vue`的筛选条件区域添加el-select组件
  - 设置选择器样式和占位符
  - 添加加载状态显示
  - _需求: 1.1_

- [x] 2.2 实现任务列表加载


  - 添加`loadAvailableTasks`方法
  - 根据period和model_version_id筛选任务
  - 仅加载status为completed的任务
  - 格式化任务选项显示文本
  - _需求: 1.2, 3.2_

- [x] 2.3 实现任务选择处理


  - 添加`onTaskChange`方法
  - 选择任务后重新加载汇总数据
  - 更新selectedTaskId状态
  - _需求: 1.3_

- [x] 2.4 实现URL参数初始化


  - 添加`initFromUrlParams`方法
  - 从route.query读取task_id参数
  - 根据task_id加载任务详情并设置筛选条件
  - 在onMounted中调用初始化方法
  - _需求: 2.2, 2.3_

- [x] 2.5 修改筛选条件变化处理

  - 当period或model_version_id变化时重新加载任务列表
  - 清空当前选中的任务
  - 清除URL中的task_id参数
  - _需求: 1.5, 2.4_

- [x] 3. 前端明细和导出功能集成

  - 修改明细查看使用selectedTaskId
  - 修改导出功能使用selectedTaskId
  - 添加缺少任务ID的错误提示
  - _需求: 4.1, 4.2, 4.3, 5.1, 5.3_

- [x] 3.1 修改明细查看功能


  - 在`viewDetail`方法中使用selectedTaskId
  - 添加任务ID缺失检查
  - 在明细对话框标题中显示任务ID
  - _需求: 4.1, 4.2, 4.3, 4.4_

- [x] 3.2 修改导出明细功能


  - 在`exportDetail`方法中使用selectedTaskId
  - 添加任务ID缺失检查和警告提示
  - 在导出文件名中包含任务ID
  - _需求: 5.1, 5.3, 5.4_

- [x] 4. 任务管理页面跳转集成

  - 修改查看结果按钮的跳转逻辑
  - 传递task_id、period、model_version_id参数
  - _需求: 2.1_

- [x] 4.1 修改viewResults方法


  - 在`frontend/src/views/CalculationTasks.vue`中修改`viewResults`方法
  - 在router.push的query中添加task_id参数
  - 确保period和model_version_id也被传递
  - _需求: 2.1_

- [x] 5. 前端类型定义更新


  - 更新API类型定义
  - 添加TaskOption接口
  - 更新FilterForm接口
  - _需求: 1.1, 1.2, 1.3_

- [x] 5.1 更新calculation-tasks.ts类型定义


  - 在`frontend/src/api/calculation-tasks.ts`中更新getCalculationTasks参数类型
  - 添加period参数到接口定义
  - _需求: 3.1_

- [x] 5.2 添加TaskOption接口

  - 在Results.vue的script部分添加TaskOption接口定义
  - 定义task_id、label、period等字段
  - _需求: 1.2_

- [ ] 6. 集成测试
  - 测试从任务管理页面跳转到报表
  - 测试在报表页面选择任务
  - 测试明细查看和导出功能
  - 测试多租户隔离
  - _需求: 所有需求_

- [ ] 6.1 测试跨页面跳转
  - 在任务管理页面点击"查看结果"
  - 验证URL参数正确传递
  - 验证报表页面正确初始化
  - 验证数据正确加载
  - _需求: 2.1, 2.2, 2.3_

- [ ] 6.2 测试任务选择功能
  - 在报表页面选择不同任务
  - 验证汇总表数据更新
  - 验证明细查看使用正确任务
  - 验证导出使用正确任务
  - _需求: 1.3, 4.1, 5.1_

- [ ]* 6.3 测试多租户隔离
  - 切换医疗机构
  - 验证任务列表仅显示当前机构任务
  - 验证跨机构访问被拒绝
  - _需求: 3.4_

- [ ]* 6.4 测试错误处理
  - 测试无效task_id的处理
  - 测试缺少任务ID的提示
  - 测试任务列表加载失败的处理
  - _需求: 4.3, 5.3_
