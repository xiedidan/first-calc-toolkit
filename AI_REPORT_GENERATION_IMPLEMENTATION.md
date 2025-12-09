# AI智能分析报告生成功能实现

## 功能概述

为分析报告管理的编辑详情页面增加AI自动编写"当前存在问题"和"未来发展计划"的功能。

## 实现内容

### 1. 后端实现

#### 新增文件
- `backend/app/models/ai_prompt_config.py` - AI提示词配置模型
- `backend/app/schemas/ai_prompt_config.py` - Pydantic模型
- `backend/app/services/ai_report_service.py` - AI报告生成服务
- `backend/app/api/ai_prompt_config.py` - API路由
- `backend/alembic/versions/20251209_add_ai_prompt_categories.py` - 数据库迁移

#### 修改文件
- `backend/app/models/__init__.py` - 添加模型导入
- `backend/app/models/hospital.py` - 添加关系
- `backend/app/schemas/__init__.py` - 添加schema导入
- `backend/app/main.py` - 注册路由
- `backend/app/utils/ai_interface.py` - 添加文本生成函数

### 2. 前端实现

#### 新增文件
- `frontend/src/api/ai-prompt-config.ts` - API接口

#### 修改文件
- `frontend/src/views/AIConfig.vue` - 添加提示词分类配置
- `frontend/src/components/ReportEditModal.vue` - 添加智能分析按钮

## 提示词分类

### 1. 智能分类分级 (classification)
用于收费项目的智能分类，支持占位符：
- `{items}` - 待分类项目列表JSON
- `{dimensions}` - 维度列表JSON

### 2. 业务价值报表-当前存在问题 (report_issues)
用于生成科室运营分析报告中的当前存在问题部分，支持占位符：
- `{hospital_name}` - 医院名称
- `{hospital_desc}` - 医院简介（预留字段，当前为空）
- `{department_name}` - 科室名称
- `{department_alignments}` - 科室的核算序列（如：医生、护理、医技）
- `{period}` - 统计周期（如：2025-10）
- `{dept_main_services}` - 科室主业（Top5维度的完整路径和业务价值数据）
- `{dept_work_substance}` - 业务内涵（Top5维度的Top5收费项目明细）

### 3. 业务价值报表-未来发展计划 (report_plans)
用于生成科室运营分析报告中的未来发展计划部分，支持与上述相同的占位符。

## 占位符数据格式说明

### `{dept_main_services}` - 科室主业
展示科室业务价值Top5的维度，包含完整的维度路径（序列-一级维度-二级维度...）：
```
- 医生-门诊-内科门诊：业务价值 125,000.00，工作量金额 98,000.00
- 医生-住院-普通病房：业务价值 98,500.00，工作量金额 76,000.00
- 护理-门诊-门诊护理：业务价值 45,000.00，工作量金额 38,000.00
- 医技-检验-生化检验：业务价值 32,000.00，工作量金额 28,000.00
- 医技-影像-CT检查：业务价值 28,000.00，工作量金额 25,000.00
```

### `{dept_work_substance}` - 业务内涵
展示Top5维度下各自收入Top5的收费项目明细，与分析报告中的"业务内涵"展示一致：
```
### 医生-门诊-内科门诊
    - 门诊诊查费：金额 35,000.00，数量 1,200
    - 处方费：金额 28,000.00，数量 980
    - 换药费：金额 15,000.00，数量 450
    - 注射费：金额 12,000.00，数量 380
    - 输液费：金额 8,000.00，数量 260

### 医生-住院-普通病房
    - 床位费：金额 42,000.00，数量 350
    - 护理费：金额 28,000.00，数量 350
    - 诊查费：金额 18,000.00，数量 350
    - 治疗费：金额 6,500.00，数量 180
    - 换药费：金额 2,000.00，数量 120
```

## 默认提示词

### 当前存在问题 - 系统提示词
```
你是一位资深的医院管理咨询专家，专注于科室运营分析和问题诊断。你需要根据提供的科室业务数据，分析该科室当前存在的问题和挑战。

请以专业、客观的角度进行分析，输出格式为Markdown，包含以下方面：
1. 业务结构问题（如业务单一、高价值业务占比低等）
2. 运营效率问题（如工作量与价值不匹配等）
3. 发展瓶颈（如技术能力、人才储备等）
4. 其他需要关注的问题

要求：
- 分析要具体、有针对性，避免泛泛而谈
- 结合数据进行分析，用数据说话
- 语言简洁专业，每个问题点控制在2-3句话
- 总字数控制在800字以内
```

