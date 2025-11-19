# 维度目录导入功能更新 - Sheet选择和跳过行数

## 📋 更新概述

为维度目录智能导入功能添加了两个重要特性：
1. **Sheet选择**：支持从多Sheet的Excel文件中选择特定的工作表
2. **跳过前N行**：支持跳过Excel文件前N行（用于处理标题行、说明行等）

## ✅ 已完成的更新

### 1. 后端更新

#### 1.1 服务层 (`dimension_import_service.py`)
- **`parse_excel()` 方法**：
  - 新增 `sheet_name` 参数：指定要读取的工作表名称
  - 新增 `skip_rows` 参数：指定跳过前N行
  - 返回所有Sheet名称列表
  - 返回当前选中的Sheet名称
  - 返回跳过的行数

- **`extract_unique_values()` 方法**：
  - 支持从指定Sheet读取数据
  - 支持跳过前N行

- **`generate_preview()` 方法**：
  - 支持从指定Sheet读取数据
  - 支持跳过前N行

#### 1.2 Schema定义 (`dimension_item.py`)
- **`SmartImportParseResponse`**：
  - 新增 `sheet_names` 字段：所有Sheet名称列表
  - 新增 `current_sheet` 字段：当前选中的Sheet
  - 新增 `skip_rows` 字段：跳过的行数

#### 1.3 API接口 (`dimension_items.py`)
- **`POST /dimension-items/smart-import/parse`**：
  - 新增查询参数 `sheet_name`：工作表名称（可选）
  - 新增查询参数 `skip_rows`：跳过前N行（默认0）

### 2. 前端更新

#### 2.1 API接口 (`dimension-import.ts`)
- **`parseExcel()` 函数**：
  - 新增 `sheetName` 参数：工作表名称（可选）
  - 新增 `skipRows` 参数：跳过前N行（可选）
  - 更新返回类型，包含Sheet信息

#### 2.2 组件更新 (`DimensionSmartImport.vue`)
- **新增Excel配置区域**：
  - Sheet选择下拉框
  - 跳过行数输入框（数字输入，范围0-100）
  - 配置说明文字

- **新增数据字段**：
  - `excelConfig`：存储Sheet名称和跳过行数

- **新增方法**：
  - `handleSheetChange()`：Sheet改变时重新解析
  - `handleSkipRowsChange()`：跳过行数改变时重新解析

## 🎯 功能特性

### 1. Sheet选择
- **自动检测**：上传文件后自动列出所有Sheet
- **默认选择**：默认选择第一个Sheet（或活动Sheet）
- **动态切换**：切换Sheet后自动重新解析数据
- **实时预览**：切换后立即显示新Sheet的数据预览

### 2. 跳过前N行
- **灵活配置**：支持跳过0-100行
- **实时生效**：修改跳过行数后自动重新解析
- **智能验证**：
  - 跳过行数不能超过总行数
  - 跳过后必须至少保留表头和数据行
- **友好提示**：提供说明文字，帮助用户理解功能

## 📊 使用场景

### 场景1：多Sheet Excel文件
```
Excel文件结构：
├─ Sheet1: 门诊项目
├─ Sheet2: 住院项目
└─ Sheet3: 手术项目

用户操作：
1. 上传文件
2. 选择 "Sheet2: 住院项目"
3. 系统自动解析该Sheet的数据
```

### 场景2：带标题行的Excel
```
Excel文件结构：
第1行: 医院名称
第2行: 报表标题
第3行: 生成日期
第4行: 列名（表头）
第5行+: 数据

用户操作：
1. 上传文件
2. 设置"跳过前N行"为 3
3. 系统从第4行开始读取（作为表头）
```

### 场景3：组合使用
```
用户操作：
1. 上传多Sheet文件
2. 选择 "Sheet2"
3. 设置跳过前2行
4. 系统从Sheet2的第3行开始读取
```

## 🔄 工作流程

```
1. 用户上传Excel文件
   ↓
2. 系统解析文件，返回所有Sheet名称
   ↓
3. 用户选择目标Sheet（可选）
   ↓
4. 用户设置跳过行数（可选）
   ↓
5. 系统重新解析，显示预览数据
   ↓
6. 用户配置字段映射
   ↓
7. 继续后续导入流程...
```

## 💡 技术实现

### 后端实现
```python
def parse_excel(cls, file_content: bytes, sheet_name: Optional[str] = None, skip_rows: int = 0):
    # 读取Excel
    wb = openpyxl.load_workbook(BytesIO(file_content), read_only=True)
    
    # 获取所有Sheet名称
    sheet_names = wb.sheetnames
    
    # 选择工作表
    if sheet_name and sheet_name in sheet_names:
        ws = wb[sheet_name]
    else:
        ws = wb.active
    
    # 获取所有行
    rows = list(ws.iter_rows(values_only=True))
    
    # 跳过前N行
    if skip_rows > 0:
        rows = rows[skip_rows:]
    
    # 处理数据...
```

### 前端实现
```vue
<el-form-item label="选择Sheet">
  <el-select v-model="excelConfig.sheetName" @change="handleSheetChange">
    <el-option
      v-for="sheet in parseResult.sheet_names"
      :key="sheet"
      :label="sheet"
      :value="sheet"
    />
  </el-select>
</el-form-item>

<el-form-item label="跳过前N行">
  <el-input-number
    v-model="excelConfig.skipRows"
    :min="0"
    :max="100"
    @change="handleSkipRowsChange"
  />
</el-form-item>
```

## ⚠️ 注意事项

### 1. 性能考虑
- 每次切换Sheet或修改跳过行数都会重新解析文件
- 对于大文件，可能需要几秒钟的处理时间
- 前端已实现loading状态提示

### 2. 数据验证
- 跳过行数不能超过总行数
- 跳过后必须至少保留1行表头和1行数据
- Sheet名称必须存在于文件中

### 3. 用户体验
- 提供清晰的说明文字
- 实时预览数据变化
- 错误提示友好明确

## 🧪 测试建议

### 测试用例1：单Sheet文件
- 上传只有一个Sheet的文件
- 验证Sheet选择器显示正确
- 验证默认选中第一个Sheet

### 测试用例2：多Sheet文件
- 上传包含3个Sheet的文件
- 切换不同Sheet
- 验证数据预览正确更新

### 测试用例3：跳过行数
- 设置跳过0行（默认）
- 设置跳过1行
- 设置跳过5行
- 验证表头和数据正确

### 测试用例4：边界情况
- 跳过行数等于总行数-1
- 跳过行数超过总行数
- 验证错误提示

### 测试用例5：组合使用
- 选择Sheet2 + 跳过3行
- 验证数据正确
- 验证后续导入流程正常

## 📚 相关文档

- [维度目录智能导入完成文档](./DIMENSION_SMART_IMPORT_COMPLETED.md)
- [需求文档](./需求文档.md) - 第3.2.5节
- [API设计文档](./API设计文档.md) - 第3.4节

## ✨ 总结

本次更新为维度目录导入功能增加了两个实用特性：
- ✅ Sheet选择：支持多Sheet Excel文件
- ✅ 跳过前N行：支持处理带标题行的Excel
- ✅ 实时预览：配置改变后立即生效
- ✅ 友好提示：清晰的说明和错误提示
- ✅ 向后兼容：不影响现有功能

这些特性大大提升了导入功能的灵活性和实用性，能够处理更多样化的Excel文件格式。
