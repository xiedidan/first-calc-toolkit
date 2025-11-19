# 业务价值报表快速测试指南

## 测试目标

验证业务价值报表的汇总表和明细表功能，包括数据展示和交互。

## 测试步骤

### 第一步：准备基础数据

确保系统中已有以下数据：

1. **模型版本**
   - 至少创建一个模型版本
   - 设置为激活状态

2. **模型结构**
   - 创建序列节点（如：医生序列、护理序列、医技序列）
   - 在序列下创建维度节点

3. **科室数据**
   - 创建至少3-5个科室
   - 勾选"参与评估"选项
   - 确保科室状态为"启用"

### 第二步：生成测试数据

#### 方式一：使用批处理脚本（推荐）

```bash
# 生成填0的测试数据
generate-report-test-data.bat

# 或生成随机值的测试数据
generate-report-test-data.bat --random
```

#### 方式二：使用Python脚本

```bash
cd backend
python generate_report_test_data.py --random
```

### 第三步：启动服务

打开3个终端窗口：

**终端1 - 后端服务**
```bash
cd backend
uvicorn app.main:app --reload
```

**终端2 - Celery Worker（可选）**
```bash
cd backend
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**终端3 - 前端服务**
```bash
cd frontend
npm run dev
```

### 第四步：访问报表页面

1. 打开浏览器访问 `http://localhost:3000`
2. 登录系统（默认账号：admin / admin123）
3. 点击左侧菜单"评估结果"

### 第五步：测试汇总表

#### 5.1 查看汇总数据

- 选择评估月份（如：2025-10）
- 系统自动加载汇总数据
- 验证第一行是"全院汇总"
- 验证各科室数据正确显示

#### 5.2 验证数据列

汇总表应包含以下列：

- 科室名称
- 医生序列（价值、占比）
- 护理序列（价值、占比）
- 医技序列（价值、占比）
- 科室总价值
- 操作（查看明细按钮）

#### 5.3 验证数据计算

- 全院汇总 = 所有科室的总和
- 科室总价值 = 医生价值 + 护理价值 + 医技价值
- 三个序列的占比之和 = 100%

### 第六步：测试明细表

#### 6.1 打开明细对话框

- 点击任意科室的"查看明细"按钮
- 对话框标题显示科室名称
- 显示序列标签页（医生、护理、医技）

#### 6.2 查看维度数据

- 切换不同的序列标签页
- 验证每个序列下的维度列表
- 验证数据列：维度名称、编码、工作量、权重、价值、占比

#### 6.3 验证序列汇总

- 对话框底部显示序列总价值
- 验证序列总价值 = 所有维度价值之和

### 第七步：测试筛选功能

#### 7.1 切换评估月份

- 选择不同的月份
- 验证数据自动刷新
- 如果没有数据，显示相应提示

#### 7.2 切换模型版本

- 选择不同的模型版本
- 验证数据自动刷新
- 清空选择则使用激活版本

### 第八步：测试导出功能（待实现）

- 点击"导出汇总表"按钮
- 点击"导出明细表"按钮
- 验证提示信息（功能开发中）

## 验证清单

### 数据完整性

- [ ] 全院汇总数据正确
- [ ] 各科室数据完整
- [ ] 医生、护理、医技价值正确
- [ ] 占比计算正确（总和100%）
- [ ] 科室总价值正确

### 界面展示

- [ ] 表格布局合理
- [ ] 数据格式化正确（千分位、小数点）
- [ ] 百分比显示正确
- [ ] 固定列正常工作
- [ ] 滚动条正常工作

### 交互功能

- [ ] 筛选条件正常工作
- [ ] 查看明细按钮正常
- [ ] 明细对话框正常打开
- [ ] 序列标签页切换正常
- [ ] 对话框关闭正常

### 错误处理

- [ ] 未选择月份时提示正确
- [ ] 无数据时提示正确
- [ ] 网络错误时提示正确
- [ ] 缺少任务ID时提示正确

## 常见问题

### Q1: 汇总表显示"未找到计算结果"

**可能原因**:
1. 没有生成测试数据
2. 选择的月份不正确
3. 任务状态不是"completed"

**解决方法**:
1. 运行测试数据生成脚本
2. 检查数据库中的任务记录
3. 确认任务状态为"completed"

### Q2: 点击"查看明细"报错"缺少任务ID"

**可能原因**:
1. API返回的数据中没有task_id
2. 前端没有正确保存task_id

**解决方法**:
1. 检查后端API是否返回task_id
2. 检查前端是否正确接收和保存task_id
3. 查看浏览器控制台的错误信息

### Q3: 明细表没有数据

**可能原因**:
1. 计算结果表中没有数据
2. 节点类型不正确
3. 序列识别逻辑有问题

**解决方法**:
1. 检查calculation_results表
2. 确认节点的node_type字段正确
3. 检查序列名称是否包含关键词

### Q4: 数据显示为0

**可能原因**:
1. 使用了默认的填0模式
2. 没有使用--random参数

**解决方法**:
1. 重新生成数据，使用--random参数
2. 或手动修改数据库中的值

## 数据库查询

### 查看生成的任务

```sql
SELECT * FROM calculation_tasks 
WHERE task_id LIKE 'test-%' 
ORDER BY created_at DESC;
```

### 查看计算结果

```sql
SELECT cr.*, d.his_name
FROM calculation_results cr
JOIN departments d ON cr.department_id = d.id
WHERE cr.task_id = 'test-2025-10-20251030123456'
ORDER BY d.his_name, cr.node_type, cr.node_name;
```

### 查看汇总数据

```sql
SELECT cs.*, d.his_name
FROM calculation_summaries cs
JOIN departments d ON cs.department_id = d.id
WHERE cs.task_id = 'test-2025-10-20251030123456'
ORDER BY cs.total_value DESC;
```

### 验证数据一致性

```sql
-- 验证汇总数据的总价值
SELECT 
    task_id,
    department_id,
    doctor_value + nurse_value + tech_value as calculated_total,
    total_value,
    CASE 
        WHEN ABS((doctor_value + nurse_value + tech_value) - total_value) < 0.01 
        THEN 'OK' 
        ELSE 'ERROR' 
    END as status
FROM calculation_summaries
WHERE task_id = 'test-2025-10-20251030123456';

-- 验证占比之和
SELECT 
    task_id,
    department_id,
    doctor_ratio + nurse_ratio + tech_ratio as total_ratio,
    CASE 
        WHEN ABS((doctor_ratio + nurse_ratio + tech_ratio) - 100) < 0.01 
        THEN 'OK' 
        ELSE 'ERROR' 
    END as status
FROM calculation_summaries
WHERE task_id = 'test-2025-10-20251030123456'
AND total_value > 0;
```

## 下一步

测试通过后，可以：

1. **实现真实计算逻辑** - 替换测试数据生成，使用真实的SQL/Python代码
2. **实现Excel导出** - 完成汇总表和明细表的导出功能
3. **优化性能** - 添加缓存、分页、索引优化
4. **完善权限控制** - 实现科室级别的数据权限
5. **添加更多功能** - 数据对比、趋势分析、图表展示

## 相关文档

- [报表测试数据生成指南](REPORT_TEST_DATA_GUIDE.md)
- [报表功能实现说明](REPORT_FEATURE_IMPLEMENTATION.md)
- [报表功能快速启动指南](REPORT_QUICKSTART.md)
