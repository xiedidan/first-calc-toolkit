# 成本基准管理 - 快速部署指南

## 5分钟快速部署

本指南提供成本基准管理功能的快速部署步骤。详细信息请参考完整的部署清单。

---

## 前置条件

- [ ] 已备份数据库
- [ ] 已准备生产环境
- [ ] 已审查所有文档

---

## 部署步骤

### 1. 数据库迁移（2分钟）

```bash
# 备份数据库
pg_dump -h localhost -U admin -d hospital_value -f backup_$(date +%Y%m%d_%H%M%S).sql

# 执行迁移
cd backend
python -m alembic upgrade head

# 验证表已创建
psql -h localhost -U admin -d hospital_value -P pager=off -c "\d cost_benchmarks"
```

**预期结果**: 看到 `cost_benchmarks` 表结构

---

### 2. 后端部署（1分钟）

```bash
# 确认文件存在
ls backend/app/models/cost_benchmark.py
ls backend/app/schemas/cost_benchmark.py
ls backend/app/api/cost_benchmarks.py

# 重启后端服务
sudo systemctl restart hospital-backend

# 或使用 pm2
pm2 restart hospital-backend

# 验证服务启动
curl http://localhost:8000/api/v1/cost-benchmarks
```

**预期结果**: 返回 401 或 403（需要认证）

---

### 3. 前端部署（2分钟）

```bash
# 确认文件存在
ls frontend/src/api/cost-benchmarks.ts
ls frontend/src/views/CostBenchmarks.vue

# 构建前端
cd frontend
npm run build

# 部署到Web服务器
cp -r dist/* /var/www/html/

# 或使用 rsync
rsync -av dist/ /var/www/html/
```

**预期结果**: 文件已复制到Web服务器

---

### 4. 功能验证（1分钟）

1. **访问页面**
   - 登录系统
   - 在左侧菜单找到"成本基准管理"
   - 点击进入

2. **测试功能**
   - [ ] 页面正常加载
   - [ ] 可以查看列表
   - [ ] 可以添加记录
   - [ ] 可以编辑记录
   - [ ] 可以删除记录
   - [ ] 可以导出Excel

---

## 快速测试脚本

### 后端API测试

```bash
# 设置变量
TOKEN="your_jwt_token"
HOSPITAL_ID=1
BASE_URL="http://localhost:8000/api/v1"

# 测试列表接口
curl -H "Authorization: Bearer $TOKEN" \
     -H "X-Hospital-ID: $HOSPITAL_ID" \
     "$BASE_URL/cost-benchmarks"

# 测试创建接口
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "X-Hospital-ID: $HOSPITAL_ID" \
     -H "Content-Type: application/json" \
     -d '{
       "department_code": "001",
       "department_name": "内科",
       "version_id": 1,
       "version_name": "2024年度模型",
       "dimension_code": "D001",
       "dimension_name": "门诊工作量",
       "benchmark_value": 50000.00
     }' \
     "$BASE_URL/cost-benchmarks"
```

---

## 常见问题快速解决

### 问题1: 迁移失败

```bash
# 检查当前迁移状态
python -m alembic current

# 如果表已存在，标记为已完成
python -m alembic stamp head
```

### 问题2: API返回404

```bash
# 检查路由注册
grep -r "cost_benchmarks" backend/app/main.py

# 重启服务
sudo systemctl restart hospital-backend
```

### 问题3: 前端页面空白

```bash
# 检查浏览器控制台错误（F12）
# 检查路由配置
grep -r "cost-benchmarks" frontend/src/router/

# 重新构建
cd frontend
npm run build
```

---

## 回滚步骤（如果需要）

```bash
# 1. 回滚数据库
cd backend
python -m alembic downgrade -1

# 2. 恢复备份（如果需要）
psql -h localhost -U admin -d hospital_value < backup_YYYYMMDD_HHMMSS.sql

# 3. 重启服务
sudo systemctl restart hospital-backend
```

---

## 验证清单

部署完成后，快速验证以下项目：

- [ ] 数据库表已创建
- [ ] 后端服务正常启动
- [ ] API端点可访问
- [ ] 前端页面可访问
- [ ] 菜单项显示正常
- [ ] 可以添加数据
- [ ] 可以查询数据
- [ ] 可以导出数据
- [ ] 多租户隔离正常

---

## 完整文档

- **API文档**: `COST_BENCHMARK_API_DOCUMENTATION.md`
- **用户指南**: `COST_BENCHMARK_USER_GUIDE.md`
- **部署清单**: `COST_BENCHMARK_DEPLOYMENT_CHECKLIST.md`
- **部署总结**: `COST_BENCHMARK_DEPLOYMENT_SUMMARY.md`

---

## 技术支持

如遇问题，请联系：
- **邮箱**: support@example.com
- **电话**: 400-xxx-xxxx

---

**提示**: 这是快速部署指南，详细步骤和故障排除请参考完整的部署清单。
