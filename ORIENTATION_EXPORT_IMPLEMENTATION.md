# 导向规则导出功能实现文档

## 概述

导向规则导出功能允许用户将导向规则及其关联数据导出为 Markdown 格式的文档，便于文档化管理和分享。

## 实现内容

### 1. 服务层实现

**文件**: `backend/app/services/orientation_rule_service.py`

#### 新增方法

##### `export_rule(db, rule_id, hospital_id)`
导出导向规则为 Markdown 文件。

**参数**:
- `db`: 数据库会话
- `rule_id`: 导向规则ID
- `hospital_id`: 当前医疗机构ID

**返回**: `(BytesIO对象, 文件名)` 元组

**功能**:
- 查询导向规则并验证权限
- 生成 Markdown 内容
- 生成文件名（格式：`{导向名称}_{时间戳}.md`）
- 返回文件流和文件名

##### `_generate_markdown(rule)`
生成导向规则的 Markdown 内容（私有方法）。

**参数**:
- `rule`: 导向规则对象

**返回**: Markdown 格式的字符串

**功能**:
- 生成基本信息（名称、类别、描述、时间）
- 根据导向类别包含关联数据：
  - `benchmark_ladder`: 包含导向基准和导向阶梯
  - `direct_ladder`: 仅包含导向阶梯
  - `other`: 不包含关联数据
- 格式化数值为4位小数
- 处理无穷值（NULL显示为 -∞ 或 +∞）
- 中文化枚举值

### 2. API 层实现

**文件**: `backend/app/api/orientation_rules.py`

#### 新增端点

```
GET /api/v1/orientation-rules/{rule_id}/export
```

**功能**: 导出导向规则为 Markdown 文件

**请求头**:
- `Authorization`: Bearer token
- `X-Hospital-ID`: 医疗机构ID

**响应**:
- 状态码: 200 OK
- Content-Type: `text/markdown; charset=utf-8`
- Content-Disposition: `attachment; filename*=UTF-8''{URL编码的文件名}`
- Body: Markdown 文件内容

**错误响应**:
- 400: 未激活医疗机构
- 403: 无权限访问该数据
- 404: 导向规则不存在

### 3. Markdown 格式

#### 基本结构

```markdown
# {导向名称}

## 基本信息

- **导向名称**: {名称}
- **导向类别**: {类别中文}
- **导向规则描述**: {描述}
- **创建时间**: {YYYY-MM-DD HH:MM:SS}
- **更新时间**: {YYYY-MM-DD HH:MM:SS}

## 导向基准 (仅 benchmark_ladder 类别)

| 科室代码 | 科室名称 | 基准类别 | 管控力度 | 统计开始时间 | 统计结束时间 | 基准值 |
|---------|---------|---------|---------|-------------|-------------|--------|
| ... | ... | ... | ... | ... | ... | ... |

## 导向阶梯 (benchmark_ladder 和 direct_ladder 类别)

| 阶梯次序 | 阶梯下限 | 阶梯上限 | 调整力度 |
|---------|---------|---------|---------|
| ... | ... | ... | ... |
```

#### 特殊处理

1. **枚举值中文化**:
   - 导向类别: `benchmark_ladder` → "基准阶梯"
   - 基准类别: `average` → "平均值", `median` → "中位数"等

2. **数值格式化**:
   - 所有数值字段格式化为4位小数（如 `0.8500`）

3. **无穷值处理**:
   - `lower_limit = NULL` → "-∞"
   - `upper_limit = NULL` → "+∞"

4. **日期格式化**:
   - 创建/更新时间: `YYYY-MM-DD HH:MM:SS`
   - 统计时间: `YYYY-MM-DD`

5. **阶梯排序**:
   - 按 `ladder_order` 升序排列

### 4. 文件名处理

#### 格式
```
{导向名称}_{时间戳}.md
```

#### 时间戳格式
```
YYYYMMDD_HHMMSS
```

#### 中文文件名处理
使用 RFC 5987 标准的 `filename*` 参数：
```
Content-Disposition: attachment; filename*=UTF-8''{URL编码的文件名}
```

示例：
- 原始文件名: `测试导向_20251126_165519.md`
- 编码后: `%E6%B5%8B%E8%AF%95%E5%AF%BC%E5%90%91_20251126_165519.md`

### 5. 多租户隔离

- 使用 `get_current_hospital_id_or_raise()` 获取当前医疗机构ID
- 使用 `apply_hospital_filter()` 过滤查询
- 使用 `validate_hospital_access()` 验证数据访问权限

## 测试

### 单元测试

**文件**: `test_orientation_export.py`

测试用例：
1. ✅ 导出基准阶梯类别的导向规则（包含基准和阶梯）
2. ✅ 导出直接阶梯类别的导向规则（仅包含阶梯）
3. ✅ 导出其他类别的导向规则（不包含关联数据）
4. ✅ 验证文件名格式（包含时间戳）

### API 测试

**文件**: `test_orientation_export_api.py`

