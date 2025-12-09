# PDF导出功能实现文档

## 概述

为系统中所有markdown导出功能添加PDF导出能力，用户可以选择导出为Markdown或PDF格式。

## 实现日期
2025-12-01

## 技术方案

### 1. PDF生成库选择

使用 **ReportLab** 库：
- `reportlab`: 纯Python实现的PDF生成库，无需外部依赖
- 支持中文字体（使用Windows系统自带的宋体）
- 跨平台兼容性好

**为什么选择ReportLab而不是WeasyPrint？**
- WeasyPrint在Windows上需要GTK库等外部依赖，安装复杂
- ReportLab是纯Python实现，安装简单，无需额外配置
- ReportLab对中文支持更好，可以直接使用系统字体

### 2. 依赖安装

在 `backend/requirements.txt` 中添加：
```
markdown==3.5.1
reportlab==4.0.7
```

安装命令：
```bash
pip install markdown==3.5.1 reportlab==4.0.7
```

## 实现内容

### 1. 后端服务层实现

**文件**: `backend/app/services/orientation_rule_service.py`

#### 新增方法

##### `export_rule_pdf(db, rule_id, hospital_id)`
导出导向规则为PDF文件。

**功能**:
1. 查询导向规则并验证权限
2. 使用ReportLab创建PDF文档
3. 注册中文字体（使用Windows系统自带的宋体）
4. 创建样式（标题、正文、表格）
5. 构建PDF内容（标题、基本信息表、基准表、阶梯表）
6. 返回PDF文件流和文件名

**PDF样式特性**:
- A4页面大小，2cm边距
- 中文字体支持（SimSun宋体）
- 表格样式：边框、斑马纹、蓝色表头
- 标题居中显示
- 专业的表格布局

### 2. API层实现

**文件**: `backend/app/api/orientation_rules.py`

#### 修改端点

```
GET /api/v1/orientation-rules/{rule_id}/export?format={format}
```

**新增参数**:
- `format`: 导出格式，可选值 `markdown` 或 `pdf`，默认 `markdown`

**响应**:
- Markdown格式: `Content-Type: text/markdown`
- PDF格式: `Content-Type: application/pdf`

### 3. 前端实现

**文件**: `frontend/src/views/OrientationRules.vue`

#### UI改进

将原来的"导出"按钮改为下拉菜单：
```vue
<el-dropdown @command="(cmd) => handleExport(row, cmd)">
  <el-button link type="info">
    导出<el-icon class="el-icon--right"><arrow-down /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="markdown">导出为Markdown</el-dropdown-item>
      <el-dropdown-item command="pdf">导出为PDF</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

#### 功能实现

修改 `handleExport` 方法：
- 接收 `format` 参数（`'markdown'` 或 `'pdf'`）
- 根据格式设置正确的MIME类型和文件扩展名
- 调用API时传递 `format` 参数
- 显示对应的成功消息

## PDF样式设计

### 页面设置
- 纸张大小: A4
- 页边距: 2cm
- 字体: SimSun（宋体）, Microsoft YaHei（微软雅黑）
- 字号: 12pt
- 行高: 1.6

### 元素样式

#### 标题
- H1: 深蓝色，底部2px蓝色边框
- H2: 深灰色，底部1px灰色边框

#### 表格
- 全宽度，边框合并
- 表头: 蓝色背景，白色文字
- 单元格: 8px内边距
- 斑马纹: 偶数行浅灰色背景

#### 列表
- 无序列表样式
- 左对齐，无缩进

## 使用示例

### Python代码

```python
from app.services.orientation_rule_service import OrientationRuleService

# 导出Markdown
buffer, filename = OrientationRuleService.export_rule(db, rule_id=1, hospital_id=1)

# 导出PDF
buffer, filename = OrientationRuleService.export_rule_pdf(db, rule_id=1, hospital_id=1)
```

### API调用

```bash
# 导出Markdown
curl -X GET "http://localhost:8000/api/v1/orientation-rules/1/export?format=markdown" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  --output "导向规则.md"

