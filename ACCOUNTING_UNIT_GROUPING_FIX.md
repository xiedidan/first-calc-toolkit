# 核算单元分组汇总修复

## 问题描述

在科室业务价值汇总表中，同一个核算单元的多个科室被重复显示，导致用户看到重复的核算单元记录。

### 问题原因

1. **数据结构**：多个科室可以共享同一个核算单元
   - 例如：`FHL02` (门诊手术室) 包含4个科室：
     - 门诊手术室(普通)
     - 门诊手术室(干眼)
     - 门诊手术室(整形)
     - 门诊手术室(玻注)

2. **原有逻辑**：汇总API按科室遍历，每个科室生成一条记录
   - 结果：同一核算单元出现多次

## 解决方案

### 修改汇总逻辑

修改 `backend/app/api/calculation_tasks.py` 中的 `get_results_summary` 函数：

**修改前**：
```python
# 按科室遍历，每个科室一条记录
for dept in all_active_depts:
    # 计算该科室的价值
    departments_data.append(CalculationSummaryResponse(
        department_id=dept.id,
        department_code=dept.accounting_unit_code,  # 可能重复
        department_name=dept.accounting_unit_name,  # 可能重复
        ...
    ))
```

**修改后**：
```python
# 1. 先按核算单元分组
accounting_units = {}
for dept in all_active_depts:
    # 计算该科室的价值
    unit_code = dept.accounting_unit_code or dept.his_code
    unit_name = dept.accounting_unit_name or dept.his_name
    unit_key = (unit_code, unit_name)
    
    # 累加到核算单元
    if unit_key not in accounting_units:
        accounting_units[unit_key] = {...}
    accounting_units[unit_key]['doctor_value'] += doctor_value
    accounting_units[unit_key]['nurse_value'] += nurse_value
    accounting_units[unit_key]['tech_value'] += tech_value

# 2. 生成汇总数据（每个核算单元一条记录）
for (unit_code, unit_name), unit_data in sorted_units:
    departments_data.append(CalculationSummaryResponse(
        department_id=representative_dept_id,  # 使用第一个科室ID作为代表
        department_code=unit_code,
        department_name=unit_name,
        ...
    ))
```

### 关键改进

1. **按核算单元分组**：使用 `(accounting_unit_code, accounting_unit_name)` 作为分组键
2. **价值累加**：同一核算单元下的所有科室价值累加
3. **代表科室ID**：使用第一个科室的ID作为代表，用于查看明细
4. **排序保持**：按原科室的 `sort_order` 排序

## 数据示例

### 修改前（有重复）
```
核算单元代码  核算单元名称        总价值
FHL02        门诊手术室          1000.00
FHL02        门诊手术室          1500.00
FHL02        门诊手术室           800.00
FHL02        门诊手术室          1200.00
```

### 修改后（已合并）
```
核算单元代码  核算单元名称        总价值
FHL02        门诊手术室          4500.00
```

## 影响范围

### 后端
- ✅ `get_results_summary` 函数：按核算单元分组汇总
- ✅ 保持API响应格式不变，前端无需修改

### 前端
- ✅ 无需修改，API响应格式保持兼容

### 数据库
- ✅ 无需修改，仅修改查询逻辑

## 测试验证

### 测试脚本
```bash
python test_accounting_unit_grouping.py
```

### 验证要点
1. 核算单元不重复
2. 价值正确累加
3. 排序正确
4. 可以正常查看明细

### 预期结果
- 33个核算单元（不是37个科室）
- `FHL02` 只出现1次，价值为4个科室的总和
- `FHL03` 只出现1次，价值为2个科室的总和

## 注意事项

1. **查看明细功能**：点击核算单元查看明细时，使用代表科室ID
   - 如果需要查看该核算单元下所有科室的明细，需要进一步修改明细API

2. **参考价值匹配**：前端使用 `department_code` 匹配参考价值
   - 确保参考价值表中使用核算单元代码而非科室代码

3. **导出功能**：导出汇总表时也会按核算单元分组

## 日期

2025-12-08
