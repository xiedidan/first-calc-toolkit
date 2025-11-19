# 中文文件名编码问题修复

## 问题描述

导出功能在实际测试中遇到错误：

```
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 29-36: ordinal not in range(256)
```

**原因**：HTTP头中的 `Content-Disposition` 使用 latin-1 编码，无法直接处理中文字符。

## 解决方案

使用URL编码（percent-encoding）处理中文文件名。

### 修改前
```python
filename = f"科室业务价值汇总_{period}.xlsx"

return StreamingResponse(
    excel_file,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"
    }
)
```

### 修改后
```python
from urllib.parse import quote

filename = f"科室业务价值汇总_{period}.xlsx"
encoded_filename = quote(filename)

return StreamingResponse(
    excel_file,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        "Access-Control-Expose-Headers": "Content-Disposition"
    }
)
```

## 编码示例

```python
原始文件名: 科室业务价值汇总_2025-10.xlsx
编码后: %E7%A7%91%E5%AE%A4%E4%B8%9A%E5%8A%A1%E4%BB%B7%E5%80%BC%E6%B1%87%E6%80%BB_2025-10.xlsx
```

## 技术说明

### RFC 2231标准

使用 `filename*=UTF-8''encoded_filename` 格式符合 RFC 2231 标准：
- `filename*` - 表示使用扩展格式
- `UTF-8` - 字符集
- `''` - 语言标签（空表示无特定语言）
- `encoded_filename` - URL编码的文件名

### 浏览器兼容性

这种方式被所有现代浏览器支持：
- ✅ Chrome
- ✅ Firefox
- ✅ Edge
- ✅ Safari

## 测试验证

### 测试脚本
```bash
python backend/test_export_api.py
```

### 测试结果
```
原始文件名: 科室业务价值汇总_2025-10.xlsx
编码后: %E7%A7%91%E5%AE%A4%E4%B8%9A%E5%8A%A1%E4%BB%B7%E5%80%BC%E6%B1%87%E6%80%BB_2025-10.xlsx

Content-Disposition header:
attachment; filename*=UTF-8''%E7%A7%91%E5%AE%A4%E4%B8%9A%E5%8A%A1%E4%BB%B7%E5%80%BC%E6%B1%87%E6%80%BB_2025-10.xlsx
```

### 实际测试
1. 启动后端服务
2. 访问前端页面
3. 点击"导出汇总表"
4. ✅ 文件正常下载
5. ✅ 文件名显示正确：`科室业务价值汇总_2025-10.xlsx`

## 相关文件

- `backend/app/api/calculation_tasks.py` - 修复的导出接口
- `backend/test_export_api.py` - 测试脚本

## 参考资料

- [RFC 2231 - MIME Parameter Value and Encoded Word Extensions](https://tools.ietf.org/html/rfc2231)
- [MDN - Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition)

## 总结

通过使用URL编码处理中文文件名，成功解决了HTTP头编码问题。现在导出功能可以正常使用，文件名正确显示中文。
