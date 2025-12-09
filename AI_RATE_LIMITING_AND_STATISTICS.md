# AI分类限流和统计功能实现总结

## 概述

本文档总结了医技智能分类分级模块中API调用限流和使用统计功能的实现。

## 实现的功能

### 1. API调用限流逻辑

#### 1.1 调用延迟控制
- **位置**: `backend/app/tasks/classification_tasks.py`
- **功能**: 在每次AI接口调用之间添加可配置的延迟
- **配置**: `AIConfig.call_delay`（默认1.0秒）
- **实现**:
  ```python
  call_delay = float(ai_config.call_delay or 1.0)
  time.sleep(call_delay)
  ```

#### 1.2 批次处理逻辑
- **功能**: 将大批量项目分批处理，批次间增加额外暂停时间
- **配置**: `AIConfig.batch_size`（默认100个项目/批次）
- **实现**:
  ```python
  batch_size = int(ai_config.batch_size or 100)
  batch_count += 1
  if batch_count >= batch_size:
      pause_duration = call_delay * 2  # 批次间暂停为调用延迟的2倍
      time.sleep(pause_duration)
      batch_count = 0
  ```

#### 1.3 每日限额检查
- **功能**: 在每次调用前检查是否达到每日限额，达到后暂停任务
- **配置**: `AIConfig.daily_limit`（默认10000次/天）
- **实现**:
  ```python
  today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
  today_calls = db.query(APIUsageLog).filter(
      APIUsageLog.hospital_id == hospital_id,
      APIUsageLog.created_at >= today_start
  ).count()
  
  if today_calls >= daily_limit:
      task.status = TaskStatus.paused
      task.error_message = f"已达到每日API调用限额 ({daily_limit} 次)，任务已暂停"
      return {"success": False, "error": error_msg}
  ```

#### 1.4 任务暂停通知
- **功能**: 达到限额时自动暂停任务并记录错误信息
- **状态**: 任务状态更新为`paused`
- **通知**: 错误信息记录在`ClassificationTask.error_message`

### 2. API使用统计功能

#### 2.1 统计指标
- **位置**: `backend/app/services/ai_config_service.py`
- **功能**: 查询APIUsageLog表，统计多个维度的使用数据

**统计指标包括**:
1. **总调用次数** (`total_calls`): 指定时间段内的所有API调用
2. **成功调用次数** (`successful_calls`): HTTP状态码为200的调用
3. **失败调用次数** (`failed_calls`): 非200状态码的调用
4. **今日调用次数** (`today_calls`): 当天的所有调用
5. **每日限额** (`daily_limit`): 配置的每日最大调用次数
6. **平均响应时间** (`avg_duration`): 成功调用的平均耗时（秒）
7. **预估成本** (`estimated_cost`): 基于可配置单价计算的总成本

#### 2.2 成本计算
- **功能**: 支持可配置的单价计算预估成本
- **默认单价**: 0.001元/次
- **计算公式**: `estimated_cost = total_calls * cost_per_call`
- **API参数**: `cost_per_call`（可选，默认0.001）

#### 2.3 API端点
```
GET /api/v1/ai-config/usage-stats?days=30&cost_per_call=0.001
```

