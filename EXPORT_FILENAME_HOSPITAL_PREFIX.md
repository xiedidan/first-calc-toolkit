# 导出文件名添加医院名称前缀

## 实施日期
2025-12-01

## 需求
所有导出文件名加上医院名称作为前缀，用下划线与原来的文件名分隔。

## 文件名格式

### 修改前
- `导向规则名称_时间戳.md`
- `导向规则名称_时间戳.pdf`
- `科室业务价值汇总_期间.xlsx`
- `业务价值明细表_期间.zip`
- `科室名称_业务价值明细_期间.xlsx`（ZIP内）
- `成本基准_时间戳.xlsx`
- `数据问题记录_日期.xlsx`

### 修改后
- `医院名称_导向规则名称_时间戳.md`
- `医院名称_导向规则名称_时间戳.pdf`
- `医院名称_科室业务价值汇总_期间.xlsx`
- `医院名称_业务价值明细表_期间.zip`
- `医院名称_科室名称_业务价值明细_期间.xlsx`（ZIP内）
- `医院名称_成本基准_时间戳.xlsx`
- `医院名称_数据问题记录_日期.xlsx`

## 实现内容

### 1. 导向规则导出（Markdown & PDF）

**文件**: `backend/app/services/orientation_rule_service.py`

#### 修改方法
- `export_rule()` - Markdown导出
- `export_rule_pdf()` - PDF导出

#### 实现
```python
# 获取医院名称
from app.models.hospital import Hospital
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
hospital_name = hospital.name if hospital else "未知医院"

# 生成文件名
filename = f"{hospital_name}_{rule.name}_{timestamp}.md"  # 或 .pdf
```

### 2. 报表导出服务

**文件**: `backend/app/services/export_service.py`

#### 修改方法
- `export_summary_to_excel()` - 添加 `hospital_name` 参数
- `export_detail_to_excel()` - 添加 `hospital_name` 参数
- `export_all_details_to_zip()` - 添加 `hospital_name` 参数，ZIP内文件名也加前缀

#### 实现
```python
# 方法签名添加参数
def export_summary_to_excel(summary_data: dict, period: str, hospital_name: str = None) -> BytesIO:

# ZIP内文件名
if hospital_name:
    filename = f"{hospital_name}_{dept_name}_业务价值明细_{period}.xlsx"
else:
    filename = f"{dept_name}_业务价值明细_{period}.xlsx"
```

### 3. 计算任务导出API

**文件**: `backend/app/api/calculation_tasks.py`

#### 修改端点
- `GET /results/export/summary` - 导出汇总表
- `GET /results/export/detail` - 导出明细表ZIP

#### 实现
```python
# 获取医院名称（通过model_version获取hospital_id）
from app.models.hospital import Hospital
hospital_id = task.model_version.hospital_id if task.model_version else None
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first() if hospital_id else None
hospital_name = hospital.name if hospital else "未知医院"

# 调用服务时传递医院名称
excel_file = ExportService.export_summary_to_excel(excel_data, period, hospital_name)

# 生成文件名
filename = f"{hospital_name}_科室业务价值汇总_{period}.xlsx"
```

**注意**: CalculationTask模型没有hospital_id字段，需要通过关联的model_version获取。

### 4. 成本基准导出

**文件**: `backend/app/api/cost_benchmarks.py`

#### 修改端点
- `GET /cost-benchmarks/export`

#### 实现
```python
# 获取医院名称
from app.models.hospital import Hospital
from app.utils.hospital_filter import get_current_hospital_id_or_raise
hospital_id = get_current_hospital_id_or_raise()
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
hospital_name = hospital.name if hospital else "未知医院"

# 生成文件名
filename = f"{hospital_name}_成本基准_{timestamp}.xlsx"
```

### 5. 数据问题导出

**文件**: `backend/app/api/data_issues.py`

#### 修改端点
- `GET /data-issues/export`

#### 实现
```python
# 获取医院名称
from app.models.hospital import Hospital
if hospital_id:
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    hospital_name = hospital.name if hospital else "未知医院"
else:
    hospital_name = "未知医院"

# 生成文件名
filename = f"{hospital_name}_数据问题记录_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
```

## 技术要点

