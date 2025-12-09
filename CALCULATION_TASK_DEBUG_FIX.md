# 计算任务执行问题修复

## 问题诊断

### 症状
- 步骤测试功能可以正确写入数据库
- 实际任务执行不能写入数据库
- 后端和Celery均没有看到相关调试信息

### 根本原因

在 `backend/app/tasks/calculation_tasks.py` 的 `execute_calculation_step` 函数中，当没有指定科室（批量处理模式）时，`{hospital_id}` 占位符被替换为字符串 `"NULL"`，导致SQL执行失败。

**问题代码：**
```python
else:
    # 未指定科室：使用空值或特殊标记
    code = code.replace("{hospital_id}", "NULL")  # ❌ 错误：字符串"NULL"
```

这会导致SQL语句变成：
```sql
INSERT INTO calculation_results (hospital_id, ...) VALUES (NULL, ...)
```

如果 `hospital_id` 字段有 NOT NULL 约束，这会导致插入失败。

### 修复方案

1. **添加 `hospital_id` 参数**：在 `execute_calculation_step` 函数中添加 `hospital_id` 参数
2. **从模型版本获取**：在任务执行开始时从 `ModelVersion` 获取 `hospital_id`
3. **正确替换占位符**：使用实际的 `hospital_id` 数值而不是字符串 "NULL"

## 修复内容

### 0. 添加缺失的导入

```python
from app.models.model_version import ModelVersion  # ✓ 添加导入
```

### 1. 更新 `execute_calculation_step` 函数签名

```python
def execute_calculation_step(
    db: Session,
    task_id: str,
    step: CalculationStep,
    department: Optional[Department],
    period: str,
    model_version_id: int,
    hospital_id: int  # ✓ 新增参数
):
```

### 2. 在任务开始时获取 `hospital_id`

```python
# 获取医疗机构ID（从模型版本获取）
model_version = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
if not model_version:
    task.status = "failed"
    task.error_message = "模型版本不存在"
    task.completed_at = datetime.now()
    db.commit()
    return {"success": False, "error": "模型版本不存在"}

hospital_id = model_version.hospital_id
```

### 3. 正确替换 `{hospital_id}` 占位符

```python
else:
    # 未指定科室：批量处理模式，使用传入的hospital_id
    code = code.replace("{hospital_id}", str(hospital_id))  # ✓ 使用实际ID
```

### 4. 传递 `hospital_id` 参数

```python
execute_calculation_step(
    db=db,
    task_id=task_id,
    step=step,
    department=department,
    period=period,
    model_version_id=model_version_id,
    hospital_id=hospital_id  # ✓ 传递参数
)
```

### 5. 增强调试日志

添加了详细的日志输出，帮助诊断问题：

```python
print(f"[INFO] 任务 {task_id} 开始执行")
print(f"[INFO] 参数: model_version_id={model_version_id}, workflow_id={workflow_id}, period={period}")
print(f"[INFO] department_ids={department_ids}")
print(f"[INFO] 医疗机构ID: {hospital_id}")
print(f"[INFO] 找到 {len(steps)} 个启用的步骤")
print(f"[INFO] 需要处理 {total_departments} 个科室/批次")
print(f"[INFO] 处理第 {idx+1}/{total_departments} 个: {dept_name}")
print(f"[INFO] 执行步骤 {step.id}: {step.name}")
```

在API层也添加了日志：

```python
print(f"[INFO] 提交Celery任务: task_id={task_id}")
result = execute_calculation_task.delay(...)
print(f"[INFO] Celery任务已提交: celery_task_id={result.id}")
```

## 验证步骤

### 1. 重启服务

```bash
# 重启后端
# 停止当前运行的后端进程，然后重新启动

# 重启Celery worker
# 停止当前运行的Celery worker，然后重新启动
cd backend
celery -A app.celery_app worker --loglevel=debug --pool=solo
```

### 2. 查看日志

**后端日志应该显示：**
```
[INFO] 提交Celery任务: task_id=xxx
[INFO] Celery任务已提交: celery_task_id=yyy
```

**Celery worker日志应该显示：**
```
[INFO] 任务 xxx 开始执行
[INFO] 参数: model_version_id=1, workflow_id=1, period=2025-10
[INFO] department_ids=None
[INFO] 医疗机构ID: 1
[INFO] 找到 3 个启用的步骤
[INFO] 需要处理 1 个科室/批次
[INFO] 处理第 1/1 个: 全部科室
[INFO] 执行步骤 1: 步骤名称
[DEBUG] 步骤 1 使用数据源: xxx (ID: 1)
[DEBUG] 开始执行SQL，task_id=xxx
[DEBUG] 提交事务，共执行 X 个语句，影响 Y 行
[DEBUG] 事务提交成功
步骤 1 (步骤名称) 在科室 全部科室 执行成功，耗时 XXXms
```

### 3. 检查数据库

执行任务后，检查 `calculation_results` 表：

```sql
SELECT COUNT(*) FROM calculation_results WHERE task_id = 'xxx';
```

应该能看到插入的记录。

### 4. 检查任务状态

```sql
SELECT task_id, status, error_message, started_at, completed_at 
FROM calculation_tasks 
ORDER BY created_at DESC 
LIMIT 5;
```

任务状态应该从 `pending` → `running` → `completed`。

## 常见问题排查

### 问题1：任务一直是 pending 状态

**原因：** Celery worker 未运行或未连接到broker

**解决：**
1. 检查 Redis 是否运行：`redis-cli ping`
2. 检查 Celery worker 是否运行
3. 查看 Celery worker 日志是否有错误

### 问题2：任务变成 failed 状态但没有错误信息

**原因：** 异常被捕获但未正确记录

**解决：**
1. 查看 Celery worker 的控制台输出
2. 检查是否有 `[ERROR]` 标记的日志
3. 查看 `calculation_step_logs` 表中的失败记录

### 问题3：SQL执行失败

**原因：** 参数替换不正确或SQL语法错误

**解决：**
1. 使用步骤测试功能验证SQL
2. 检查所有占位符是否正确替换
3. 查看 Celery worker 日志中的完整错误信息

## 测试建议

### 测试场景1：批量处理（不指定科室）

创建任务时不选择科室，让SQL处理所有科室：

```json
{
  "model_version_id": 1,
  "workflow_id": 1,
  "period": "2025-10",
  "department_ids": null
}
```

### 测试场景2：指定科室

创建任务时选择特定科室：

```json
{
  "model_version_id": 1,
  "workflow_id": 1,
  "period": "2025-10",
  "department_ids": [1, 2, 3]
}
```

### 测试场景3：单个科室

创建任务时只选择一个科室：

```json
{
  "model_version_id": 1,
  "workflow_id": 1,
  "period": "2025-10",
  "department_ids": [1]
}
```

## 总结

修复的核心是确保 `{hospital_id}` 占位符始终被替换为有效的数值，而不是字符串 "NULL"。通过从 `ModelVersion` 获取 `hospital_id` 并传递给 `execute_calculation_step` 函数，解决了批量处理模式下的参数替换问题。

同时增强了日志输出，使得问题诊断更加容易。
