# 计算流程管理功能 - 架构调整说明

> **创建日期**: 2025-10-27
> **版本**: V1.4 (需求文档) / V1.1 (系统设计、API设计)
> **状态**: 待确认

---

## 1. 变更概述

本次调整对系统进行了重大架构优化，主要目的是**将代码逻辑从模型结构中分离**，引入独立的**计算流程管理功能**，实现更灵活的计算任务管理。

### 1.1. 核心变更

1. **新增计算流程管理模块**
   - 新增计算流程（Calculation Workflow）实体
   - 新增计算步骤（Calculation Step）实体
   - 提供独立的代码编辑、测试和管理功能

2. **模型结构简化**
   - 模型节点（Model Node）不再包含代码字段
   - 模型专注于业务价值的组织结构
   - 原有的script字段保留但标记为已废弃

3. **计算引擎调整**
   - 计算任务执行时，从计算流程中读取步骤并执行
   - 不再从模型节点读取代码
   - 新增步骤级别的执行日志和错误追踪

---

## 2. 已修改的文档

### 2.1. 需求文档.md (V1.4)

#### 新增章节
- **4.5. 计算流程管理 (FR-CALC-FLOW)**
  - 4.5.1. 功能概述
  - 4.5.2. 计算流程管理 (FR-CALC-FLOW-01)
  - 4.5.3. 计算步骤管理 (FR-CALC-FLOW-02)
  - 4.5.4. 代码编辑器 (FR-CALC-FLOW-03)
  - 4.5.5. 代码测试功能 (FR-CALC-FLOW-04)
  - 4.5.6. 计算任务执行调整 (FR-CALC-FLOW-05)
  - 4.5.7. 数据迁移 (FR-CALC-FLOW-06)
  - 4.5.8. 向后兼容 (FR-CALC-FLOW-07)

- **6. 重要变更说明 (V1.4)**
  - 6.1. 架构调整概述
  - 6.2. 受影响的功能模块
  - 6.3. 数据迁移要求
  - 6.4. API变更
  - 6.5. 前端界面变更
  - 6.6. 向后兼容性

#### 修改内容
- **3.2.3. 节点属性配置**: 标注"计算逻辑"配置项已废弃
- **3.2.6. SQL/Python编辑器与测试**: 标注功能已迁移

### 2.2. 系统设计文档.md (V1.1)

#### 新增章节
- **3.2.5. 计算流程管理服务 (Calculation Workflow Service)**
  - 3.2.5.1. 功能设计
  - 3.2.5.2. 核心实体
  - 3.2.5.3. 接口说明

- **4.1.3. 计算流程管理** (数据库表)
  - `calculation_workflows`: 计算流程表
  - `calculation_steps`: 计算步骤表

- **4.2. 关键表字段设计**
  - `calculation_workflows` 表结构
  - `calculation_steps` 表结构
  - `calculation_step_logs` 表结构

- **5.2. UI原型设计** (新增页面)
  - 5.2.7. 计算流程管理页
  - 5.2.8. 计算步骤管理页
  - 5.2.9. 计算步骤编辑对话框

- **7. 重要架构变更说明 (V1.1)**
  - 7.1. 变更概述
  - 7.2. 核心变更
  - 7.3. 数据迁移策略
  - 7.4. 向后兼容性
  - 7.5. 性能优化
  - 7.6. 安全性增强
  - 7.7. 升级路径
  - 7.8. 未来规划

#### 修改内容
- **3.2.1. 模型管理服务**: 标注代码管理功能已迁移
- **3.5.1. 计算引擎服务**: 更新逻辑处理流程，说明不再从节点读取代码
- **4.1.2. 模型管理**: 标注model_nodes表的script字段已废弃
- **4.1.5. 计算与结果**: 新增calculation_step_logs表
- **4.2. model_nodes表**: 标注script字段已废弃

### 2.3. API设计文档.md (V1.1)

