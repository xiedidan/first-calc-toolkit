# 汇总表导出功能使用指南

## 功能概述

实现了全院业务价值汇总表的Excel导出功能，支持同步下载，完美还原页面展示效果。

## 功能特点

### 1. Excel格式
- ✅ 标准Excel格式（.xlsx）
- ✅ 单Sheet展示
- ✅ 专业的表格样式
- ✅ 支持二次编辑和分析

### 2. 表格结构
```
标题行：科室业务价值汇总（2025-10）
├─ 表头（两层）
│  ├─ 第一层：科室 | 医生序列 | 护理序列 | 医技序列 | 科室总价值
│  └─ 第二层：价值/占比（每个序列）
├─ 全院汇总行（高亮显示）
└─ 各科室数据行
```

### 3. 样式特点
- **标题行**：14号字体，加粗，居中，合并单元格
- **表头**：白色字体，蓝色背景，加粗，居中
- **全院汇总**：加粗字体，灰色背景
- **数据格式**：
  - 价值列：千分位，2位小数（如：1,500,000.50）
  - 占比列：百分比格式（如：45.50%）
- **边框**：所有单元格有边框
- **对齐**：科室名称左对齐，数值右对齐，占比居中

## 使用方法

### 前端使用

1. 访问"评估结果"页面
2. 选择评估月份和模型版本
3. 点击"导出汇总表"按钮
4. 浏览器自动下载Excel文件

### API调用

**接口地址**：`GET /calculation/results/export/summary`

**请求参数**：
```
period: 评估月份（必填，格式：YYYY-MM）
model_version_id: 模型版本ID（可选，不填则使用激活版本）
```

**响应**：
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 文件名：`科室业务价值汇总_2025-10.xlsx`

**示例**：
```bash
curl -X GET "http://localhost:8000/calculation/results/export/summary?period=2025-10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output 汇总表.xlsx
```

## 测试方法

### 方法一：使用测试脚本

```bash
# 运行批处理脚本
test-export-summary.bat

# 或直接运行Python脚本
python backend/test_export_summary.py
```

测试脚本会：
1. 生成模拟数据（3个科室）
2. 创建Excel文件
3. 保存到项目根目录
4. 显示文件路径和大小

### 方法二：通过前端测试

1. 确保已有计算结果数据
2. 启动后端服务：`uvicorn app.main:app --reload`
3. 启动前端服务：`npm run dev`
4. 访问评估结果页面
5. 点击"导出汇总表"按钮

### 方法三：使用API测试工具

使用Postman或curl测试API接口：

```bash
# 获取token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 导出汇总表
curl -X GET "http://localhost:8000/calculation/results/export/summary?period=2025-10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output 汇总表.xlsx
```

## 验证清单

打开生成的Excel文件，检查以下内容：

### 1. 标题和表头
- [ ] 标题行显示正确：科室业务价值汇总（YYYY-MM）
- [ ] 标题行合并单元格，居中显示
- [ ] 表头有两层，序列分组正确
- [ ] 表头背景色为蓝色，字体为白色

### 2. 数据内容
- [ ] 第一行是"全院汇总"
- [ ] 全院汇总行加粗，背景色为灰色
- [ ] 各科室数据按顺序显示
- [ ] 所有数据都有值，无空白

### 3. 数据格式
- [ ] 价值列显示千分位（如：1,500,000.50）
- [ ] 价值列保留2位小数
- [ ] 占比列显示为百分比（如：45.50%）
- [ ] 占比列保留2位小数

### 4. 样式和布局
- [ ] 所有单元格有边框
- [ ] 科室名称左对齐
- [ ] 价值列右对齐
- [ ] 占比列居中对齐
- [ ] 列宽适中，内容不被截断

### 5. 数据准确性
- [ ] 全院汇总 = 各科室总和
- [ ] 每个科室的总价值 = 三个序列之和
- [ ] 每个科室的三个序列占比之和 = 100%

