# 测试结果数据插入指南

用于快速生成测试数据，验证报表功能。

---

## 📋 准备工作

### 1. 获取任务ID

有两种方式获取任务ID：

**方式一：创建一个新任务**
1. 进入"计算任务管理"页面
2. 创建一个新的计算任务
3. 复制任务ID（UUID格式，如：`abc123-def456-...`）

**方式二：查询现有任务**
```sql
SELECT task_id, period, status, created_at 
FROM calculation_tasks 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## 🚀 使用方法

### 方法一：使用 Python 脚本（推荐）

**优点**：自动处理、更灵活、有进度显示

```bash
# 进入 backend 目录
cd backend

# 基本用法
python insert_test_results.py YOUR_TASK_ID

# 指定计算周期
python insert_test_results.py YOUR_TASK_ID --period 2025-11

# 限制科室数量（默认20个）
python insert_test_results.py YOUR_TASK_ID --limit 10

# 完整示例
python insert_test_results.py abc123-def456-ghi789 --period 2025-10 --limit 15
```

**参数说明：**
- `task_id`：必填，计算任务ID
- `--period`：可选，计算周期（默认：2025-10）
- `--limit`：可选，科室数量限制（默认：20）

**输出示例：**
```
开始插入测试数据...
任务ID: abc123-def456-ghi789
计算周期: 2025-10
科室数量限制: 20
------------------------------------------------------------
找到 20 个科室
------------------------------------------------------------
[1/20] 处理科室: NK - 内科
[2/20] 处理科室: WK - 外科
...
[20/20] 处理科室: FCK - 妇产科
------------------------------------------------------------
✅ 测试数据插入完成！
------------------------------------------------------------
插入结果记录数: 160
插入汇总记录数: 20
平均每科室记录数: 8.0
```

---

### 方法二：使用 SQL 脚本

**优点**：直接在数据库中执行

1. 打开 `test_insert_results.sql` 文件
2. 将所有 `YOUR_TASK_ID` 替换为实际的任务ID
3. 在 PostgreSQL 中执行脚本

```sql
-- 使用 psql 命令行
psql -U your_username -d your_database -f test_insert_results.sql

-- 或者在 pgAdmin 中直接执行
```

**注意**：SQL 脚本需要手动替换任务ID，共有 3 处需要替换。

---

## 📊 生成的数据结构

### 每个科室生成的数据：

#### 1. 医生序列（3个维度）
- **门诊诊察**
  - 工作量：500-1500 人次
  - 权重：30-50 元/人次
  - 价值：2万-6万 元
  
- **住院诊察**
  - 工作量：200-600 人次
  - 权重：80-120 元/人次
  - 价值：1.5万-5万 元
  
- **手术**
  - 工作量：50-200 台
  - 权重：200-500 元/台
  - 价值：1.5万-5.5万 元

#### 2. 护理序列（2个维度）
- **床日护理**
  - 工作量：800-2000 床日
  - 权重：25-40 元/床日
  - 价值：2万-6万 元
  
- **专科护理**
  - 工作量：100-400 人次
  - 权重：50-100 元/人次
  - 价值：1万-4万 元

#### 3. 医技序列（2个维度）
- **放射检查**
  - 工作量：200-600 人次
  - 权重：40-70 元/人次
  - 价值：1万-3.5万 元
  
- **检验**
  - 工作量：300-800 人次
  - 权重：20-40 元/人次
  - 价值：0.8万-2.8万 元

### 数据特点：
- ✅ 每个科室有随机因子（0.5-1.5），模拟不同科室的规模差异
- ✅ 数值在合理范围内随机生成
- ✅ 自动计算汇总数据和占比
- ✅ 包含序列和维度两级数据

---

## 🔍 验证数据

### 1. 查看插入的数据统计

```sql
SELECT 
    task_id,
    COUNT(DISTINCT department_id) as department_count,
    COUNT(*) FILTER (WHERE node_type = 'sequence') as sequence_count,
    COUNT(*) FILTER (WHERE node_type = 'dimension') as dimension_count,
    COUNT(*) as total_records,
    SUM(value) as total_value
FROM calculation_results
WHERE task_id = 'YOUR_TASK_ID';
```

### 2. 查看汇总数据（前10名）

```sql
SELECT 
    d.his_name as department_name,
    cs.doctor_value,
    ROUND(cs.doctor_ratio, 2) as doctor_ratio,
    cs.nurse_value,
    ROUND(cs.nurse_ratio, 2) as nurse_ratio,
    cs.tech_value,
    ROUND(cs.tech_ratio, 2) as tech_ratio,
    cs.total_value
