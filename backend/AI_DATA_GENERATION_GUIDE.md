# AI智能数据生成使用指南

## 概述

`populate_report_data_ai.py` 是一个基于AI大模型的智能数据生成工具，能够根据医院特点和科室业务特征，自动生成符合实际业务逻辑的报表数据。

## 核心功能

1. **科室级工作量分配**：根据医院背景和科室特点，AI智能分配各科室的工作量比例
2. **维度级工作量分配**：根据科室业务特点，AI智能分配各维度的具体工作量
3. **业务逻辑验证**：确保生成的数据符合医疗业务规则（如医生专科不应有手术台次等）
4. **自动计算价值和占比**：基于工作量和权重自动计算价值，并计算各维度占比

## 工作流程

```
配置文件 → AI分配科室工作量 → AI分配维度工作量 → 计算价值和占比 → 生成汇总数据
```

### 详细步骤

1. **读取配置文件**
   - 医院信息（类型、特色、背景）
   - 总工作量数据（各项指标的总量）
   - 科室信息（业务特点、约束条件）

2. **AI分配科室工作量**
   - 调用AI模型，根据医院特点分配各科室的工作量比例
   - 确保分配符合医院业务特点（如眼科医院眼科科室占主导）

3. **AI分配维度工作量**
   - 对每个科室，调用AI模型分配各维度的工作量
   - 确保分配符合科室业务特点（如医生专科主要在医生维度）

4. **计算价值和占比**
   - 价值 = 工作量 × 权重
   - 占比 = 该维度价值 / 同级维度价值总和 × 100%

5. **生成汇总数据**
   - 汇总序列价值
   - 生成科室汇总表数据

## 配置文件格式

### 1. 医院信息 (hospital_info)

```json
{
  "hospital_info": {
    "name": "医院名称",
    "type": "医院类型（综合医院/专科医院）",
    "specialty": "专科类型（如：眼科、心血管等）",
    "description": "医院详细描述",
    "characteristics": [
      "医院特点1",
      "医院特点2"
    ]
  }
}
```

### 2. 总工作量 (total_workload)

```json
{
  "total_workload": {
    "workload_based_total": {
      "value": 1000000,
      "description": "按工作量权重计提的维度总额",
      "note": "分配备注"
    },
    "consultation_total": {
      "value": 500,
      "description": "医生总会诊数",
      "note": "分配备注"
    },
    "mdt_total": {
      "value": 100,
      "description": "医生总MDT数",
      "note": "分配备注"
    },
    "case_total": {
      "value": 3000,
      "description": "医生总病案数",
      "note": "分配备注"
    },
    "nursing_bed_days_total": {
      "value": 15000,
      "description": "护理总床日数",
      "note": "分配备注"
    },
    "surgery_total": {
      "value": 2000,
      "description": "手术总台次数",
      "note": "分配备注"
    },
    "observation_total": {
      "value": 800,
      "description": "留观数",
      "note": "分配备注"
    }
  }
}
```

### 3. 科室信息 (departments)

```json
{
  "departments": [
    {
      "his_code": "01",
      "his_name": "科室名称",
      "category": "科室类别（医生专科/护理病区/护理非病区/医技科室/行政后勤）",
      "business_characteristics": "科室业务特点描述",
      "constraints": [
        "业务约束1",
        "业务约束2"
      ]
    }
  ]
}
```

## 使用方法

### 1. 准备工作

#### 安装依赖

```bash
pip install openai
```

#### 设置API密钥

方式1：环境变量
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

方式2：命令行参数
```bash
python populate_report_data_ai.py --config config.json --api-key your_api_key_here
```

### 2. 创建配置文件

复制示例配置文件并修改：

```bash
cp report_data_config.example.json report_data_config.json
```

根据实际情况修改配置文件中的：
- 医院信息
- 总工作量数据
- 科室列表和业务特点

### 3. 运行脚本

#### 基本用法

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10
```

#### 指定API密钥

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --api-key YOUR_KEY
```

#### 使用GPT-4模型

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --model gpt-4
```

#### 使用自定义API端点

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --base-url https://api.example.com/v1
```