测试用例：
1. ✅ 完整的导出流程（创建规则 → 导出 → 验证内容 → 清理）
2. ✅ 导出不存在的规则（返回404）
3. ✅ 未激活医疗机构时导出（返回400）
4. ✅ 验证中文文件名编码
5. ✅ 验证响应头（Content-Type, Content-Disposition）

## 使用示例

### Python 代码

```python
from app.services.orientation_rule_service import OrientationRuleService

# 导出规则
buffer, filename = OrientationRuleService.export_rule(db, rule_id=1, hospital_id=1)

# 保存到文件
with open(filename, 'wb') as f:
    f.write(buffer.read())
```

### API 调用

```bash
curl -X GET "http://localhost:8000/api/v1/orientation-rules/1/export" \
  -H "Authorization: Bearer {token}" \
  -H "X-Hospital-ID: 1" \
  --output "导向规则.md"
```

### JavaScript (前端)

```javascript
async function exportOrientationRule(ruleId) {
  const response = await fetch(`/api/v1/orientation-rules/${ruleId}/export`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Hospital-ID': hospitalId
    }
  });
  
  if (response.ok) {
    // 获取文件名
    const contentDisposition = response.headers.get('Content-Disposition');
    const filename = decodeURIComponent(
      contentDisposition.split("filename*=UTF-8''")[1]
    );
    
    // 下载文件
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
}
```

## 导出示例

### 基准阶梯类别

```markdown
# 科室业务价值导向

## 基本信息

- **导向名称**: 科室业务价值导向
- **导向类别**: 基准阶梯
- **导向规则描述**: 基于科室历史数据的基准值和阶梯调整
- **创建时间**: 2025-11-26 08:55:19
- **更新时间**: 2025-11-26 08:55:19

## 导向基准

| 科室代码 | 科室名称 | 基准类别 | 管控力度 | 统计开始时间 | 统计结束时间 | 基准值 |
|---------|---------|---------|---------|-------------|-------------|--------|
| D001 | 内科 | 平均值 | 0.8500 | 2024-01-01 | 2024-12-31 | 1000.5000 |
| D002 | 外科 | 中位数 | 0.9000 | 2024-01-01 | 2024-12-31 | 1200.7500 |

## 导向阶梯

| 阶梯次序 | 阶梯下限 | 阶梯上限 | 调整力度 |
|---------|---------|---------|---------|
| 1 | -∞ | 0.8000 | 0.5000 |
| 2 | 0.8000 | 1.2000 | 1.0000 |
| 3 | 1.2000 | +∞ | 1.5000 |
```

### 直接阶梯类别

```markdown
# 工作量阶梯导向

## 基本信息

- **导向名称**: 工作量阶梯导向
- **导向类别**: 直接阶梯
- **导向规则描述**: 基于工作量的直接阶梯调整
- **创建时间**: 2025-11-26 08:55:19
- **更新时间**: 2025-11-26 08:55:19

## 导向阶梯

| 阶梯次序 | 阶梯下限 | 阶梯上限 | 调整力度 |
|---------|---------|---------|---------|
| 1 | 0.0000 | 50.0000 | 0.8000 |
| 2 | 50.0000 | 100.0000 | 1.0000 |
```

### 其他类别

```markdown
# 自定义导向

## 基本信息

- **导向名称**: 自定义导向
- **导向类别**: 其他
- **导向规则描述**: 自定义的导向规则
- **创建时间**: 2025-11-26 08:55:19
- **更新时间**: 2025-11-26 08:55:19
```

## 技术细节

### 依赖项

- `fastapi`: Web 框架
- `sqlalchemy`: ORM
- `urllib.parse.quote`: URL 编码

### 性能考虑

1. **预加载关联数据**: 使用 SQLAlchemy 的关系自动加载基准和阶梯
2. **内存效率**: 使用 BytesIO 在内存中生成文件，避免磁盘IO
3. **流式响应**: 使用 StreamingResponse 支持大文件下载

### 安全考虑

1. **权限验证**: 验证用户是否有权访问该导向规则
2. **多租户隔离**: 确保只能导出当前医疗机构的数据
3. **输入验证**: 验证 rule_id 的有效性

## 验证需求

根据需求文档验证：

- ✅ **需求 3.1**: 导出的 Markdown 文件包含导向规则详细信息
- ✅ **需求 3.2**: "基准阶梯"类别的导向规则导出包含所有关联的导向基准数据
- ✅ **需求 3.3**: "基准阶梯"或"直接阶梯"类别的导向规则导出包含所有关联的导向阶梯数据
- ✅ **需求 3.4**: 导出文件使用导向名称作为文件名，并添加时间戳避免冲突
- ✅ **需求 3.5**: 导出文件正确处理中文文件名，确保跨平台兼容性

## 后续工作

1. 前端实现导出按钮和下载逻辑
2. 支持批量导出多个导向规则
3. 支持导出为其他格式（PDF、Excel）
4. 添加导出历史记录

## 总结

导向规则导出功能已完整实现，包括：
- ✅ 服务层导出逻辑
- ✅ API 端点
- ✅ Markdown 格式生成
- ✅ 中文文件名处理
- ✅ 多租户隔离
- ✅ 完整的测试覆盖

所有测试通过，功能符合需求规范。