### 1. 医院名称获取
```python
from app.models.hospital import Hospital

# 方式1：从task对象通过model_version获取hospital_id
hospital_id = task.model_version.hospital_id if task.model_version else None
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first() if hospital_id else None

# 方式2：从当前上下文获取
from app.utils.hospital_filter import get_current_hospital_id_or_raise
hospital_id = get_current_hospital_id_or_raise()
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

# 方式3：从已有的hospital_id变量
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

# 方式4：从关联对象获取（如OrientationRule）
hospital_id = rule.hospital_id
hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

# 获取名称（提供默认值）
hospital_name = hospital.name if hospital else "未知医院"
```

**重要提示**: 
- CalculationTask模型没有hospital_id字段，需要通过`task.model_version.hospital_id`获取
- 确保在访问关联对象前检查其是否存在（使用条件表达式）

### 2. 文件名格式
- 使用下划线 `_` 分隔各部分
- 格式：`{医院名称}_{原文件名}`
- 保持原有的时间戳格式

### 3. 中文文件名处理
- 使用 `urllib.parse.quote()` 进行URL编码
- HTTP响应头格式: `filename*=UTF-8''{encoded_filename}`
- 符合RFC 5987标准

### 4. 向后兼容
- 服务层方法的 `hospital_name` 参数设为可选（默认None）
- 如果未提供医院名称，使用原有格式或"未知医院"

## 影响范围

### 后端文件
- ✅ `backend/app/services/orientation_rule_service.py`
- ✅ `backend/app/services/export_service.py`
- ✅ `backend/app/api/calculation_tasks.py`
- ✅ `backend/app/api/cost_benchmarks.py`
- ✅ `backend/app/api/data_issues.py`

### 前端影响
- 无需修改前端代码
- 浏览器自动处理文件名下载
- 用户看到的文件名自动包含医院名称

## 测试验证

### 测试项目
1. ✅ 导向规则导出Markdown - 文件名包含医院名称
2. ✅ 导向规则导出PDF - 文件名包含医院名称
3. ⏳ 导出汇总表 - 文件名包含医院名称
4. ⏳ 导出明细表ZIP - 文件名和ZIP内文件都包含医院名称
5. ⏳ 导出成本基准 - 文件名包含医院名称
6. ⏳ 导出数据问题记录 - 文件名包含医院名称

### 测试方法
```bash
# 1. 启动后端服务
cd backend
python -m uvicorn app.main:app --reload

# 2. 登录并获取token
# 3. 调用各个导出API
# 4. 验证下载的文件名格式
```

### 预期结果
所有导出的文件名都应该以医院名称开头，格式为：
```
{医院名称}_{原文件名}
```

例如：
- `北京协和医院_科室业务价值汇总_2025-11.xlsx`
- `上海瑞金医院_导向规则_20251201_143022.pdf`
- `广州中山医院_成本基准_20251201_143022.xlsx`

## 注意事项

### 1. 医院名称特殊字符
- 医院名称可能包含特殊字符（如括号、空格）
- URL编码会自动处理这些字符
- 文件系统会自动处理或替换不支持的字符

### 2. 文件名长度
- 医院名称可能较长
- 完整文件名可能超过某些文件系统的限制（通常255字符）
- 如需要，可以截断医院名称或使用医院编码

### 3. 多租户隔离
- 确保每个导出都正确获取当前医疗机构ID
- 使用 `get_current_hospital_id_or_raise()` 确保安全性
- 验证用户有权访问该医疗机构的数据

## 后续优化

### 可选改进
1. 使用医院编码代替医院名称（更短、更规范）
   ```python
   filename = f"{hospital.code}_{original_filename}"
   ```

2. 添加配置选项，允许用户选择是否包含医院名称
   ```python
   if settings.INCLUDE_HOSPITAL_IN_FILENAME:
       filename = f"{hospital_name}_{original_filename}"
   ```

3. 文件名长度限制
   ```python
   max_hospital_name_length = 20
   short_hospital_name = hospital_name[:max_hospital_name_length]
   filename = f"{short_hospital_name}_{original_filename}"
   ```

## 总结

所有导出功能已成功添加医院名称前缀，包括：
- ✅ 导向规则导出（Markdown & PDF）
- ✅ 报表导出（汇总表 & 明细表）
- ✅ 成本基准导出
- ✅ 数据问题记录导出

文件名格式统一为：`{医院名称}_{原文件名}`，便于用户识别和管理不同医疗机构的导出文件。
