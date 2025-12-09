# 科室业务价值标准计算流程

## 简介

本目录包含科室业务价值评估的标准计算流程SQL代码和导入脚本。这套标准流程基于《科室业务价值评估数据集.md》定义的数据模型,提供了一套开箱即用的计算流程模板。

## 文件说明

| 文件名 | 说明 |
|--------|------|
| `step1_data_preparation.sql` | 步骤1: 数据准备 - 从门诊和住院收费明细表生成统一的收费明细数据 |
| `step2_dimension_catalog.sql` | 步骤2: 维度目录统计 - 根据维度-收费项目映射统计各维度的工作量 |
| `step3a_orientation_adjustment.sql` | 步骤3a: 业务导向调整 - 根据业务导向规则调整维度的学科业务价值 |
| `step3b_indicator_calculation.sql` | 步骤3b: 指标计算-护理床日数 - 从工作量统计表中提取护理床日数 |
| `step3c_workload_dimensions.sql` | 步骤3c: 工作量维度统计 - 从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量 |
| `step5_value_aggregation.sql` | 步骤5: 业务价值汇总 - 根据模型结构和权重汇总各科室的业务价值 |
| `import_standard_workflow.sh` | 自动导入脚本 - 一键将SQL代码导入到系统 |
| `README.md` | 本文档 - 使用说明和常见问题 |


## 快速开始

### 1. 准备工作

在导入标准流程之前,请确保已完成以下准备:

- ✅ 系统已部署并正常运行
- ✅ 已创建模型版本(在前端"模型版本管理"页面)
- ✅ 已配置数据源(指向HIS系统或数据仓库)
- ✅ 已导入科室信息(departments表)
- ✅ 已导入收费项目(charge_items表)
- ✅ 已配置维度-收费项目映射(dimension_item_mappings表)
- ✅ backend/.env文件已正确配置数据库连接信息
- ✅ **外部数据源中存在所需的表** (见下方说明)

#### 外部数据源表要求

标准流程需要以下外部数据表:

| 表名 | 用途 | 是否必需 |
|------|------|---------|
| `charge_details` | 收费明细数据 | 步骤1必需 |
| `workload_statistics` | 工作量统计数据 | 步骤2必需 |

**测试环境**: 如果是测试环境，可以使用 `create_test_tables.sql` 创建测试表和数据：

```bash
# 连接到外部数据源数据库
psql -h <host> -p <port> -U <user> -d <database>

# 执行测试表创建脚本
\i create_test_tables.sql
```

**生产环境**: 请确保外部数据源中存在这些表，或修改 SQL 文件使用实际的表名。

### 2. 导入标准流程

```bash
# 进入模板目录
cd backend/standard_workflow_templates

# 执行导入脚本(替换123为实际的模型版本ID)
bash import_standard_workflow.sh --version-id 123

# 或指定自定义流程名称
bash import_standard_workflow.sh \
  --version-id 123 \
  --workflow-name "标准计算流程-2025年10月"

# 或指定医疗机构ID(通常不需要,会自动从版本中获取)
bash import_standard_workflow.sh \
  --version-id 123 \
  --hospital-id 1
```

**说明**: 
- 脚本会自动读取`backend/.env`文件中的数据库配置
- 支持两种.env格式:
  - `DATABASE_URL=postgresql://user:password@host:port/database`
  - 或分离的变量: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- 医疗机构ID会自动从模型版本中获取,通常无需手动指定
- 无需手动输入数据库密码
- 导入成功后会显示流程ID和访问URL

### 3. 调整SQL代码(可选)

如果需要根据实际数据库结构调整SQL代码:

1. **修改表名和字段名**: 如果外部数据源的表名或字段名不同,请修改SQL文件
2. **调整数据筛选条件**: 根据实际业务需求调整WHERE条件
3. **添加更多指标计算步骤**: 复制`step2_indicator_calculation.sql`中的示例,创建新的指标计算步骤

**注意**: 修改SQL代码后,需要重新执行导入脚本

### 4. 在前端查看

导入成功后,访问前端"计算流程管理"页面:

1. 找到刚导入的标准流程
2. 点击"查看步骤"查看3个计算步骤
3. 可以编辑步骤的SQL代码
4. 可以添加更多自定义步骤

### 5. 创建计算任务

在"计算任务"页面创建新任务:

1. 选择模型版本
2. 选择刚导入的标准计算流程
3. 选择科室范围(全部科室或指定科室)
4. 点击"开始计算"


## SQL代码说明

### 步骤1: 维度目录统计

**功能**: 根据维度-收费项目映射关系,从收费明细表中统计各维度的工作量

