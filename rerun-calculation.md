# 重新运行计算任务

## 问题总结

报表显示全0的原因：
- `calculation_results` 表中只有维度（dimension）节点的数据
- 报表查询需要序列（sequence）节点的数据
- Step3 原来是插入到 `calculation_summaries` 表，但报表查询的是 `calculation_results` 表

## 解决方案

修改 Step3 的 SQL，让它将序列节点的汇总数据插入到 `calculation_results` 表。

## 已完成的操作

1. ✅ 修改了 `step3_value_aggregation.sql`
2. ✅ 更新了数据库中 workflow_id=20 的 Step3

## 下一步操作

### 方案1：重新运行完整计算（推荐）

在前端操作：
1. 进入"计算任务"页面
2. 创建新任务，选择：
   - 评估月份：2025-10
   - 模型版本：2025年标准版（ID=1）
   - 计算流程：标准计算流程（ID=20）
   - 科室：全部或选择特定科室
3. 点击"开始计算"
4. 等待任务完成
5. 查看报表，应该能看到正确的数据

### 方案2：只运行 Step3 补充序列数据

如果不想重新运行 Step1 和 Step2，可以只运行 Step3：

```python
# 在 backend 目录下运行
python补充序列数据.py
```

这个脚本会：
1. 读取任务 `124694a7-3f17-4ff3-831e-5e7efb6febe2` 的维度数据
2. 执行 Step3 的 SQL
3. 将序列数据插入到 `calculation_results` 表
4. 报表就能正常显示了

## 验证

运行后，检查：
```sql
SELECT node_type, COUNT(*) 
FROM calculation_results 
WHERE task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'
GROUP BY node_type;
```

应该看到：
- dimension: 846 条
- sequence: 约 30-60 条（每个科室 2-3 个序列）
