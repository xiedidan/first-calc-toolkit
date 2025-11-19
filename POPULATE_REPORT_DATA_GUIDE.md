# 业务价值报表数据填充指南

## 概述

`populate_report_data.py` 脚本用于向业务价值报表填充测试或生产数据。该脚本会：

1. ✅ 清理指定周期的现有数据
2. ✅ 覆盖所有启用科室
3. ✅ 覆盖所有模型维度
4. ✅ 自动计算序列汇总值
5. ✅ 根据真实数据计算占比
6. ✅ 生成汇总表数据

## 快速开始

### 方式一：使用批处理文件（推荐）

```bash
# Windows系统
populate-report-data.bat
```

然后按照提示选择操作即可。

### 方式二：直接运行Python脚本

```bash
# 进入backend目录
cd backend

# 填充当前年月数据（使用0值）
python populate_report_data.py

# 填充指定周期数据（使用0值）
python populate_report_data.py --period 2025-10

# 填充随机值数据
python populate_report_data.py --period 2025-10 --random

# 指定模型版本
python populate_report_data.py --period 2025-10 --model-version-id 1

# 不清理现有数据（追加模式）
python populate_report_data.py --period 2025-10 --no-clean
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--period` | 计算周期 (YYYY-MM) | 当前年月 |
| `--random` | 使用随机值 | False（使用0值） |
| `--model-version-id` | 指定模型版本ID | 使用激活版本 |
| `--no-clean` | 不清理现有数据 | False（会清理） |

## 数据生成逻辑

### 1. 维度数据生成

对于每个科室的每个维度节点，脚本会生成：

- **工作量 (workload)**: 根据维度类型生成合理范围的值
- **权重/单价 (weight)**: 根据维度类型生成合理范围的值
- **价值 (value)**: 工作量 × 权重
- **占比 (ratio)**: 该维度价值 / 同序列下所有维度价值总和 × 100%

#### 随机值范围示例

| 维度类型 | 工作量范围 | 权重范围 |
|----------|-----------|----------|
| 门诊诊察 | 500-2000 | 20-50 |
| 住院诊察/床日 | 200-800 | 50-150 |
| 手术 | 50-300 | 200-800 |
| 护理 | 300-1500 | 20-80 |
| 检查/检验 | 200-1000 | 30-100 |

### 2. 序列数据生成

序列的价值是其下所有维度价值的总和：

```
序列价值 = Σ(该序列下所有维度的价值)
```

### 3. 汇总数据生成

汇总表包含三个序列的数据：

- **医生序列**: 包含"医生"、"医疗"、"医师"关键词的序列
- **护理序列**: 包含"护理"、"护士"关键词的序列
- **医技序列**: 包含"医技"、"技师"关键词的序列

每个序列的占比计算：

```
序列占比 = 序列价值 / 科室总价值 × 100%
科室总价值 = 医生价值 + 护理价值 + 医技价值
```

## 数据结构

### 计算结果表 (calculation_results)

| 字段 | 说明 | 示例 |
|------|------|------|
| task_id | 任务ID | report-2025-10-20251030123456 |
| department_id | 科室ID | 1 |
| node_id | 节点ID | 11 |
| node_name | 节点名称 | 门诊诊察 |
| node_type | 节点类型 | dimension/sequence |
| parent_id | 父节点ID | 1 |
| workload | 工作量 | 1500.0000 |
| weight | 权重/单价 | 35.0000 |
| value | 价值 | 52500.0000 |
| ratio | 占比 | 45.50 |

### 汇总表 (calculation_summaries)

| 字段 | 说明 | 示例 |
|------|------|------|
| task_id | 任务ID | report-2025-10-20251030123456 |
| department_id | 科室ID | 1 |
| doctor_value | 医生价值 | 150000.0000 |
| doctor_ratio | 医生占比 | 45.50 |
| nurse_value | 护理价值 | 100000.0000 |
| nurse_ratio | 护理占比 | 30.30 |
| tech_value | 医技价值 | 80000.0000 |
| tech_ratio | 医技占比 | 24.20 |
| total_value | 科室总价值 | 330000.0000 |