**关键逻辑**:
1. 从`dimension_item_mappings`表读取维度-收费项目映射关系
2. 关联`charge_details`表获取收费明细数据
3. 按维度和科室汇总金额、数量、患者人次
4. 自动处理一个收费项目属于多个维度的情况

**占位符**:
- `{current_year_month}`: 当期年月 (如: 2025-10)
- `{hospital_id}`: 医疗机构ID
- `{start_date}`: 开始日期 (当月第一天)
- `{end_date}`: 结束日期 (当月最后一天)

**输出字段**:
- `dimension_id`: 维度ID
- `department_id`: 科室ID
- `workload_amount`: 工作量金额
- `workload_quantity`: 工作量数量
- `workload_patient_count`: 患者人次

### 步骤3b: 指标计算-护理床日数

**功能**: 从工作量统计表中提取护理床日数

**关键逻辑**:
1. 从`workload_statistics`表提取护理床日数(stat_type='nursing_days')
2. 汇总各级护理床日数(一级、二级、三级、特级等)
3. 按科室输出工作量数值

**占位符**:
- `{task_id}`: 计算任务ID
- `{current_year_month}`: 当期年月
- `{hospital_id}`: 医疗机构ID
- `{version_id}`: 模型版本ID

**输出字段**:
- `task_id`: 任务ID
- `node_id`: 节点ID
- `department_id`: 科室ID
- `workload`: 工作量数值
- `weight`: 权重
- `value`: 价值

### 步骤3c: 工作量维度统计

**功能**: 从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量

**支持的维度类型**:
- `nursing_bed_days`: 护理床日
- `admission_discharge_transfer`: 出入转院
- `surgery_management`: 手术管理
- `operating_room_nursing`: 手术室护理

**关键逻辑**:
1. 从`workload_statistics`表读取各类工作量数据
2. 根据统计类型(stat_type)匹配到对应的维度(通过code)
3. 按科室汇总工作量
4. 插入到`calculation_results`表

**占位符**:
- `{task_id}`: 计算任务ID
- `{current_year_month}`: 当期年月
- `{hospital_id}`: 医疗机构ID
- `{version_id}`: 模型版本ID

**输出字段**:
- `task_id`: 任务ID
- `node_id`: 节点ID
- `department_id`: 科室ID
- `workload`: 工作量数值
- `weight`: 权重
- `value`: 价值

**维度匹配规则**:
- 通过维度的`code`字段进行模糊匹配
- 例如: `code LIKE '%nursing_bed_days%'` 或 `code LIKE '%护理床日%'`
- 如果维度code与stat_type不匹配,需要调整SQL中的匹配条件

### 步骤3: 业务价值汇总

**功能**: 根据模型结构和权重,自下而上汇总各科室的业务价值

**关键逻辑**:
1. 加载模型结构(树形结构,包含层级关系和权重)
2. 加载所有维度的计算结果
3. 根据权重类型计算维度得分:
   - 百分比权重: 得分 = 工作量 × 权重
   - 固定值权重: 得分 = 工作量 × 单价
4. 使用递归CTE自下而上汇总父节点得分
5. 提取序列得分(医生、护理、医技)
6. 计算科室总价值

**占位符**:
- `{task_id}`: 计算任务ID
- `{version_id}`: 模型版本ID

**输出字段**:
- `task_id`: 任务ID
- `department_id`: 科室ID
- `doctor_value`: 医生序列价值
- `nursing_value`: 护理序列价值
- `medical_tech_value`: 医技序列价值
- `total_value`: 科室总价值

**注意事项**:
- 序列识别基于节点名称的模糊匹配(包含"医生"、"护理"、"医技"等关键词)
- 如果模型结构不同,可能需要调整序列识别逻辑
- 当前假设序列在第1层(level=1),如果不同需要调整


## 常见问题

### Q1: 导入失败,提示"模型版本不存在"

**A**: 请确认`--version-id`参数是否正确。

**解决方法**:
1. 在前端"模型版本管理"页面查看可用的版本ID
2. 确保使用的是正确的版本ID
3. 确保该版本属于当前医疗机构

### Q2: 导入失败,提示"数据库连接失败"

**A**: 请检查数据库配置和连接。

**解决方法**:
1. 检查`backend/.env`文件中的数据库配置是否正确
2. 确认.env文件格式正确:
   - 方式1: `DATABASE_URL=postgresql://user:password@host:port/database`
   - 方式2: 分离的变量 `DATABASE_HOST=localhost`, `DATABASE_PORT=5432` 等
