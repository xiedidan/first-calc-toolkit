# 成本基准管理功能 - 部署清单

## 概述

本文档提供成本基准管理功能的完整部署清单，确保功能在生产环境中正确部署和运行。

**功能版本**: v1.0.0  
**部署日期**: ___________  
**部署人员**: ___________

---

## 部署前检查

### 1. 环境要求

#### 后端环境

- [ ] Python 3.12+
- [ ] PostgreSQL 12+
- [ ] Redis（用于Celery，如果使用）
- [ ] 所需Python包已安装（见requirements.txt）

#### 前端环境

- [ ] Node.js 16+
- [ ] npm 或 yarn
- [ ] 所需npm包已安装（见package.json）

#### 系统资源

- [ ] 数据库磁盘空间充足（建议预留至少1GB）
- [ ] 应用服务器内存充足（建议至少2GB可用内存）
- [ ] 网络连接正常

### 2. 依赖检查

#### 数据库表依赖

- [ ] `hospitals` 表存在且有数据
- [ ] `model_versions` 表存在且有数据
- [ ] `departments` 表存在且有数据（用于前端下拉选项）
- [ ] `model_nodes` 表存在且有数据（用于前端下拉选项）

#### 后端模块依赖

- [ ] `app.models.hospital` 模块正常
- [ ] `app.models.model_version` 模块正常
- [ ] `app.utils.hospital_filter` 模块正常
- [ ] `app.api.deps` 模块正常

#### 前端模块依赖

- [ ] Element Plus 已安装
- [ ] Axios 已配置
- [ ] 路由系统正常工作
- [ ] 认证系统正常工作

---

## 数据库迁移

### 1. 备份数据库

**重要**: 在执行任何数据库迁移前，必须先备份数据库！

```bash
# 备份数据库
pg_dump -h localhost -U admin -d hospital_value -F c -f backup_before_cost_benchmark_$(date +%Y%m%d_%H%M%S).dump

# 或使用SQL格式（推荐，兼容性更好）
pg_dump -h localhost -U admin -d hospital_value -f backup_before_cost_benchmark_$(date +%Y%m%d_%H%M%S).sql
```

- [ ] 数据库备份已完成
- [ ] 备份文件已验证（可以正常打开/读取）
- [ ] 备份文件已保存到安全位置

### 2. 执行迁移脚本

#### 检查迁移状态

```bash
cd backend
python -m alembic current
```

- [ ] 当前迁移版本已确认

#### 执行迁移

```bash
cd backend
python -m alembic upgrade head
```

- [ ] 迁移执行成功，无错误
- [ ] 迁移日志已保存

#### 验证迁移结果

```bash
# 连接数据库
psql -h localhost -U admin -d hospital_value

# 检查表是否创建
\d cost_benchmarks

# 检查表结构
\d+ cost_benchmarks

# 检查索引
\di cost_benchmarks*

# 检查约束
\d cost_benchmarks
```

预期结果：

- [ ] `cost_benchmarks` 表已创建
- [ ] 所有字段类型正确
- [ ] 索引已创建：
  - `cost_benchmarks_pkey` (主键)
  - `ix_cost_benchmarks_hospital_id`
  - `ix_cost_benchmarks_department_code`
  - `ix_cost_benchmarks_version_id`
  - `ix_cost_benchmarks_dimension_code`
- [ ] 唯一约束已创建：`uq_cost_benchmark_dept_version_dimension`
- [ ] 外键约束已创建：
  - `cost_benchmarks_hospital_id_fkey`
  - `cost_benchmarks_version_id_fkey`

### 3. 回滚计划（如果需要）

如果迁移失败或需要回滚：

```bash
# 查看迁移历史
python -m alembic history

# 回滚到上一个版本
python -m alembic downgrade -1

# 或回滚到特定版本
python -m alembic downgrade <revision_id>

# 恢复数据库备份
psql -h localhost -U admin -d hospital_value < backup_before_cost_benchmark_YYYYMMDD_HHMMSS.sql
```

- [ ] 回滚脚本已准备
- [ ] 回滚流程已测试（在测试环境）

---

## 后端部署

### 1. 代码部署

#### 文件清单

确认以下文件已部署到生产环境：

**模型文件**
- [ ] `backend/app/models/cost_benchmark.py`
- [ ] `backend/app/models/__init__.py` (已更新导入)

**Schema文件**
- [ ] `backend/app/schemas/cost_benchmark.py`

**API文件**
- [ ] `backend/app/api/cost_benchmarks.py`

**迁移文件**
- [ ] `backend/alembic/versions/20251127_add_cost_benchmarks.py`

**主应用文件**
- [ ] `backend/app/main.py` (已注册路由)