## 技术实现

### 核心文件

1. **backend/app/services/export_service.py**
   - ExportService类
   - export_summary_to_excel方法
   - 使用openpyxl库生成Excel

2. **backend/app/api/calculation_tasks.py**
   - export_summary接口
   - 查询汇总数据
   - 调用ExportService生成Excel
   - 返回StreamingResponse

3. **frontend/src/views/Results.vue**
   - exportSummary方法
   - 使用axios下载文件（responseType: 'blob'）
   - 创建下载链接触发下载

### 关键技术点

#### 1. Excel样式设置

```python
# 字体
Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')

# 填充色
PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

# 对齐
Alignment(horizontal='center', vertical='center')

# 边框
Border(left=Side(style='thin'), right=Side(style='thin'), ...)
```

#### 2. 数字格式化

```python
# 千分位，2位小数
cell.number_format = '#,##0.00'

# 百分比
cell.number_format = '0.00%'
```

#### 3. 合并单元格

```python
ws.merge_cells('A1:H1')  # 标题行
ws.merge_cells('B2:C2')  # 序列分组
```

#### 4. 文件下载

```python
# 后端：返回StreamingResponse
return StreamingResponse(
    excel_file,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
)

# 前端：使用Blob下载
const url = window.URL.createObjectURL(new Blob([response]))
const link = document.createElement('a')
link.href = url
link.setAttribute('download', filename)
link.click()
```

## 常见问题

### Q1: 下载的文件打不开

**原因**：文件损坏或格式不正确

**解决方法**：
1. 检查后端是否正常生成Excel
2. 检查前端responseType是否设置为'blob'
3. 查看浏览器控制台是否有错误

### Q2: 中文文件名乱码

**原因**：文件名编码问题

**解决方法**：
- 后端使用UTF-8编码：`filename*=UTF-8''文件名.xlsx`
- 前端正确处理文件名

### Q3: 数据格式不正确

**原因**：数字格式设置错误

**解决方法**：
- 检查number_format设置
- 确保数据类型正确（float而非Decimal）

### Q4: 样式不生效

**原因**：样式对象未正确应用

**解决方法**：
- 确保每个单元格都设置了样式
- 检查样式对象的属性是否正确

## 性能考虑

### 当前实现（同步）
- **优点**：实现简单，立即下载
- **缺点**：大数据量时可能超时
- **适用场景**：科室数量 < 100

### 未来优化（异步）
如果需要支持大数据量导出：
1. 使用Celery异步任务
2. 生成文件后保存到服务器
3. 返回下载链接
4. 支持导出进度查询

## 下一步计划

### 1. 明细表导出
- 支持全院明细导出
- 支持单科室明细导出
- 多Sheet展示（按序列分Sheet）
- 树形结构用缩进表示

### 2. 导出选项
- 选择导出科室范围
- 选择导出序列
- 自定义文件名

### 3. 模板管理
- 支持自定义Excel模板
- 支持多种报表格式
- 模板参数配置

### 4. 批量导出
- 导出多个月份的数据
- 导出对比报表
- 打包下载

## 相关文件

### 新增文件
```
backend/app/services/export_service.py    # 导出服务
backend/test_export_summary.py            # 测试脚本
test-export-summary.bat                   # 批处理脚本
EXPORT_SUMMARY_GUIDE.md                   # 本文档
```

### 修改文件
```
backend/app/api/calculation_tasks.py      # 导出接口
frontend/src/views/Results.vue            # 前端导出逻辑
```

## 总结

全院汇总表导出功能已完成，主要特点：

1. ✅ **同步下载** - 点击即下载，无需等待
2. ✅ **专业样式** - 完美还原页面展示效果
3. ✅ **数据准确** - 复用现有汇总逻辑，确保一致性
4. ✅ **易于使用** - 一键导出，自动命名
5. ✅ **可扩展** - 代码结构清晰，易于添加新功能

现在可以在实际环境中测试和使用了！