3. 确认数据库服务是否正常运行
4. 测试网络连接: `psql -h <host> -p <port> -U <user> -d <database>`
5. 检查防火墙规则是否允许连接

### Q3: SQL执行失败,提示"表不存在"

**A**: 外部数据源的表名或字段名可能不同。

**解决方法**:
1. 检查数据源配置是否正确
2. 确认外部数据库中的表名和字段名
3. 修改SQL文件中的表名和字段名
4. 确保有权限访问外部数据表

**常见表名差异**:
- `charge_details` 可能是 `dwd_sfmxb` 或其他名称
- `workload_statistics` 可能是 `workload_stats` 或其他名称

### Q4: 如何添加更多指标计算步骤?

**A**: 有两种方法添加新的指标计算步骤。

**方法1: 在前端手动添加**
1. 访问"计算流程管理"页面
2. 找到标准计算流程,点击"查看步骤"
3. 点击"新建步骤"
4. 复制`step2_indicator_calculation.sql`中的示例SQL
5. 修改维度ID和计算逻辑
6. 保存步骤

**方法2: 修改导入脚本**
1. 创建新的SQL文件(如`step2_consultation.sql`)
2. 修改`import_standard_workflow.sh`脚本
3. 添加新步骤的INSERT语句
4. 重新执行导入脚本

### Q5: 占位符如何替换?

**A**: 占位符由系统在执行计算步骤时自动替换,无需手动处理。

**占位符列表**:
- `{current_year_month}` → 当期年月 (如: 2025-10)
- `{department_id}` → 科室ID (如: 123)
- `{department_code}` → 科室编码 (如: NEI01)
- `{start_date}` → 开始日期 (如: 2025-10-01)
- `{end_date}` → 结束日期 (如: 2025-10-31)
- `{hospital_id}` → 医疗机构ID (如: 1)
- `{dimension_id}` → 维度ID (如: 789)
- `{task_id}` → 计算任务ID (如: task_20251113_001)
- `{version_id}` → 模型版本ID (如: 123)

### Q6: 如何验证SQL代码是否正确?

**A**: 可以在数据库中手动测试SQL代码。

**测试步骤**:
1. 连接到数据库: `psql -h <host> -p <port> -U <user> -d <database>`
2. 手动替换占位符为实际值
3. 执行SQL查看结果
4. 检查返回的字段和数据是否符合预期

**示例**:
```sql
-- 将占位符替换为实际值
-- {current_year_month} → '2025-10'
-- {hospital_id} → 1
-- {start_date} → '2025-10-01'
-- {end_date} → '2025-10-31'

-- 然后执行SQL
```

### Q7: 计算结果不正确怎么办?

**A**: 请检查以下几个方面。

**检查清单**:
1. ✅ 维度-收费项目映射是否正确配置
2. ✅ 收费明细数据是否完整
3. ✅ 工作量统计数据是否存在
4. ✅ 模型结构和权重是否正确
5. ✅ 占位符是否正确替换
6. ✅ SQL逻辑是否符合业务需求

**调试方法**:
1. 在前端查看"计算步骤执行日志"
2. 检查每个步骤的执行结果
3. 查看错误信息和堆栈跟踪
4. 在数据库中手动执行SQL验证

### Q8: 是否需要指定医疗机构ID?

**A**: 通常不需要,脚本会自动从模型版本中获取。

**说明**:
- 每个模型版本都关联到一个医疗机构
- 脚本会自动查询版本的`hospital_id`并使用
- 只有在特殊情况下才需要手动指定`--hospital-id`参数

**示例**:
```bash
# 自动获取(推荐)
bash import_standard_workflow.sh --version-id 123

# 手动指定(通常不需要)
bash import_standard_workflow.sh --version-id 123 --hospital-id 1
```

**注意**: 如果手动指定的医疗机构ID与版本中的不一致,脚本会使用版本中的ID并显示警告。

### Q9: 如何修改序列识别逻辑?

**A**: 修改`step3_value_aggregation.sql`中的CASE语句。

**当前逻辑**:
```sql
-- 基于节点名称模糊匹配
WHEN node_name LIKE '%医生%' OR node_name LIKE '%doctor%' THEN score
```

**修改建议**:
1. 如果序列名称固定,使用精确匹配: `node_name = '医生序列'`
2. 如果有序列类型字段,使用字段判断: `sequence_type = 'doctor'`
3. 如果序列在固定层级,使用层级判断: `level = 1 AND parent_id IS NULL`

## 技术支持

如有其他问题,请:
1. 查看系统文档
2. 联系系统管理员
3. 在前端"帮助中心"提交问题

---

**文档版本**: 1.0  
**最后更新**: 2025-11-17