## 使用场景

### 场景1：开发测试

```bash
# 使用随机值快速生成测试数据
python populate_report_data.py --period 2025-10 --random
```

### 场景2：演示数据

```bash
# 使用0值生成空白数据框架
python populate_report_data.py --period 2025-10
```

### 场景3：多周期数据

```bash
# 生成多个月份的数据
python populate_report_data.py --period 2025-08 --random
python populate_report_data.py --period 2025-09 --random
python populate_report_data.py --period 2025-10 --random
```

### 场景4：特定模型版本

```bash
# 使用特定模型版本生成数据
python populate_report_data.py --period 2025-10 --model-version-id 2 --random
```

## 验证数据

### 1. 检查任务

```sql
SELECT * FROM calculation_tasks 
WHERE period = '2025-10' 
ORDER BY created_at DESC;
```

### 2. 检查计算结果

```sql
-- 查看某个科室的计算结果
SELECT 
    node_name,
    node_type,
    workload,
    weight,
    value,
    ratio
FROM calculation_results
WHERE task_id = 'report-2025-10-20251030123456'
  AND department_id = 1
ORDER BY node_type, parent_id, node_id;
```

### 3. 检查汇总数据

```sql
-- 查看汇总数据
SELECT 
    d.his_name,
    cs.doctor_value,
    cs.doctor_ratio,
    cs.nurse_value,
    cs.nurse_ratio,
    cs.tech_value,
    cs.tech_ratio,
    cs.total_value
FROM calculation_summaries cs
JOIN departments d ON cs.department_id = d.id
WHERE cs.task_id = 'report-2025-10-20251030123456'
ORDER BY cs.total_value DESC;
```

### 4. 验证占比计算

```sql
-- 验证维度占比是否正确
SELECT 
    parent_id,
    SUM(ratio) as total_ratio
FROM calculation_results
WHERE task_id = 'report-2025-10-20251030123456'
  AND node_type = 'dimension'
GROUP BY parent_id, department_id;
-- 结果应该接近100%

-- 验证序列占比是否正确
SELECT 
    department_id,
    doctor_ratio + nurse_ratio + tech_ratio as total_ratio
FROM calculation_summaries
WHERE task_id = 'report-2025-10-20251030123456';
-- 结果应该接近100%
```

## 注意事项

1. **数据清理**: 默认会清理指定周期的所有现有数据，使用 `--no-clean` 可以避免清理
2. **模型版本**: 确保使用的模型版本有完整的节点结构
3. **科室状态**: 只会为 `is_active=True` 的科室生成数据
4. **占比精度**: 占比保留2位小数，可能存在微小的舍入误差
5. **性能**: 大量科室和维度时可能需要较长时间，请耐心等待

## 故障排除

### 问题1: 未找到模型版本

```
❌ 错误: 未找到模型版本
```

**解决方案**: 
- 检查是否有激活的模型版本
- 或使用 `--model-version-id` 指定具体版本

### 问题2: 未找到启用的科室

```
❌ 错误: 未找到启用的科室
```

**解决方案**: 
- 检查 departments 表中是否有 `is_active=True` 的记录
- 运行科室数据初始化脚本

### 问题3: 模型版本没有节点

```
❌ 错误: 模型版本没有节点
```

**解决方案**: 
- 检查 model_nodes 表中是否有对应版本的节点
- 确保模型结构已正确配置

### 问题4: 数据库连接失败

**解决方案**: 
- 检查 `.env` 文件中的数据库配置
- 确保数据库服务正在运行
- 检查数据库连接权限

## 相关文档

- [报表功能快速开始](REPORT_QUICKSTART.md)
- [报表功能实现总结](REPORT_IMPLEMENTATION_SUMMARY.md)
- [报表测试数据指南](REPORT_TEST_DATA_GUIDE.md)
- [API测试指南](API_TESTING_GUIDE.md)

## 技术支持

如有问题，请查看：
1. 脚本输出的详细日志
2. 数据库表结构和约束
3. 模型版本和节点配置
4. 科室数据状态