**请求参数**:
- `days`: 统计天数（默认30天）
- `cost_per_call`: 每次调用成本（元，默认0.001）

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_calls": 1250,
    "successful_calls": 1200,
    "failed_calls": 50,
    "today_calls": 45,
    "daily_limit": 10000,
    "avg_duration": 1.234,
    "estimated_cost": 1.25,
    "period_days": 30
  }
}
```

## 配置说明

### AI配置表字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `call_delay` | Float | 1.0 | 调用延迟（秒），范围0.1-10 |
| `batch_size` | Integer | 100 | 批次大小（项目数） |
| `daily_limit` | Integer | 10000 | 每日调用限额 |

### 配置建议

#### 1. 调用延迟 (call_delay)
- **低频场景**: 1.0-2.0秒（推荐）
- **高频场景**: 0.5-1.0秒（需确保不超过API限制）
- **保守场景**: 2.0-5.0秒（避免触发限流）

#### 2. 批次大小 (batch_size)
- **小批量**: 50-100个项目（适合测试）
- **中批量**: 100-200个项目（推荐）
- **大批量**: 200-500个项目（适合夜间处理）

#### 3. 每日限额 (daily_limit)
- **测试环境**: 100-1000次
- **生产环境**: 5000-10000次
- **企业版**: 10000-50000次

## 性能影响分析

### 处理时间估算

假设配置:
- 调用延迟: 1.0秒
- 批次大小: 100
- 总项目数: 350

**计算**:
- 批次数: 4批
- 项目间延迟: (350-1) × 1.0 = 349秒
- 批次间暂停: (4-1) × 2.0 = 6秒
- **总时间**: 355秒 ≈ 5.9分钟

### 不同配置对比

| 项目数 | 延迟(秒) | 批次大小 | 预计时间 |
|--------|----------|----------|----------|
| 100 | 1.0 | 100 | 1.7分钟 |
| 500 | 1.0 | 100 | 8.5分钟 |
| 1000 | 1.0 | 100 | 17.0分钟 |
| 1000 | 0.5 | 200 | 8.5分钟 |
| 1000 | 2.0 | 100 | 34.0分钟 |

## 监控和告警

### 1. 实时监控
- **Celery任务状态**: 通过`self.update_state()`更新进度
- **进度元数据**: 包含`current`、`total`、`failed`、`batch`
- **前端轮询**: 定期查询任务进度

### 2. 限额告警
- **触发条件**: `today_calls >= daily_limit`
- **任务状态**: 自动更新为`paused`
- **错误信息**: 记录在`task.error_message`
- **恢复方式**: 次日自动重置，或手动调整限额后继续

### 3. 使用统计
- **查看方式**: AI配置页面的"使用统计"面板
- **统计周期**: 可选7天、30天、90天
- **成本分析**: 支持自定义单价计算

## 测试验证

### 测试文件
- `test_rate_limiting.py`: 限流和统计功能测试

### 测试覆盖
1. ✓ 限流配置读取
2. ✓ 使用统计查询
3. ✓ 每日限额检查
4. ✓ 批次处理逻辑
5. ✓ 成本计算（可配置单价）

### 运行测试
```bash
python test_rate_limiting.py
```

## 数据库表

### APIUsageLog（API使用日志）
```sql
CREATE TABLE api_usage_logs (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    charge_item_id INTEGER NOT NULL,
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    error_message TEXT,
    call_duration FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_usage_logs_hospital_created 
    ON api_usage_logs(hospital_id, created_at);
```

## 最佳实践

### 1. 配置优化
- 根据API提供商的限流策略调整`call_delay`
- 根据任务紧急程度调整`batch_size`
- 根据预算和需求设置`daily_limit`

### 2. 成本控制
- 定期查看使用统计，分析成本趋势
- 设置合理的每日限额，避免超支
- 优化提示词，减少不必要的调用

### 3. 任务管理
- 优先处理高确信度项目
- 失败项目单独重试，避免浪费额度
- 夜间处理大批量任务，避免影响白天使用

### 4. 监控告警
- 设置每日使用率告警（如80%、90%）
- 监控失败率，及时发现配置问题
- 记录平均响应时间，评估API性能

## 相关文件

### 后端
- `backend/app/tasks/classification_tasks.py`: Celery任务（限流逻辑）
- `backend/app/services/ai_config_service.py`: AI配置服务（统计功能）
- `backend/app/api/ai_config.py`: AI配置API
- `backend/app/models/api_usage_log.py`: API使用日志模型
- `backend/app/models/ai_config.py`: AI配置模型

### 测试
- `test_rate_limiting.py`: 限流和统计功能测试

## 需求验证

### 需求12.1: API调用延迟控制 ✓
- 实现了可配置的调用延迟
- 每次调用之间添加延迟
- 默认1秒，可配置0.1-10秒

### 需求12.2: 调用延迟配置验证 ✓
- 在AIConfig模型中定义了call_delay字段
- 支持0.1-10秒范围
- 在Celery任务中读取并应用

### 需求12.3: 批次处理逻辑 ✓
- 实现了批次大小控制
- 批次间增加额外暂停时间
- 支持配置批次大小

### 需求12.4: 每日限额控制 ✓
- 实现了每日调用次数检查
- 达到限额时自动暂停任务
- 记录错误信息并通知

### 需求12.5: API使用统计 ✓
- 实现了多维度统计
- 支持按日期统计调用次数
- 支持可配置单价计算成本
- 提供API端点查询统计数据

## 总结

本次实现完成了AI分类模块的限流和统计功能，包括:

1. **限流控制**: 调用延迟、批次处理、每日限额
2. **使用统计**: 多维度统计、成本计算、API查询
3. **任务管理**: 自动暂停、错误记录、进度跟踪
4. **测试验证**: 完整的测试覆盖和验证

所有功能均已实现并通过测试，满足需求文档中的所有验收标准。
