# AI智能数据生成快速开始

## 5分钟快速上手

### 步骤1: 安装依赖

```bash
pip install openai
```

### 步骤2: 设置API密钥

**Windows:**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

### 步骤3: 准备配置文件

复制示例配置文件：
```bash
# 眼科医院示例
copy report_data_config.example.json my_config.json

# 综合医院示例
copy report_data_config_comprehensive.example.json my_config.json
```

### 步骤4: 验证配置文件

```bash
python validate_config.py my_config.json
```

### 步骤5: 生成数据

```bash
python populate_report_data_ai.py --config my_config.json --period 2025-10
```

## 完整示例

### DeepSeek API示例（推荐，性价比高）

```bash
# 1. 设置API密钥
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# 2. 使用DeepSeek配置
python populate_report_data_ai.py --config report_data_config_deepseek.example.json --period 2025-10

# 3. 查看生成的数据
# 启动后端服务，访问前端报表页面
```

### OpenAI API示例

```bash
# 1. 设置API密钥
set OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# 2. 使用OpenAI配置
python populate_report_data_ai.py --config report_data_config.example.json --period 2025-10

# 3. 查看生成的数据
```

### 综合医院示例

```bash
# 1. 设置API密钥（根据配置文件中的设置）
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# 2. 使用综合医院配置
python populate_report_data_ai.py --config report_data_config_comprehensive.example.json --period 2025-10

# 3. 查看生成的数据
```

## 常用命令

### 使用GPT-4（更准确）

```bash
python populate_report_data_ai.py --config my_config.json --period 2025-10 --model gpt-4
```

### 使用自定义API端点

```bash
python populate_report_data_ai.py --config my_config.json --period 2025-10 --base-url https://api.example.com/v1
```

### 不清理现有数据

```bash
python populate_report_data_ai.py --config my_config.json --period 2025-10 --no-clean
```

### 指定模型版本

```bash
python populate_report_data_ai.py --config my_config.json --period 2025-10 --model-version-id 1
```

## 配置文件模板

### 最小配置

```json
{
  "hospital_info": {
    "name": "某某医院",
    "type": "综合医院",
    "specialty": "综合",
    "description": "医院描述",
    "characteristics": ["特点1", "特点2"]
  },
  "total_workload": {
    "workload_based_total": {"value": 1000000, "description": "工作量总额", "note": "备注"},
    "consultation_total": {"value": 500, "description": "会诊总数", "note": "备注"},
    "mdt_total": {"value": 100, "description": "MDT总数", "note": "备注"},
    "case_total": {"value": 3000, "description": "病案总数", "note": "备注"},
    "nursing_bed_days_total": {"value": 15000, "description": "床日总数", "note": "备注"},
    "surgery_total": {"value": 2000, "description": "手术总台次", "note": "备注"},
    "observation_total": {"value": 800, "description": "留观总数", "note": "备注"}
  },
  "departments": [
    {
      "his_code": "01",
      "his_name": "科室名称",
      "category": "医生专科",
      "business_characteristics": "业务特点",
      "constraints": ["约束1", "约束2"]
    }
  ]
}
```

## 输出示例

