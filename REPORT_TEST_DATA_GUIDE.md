# 业务价值报表测试数据生成指南

## 功能概述

本指南介绍如何快速生成业务价值报表的测试数据，用于验证汇总表和明细表的展示功能。

## 前置条件

1. 数据库已完成迁移（运行过 `alembic upgrade head`）
2. 系统中已有以下基础数据：
   - 至少一个模型版本（建议设置为激活状态）
   - 模型版本中已创建完整的节点结构（序列和维度）
   - 至少创建了几个科室，并标记为"参与评估"

## 快速开始

### 方式一：使用批处理脚本（推荐）

#### 1. 生成填0的测试数据

```bash
generate-report-test-data.bat
```

这将为所有参与评估的科室生成测试数据，所有工作量和价值字段填0。

#### 2. 生成随机值的测试数据

```bash
generate-report-test-data.bat --random
```

这将生成随机的工作量和价值数据，更接近真实场景。

### 方式二：使用Python脚本

#### 1. 基本用法

```bash
cd backend
python generate_report_test_data.py
```

#### 2. 指定计算周期

```bash
python generate_report_test_data.py --period 2025-11
```

#### 3. 使用随机值

```bash
python generate_report_test_data.py --random
```

#### 4. 指定模型版本

```bash
python generate_report_test_data.py --model-version-id 1
```

#### 5. 组合参数

```bash
python generate_report_test_data.py --period 2025-11 --random --model-version-id 1
```

## 生成的数据

脚本会生成以下数据：

### 1. 计算任务（calculation_tasks）

- 任务ID: `test-{period}-{timestamp}`
- 状态: `completed`
- 进度: 100%
- 描述: "测试数据生成任务"

### 2. 计算结果明细（calculation_results）

为每个科室的每个节点生成一条记录，包含：

- 节点ID、名称、编码、类型
- 工作量（workload）
- 权重/单价（weight）
- 价值（value）
- 占比（ratio）

### 3. 计算结果汇总（calculation_summaries）

为每个科室生成一条汇总记录，包含：

- 医生价值和占比
- 护理价值和占比
- 医技价值和占比
- 科室总价值

## 查看生成的数据

### 1. 启动服务

```bash
# 终端1: 启动后端
cd backend
uvicorn app.main:app --reload

# 终端2: 启动前端
cd frontend
npm run dev
```

### 2. 访问报表页面

1. 打开浏览器访问 `http://localhost:3000`
2. 登录系统
3. 点击左侧菜单"评估结果"
4. 选择对应的计算周期（如：2025-10）
5. 查看汇总表和明细表

### 3. 查看汇总表

汇总表展示：

- 全院汇总行（第一行）
- 各科室的医生、护理、医技价值和占比
- 科室总价值

### 4. 查看明细表

点击某个科室的"查看明细"按钮，可以看到：

- 按序列分类的维度数据
- 每个维度的工作量、权重、价值和占比

## 数据验证

### 1. 检查数据库

```sql
-- 查看生成的任务
SELECT * FROM calculation_tasks 
WHERE task_id LIKE 'test-%' 
ORDER BY created_at DESC;

-- 查看计算结果数量
SELECT task_id, COUNT(*) as count
FROM calculation_results
WHERE task_id LIKE 'test-%'
GROUP BY task_id;

-- 查看汇总数据
SELECT cs.*, d.his_name
FROM calculation_summaries cs
JOIN departments d ON cs.department_id = d.id
WHERE cs.task_id LIKE 'test-%'
ORDER BY cs.total_value DESC;
```

### 2. 验证数据完整性

- 每个科室应该有 N 条计算结果（N = 模型节点数量）
- 每个科室应该有 1 条汇总记录
- 汇总数据的总价值 = 医生价值 + 护理价值 + 医技价值
- 三个序列的占比之和应该等于 100%

## 清理测试数据

如果需要清理生成的测试数据：

```sql
-- 删除测试任务（会级联删除相关数据）
DELETE FROM calculation_tasks WHERE task_id LIKE 'test-%';

-- 或者删除特定任务
DELETE FROM calculation_tasks WHERE task_id = 'test-2025-10-20251030123456';
```

## 常见问题

### Q1: 脚本报错"未找到模型版本"

**原因**: 系统中没有激活的模型版本

**解决方法**:
1. 在模型管理页面创建一个模型版本
2. 将其设置为激活状态
3. 或者使用 `--model-version-id` 参数指定版本ID

### Q2: 脚本报错"未找到参与评估的科室"

**原因**: 没有科室被标记为"参与评估"

**解决方法**:
1. 在科室管理页面至少创建几个科室
2. 勾选"参与评估"选项
3. 确保科室状态为"启用"

### Q3: 脚本报错"模型版本没有节点"

**原因**: 模型版本中没有创建节点结构

**解决方法**:
1. 在模型结构编辑页面创建节点
2. 至少创建序列节点（如：医生序列、护理序列、医技序列）
3. 在序列下创建维度节点

### Q4: 生成的数据都是0

**原因**: 默认情况下脚本填充0值

**解决方法**:
- 使用 `--random` 参数生成随机值
- 或者手动修改数据库中的值

### Q5: 汇总表显示不正确

**原因**: 序列名称不匹配

**解决方法**:
- 确保序列节点的名称包含"医生"、"护理"或"医技"关键词
- 或者修改脚本中的匹配逻辑

## 下一步

生成测试数据后，可以：

1. **验证报表展示** - 确认汇总表和明细表的数据结构正确
2. **测试筛选功能** - 测试按周期、版本筛选
3. **测试导出功能** - 实现Excel导出功能（待开发）
4. **完善计算逻辑** - 实现真实的SQL/Python代码执行
5. **添加更多测试场景** - 测试边界情况和异常处理

## 技术说明

### 数据生成逻辑

1. **查找模型版本**: 使用激活版本或指定版本
2. **查找科室**: 只处理参与评估的科室
3. **查找节点**: 获取模型版本的所有节点
4. **生成结果**: 为每个科室的每个节点生成一条记录
5. **计算汇总**: 根据序列名称汇总医生、护理、医技价值

### 序列识别规则

脚本通过节点名称识别序列类型：

- 包含"医生"或"医疗" → 医生序列
- 包含"护理" → 护理序列
- 包含"医技" → 医技序列

如果你的序列名称不同，需要修改脚本中的匹配逻辑。

### 随机值范围

使用 `--random` 参数时：

- 工作量: 100 ~ 10000
- 权重: 0.01 ~ 1.0
- 价值: 工作量 × 权重

## 相关文档

- [报表功能实现说明](REPORT_FEATURE_IMPLEMENTATION.md)
- [报表功能快速启动指南](REPORT_QUICKSTART.md)
- [报表功能验证清单](REPORT_FEATURE_CHECKLIST.md)
