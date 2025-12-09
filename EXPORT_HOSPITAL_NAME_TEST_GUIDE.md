# 导出文件名医院前缀测试指南

## 前提条件

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **启动前端服务**（如果需要通过UI测试）
   ```bash
   cd frontend
   npm run dev
   ```

## 快速验证方法

### 方法1：通过前端UI测试（推荐）

#### 1. 导向规则导出
1. 登录系统
2. 进入"导向规则管理"页面
3. 点击任意规则的"导出"下拉按钮
4. 选择"导出为Markdown"或"导出为PDF"
5. **检查下载的文件名**，应该是：`医院名称_规则名称_时间戳.md` 或 `.pdf`

#### 2. 成本基准导出
1. 进入"成本基准管理"页面
2. 点击"导出"按钮
3. **检查下载的文件名**，应该是：`医院名称_成本基准_时间戳.xlsx`

#### 3. 数据问题导出
1. 进入"数据问题管理"页面
2. 点击"导出"按钮
3. **检查下载的文件名**，应该是：`医院名称_数据问题记录_日期.xlsx`

#### 4. 报表导出
1. 进入"计算结果"页面
2. 点击"导出汇总表"按钮
3. **检查下载的文件名**，应该是：`医院名称_科室业务价值汇总_期间.xlsx`
4. 点击"导出明细表"按钮
5. **检查下载的文件名**，应该是：`医院名称_业务价值明细表_期间.zip`
6. 解压ZIP文件，**检查内部文件名**，应该是：`医院名称_科室名称_业务价值明细_期间.xlsx`

### 方法2：通过API测试

#### 准备工作
```bash
# 1. 登录获取token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 保存返回的access_token
TOKEN="your_token_here"
```

#### 测试各个导出端点

**1. 导向规则导出（Markdown）**
```bash
curl -X GET "http://localhost:8000/api/v1/orientation-rules/1/export?format=markdown" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```
查看响应头中的 `Content-Disposition`，应包含医院名称。

**2. 导向规则导出（PDF）**
```bash
curl -X GET "http://localhost:8000/api/v1/orientation-rules/1/export?format=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```

**3. 成本基准导出**
```bash
curl -X GET "http://localhost:8000/api/v1/cost-benchmarks/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```

**4. 数据问题导出**
```bash
curl -X GET "http://localhost:8000/api/v1/data-issues/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```

**5. 汇总表导出**
```bash
curl -X GET "http://localhost:8000/api/v1/calculation-tasks/results/export/summary?period=2025-11" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```

**6. 明细表导出**
```bash
curl -X GET "http://localhost:8000/api/v1/calculation-tasks/results/export/detail?task_id=your_task_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Hospital-ID: 1" \
  -I
```

### 方法3：使用测试脚本

```bash
# 确保后端服务已启动
python test_export_hospital_name.py
```

## 预期结果

所有导出的文件名都应该遵循以下格式：

```
{医院名称}_{原文件名}
```

### 示例

假设医院名称是"北京协和医院"：

- ✅ `北京协和医院_科室业务价值汇总_2025-11.xlsx`
- ✅ `北京协和医院_导向规则_20251201_143022.pdf`
- ✅ `北京协和医院_成本基准_20251201_143022.xlsx`
- ✅ `北京协和医院_数据问题记录_20251201.xlsx`
- ✅ `北京协和医院_业务价值明细表_2025-11.zip`
- ✅ `北京协和医院_内科_业务价值明细_2025-11.xlsx`（ZIP内）

### 错误示例

- ❌ `科室业务价值汇总_2025-11.xlsx`（缺少医院名称）
- ❌ `导向规则_20251201_143022.pdf`（缺少医院名称）

## 常见问题

### Q1: 文件名没有医院名称前缀？

**可能原因：**
1. 后端服务没有重启
2. 代码修改后没有生效
3. 医院数据不存在

**解决方法：**
```bash
# 1. 重启后端服务
cd backend
# 停止现有服务（Ctrl+C）
python -m uvicorn app.main:app --reload

# 2. 检查医院数据
python -c "
from app.database import SessionLocal
from app.models.hospital import Hospital
db = SessionLocal()
hospitals = db.query(Hospital).all()
for h in hospitals:
    print(f'ID: {h.id}, 名称: {h.name}')
db.close()
"
```

### Q2: 测试脚本连接失败？

**错误信息：** `ConnectionRefusedError: [WinError 10061]`

**解决方法：**
确保后端服务正在运行：
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Q3: 文件名中医院名称显示为"未知医院"？

**可能原因：**
1. hospital_id 为 None
2. 数据库中没有对应的医院记录

**解决方法：**
检查数据库中的医院数据，确保有有效的医院记录。

### Q4: 前端下载的文件名不对？

**可能原因：**
浏览器缓存了旧的响应

**解决方法：**
1. 清除浏览器缓存
2. 使用隐私模式/无痕模式测试
3. 硬刷新页面（Ctrl+F5）

## 验证清单

使用以下清单逐一验证：

- [ ] 后端服务已启动
- [ ] 前端服务已启动（如果通过UI测试）
- [ ] 已登录系统
- [ ] 导向规则导出（Markdown）- 文件名包含医院名称
- [ ] 导向规则导出（PDF）- 文件名包含医院名称
- [ ] 成本基准导出 - 文件名包含医院名称
- [ ] 数据问题导出 - 文件名包含医院名称
- [ ] 汇总表导出 - 文件名包含医院名称
- [ ] 明细表导出 - 文件名包含医院名称
- [ ] ZIP内文件 - 文件名包含医院名称

## 调试技巧

### 1. 查看响应头
使用浏览器开发者工具（F12）：
1. 打开"网络"标签
2. 执行导出操作
3. 找到导出请求
4. 查看响应头中的 `Content-Disposition`
5. 应该看到类似：`filename*=UTF-8''%E5%8C%97%E4%BA%AC%E5%8D%8F%E5%92%8C%E5%8C%BB%E9%99%A2_...`

### 2. 检查后端日志
查看后端控制台输出，确认：
1. 是否成功获取医院名称
2. 是否有错误信息
3. 生成的文件名是什么

### 3. 直接测试服务层
```python
from app.database import SessionLocal
from app.services.orientation_rule_service import OrientationRuleService

db = SessionLocal()
buffer, filename = OrientationRuleService.export_rule(db, rule_id=1, hospital_id=1)
print(f"生成的文件名: {filename}")
db.close()
```

## 总结

所有导出功能都已添加医院名称前缀。如果测试不通过：
1. 确保后端服务已重启
2. 清除浏览器缓存
3. 检查医院数据是否存在
4. 查看后端日志排查问题

如有问题，请提供：
- 具体哪个导出功能有问题
- 实际下载的文件名
- 后端日志输出
- 浏览器控制台的网络请求详情