```
======================================================================
基于AI的业务价值报表数据智能生成
======================================================================
计算周期: 2025-10
医院名称: 某某眼科医院
医院类型: 专科医院
======================================================================

✓ AI模型初始化完成: gpt-3.5-turbo

清理周期 2025-10 的现有数据...
  删除 1 个任务
  删除 150 条计算结果
  删除 8 条汇总数据

使用模型版本: 默认模型 (ID: 1)
找到 8 个配置的科室
找到 3 个序列节点
找到 15 个维度节点

======================================================================
步骤1: AI分配各科室工作量比例
======================================================================
正在调用AI模型进行科室工作量分配...
正在解析AI响应...
  01 - 白内障科
    工作量: 35.0%
    会诊: 20.0%
    MDT: 15.0%
    病案: 40.0%
    床日: 0.0%
    手术: 0.0%
    留观: 0.0%
    理由: 白内障科是眼科主要专科，工作量占比最大
  ...

✓ 完成 8 个科室的工作量分配

======================================================================
步骤2: 为各科室生成维度数据
======================================================================

[1/8] 01 - 白内障科

为科室 01 - 白内障科 分配维度工作量...
  正在调用AI模型进行维度工作量分配...
  正在解析AI响应...
    门诊诊察: 工作量=50000
    住院床日: 工作量=30000
    医生治疗手术: 工作量=20000
    ...
  ✓ 完成 15 个维度的工作量分配
  ✓ 科室 白内障科 数据生成完成

...

======================================================================
步骤3: 生成汇总数据
======================================================================
[1/8] 01 - 白内障科
  医生=150000, 护理=0, 医技=0, 总计=150000
...

======================================================================
✅ AI智能数据生成完成!
======================================================================
任务ID: report-ai-2025-10-20251031120000
计算周期: 2025-10
模型版本: 默认模型
科室数量: 8
计算结果总数: 128
汇总记录数: 8
======================================================================

💡 下一步:
1. 启动后端服务查看数据
2. 访问前端报表页面验证
3. 检查汇总表和明细表数据
```

## 故障排除

### 问题1: API密钥错误

```
❌ 错误: 未提供API密钥
```

**解决方法:**
- 检查环境变量是否设置正确
- 或使用 `--api-key` 参数提供密钥

### 问题2: 配置文件格式错误

```
❌ 错误: 配置文件格式错误: Expecting property name enclosed in double quotes
```

**解决方法:**
- 运行 `python validate_config.py my_config.json` 检查配置
- 确保JSON格式正确（注意逗号、引号等）

### 问题3: 科室未找到

```
❌ 错误: 未找到配置中的科室
```

**解决方法:**
- 确保配置文件中的科室代码与数据库中的科室代码一致
- 确保数据库中的科室已启用（is_active=True）

### 问题4: AI返回格式错误

```
❌ JSON解析失败: Expecting value
```

**解决方法:**
- 检查网络连接
- 尝试使用更稳定的模型（如gpt-4）
- 检查提示词是否过长

### 问题5: 数据不合理

**解决方法:**
- 检查配置文件中的医院信息和科室特点是否准确
- 增加更详细的业务约束
- 调整 `ai_prompts.json` 中的提示词
- 使用GPT-4获得更好的结果

## 进阶使用

### 自定义提示词

编辑 `ai_prompts.json` 文件，修改提示词模板：

```json
{
  "department_allocation_prompt": {
    "system": "你是一个医院业务数据分析专家...",
    "user_template": "请根据以下医院信息..."
  }
}
```

### 批量生成多个周期

```bash
# 生成多个月份的数据
for /L %m in (1,1,12) do (
  python populate_report_data_ai.py --config my_config.json --period 2025-%m --no-clean
)
```

### 使用不同的AI服务

```bash
# 使用Azure OpenAI
python populate_report_data_ai.py --config my_config.json --period 2025-10 ^
  --base-url https://your-resource.openai.azure.com/openai/deployments/your-deployment ^
  --api-key your_azure_key

# 使用其他兼容OpenAI API的服务
python populate_report_data_ai.py --config my_config.json --period 2025-10 ^
  --base-url https://api.example.com/v1 ^
  --api-key your_key
```

## 性能优化建议

1. **使用gpt-3.5-turbo进行测试**（速度快，成本低）
2. **使用gpt-4进行生产**（质量高，更准确）
3. **合理设置科室数量**（建议每次不超过50个科室）
4. **保存AI响应结果**（避免重复调用）
5. **使用批处理**（大量数据分批生成）

## 成本估算

### GPT-3.5-turbo

- 每个科室约消耗 2000 tokens
- 20个科室约 40000 tokens
- 成本约 $0.06（输入）+ $0.12（输出）= $0.18

### GPT-4

- 每个科室约消耗 2000 tokens
- 20个科室约 40000 tokens
- 成本约 $1.20（输入）+ $3.60（输出）= $4.80

## 下一步

- 查看完整文档：`AI_DATA_GENERATION_GUIDE.md`
- 了解配置文件格式：查看示例配置文件
- 自定义提示词：编辑 `ai_prompts.json`
- 验证生成的数据：启动后端服务查看报表
