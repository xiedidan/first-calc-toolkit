# 导向汇总功能实现总结

## 实现的功能

### 1. 业务明细表显示导向名称

**后端实现** (`backend/app/api/calculation_tasks.py`)：
- 在 `get_results_detail` API中，从 `orientation_rule_ids` 关联查询导向规则名称
- 将多个导向规则名称用顿号（、）连接显示
- 如果没有关联导向规则，则显示原有的 `business_guide` 字段

**关键代码**：
```python
# 查询导向规则名称映射
orientation_rule_ids = set()
for node in model_nodes:
    if node.orientation_rule_ids:
        orientation_rule_ids.update(node.orientation_rule_ids)

orientation_rules = {}
if orientation_rule_ids:
    rules = db.query(OrientationRule).filter(OrientationRule.id.in_(orientation_rule_ids)).all()
    orientation_rules = {rule.id: rule.name for rule in rules}

# 获取导向规则名称
orientation_names = []
if node_info and node_info.orientation_rule_ids:
    orientation_names = [
        orientation_rules.get(rule_id, f"规则{rule_id}")
        for rule_id in node_info.orientation_rule_ids
    ]
business_guide = "、".join(orientation_names) if orientation_names else (node_info.business_guide if node_info else None)
```

### 2. 导向汇总Tab页

**后端实现** (`backend/app/api/calculation_tasks.py`)：
- 新增 API: `GET /api/v1/calculation/results/orientation-summary`
- 查询 `orientation_adjustment_details` 表的数据
- 按序列类型（医生/护理/医技）分组返回数据
- 支持按科室筛选（dept_id参数）

**返回数据格式**：
```json
{
  "doctor": [
    {
      "id": 1,
      "department_name": "内科",
      "node_name": "门诊诊疗",
      "orientation_rule_name": "门诊量导向",
      "orientation_type": "benchmark_ladder",
      "actual_value": 1500.0,
      "benchmark_value": 1000.0,
      "orientation_ratio": 1.5,
      "adjustment_intensity": 1.2,
      "original_weight": 100.0,
      "adjusted_weight": 120.0,
      "is_adjusted": true,
      "adjustment_reason": null
    }
  ],
  "nurse": [...],
  "tech": [...]
}
```

**前端实现** (`frontend/src/views/Results.vue`)：
- 在明细对话框中添加"导向汇总"Tab
- 在导向汇总Tab内使用二级Tab区分三个序列
- 显示完整的导向调整过程：
  - 实际值、基准值
  - 导向比例
  - 调整力度
  - 原始权重、调整后权重
  - 是否调整、未调整原因

**表格列**：
- 科室
- 维度名称
- 导向规则
- 导向类型（基准阶梯/固定基准）
- 实际值
- 基准值
- 导向比例
- 调整力度
- 原始权重
- 调整后权重
- 是否调整
- 未调整原因

## 数据流程

1. 用户在汇总表中点击"查看明细"
2. 调用 `viewDetail` 方法
3. 加载科室业务价值明细数据（三个序列的树形表格）
4. 同时调用 `loadOrientationSummary` 加载导向汇总数据
5. 用户可以在Tab之间切换查看：
   - 医生序列明细
   - 护理序列明细
   - 医技序列明细
   - **导向汇总**（新增）

## 测试方法

运行测试脚本：
```bash
python test_orientation_summary.py
```

测试内容：
1. 验证导向汇总API返回正确的数据结构
2. 验证数据按序列正确分组
3. 验证业务明细表中显示导向规则名称

## 注意事项

1. **多租户隔离**：所有API都通过 `_get_task_with_hospital_check` 验证任务所属医疗机构
2. **序列判断**：通过递归查找父节点确定维度所属序列
3. **空数据处理**：如果没有导向调整数据，返回空数组而不报错
4. **导向名称显示**：优先显示关联的导向规则名称，其次显示 business_guide 字段

## 相关文件

### 后端
- `backend/app/api/calculation_tasks.py` - API接口
- `backend/app/schemas/calculation_task.py` - Schema定义
- `backend/app/models/orientation_adjustment_detail.py` - 数据模型
- `backend/app/models/orientation_rule.py` - 导向规则模型

### 前端
- `frontend/src/views/Results.vue` - 报表页面

## 数据库表

- `orientation_adjustment_details` - 业务导向调整明细表
- `orientation_rules` - 导向规则表
- `model_nodes` - 模型节点表（包含 orientation_rule_ids 字段）