### 当前存在问题 - 用户提示词
```
请分析以下科室当前存在的问题：

## 基本信息
- 医院名称：{hospital_name}
- 医院简介：{hospital_desc}
- 科室名称：{department_name}
- 核算序列：{department_alignments}
- 统计周期：{period}

## 业务数据
- 科室主业：{dept_main_services}
- 业务内涵：{dept_work_substance}

请基于以上信息，分析该科室当前存在的问题和挑战，输出Markdown格式的分析报告。
```

### 未来发展计划 - 系统提示词
```
你是一位资深的医院管理咨询专家，专注于科室发展规划和战略制定。你需要根据提供的科室业务数据，为该科室制定未来发展计划和建议。

请以专业、前瞻的角度进行规划，输出格式为Markdown，包含以下方面：
1. 业务发展方向（如拓展新业务、提升高价值业务占比等）
2. 能力建设计划（如技术提升、人才培养等）
3. 运营优化措施（如流程改进、效率提升等）
4. 短期目标（3-6个月）和中期目标（1-2年）

要求：
- 建议要具体可行，避免空洞的口号
- 结合科室实际情况，有针对性地提出建议
- 语言简洁专业，每个建议点控制在2-3句话
- 总字数控制在800字以内
```

### 未来发展计划 - 用户提示词
```
请为以下科室制定未来发展计划：

## 基本信息
- 医院名称：{hospital_name}
- 医院简介：{hospital_desc}
- 科室名称：{department_name}
- 核算序列：{department_alignments}
- 统计周期：{period}

## 业务数据
- 科室主业：{dept_main_services}
- 业务内涵：{dept_work_substance}

请基于以上信息，为该科室制定未来发展计划和建议，输出Markdown格式的规划报告。
```

## API接口

### 获取提示词分类
```
GET /api/v1/ai-prompt-config/categories
```

### 获取所有提示词配置
```
GET /api/v1/ai-prompt-config
```

### 获取指定分类的提示词配置
```
GET /api/v1/ai-prompt-config/{category}
```

### 保存提示词配置
```
POST /api/v1/ai-prompt-config/{category}
Body: { system_prompt: string, user_prompt: string }
```

### 生成报告内容
```
POST /api/v1/ai-prompt-config/generate/report
Body: { report_id: number, category: "report_issues" | "report_plans" }
```

## 数据库迁移

执行迁移：
```bash
cd backend
alembic upgrade head
```

## 使用说明

1. 在"系统设置 > AI接口管理"中配置API密钥和端点
2. 在"提示词配置"标签页中可以自定义各分类的提示词
3. 在"分析报告管理"中编辑报告时，点击"智能分析"按钮即可自动生成内容
4. 生成的内容为Markdown格式，可以在编辑器中进一步修改


---

## 维度下钻功能扩展

### 功能说明

为新建和编辑分析报告页面的"科室主业价值分布"表格添加下钻功能，与查看报告详情页面保持一致。

### 后端实现

#### 新增API端点
`GET /api/v1/analysis-reports/preview/dimension-drilldown`

参数：
- `department_id` - 科室ID
- `period` - 年月 (YYYY-MM)
- `node_id` - 节点ID

返回：`DimensionDrillDownResponse`，包含收费项目明细

### 前端实现

#### API函数
`frontend/src/api/analysis-reports.ts` 新增：
```typescript
export function previewDimensionDrillDown(departmentId: number, period: string, nodeId: number)
```

#### ReportCreateModal.vue
- 价值分布表格添加"操作"列，显示"下钻"按钮
- 添加下钻对话框，显示收费项目明细
- 使用 `previewDimensionDrillDown` API（预览模式）

#### ReportEditModal.vue
- 价值分布表格添加"操作"列，显示"下钻"按钮
- 添加下钻对话框，显示收费项目明细
- 使用 `getDimensionDrillDown` API（报告已有ID）

### 下钻规则

- 仅叶子维度节点可下钻
- 支持医生、医技、护理（收费类）序列的维度
- 显示收费项目明细：年月、科室、项目编码、项目名称、类别、单价、金额、数量
- 支持分页和汇总信息显示
