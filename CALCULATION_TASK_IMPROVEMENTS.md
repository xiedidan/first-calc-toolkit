# 计算任务改进说明

## 改进内容

### 1. 任务创建逻辑优化

**改进前：** 创建任务时需要等待异步任务提交成功才返回

**改进后：** 任务写入数据库即认为创建成功，立即返回任务信息

**影响文件：**
- `backend/app/api/calculation_tasks.py` - `create_calculation_task` 函数

**改进点：**
- 提高API响应速度
- 即使异步任务队列出现问题，任务记录也已创建
- 用户可以立即看到任务已创建，状态为"排队中"

### 2. 任务失败逻辑优化

**改进前：** 某个科室的步骤失败后，继续处理其他科室

**改进后：** 任何步骤失败，整个任务立即标记为失败并停止执行

**影响文件：**
- `backend/app/tasks/calculation_tasks.py` - `execute_calculation_task` 函数

**改进点：**
- 更符合业务逻辑：计算任务应该是原子性的
- 避免部分成功部分失败的混乱状态
- 失败时立即停止，节省资源

### 3. 执行日志UI优化

**改进前：**
- 字段名为"错误信息"（error_message）
- 表格中包含错误信息列，导致排版拥挤
- 只有失败时才有信息显示

**改进后：**
- 字段名改为"执行信息"（execution_info）
- 表格中移除执行信息列，优化排版
- 新增独立的"执行信息"时间线展示区域
- 成功和失败都有执行信息

**影响文件：**
- `backend/app/models/calculation_step_log.py` - 字段重命名
- `backend/app/api/calculation_tasks.py` - API返回字段更新
- `backend/app/tasks/calculation_tasks.py` - 记录执行信息
- `frontend/src/views/CalculationTasks.vue` - UI优化
- `backend/alembic/versions/3900f968ffe3_rename_error_message_to_execution_info.py` - 数据库迁移

**UI改进：**
- 步骤执行详情表格更简洁，只显示关键信息
- 新增时间线视图展示执行信息，更直观
- 成功步骤显示"执行成功，返回 X 行数据"
- 失败步骤显示"执行失败: 错误原因"

## 数据库迁移 ⚠️ 重要

**必须先执行数据库迁移，否则任务执行会失败！**

执行以下命令应用数据库迁移：

```bash
cd backend
alembic upgrade head
```

迁移内容：
1. **字段重命名** - 将 `calculation_step_logs.error_message` 重命名为 `execution_info`
2. **移除外键约束** - 移除 `calculation_results` 和 `calculation_summaries` 表的外键约束
3. **添加唯一约束** - 为 `calculation_summaries` 添加 `(task_id, department_id)` 唯一约束以支持 `ON CONFLICT`

**为什么移除外键约束？**
- 计算结果表是历史数据，不应该受到主表数据变更的影响
- 即使科室或节点被删除，历史计算结果仍应保留
- 提高数据插入性能，避免外键检查开销
- 支持更灵活的数据导入和测试场景

**验证迁移是否成功：**

```sql
-- 检查字段是否已重命名
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'calculation_step_logs' 
  AND column_name IN ('error_message', 'execution_info');

-- 应该只看到 execution_info，不应该有 error_message
```

**如果看到错误 "column error_message does not exist"：**
说明代码已更新但数据库迁移未执行，请立即执行上述迁移命令。

## 错误处理增强

为了确保任务失败时状态能正确更新，添加了以下增强：

1. **详细的日志输出**
   - 所有关键步骤都有日志输出
   - 错误信息带有 `[ERROR]` 前缀
   - 包含完整的堆栈跟踪信息

2. **多层异常捕获**
   - 步骤执行层：捕获单个步骤的异常
   - 科室循环层：捕获科室级别的异常
   - 任务执行层：捕获整个任务的异常
   - 每层都确保数据库状态正确更新

3. **任务超时处理**
   - 软超时：58分钟（给予清理时间）
   - 硬超时：60分钟（强制终止）
   - 超时时自动标记任务为失败

4. **状态更新保护**
   - 避免覆盖已设置的失败状态
   - 日志记录失败不影响任务执行
   - 数据库提交失败有独立的错误处理

## 调试建议

如果任务状态仍然卡在"running"：

1. **检查Celery Worker日志**
   ```bash
   # 查看worker输出，寻找 [ERROR] 标记的错误
   ```

2. **检查数据库连接**
   - 确认数据库连接正常
   - 检查是否有长时间未提交的事务

3. **检查步骤日志表**
   ```sql
   SELECT * FROM calculation_step_logs 
   WHERE task_id = '任务ID' 
   ORDER BY start_time DESC;
   ```
   查看哪个步骤失败了

4. **手动修复卡住的任务**
   ```sql
   UPDATE calculation_tasks 
   SET status = 'failed', 
       error_message = '任务执行异常，已手动标记为失败',
       completed_at = NOW()
   WHERE task_id = '任务ID' AND status = 'running';
   ```

## 测试建议

1. **任务创建测试**
   - 创建任务后立即检查数据库，确认任务记录已存在
   - 验证任务状态为"pending"
   - 验证API响应时间明显缩短

2. **任务失败测试**
   - 创建一个包含错误SQL的计算步骤
   - 验证任务在第一个失败步骤后立即停止
   - 验证任务状态为"failed"
   - 验证错误信息正确记录
   - 检查Celery日志中的错误输出

3. **UI测试**
   - 查看执行日志，验证表格排版更整洁
   - 验证执行信息时间线正确显示
   - 验证成功和失败步骤都有执行信息
   - 验证详情对话框中执行信息正确显示

4. **异常场景测试**
   - 数据库连接断开
   - SQL语法错误
   - 数据源不存在
   - 任务超时（可以设置较短的超时时间测试）

## 兼容性说明

- 数据库迁移会自动重命名字段，不影响现有数据
- API字段名变更，前端已同步更新
- 旧的执行日志数据会自动迁移到新字段
- 增加的日志输出不影响现有功能