#### 代码验证

```bash
# 检查Python语法
cd backend
python -m py_compile app/models/cost_benchmark.py
python -m py_compile app/schemas/cost_benchmark.py
python -m py_compile app/api/cost_benchmarks.py

# 检查导入
python -c "from app.models.cost_benchmark import CostBenchmark; print('Model OK')"
python -c "from app.schemas.cost_benchmark import CostBenchmark; print('Schema OK')"
python -c "from app.api.cost_benchmarks import router; print('API OK')"
```

- [ ] 所有文件语法正确
- [ ] 所有导入正常

### 2. 配置更新

#### 路由注册

确认 `backend/app/main.py` 中已注册路由：

```python
from app.api import cost_benchmarks

app.include_router(
    cost_benchmarks.router,
    prefix="/api/v1/cost-benchmarks",
    tags=["cost-benchmarks"]
)
```

- [ ] 路由已注册
- [ ] 路由前缀正确
- [ ] 路由标签正确

#### 模型导入

确认 `backend/app/models/__init__.py` 中已导入模型：

```python
from app.models.cost_benchmark import CostBenchmark
```

- [ ] 模型已导入
- [ ] 导入顺序正确（在依赖模型之后）

### 3. 服务重启

```bash
# 停止服务
sudo systemctl stop hospital-backend

# 或使用进程管理器
pm2 stop hospital-backend

# 启动服务
sudo systemctl start hospital-backend

# 或
pm2 start hospital-backend

# 检查服务状态
sudo systemctl status hospital-backend

# 或
pm2 status
```

- [ ] 服务已重启
- [ ] 服务状态正常
- [ ] 无启动错误

### 4. API测试

#### 健康检查

```bash
# 检查API是否可访问
curl http://localhost:8000/api/v1/cost-benchmarks

# 应返回401（未认证）或403（未激活医疗机构）
```

- [ ] API端点可访问
- [ ] 返回预期的错误码

#### 功能测试

使用测试脚本或Postman测试以下功能：

```bash
# 运行API测试
cd backend
python test_cost_benchmark_api.py
```

- [ ] 列表查询正常
- [ ] 创建功能正常
- [ ] 更新功能正常
- [ ] 删除功能正常
- [ ] 导出功能正常
- [ ] 多租户隔离正常

---

## 前端部署

### 1. 代码部署

#### 文件清单

确认以下文件已部署到生产环境：

**API文件**
- [ ] `frontend/src/api/cost-benchmarks.ts`

**视图文件**
- [ ] `frontend/src/views/CostBenchmarks.vue`

**路由文件**
- [ ] `frontend/src/router/index.ts` (已添加路由)

**布局文件**
- [ ] `frontend/src/views/Layout.vue` (已添加菜单项)

#### 代码验证

```bash
# 检查TypeScript语法
cd frontend
npm run type-check

# 或
yarn type-check
```

- [ ] TypeScript编译无错误
- [ ] 无类型错误

### 2. 构建和部署

#### 开发环境测试

```bash
cd frontend
npm run dev

# 或
yarn dev
```

- [ ] 开发服务器启动正常
- [ ] 页面可以访问
- [ ] 无控制台错误

#### 生产构建

```bash
cd frontend
npm run build

# 或
yarn build
```

- [ ] 构建成功，无错误
- [ ] 构建产物在 `dist` 目录

#### 部署到Web服务器

```bash
# 复制构建产物到Web服务器
cp -r dist/* /var/www/html/

# 或使用rsync
rsync -av dist/ /var/www/html/
```

- [ ] 文件已复制到Web服务器
- [ ] 文件权限正确

### 3. 路由配置

确认 `frontend/src/router/index.ts` 中已添加路由：

```typescript
{
  path: '/cost-benchmarks',
  name: 'CostBenchmarks',
  component: () => import('@/views/CostBenchmarks.vue'),
  meta: { title: '成本基准管理', requiresAuth: true }
}
```

- [ ] 路由已添加
- [ ] 路由路径正确
- [ ] 组件导入正确
- [ ] Meta信息正确

### 4. 菜单配置

确认 `frontend/src/views/Layout.vue` 中已添加菜单项：

```vue
<el-menu-item index="/cost-benchmarks">
  <el-icon><Money /></el-icon>
  <span>成本基准管理</span>
</el-menu-item>
```

- [ ] 菜单项已添加
- [ ] 菜单图标正确
- [ ] 菜单文本正确
- [ ] 菜单位置正确（在维度目录管理之后）

### 5. 前端测试

#### 功能测试