#### 新增章节
- **8. 计算流程管理服务 API**
  - 8.1. 计算流程管理 (6个接口)
  - 8.2. 计算步骤管理 (8个接口)
  - 8.3. 数据迁移 (1个接口)

- **9. API变更说明 (V1.1)**
  - 9.1. 已弃用的API
  - 9.2. 修改的API
  - 9.3. 新增的API
  - 9.4. 兼容性说明

#### 新增API接口（共15个）

**计算流程管理 (6个)**
1. `GET /calculation-workflows` - 获取计算流程列表
2. `POST /calculation-workflows` - 创建计算流程
3. `GET /calculation-workflows/{id}` - 获取计算流程详情
4. `PUT /calculation-workflows/{id}` - 更新计算流程
5. `DELETE /calculation-workflows/{id}` - 删除计算流程
6. `POST /calculation-workflows/{id}/copy` - 复制计算流程

**计算步骤管理 (8个)**
7. `GET /calculation-steps` - 获取计算步骤列表
8. `POST /calculation-steps` - 创建计算步骤
9. `GET /calculation-steps/{id}` - 获取计算步骤详情
10. `PUT /calculation-steps/{id}` - 更新计算步骤
11. `DELETE /calculation-steps/{id}` - 删除计算步骤
12. `POST /calculation-steps/{id}/move-up` - 上移计算步骤
13. `POST /calculation-steps/{id}/move-down` - 下移计算步骤
14. `POST /calculation-steps/{id}/test` - 测试计算步骤代码

**数据迁移 (1个)**
15. `POST /calculation-workflows/migrate` - 执行数据迁移

#### 修改的API
- `POST /calculation/tasks` - 新增workflow_id参数（可选）

#### 已弃用的API
- `POST /model-nodes/{id}/test-code` - 已弃用，使用计算步骤测试接口替代

---

## 3. 数据库变更

### 3.1. 新增表

