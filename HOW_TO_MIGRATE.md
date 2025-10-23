# 如何执行数据库迁移

> 解决 "relation model_versions does not exist" 错误

---

## 🎯 最简单的方法

### 步骤1: 打开Anaconda Prompt

双击项目根目录的 **`open-anaconda-prompt.bat`**

### 步骤2: 进入backend目录

```bash
cd backend
```

### 步骤3: 执行迁移

```bash
alembic upgrade head
```

### 步骤4: 看到成功提示

```
INFO  [alembic.runtime.migration] Running upgrade f0384ea4c792 -> g1h2i3j4k5l6
```

### 步骤5: 重启后端

在后端服务窗口按 `Ctrl+C`，然后重新运行：
```bash
.\scripts\dev-start-backend.ps1
```

### 步骤6: 刷新浏览器

问题解决！✅

---

## 📸 截图说明

### 1. 打开Anaconda Prompt
```
双击这个文件 → open-anaconda-prompt.bat
```

### 2. 输入命令
```
(hospital_value) C:\project\first-calc-toolkit> cd backend
(hospital_value) C:\project\first-calc-toolkit\backend> alembic upgrade head
```

### 3. 看到成功信息
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade f0384ea4c792 -> g1h2i3j4k5l6, Add model_versions and model_nodes tables
```

---

## ❓ 常见问题

### Q: 提示 "alembic: command not found"

**A**: 环境没有激活，运行：
```bash
conda activate hospital_value
```

### Q: 提示 "Could not find conda environment: hospital_value"

**A**: 环境还没创建，运行：
```bash
.\scripts\setup-conda-env.ps1
```

### Q: 提示 "No module named 'alembic'"

**A**: 安装alembic：
```bash
pip install alembic
```

### Q: 迁移执行失败

**A**: 检查：
1. PostgreSQL是否运行？
2. 数据库连接配置是否正确？（backend/.env）
3. 查看错误信息

---

## 🔍 验证迁移

### 检查迁移状态

```bash
cd backend
alembic current
```

应该显示：
```
g1h2i3j4k5l6 (head)
```

### 检查数据库表

使用数据库工具连接PostgreSQL，执行：
```sql
SELECT * FROM model_versions;
SELECT * FROM model_nodes;
```

应该能看到空表（不报错）

---

## 🎉 完成

迁移成功后：
1. 重启后端服务
2. 刷新浏览器
3. 点击"评估模型管理"
4. 应该能正常使用了！

---

**预计时间**: 2分钟  
**难度**: ⭐☆☆☆☆