# 导出PDF
curl -X GET "http://localhost:8000/api/v1/orientation-rules/1/export?format=pdf" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  --output "导向规则.pdf"
```

### JavaScript (前端)

```javascript
async function exportOrientationRule(ruleId, format = 'markdown') {
  const response = await fetch(
    `/api/v1/orientation-rules/${ruleId}/export?format=${format}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Hospital-ID': hospitalId
      }
    }
  );
  
  if (response.ok) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `导向规则_${Date.now()}.${format === 'pdf' ? 'pdf' : 'md'}`;
    a.click();
    URL.revokeObjectURL(url);
  }
}
```

## 测试

### 测试脚本

**文件**: `test_orientation_export_pdf.py`

测试用例：
1. ✅ 登录获取token
2. ✅ 创建测试导向规则
3. ✅ 导出Markdown格式
4. ✅ 导出PDF格式
5. ✅ 验证Content-Type
6. ✅ 验证PDF文件格式
7. ✅ 清理测试数据

运行测试：
```bash
python test_orientation_export_pdf.py
```

## 扩展到其他功能

如果系统中有其他markdown导出功能，可以按照相同模式扩展：

### 1. 服务层添加PDF导出方法

```python
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

@staticmethod
def export_xxx_pdf(db: Session, xxx_id: int, hospital_id: int) -> tuple[BytesIO, str]:
    # 1. 查询数据
    xxx = query_xxx(db, xxx_id, hospital_id)
    
    # 2. 创建PDF文档
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 3. 注册中文字体
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        font_name = 'SimSun'
    except:
        font_name = 'Helvetica'  # 回退到默认字体
    
    # 4. 创建样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # 5. 构建PDF内容
    story = []
    story.append(Paragraph(xxx.name, title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 添加表格
    data = [['字段', '值'], ['名称', xxx.name], ...]
    table = Table(data, colWidths=[4*cm, 12*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    
    # 6. 生成PDF
    doc.build(story)
    buffer.seek(0)
    
    # 7. 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{xxx.name}_{timestamp}.pdf"
    
    return buffer, filename
```

### 2. API层添加format参数

```python
@router.get("/{xxx_id}/export")
def export_xxx(
    xxx_id: int,
    format: str = Query("markdown", description="导出格式: markdown 或 pdf"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    hospital_id = get_current_hospital_id_or_raise()
    
    if format.lower() == "pdf":
        buffer, filename = XxxService.export_xxx_pdf(db, xxx_id, hospital_id)
        media_type = "application/pdf"
    else:
        buffer, filename = XxxService.export_xxx(db, xxx_id, hospital_id)
        media_type = "text/markdown"
    
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )
```

### 3. 前端添加下拉菜单

```vue
<el-dropdown @command="(cmd) => handleExport(row, cmd)">
  <el-button link type="info">
    导出<el-icon class="el-icon--right"><arrow-down /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="markdown">导出为Markdown</el-dropdown-item>
      <el-dropdown-item command="pdf">导出为PDF</el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

## 注意事项

### 1. 中文字体支持

ReportLab使用系统字体：
- Windows: 自动使用 `C:/Windows/Fonts/simsun.ttc`（宋体）
- Linux: 需要安装中文字体并指定路径
  ```bash
  apt-get install fonts-wqy-microhei fonts-wqy-zenhei
  ```
  然后在代码中指定字体路径：`/usr/share/fonts/truetype/wqy/wqy-microhei.ttc`
- Docker: 在Dockerfile中添加字体安装
  ```dockerfile
  RUN apt-get update && apt-get install -y fonts-wqy-microhei
  ```

### 2. 性能考虑

- PDF生成比Markdown慢，适合小到中等规模文档
- 大文档建议分页或异步生成
- 可以添加缓存机制

### 3. 错误处理

- 捕获PDF生成异常
- 提供友好的错误消息
- 记录详细日志便于调试

### 4. 样式定制

可以根据需求调整CSS样式：
- 修改颜色主题
- 调整字体大小
- 添加页眉页脚
- 添加水印

## 部署清单

### 开发环境
- [x] 安装依赖: `pip install markdown weasyprint`
- [x] 修改服务层代码
- [x] 修改API层代码
- [x] 修改前端代码
- [x] 本地测试

### 生产环境
- [ ] 更新requirements.txt
- [ ] 安装系统字体（Linux）
- [ ] 更新Docker镜像
- [ ] 部署后端服务
- [ ] 部署前端代码
- [ ] 生产环境测试

## 总结

PDF导出功能已完整实现，包括：
- ✅ 后端PDF生成逻辑
- ✅ API端点format参数支持
- ✅ 前端下拉菜单UI
- ✅ 中文字体和样式支持
- ✅ 测试脚本
- ✅ 扩展指南

用户现在可以选择导出为Markdown或PDF格式，PDF文档具有专业的排版和样式。

## 后续优化

1. 添加PDF模板系统，支持自定义样式
2. 支持批量导出多个规则为单个PDF
3. 添加PDF书签和目录
4. 支持PDF加密和权限控制
5. 添加导出历史记录
6. 支持异步生成大文档