#### 指定模型版本

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --model-version-id 1
```

#### 不清理现有数据（追加模式）

```bash
python populate_report_data_ai.py --config report_data_config.json --period 2025-10 --no-clean
```

### 4. 自定义提示词

如果需要调整AI的行为，可以修改 `ai_prompts.json` 文件中的提示词模板。

提示词文件包含三个模板：
- `department_allocation_prompt`：科室工作量分配提示词
- `dimension_allocation_prompt`：维度工作量分配提示词
- `validation_prompt`：数据验证提示词（预留）

## 配置示例

### 眼科专科医院示例

```json
{
  "hospital_info": {
    "name": "某某眼科医院",
    "type": "专科医院",
    "specialty": "眼科",
    "description": "三级甲等眼科专科医院，以眼科诊疗为主",
    "characteristics": [
      "眼科专科医院，眼科相关科室工作量占主导",
      "手术主要集中在眼科手术室",
      "护理工作主要在眼科病区"
    ]
  },
  "total_workload": {
    "workload_based_total": {"value": 1000000, "description": "工作量总额"},
    "consultation_total": {"value": 500, "description": "会诊总数"},
    "surgery_total": {"value": 2000, "description": "手术总台次"}
  },
  "departments": [
    {
      "his_code": "01",
      "his_name": "白内障科",
      "category": "医生专科",
      "business_characteristics": "主要进行白内障手术治疗",
      "constraints": [
        "护理工作量应该很少或为0",
        "手术台次应该为0（手术在手术室科室）",
        "主要工作量在门诊诊察、住院治疗等医生维度"
      ]
    }
  ]
}
```

### 综合医院示例

```json
{
  "hospital_info": {
    "name": "某某综合医院",
    "type": "综合医院",
    "specialty": "综合",
    "description": "三级甲等综合医院，设有内科、外科、妇产科等多个科室",
    "characteristics": [
      "综合医院，各科室工作量相对均衡",
      "内科、外科、妇产科等主要科室工作量较大",
      "手术主要在手术室，护理主要在病区"
    ]
  },
  "total_workload": {
    "workload_based_total": {"value": 2000000, "description": "工作量总额"},
    "consultation_total": {"value": 1000, "description": "会诊总数"},
    "surgery_total": {"value": 5000, "description": "手术总台次"}
  },
  "departments": [
    {
      "his_code": "01",
      "his_name": "心内科",
      "category": "医生专科",
      "business_characteristics": "主要诊治心血管疾病",
      "constraints": [
        "护理工作量应该很少或为0",
        "手术台次应该为0",
        "主要工作量在门诊、住院、治疗等医生维度"
      ]
    },
    {
      "his_code": "02",
      "his_name": "普外科",
      "category": "医生专科",
      "business_characteristics": "主要进行普通外科手术",
      "constraints": [
        "护理工作量应该很少或为0",
        "手术台次应该为0",
        "主要工作量在门诊、住院、治疗等医生维度"
      ]
    }
  ]
}
```

## 业务规则说明

### 科室类别与工作量分配规则

| 科室类别 | 主要工作量维度 | 应为0的维度 |
|---------|--------------|-----------|
| 医生专科 | 门诊诊察、住院床日、医生治疗手术、会诊、MDT、病案 | 护理操作、手术台次、医技项目 |
| 护理病区 | 床日护理、护理操作 | 医生诊疗、手术台次、医技项目 |
| 护理非病区（手术室） | 手术室护理 | 医生诊疗、床日护理、医技项目 |
| 护理非病区（留观室） | 留观护理 | 医生诊疗、床日护理、手术台次、医技项目 |
| 医技科室 | 对应的医技项目（检验、影像、放射等） | 医生诊疗、护理操作、手术台次 |
| 行政后勤 | 行政管理、后勤保障 | 医生诊疗、护理操作、手术台次、医技项目 |

### 专科医院特点

- **眼科医院**：眼科相关科室工作量占80%以上
- **心血管医院**：心血管相关科室工作量占80%以上
- **肿瘤医院**：肿瘤相关科室工作量占80%以上
- **妇幼医院**：妇产科、儿科工作量占80%以上

### 综合医院特点

- 各科室工作量相对均衡
- 内科、外科、妇产科等主要科室工作量较大
- 医技科室工作量根据检查需求分配

## 常见问题

### 1. API调用失败

**问题**：提示"未提供API密钥"或"API调用失败"

**解决**：
- 检查API密钥是否正确设置
- 检查网络连接是否正常
- 检查API端点是否可访问

### 2. 数据不合理

**问题**：生成的数据不符合业务逻辑

**解决**：
- 检查配置文件中的医院信息和科室特点是否准确
- 检查科室的业务约束是否完整
- 调整提示词模板，增加更多业务规则说明
- 使用更强大的模型（如GPT-4）

### 3. 比例不等于100%

**问题**：AI返回的比例之和不等于100%

**解决**：
- 在提示词中强调"所有比例之和必须等于100%"
- 增加后处理逻辑，自动调整比例使其和为100%
- 重新运行脚本，AI通常会自我纠正

### 4. 科室未找到

**问题**：提示"未找到配置中的科室"

**解决**：
- 确保配置文件中的科室代码与数据库中的科室代码一致
- 确保数据库中的科室已启用（is_active=True）
- 检查科室是否已导入到数据库

## 性能优化

### 1. 批量处理

如果科室数量较多，可以考虑：
- 分批处理科室
- 使用异步API调用
- 缓存AI响应结果

### 2. 成本控制

- 使用较便宜的模型（如gpt-3.5-turbo）进行测试
- 只在需要高质量结果时使用GPT-4
- 合理设置max_tokens参数

### 3. 结果缓存

- 保存AI响应结果到文件
- 相同配置可以复用之前的结果
- 只在配置变化时重新调用AI

## 扩展功能

### 1. 数据验证

可以添加验证步骤，使用AI检查生成的数据是否合理：

```python
# 在生成数据后调用验证
validation_result = ai_generator.validate_data(config, allocations)
if not validation_result['is_valid']:
    print("数据验证失败:", validation_result['errors'])
```

### 2. 多轮优化

可以实现多轮对话，让AI根据反馈优化分配：

```python
# 第一轮生成
allocations = ai_generator.allocate_departments(config)

# 检查并提供反馈
feedback = check_allocations(allocations)

# 第二轮优化
improved_allocations = ai_generator.improve_allocations(allocations, feedback)
```

### 3. 历史数据学习

可以让AI学习历史数据，生成更符合实际的数据：

```python
# 提供历史数据作为参考
historical_data = load_historical_data(period="2024-10")
allocations = ai_generator.allocate_with_reference(config, historical_data)
```

## 总结

AI智能数据生成工具能够：
- ✅ 根据医院特点智能分配工作量
- ✅ 确保数据符合业务逻辑
- ✅ 大幅减少手工配置工作
- ✅ 生成更真实的测试数据

建议：
- 首次使用时仔细配置医院和科室信息
- 使用GPT-4获得更好的结果
- 根据实际情况调整提示词模板
- 生成后检查数据合理性
