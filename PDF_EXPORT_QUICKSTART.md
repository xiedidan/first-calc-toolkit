# PDF导出功能快速开始

## 快速安装

```bash
# 激活环境并安装依赖
cd backend
pip install reportlab==4.0.7
```

## 验证安装

```bash
python -c "from app.services.orientation_rule_service import OrientationRuleService; print('✓ 安装成功')"
```

## 使用方法

### 前端使用

1. 点击导向规则列表中的"导出"按钮
2. 选择"导出为PDF"或"导出为Markdown"
3. 文件自动下载

### API调用

```bash
# 导出PDF
curl "http://localhost:8000/api/v1/orientation-rules/1/export?format=pdf" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  --output "导向规则.pdf"

# 导出Markdown
curl "http://localhost:8000/api/v1/orientation-rules/1/export?format=markdown" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  --output "导向规则.md"
```

## 测试

```bash
# 运行测试脚本
python test_orientation_export_pdf.py
```

## 技术栈

- **ReportLab**: 纯Python PDF生成库
- **中文字体**: Windows系统自带宋体
- **无需外部依赖**: 不需要GTK等系统库

## 已实现功能

✅ 后端PDF生成
✅ API端点支持format参数
✅ 前端下拉菜单UI
✅ 中文字体支持
✅ 专业表格样式
✅ A4页面布局

## 文件清单

- `backend/app/services/orientation_rule_service.py` - PDF生成逻辑
- `backend/app/api/orientation_rules.py` - API端点
- `frontend/src/views/OrientationRules.vue` - 前端UI
- `backend/requirements.txt` - 依赖配置
- `test_orientation_export_pdf.py` - 测试脚本
- `PDF_EXPORT_IMPLEMENTATION.md` - 详细文档

## 下一步

如需为其他功能添加PDF导出，参考 `PDF_EXPORT_IMPLEMENTATION.md` 中的扩展指南。