- [ ] 页面可以正常访问
- [ ] 列表数据正常加载
- [ ] 筛选功能正常
- [ ] 搜索功能正常
- [ ] 添加功能正常
- [ ] 编辑功能正常
- [ ] 删除功能正常
- [ ] 导出功能正常
- [ ] 分页功能正常

#### UI测试

- [ ] 页面布局正确
- [ ] 样式与其他页面一致
- [ ] 响应式布局正常
- [ ] 加载状态显示正常
- [ ] 错误提示显示正常
- [ ] 成功提示显示正常

#### 浏览器兼容性测试

- [ ] Chrome浏览器正常
- [ ] Firefox浏览器正常
- [ ] Edge浏览器正常
- [ ] Safari浏览器正常（如果适用）

---

## 数据初始化（可选）

### 1. 准备初始数据

如果需要预先导入一些成本基准数据：

```python
# 创建初始化脚本 init_cost_benchmarks.py
from app.database import SessionLocal
from app.models.cost_benchmark import CostBenchmark
from decimal import Decimal

db = SessionLocal()

# 示例数据
benchmarks = [
    {
        "hospital_id": 1,
        "department_code": "001",
        "department_name": "内科",
        "version_id": 1,
        "version_name": "2024年度模型",
        "dimension_code": "D001",
        "dimension_name": "门诊工作量",
        "benchmark_value": Decimal("50000.00")
    },
    # 添加更多数据...
]

for data in benchmarks:
    benchmark = CostBenchmark(**data)
    db.add(benchmark)

db.commit()
db.close()
```

- [ ] 初始化脚本已准备
- [ ] 初始数据已验证
- [ ] 初始化脚本已执行

### 2. 验证初始数据

```sql
-- 检查数据是否导入成功
SELECT COUNT(*) FROM cost_benchmarks;

-- 检查数据分布
SELECT hospital_id, COUNT(*) 
FROM cost_benchmarks 
GROUP BY hospital_id;
```

- [ ] 数据导入成功
- [ ] 数据数量正确
- [ ] 数据分布合理

---

## 监控和日志

### 1. 日志配置

确认日志配置正确：

```python
# 在 backend/app/main.py 或日志配置文件中
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

- [ ] 日志级别正确（生产环境建议INFO或WARNING）
- [ ] 日志格式正确
- [ ] 日志文件路径正确

### 2. 监控指标

建议监控以下指标：

- [ ] API响应时间
- [ ] API错误率
- [ ] 数据库查询性能
- [ ] 成本基准记录数量
- [ ] 用户操作频率

### 3. 告警配置

建议配置以下告警：

- [ ] API错误率超过阈值
- [ ] 数据库连接失败
- [ ] 磁盘空间不足
- [ ] 内存使用率过高

---

## 安全检查

### 1. 认证和授权

- [ ] 所有API端点需要认证
- [ ] JWT Token验证正常
- [ ] 多租户隔离正常工作
- [ ] 跨租户访问被正确阻止

### 2. 数据验证

- [ ] 输入数据验证正常
- [ ] SQL注入防护正常
- [ ] XSS防护正常
- [ ] CSRF防护正常（如果适用）

### 3. 权限控制

- [ ] 用户只能访问自己医疗机构的数据
- [ ] 管理员权限正确配置
- [ ] 普通用户权限正确限制

---

## 性能测试

### 1. 负载测试

使用工具（如Apache Bench、JMeter）进行负载测试：

```bash
# 使用Apache Bench测试列表接口
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" -H "X-Hospital-ID: 1" \
   http://localhost:8000/api/v1/cost-benchmarks