#### calculation_workflows (计算流程表)
```sql
CREATE TABLE calculation_workflows (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL REFERENCES model_versions(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### calculation_steps (计算步骤表)
```sql
CREATE TABLE calculation_steps (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES calculation_workflows(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    code_type VARCHAR(20) NOT NULL CHECK (code_type IN ('python', 'sql')),
    code_content TEXT NOT NULL,
    sort_order NUMERIC(10, 2) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### calculation_step_logs (计算步骤执行日志表)
```sql
CREATE TABLE calculation_step_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(100) NOT NULL,
    step_id INTEGER NOT NULL REFERENCES calculation_steps(id),
    department_id INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_ms INTEGER,
    result_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2. 修改表

#### calculation_tasks (计算任务表)
```sql
-- 新增字段
ALTER TABLE calculation_tasks ADD COLUMN workflow_id INTEGER REFERENCES calculation_workflows(id);
```

#### model_nodes (模型节点表)
```sql
-- script字段保留但标记为已废弃
-- 不需要修改表结构，仅在应用层标记为deprecated
```

---

## 4. 前端界面变更

### 4.1. 新增页面

1. **计算流程管理页**
   - 路径: `/calculation-workflows`
   - 功能: 列表展示、创建、编辑、删除、复制计算流程

2. **计算步骤管理页**
   - 路径: `/calculation-workflows/{id}/steps`
   - 功能: 列表展示、创建、编辑、删除、排序计算步骤

3. **计算步骤编辑对话框**
   - 功能: 编辑步骤信息、代码编辑器、代码测试

### 4.2. 修改页面

1. **模型结构编辑页**
   - 移除: 代码编辑器
   - 移除: 代码测试按钮
   - 新增: 跳转到计算流程管理的链接

2. **计算任务创建页**
   - 新增: 计算流程选择下拉框
   - 逻辑: 根据选择的模型版本动态加载计算流程列表

3. **计算任务详情页**
   - 新增: 步骤执行日志查看功能
   - 显示: 每个步骤的执行状态、耗时、结果

### 4.3. 菜单调整

```
评估模型管理
├── 模型版本管理
├── 模型结构编辑
├── 计算流程管理 (新增)
└── 维度目录管理

计算任务管理
├── 创建计算任务
└── 任务列表
```

---

## 5. 数据迁移方案

### 5.1. 迁移工具

系统提供数据迁移工具，位于：
- API接口: `POST /calculation-workflows/migrate`
- 命令行工具: `python -m app.scripts.migrate_workflows`

### 5.2. 迁移流程

1. **预览模式**
   ```bash
   # 预览将要迁移的数据
   curl -X POST http://localhost:8000/api/v1/calculation-workflows/migrate \
     -H "Content-Type: application/json" \
     -d '{"preview_only": true}'
   ```

2. **执行迁移**
   ```bash
   # 执行实际迁移
   curl -X POST http://localhost:8000/api/v1/calculation-workflows/migrate \
     -H "Content-Type: application/json" \
     -d '{"preview_only": false}'
   ```

3. **验证结果**
   - 检查迁移报告
   - 在测试环境执行计算任务
   - 对比新旧计算结果

### 5.3. 迁移策略

- **流程创建**: 为每个模型版本创建一个默认计算流程
- **步骤创建**: 为每个包含代码的节点创建一个计算步骤
- **顺序保持**: 步骤的执行顺序与节点的层级顺序一致
- **数据保留**: 原节点的script字段保留，不删除

### 5.4. 回滚方案

如果迁移失败或结果不符合预期：
1. 删除新创建的计算流程和步骤
2. 启用兼容模式，继续使用节点中的代码
3. 修复问题后重新执行迁移

---

## 6. 向后兼容性

### 6.1. 兼容模式

**启用条件**:
- 系统配置中 `enable_compatibility_mode = true`
- 计算任务未指定 `workflow_id`

**兼容行为**:
- 系统尝试从模型节点的script字段读取代码
- 按原有逻辑执行计算
- 记录兼容模式使用日志

**禁用时机**:
- 完成数据迁移并验证后
- 所有计算任务都指定了workflow_id
- 过渡期结束（2026-04-27）

### 6.2. API兼容性

**已弃用但仍可用**:
- `POST /model-nodes/{id}/test-code` - 继续可用，但返回警告
- `model_nodes.script` 字段 - 继续返回，但标记为deprecated

**新旧混用**:
- 过渡期内，新旧API可以混用
- 建议尽快迁移到新API
- 新功能仅在新API中提供

### 6.3. 数据兼容性

**数据保留**:
- 模型节点的script字段不会被删除
- 可以随时回滚到旧版本
- 迁移后的数据可以导出备份

---

## 7. 升级步骤

### 7.1. 准备阶段

1. **备份数据库**
   ```bash
   pg_dump -h localhost -U postgres hospital_value > backup_$(date +%Y%m%d).sql
   ```

2. **备份代码**
   ```bash
   git tag v1.3-before-workflow-migration
   git push origin v1.3-before-workflow-migration
   ```

3. **准备测试环境**
   - 复制生产数据到测试环境
   - 确保测试环境与生产环境一致

### 7.2. 升级阶段

1. **部署新版本代码**
   ```bash
   git pull origin main
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

2. **执行数据库迁移**
   ```bash
   # 创建新表
   docker-compose exec backend alembic upgrade head
   ```

3. **执行数据迁移**
   ```bash
   # 预览迁移
   docker-compose exec backend python -m app.scripts.migrate_workflows --preview
   
   # 执行迁移
   docker-compose exec backend python -m app.scripts.migrate_workflows
   ```

4. **验证迁移结果**
   - 检查迁移报告
   - 在测试环境创建计算任务
   - 对比计算结果

### 7.3. 验证阶段

1. **功能测试**
   - 创建计算流程
   - 创建计算步骤
   - 测试步骤代码
   - 执行计算任务
   - 查看步骤日志

2. **性能测试**
   - 执行大规模计算任务
   - 监控系统资源使用
   - 对比新旧版本性能

3. **回归测试**
   - 测试所有现有功能
   - 确保没有破坏性变更

### 7.4. 生产部署

1. **选择低峰时段**
   - 建议在凌晨或周末部署
   - 提前通知用户系统维护

2. **执行部署**
   - 按照升级阶段的步骤执行
   - 实时监控系统状态

3. **监控观察**
   - 监控系统日志
   - 监控性能指标
   - 收集用户反馈

4. **禁用兼容模式**（可选）
   - 确认所有功能正常后
   - 修改系统配置禁用兼容模式
   - 继续监控一段时间

---

## 8. 风险评估

### 8.1. 高风险项

1. **数据迁移失败**
   - 风险: 代码迁移不完整或错误
   - 缓解: 提供预览功能，支持回滚
   - 应对: 保留原数据，启用兼容模式

2. **计算结果不一致**
   - 风险: 新旧计算结果不一致
   - 缓解: 在测试环境充分验证
   - 应对: 对比分析差异，修复问题

3. **性能下降**
   - 风险: 新架构性能不如旧架构
   - 缓解: 进行性能测试和优化
   - 应对: 回滚到旧版本，优化后再升级

### 8.2. 中风险项

1. **用户学习成本**
   - 风险: 用户不熟悉新界面
   - 缓解: 提供用户手册和培训
   - 应对: 提供在线帮助和技术支持

2. **API兼容性问题**
   - 风险: 第三方集成受影响
   - 缓解: 保持API向后兼容
   - 应对: 提供迁移指南和技术支持

### 8.3. 低风险项

1. **前端界面调整**
   - 风险: 界面变化导致用户不适应
   - 缓解: 保持界面风格一致
   - 应对: 收集反馈，持续优化

---

## 9. 后续工作

### 9.1. 短期（1-3个月）

1. **监控和优化**
   - 收集用户反馈
   - 修复发现的问题
   - 优化性能

2. **文档完善**
   - 编写用户手册
   - 录制操作视频
   - 更新API文档

3. **培训支持**
   - 组织用户培训
   - 提供技术支持
   - 建立FAQ

### 9.2. 中期（3-6个月）

1. **功能增强**
   - 步骤级别的并行执行
   - 步骤结果缓存
   - 可视化流程编排

2. **代码模板库**
   - 提供常用代码模板
   - 支持代码片段复用
   - 支持团队代码共享

3. **禁用兼容模式**
   - 确认所有用户已迁移
   - 禁用兼容模式
   - 移除已弃用的API

### 9.3. 长期（6-12个月）

1. **AI辅助编码**
   - AI代码补全
   - 代码优化建议
   - 代码错误检测

2. **高级流程控制**
   - 条件分支
   - 循环执行
   - 步骤间数据传递

3. **性能优化**
   - 分布式计算
   - 增量计算
   - 智能缓存

---

## 10. 总结

本次架构调整是系统的一次重大升级，主要目的是提高系统的灵活性、可维护性和可扩展性。通过将代码逻辑从模型结构中分离，我们实现了：

1. **更清晰的职责划分**: 模型专注于业务价值的组织，计算流程专注于计算逻辑
2. **更灵活的管理**: 可以独立管理计算流程和步骤，不影响模型结构
3. **更好的可追溯性**: 步骤级别的执行日志，便于问题定位和性能分析
4. **更强的扩展性**: 为未来的功能增强（如并行执行、可视化编排）奠定基础

同时，我们也充分考虑了向后兼容性，提供了兼容模式和数据迁移工具，确保平滑过渡。

**下一步行动**:
1. 请您审阅本文档和修改后的需求、设计、API文档
2. 确认变更方案是否符合预期
3. 如有疑问或需要调整，请及时反馈
4. 确认后，我们将进入编码阶段