FROM calculation_summaries cs
JOIN departments d ON d.id = cs.department_id
WHERE cs.task_id = 'YOUR_TASK_ID'
ORDER BY cs.total_value DESC
LIMIT 10;
```

### 3. 查看某个科室的详细数据

```sql
SELECT 
    node_name,
    node_type,
    ROUND(workload, 2) as workload,
    ROUND(weight, 2) as weight,
    ROUND(value, 2) as value,
    ROUND(ratio, 2) as ratio
FROM calculation_results
WHERE task_id = 'YOUR_TASK_ID'
  AND department_id = (
      SELECT id FROM departments 
      WHERE is_active = TRUE 
      ORDER BY sort_order 
      LIMIT 1
  )
ORDER BY 
    CASE node_type 
        WHEN 'sequence' THEN 1 
        WHEN 'dimension' THEN 2 
        ELSE 3 
    END,
    node_id;
```

---

## 🎯 测试报表功能

数据插入完成后，可以测试以下功能：

### 1. 汇总表查询
- 进入"结果查询"页面
- 选择对应的计算周期
- 查看科室汇总列表
- 验证排序、筛选功能

### 2. 详细数据查询
- 点击某个科室的"查看详情"
- 查看序列和维度的详细数据
- 验证数据展示是否正确

### 3. 数据导出
- 测试导出汇总表为 Excel
- 测试导出详细数据为 Excel
- 验证导出的数据格式

### 4. 数据可视化（如果有）
- 查看科室价值对比图表
- 查看序列占比饼图
- 验证图表数据准确性

---

## 🧹 清理测试数据

如果需要清理测试数据：

```sql
-- 删除指定任务的结果数据
DELETE FROM calculation_results WHERE task_id = 'YOUR_TASK_ID';
DELETE FROM calculation_summaries WHERE task_id = 'YOUR_TASK_ID';

-- 或者删除整个任务（级联删除所有相关数据）
DELETE FROM calculation_tasks WHERE task_id = 'YOUR_TASK_ID';
```

---

## ⚠️ 注意事项

1. **任务ID必须存在**
   - 确保任务ID在 `calculation_tasks` 表中存在
   - 任务状态可以是任意状态

2. **科室数据**
   - 确保数据库中有启用的科室（`is_active = TRUE`）
   - 至少需要1个科室才能插入数据

3. **节点ID**
   - 脚本使用虚拟的节点ID（1, 2, 3, 11, 12...）
   - 如果数据库中有实际的模型节点，会自动使用实际ID
   - 不影响报表功能测试

4. **数据量**
   - 默认插入20个科室的数据
   - 每个科室8条记录（3个序列 + 7个维度 - 2个重复的序列）
   - 总共约 160 条结果记录 + 20 条汇总记录

5. **性能**
   - Python 脚本执行时间：约 2-5 秒（20个科室）
   - SQL 脚本执行时间：约 1-3 秒（20个科室）

---

## 🐛 常见问题

### Q1: 提示"没有找到启用的科室"

**解决方法：**
```sql
-- 检查科室数据
SELECT COUNT(*) FROM departments WHERE is_active = TRUE;

-- 如果没有，启用一些科室
UPDATE departments SET is_active = TRUE WHERE id <= 20;
```

### Q2: Python 脚本报错"ModuleNotFoundError"

**解决方法：**
```bash
# 确保在 backend 目录下执行
cd backend

# 确保虚拟环境已激活
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### Q3: 数据插入成功但前端看不到

**检查步骤：**
1. 确认任务ID正确
2. 确认任务的 `period` 字段与查询条件匹配
3. 刷新前端页面
4. 检查浏览器控制台是否有错误

### Q4: 想要更多或更少的科室数据

**Python 脚本：**
```bash
# 插入10个科室
python insert_test_results.py YOUR_TASK_ID --limit 10

# 插入50个科室
python insert_test_results.py YOUR_TASK_ID --limit 50
```

**SQL 脚本：**
修改 `LIMIT 20` 为其他数值

---

## 📚 相关文档

- [报表功能实现文档](REPORT_FEATURE_IMPLEMENTATION.md)
- [报表功能快速开始](REPORT_QUICKSTART.md)
- [SQL 参数使用指南](SQL_PARAMETERS_GUIDE.md)