```

- [ ] 并发10用户，1000请求测试通过
- [ ] 平均响应时间 < 500ms
- [ ] 错误率 < 1%

### 2. 压力测试

- [ ] 大数据量查询测试（1000+记录）
- [ ] 并发创建测试
- [ ] 并发更新测试
- [ ] 导出大数据量测试

### 3. 性能优化

如果性能不达标，考虑以下优化：

- [ ] 添加数据库索引
- [ ] 启用查询缓存
- [ ] 优化SQL查询
- [ ] 增加服务器资源

---

## 文档和培训

### 1. 文档准备

- [ ] API文档已准备（COST_BENCHMARK_API_DOCUMENTATION.md）
- [ ] 用户使用指南已准备（COST_BENCHMARK_USER_GUIDE.md）
- [ ] 部署文档已准备（本文档）
- [ ] 故障排除文档已准备

### 2. 用户培训

- [ ] 培训材料已准备
- [ ] 培训计划已制定
- [ ] 关键用户已培训
- [ ] 培训反馈已收集

### 3. 技术支持

- [ ] 技术支持联系方式已公布
- [ ] 问题反馈渠道已建立
- [ ] 常见问题FAQ已准备

---

## 上线检查

### 1. 最终验证

在正式上线前，进行最终验证：

- [ ] 所有功能正常工作
- [ ] 所有测试用例通过
- [ ] 性能满足要求
- [ ] 安全检查通过
- [ ] 文档完整

### 2. 上线准备

- [ ] 上线时间已确定
- [ ] 相关人员已通知
- [ ] 回滚计划已准备
- [ ] 应急联系人已确定

### 3. 上线执行

- [ ] 数据库迁移已执行
- [ ] 后端代码已部署
- [ ] 前端代码已部署
- [ ] 服务已重启
- [ ] 功能验证通过

### 4. 上线后监控

上线后持续监控以下指标（至少24小时）：

- [ ] API错误率
- [ ] 响应时间
- [ ] 用户反馈
- [ ] 系统资源使用率

---

## 故障排除

### 常见问题

#### 1. 数据库迁移失败

**症状**: 执行 `alembic upgrade head` 时报错

**可能原因**:
- 数据库连接失败
- 表已存在
- 权限不足

**解决方案**:
```bash
# 检查数据库连接
psql -h localhost -U admin -d hospital_value -c "SELECT 1"

# 检查表是否已存在
psql -h localhost -U admin -d hospital_value -c "\dt cost_benchmarks"

# 如果表已存在，标记迁移为已完成
python -m alembic stamp head
```

#### 2. API返回404

**症状**: 访问 `/api/v1/cost-benchmarks` 返回404

**可能原因**:
- 路由未注册
- 服务未重启
- URL路径错误

**解决方案**:
```bash
# 检查路由注册
grep -r "cost_benchmarks" backend/app/main.py

# 重启服务
sudo systemctl restart hospital-backend

# 检查API文档
curl http://localhost:8000/docs
```

#### 3. 前端页面空白

**症状**: 访问成本基准管理页面显示空白

**可能原因**:
- JavaScript错误
- 路由配置错误
- 组件导入失败

**解决方案**:
```bash
# 检查浏览器控制台错误
# F12 -> Console

# 检查路由配置
grep -r "cost-benchmarks" frontend/src/router/

# 重新构建前端
cd frontend
npm run build
```

#### 4. 多租户隔离失败

**症状**: 用户可以看到其他医疗机构的数据

**可能原因**:
- `X-Hospital-ID` 请求头未传递
- 后端过滤逻辑错误

**解决方案**:
```bash
# 检查请求头
# 在浏览器开发者工具中查看Network -> Headers

# 检查后端过滤逻辑
grep -r "apply_hospital_filter" backend/app/api/cost_benchmarks.py
```

---

## 回滚计划

如果部署后发现严重问题，需要回滚：

### 1. 回滚数据库

```bash
# 回滚迁移
cd backend
python -m alembic downgrade -1

# 或恢复备份
psql -h localhost -U admin -d hospital_value < backup_before_cost_benchmark_YYYYMMDD_HHMMSS.sql
```

### 2. 回滚后端代码

```bash
# 使用Git回滚
git revert <commit_hash>

# 或恢复备份
cp -r backup/backend/* backend/

# 重启服务
sudo systemctl restart hospital-backend
```

### 3. 回滚前端代码

```bash
# 使用Git回滚
git revert <commit_hash>

# 重新构建
cd frontend
npm run build

# 部署
cp -r dist/* /var/www/html/
```

### 4. 验证回滚

- [ ] 系统恢复到回滚前状态
- [ ] 原有功能正常工作
- [ ] 无新的错误

---

## 签字确认

### 部署团队

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 项目经理 | | | |
| 后端开发 | | | |
| 前端开发 | | | |
| 数据库管理员 | | | |
| 测试工程师 | | | |
| 运维工程师 | | | |

### 验收确认

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 产品负责人 | | | |
| 技术负责人 | | | |
| 质量负责人 | | | |

---

## 附录

### A. 相关文档

- API文档: `COST_BENCHMARK_API_DOCUMENTATION.md`
- 用户指南: `COST_BENCHMARK_USER_GUIDE.md`
- 设计文档: `.kiro/specs/cost-benchmark-management/design.md`
- 需求文档: `.kiro/specs/cost-benchmark-management/requirements.md`

### B. 测试脚本

- API测试: `test_cost_benchmark_api.py`
- 多租户测试: `test_cost_benchmark_multi_tenant.py`
- Schema测试: `test_cost_benchmark_schemas.py`

### C. 联系方式

- 技术支持: support@example.com
- 紧急联系: 400-xxx-xxxx

---

**文档版本**: v1.0.0  
**最后更新**: 2024-11-27
