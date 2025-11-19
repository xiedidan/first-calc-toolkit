# AI智能数据生成系统

## 📋 快速导航

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [快速开始](AI_DATA_GENERATION_QUICKSTART.md) | 5分钟快速上手 | 新用户 |
| [完整指南](AI_DATA_GENERATION_GUIDE.md) | 详细使用说明 | 所有用户 |
| [实现总结](AI_DATA_GENERATION_SUMMARY.md) | 技术实现细节 | 开发者 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install openai
```

### 2. 设置API密钥

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

### 3. 生成数据

```bash
# 使用眼科医院示例
python populate_report_data_ai.py --config report_data_config.example.json --period 2025-10

# 使用综合医院示例
python populate_report_data_ai.py --config report_data_config_comprehensive.example.json --period 2025-10

# Windows用户可以使用批处理脚本
generate_ai_data.bat report_data_config.example.json 2025-10
```

## 📁 文件说明

### 核心程序

- **populate_report_data_ai.py** - AI智能数据生成主程序
- **populate_report_data.py** - 原始随机数据生成程序（保留）

### 配置文件

- **report_data_config.example.json** - 眼科医院配置示例
- **report_data_config_comprehensive.example.json** - 综合医院配置示例
- **ai_prompts.json** - AI提示词配置（可自定义）

### 工具脚本

- **validate_config.py** - 配置文件验证工具
- **test_ai_generation.py** - 功能测试脚本
- **generate_ai_data.bat** - Windows批处理脚本

### 文档

- **AI_DATA_GENERATION_QUICKSTART.md** - 快速开始指南
- **AI_DATA_GENERATION_GUIDE.md** - 完整使用指南
- **AI_DATA_GENERATION_SUMMARY.md** - 实现总结文档
- **README_AI_GENERATION.md** - 本文档

## 🎯 核心功能

### 1. 智能科室分配

AI根据医院特点，自动分配各科室的工作量比例：

```
医院信息 + 总工作量 → AI分析 → 各科室工作量比例
```

### 2. 智能维度分配

AI根据科室业务特点，自动分配各维度的工作量：

```
科室信息 + 科室工作量 → AI分析 → 各维度工作量
```

### 3. 自动计算

自动计算价值、占比和汇总数据：

```
工作量 × 权重 = 价值
价值 / 总价值 = 占比
```

## 💡 使用场景

### 场景1: 眼科专科医院

```bash
# 使用眼科医院配置
python populate_report_data_ai.py --config report_data_config.example.json --period 2025-10
```

特点：
- 眼科科室工作量占主导（80%+）
- 手术集中在眼科手术室
- 护理集中在眼科病区

### 场景2: 综合医院

```bash
# 使用综合医院配置
python populate_report_data_ai.py --config report_data_config_comprehensive.example.json --period 2025-10
```

特点：
- 各科室工作量相对均衡
- 内科、外科、妇产科等主要科室工作量较大
- 医技科室根据检查需求分配

### 场景3: 自定义医院

```bash
# 1. 复制示例配置
copy report_data_config.example.json my_hospital.json

# 2. 编辑配置文件（修改医院信息、科室列表等）

# 3. 验证配置
python validate_config.py my_hospital.json

# 4. 生成数据
python populate_report_data_ai.py --config my_hospital.json --period 2025-10
```

## 🔧 常用命令

### 验证配置文件

```bash
python validate_config.py my_config.json
```

### 测试功能

```bash
python test_ai_generation.py
```

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

## 📊 业务规则

### 科室类别规则

| 科室类别 | 主要工作量 | 应为0的工作量 |
|---------|-----------|-------------|
| 医生专科 | 门诊、住院、治疗手术、会诊、MDT、病案 | 护理操作、手术台次、医技项目 |
| 护理病区 | 床日护理、护理操作 | 医生诊疗、手术台次、医技项目 |
| 手术室 | 手术室护理 | 医生诊疗、床日护理、医技项目 |
| 医技科室 | 对应医技项目 | 医生诊疗、护理操作、手术台次 |

### 医院类型规则

**专科医院：**
- 专科相关科室工作量占80%以上
- 手术集中在专科手术室
- 护理集中在专科病区

**综合医院：**
- 各科室工作量相对均衡
- 主要科室工作量较大
- 医技科室根据需求分配

## ⚠️ 注意事项

### API成本

- **GPT-3.5-turbo**：约$0.18/20科室（推荐测试用）
- **GPT-4**：约$4.80/20科室（推荐生产用）

### 数据质量

- 配置文件质量直接影响生成结果
- 建议详细描述医院和科室特点
- 建议明确业务约束条件

### 网络要求

- 需要稳定的网络连接
- 需要能访问OpenAI API
- 可使用代理或自定义端点

## 🐛 故障排除

### 问题1: API密钥错误

```
❌ 错误: 未提供API密钥
```

**解决：** 设置环境变量或使用 `--api-key` 参数

### 问题2: 配置文件格式错误

```
❌ 错误: 配置文件格式错误
```

**解决：** 运行 `python validate_config.py my_config.json` 检查

### 问题3: 科室未找到

```
❌ 错误: 未找到配置中的科室
```

**解决：** 确保配置文件中的科室代码与数据库一致

### 问题4: 数据不合理

**解决：**
- 检查配置文件中的医院信息和科室特点
- 使用GPT-4获得更好的结果
- 调整 `ai_prompts.json` 中的提示词

## 📚 更多资源

- [快速开始指南](AI_DATA_GENERATION_QUICKSTART.md) - 5分钟快速上手
- [完整使用指南](AI_DATA_GENERATION_GUIDE.md) - 详细的使用说明
- [实现总结文档](AI_DATA_GENERATION_SUMMARY.md) - 技术实现细节
- [原始数据生成指南](POPULATE_REPORT_DATA_GUIDE.md) - 随机数据生成方法

## 🤝 技术支持

如有问题或建议：
1. 查看文档中的故障排除部分
2. 运行 `python test_ai_generation.py` 诊断问题
3. 检查配置文件格式
4. 联系技术支持团队

## 📝 版本历史

- **v1.0** - 初始版本
  - 支持AI智能数据生成
  - 支持眼科和综合医院配置
  - 提供完整的文档和工具

## 🎉 开始使用

现在就开始使用AI智能数据生成系统吧！

```bash
# 1. 安装依赖
pip install openai

# 2. 设置API密钥
set OPENAI_API_KEY=your_key

# 3. 生成数据
python populate_report_data_ai.py --config report_data_config.example.json --period 2025-10
```

祝使用愉快！🚀
