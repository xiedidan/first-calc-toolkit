# Excel批量导入功能设计

## 设计目标

设计一个通用的、可复用的Excel导入功能模块，支持：
1. **灵活的字段映射** - 用户可以自定义Excel列与系统字段的对应关系
2. **数据预览** - 导入前预览数据，确认映射正确
3. **数据验证** - 导入时进行数据格式和业务规则验证
4. **错误处理** - 清晰展示导入成功和失败的记录
5. **可复用性** - 多个模块（收费项目、维度目录、科室等）都可以使用

## 整体流程

```
┌─────────────┐
│ 1. 上传文件 │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 2. 解析Excel    │
│    读取表头和数据│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 3. 字段映射     │
│    用户配置映射 │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 4. 数据预览     │
│    显示前N条数据│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 5. 确认导入     │
│    执行导入操作 │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ 6. 结果展示     │
│    成功/失败统计│
└─────────────────┘
```

## 技术架构

### 后端架构

#### 1. 通用导入服务类

```python
# backend/app/services/excel_import_service.py

class ExcelImportService:
    """通用Excel导入服务"""
    
    def __init__(self, model_class, field_config):
        """
        初始化导入服务
        
        Args:
            model_class: 数据模型类（如 ChargeItem）
            field_config: 字段配置（定义必填字段、验证规则等）
        """
        self.model_class = model_class
        self.field_config = field_config
    
    def parse_excel(self, file) -> dict:
        """
        解析Excel文件
        
        Returns:
            {
                "headers": ["列1", "列2", ...],
                "preview_data": [[值1, 值2, ...], ...],  # 前10行
                "total_rows": 100
            }
        """
        pass
    
    def validate_mapping(self, mapping: dict) -> dict:
        """
        验证字段映射配置
        
        Args:
            mapping: {"excel_column": "system_field", ...}
        
        Returns:
            {
                "valid": True/False,
                "missing_required": ["field1", ...],
                "errors": [...]
            }
        """
        pass
    
    def import_data(self, file, mapping: dict, db: Session) -> dict:
        """
        执行数据导入
        
        Returns:
            {
                "success_count": 80,
                "failed_count": 20,
                "failed_items": [
                    {
                        "row": 5,
                        "data": {...},
                        "reason": "错误原因"
                    }
                ]
            }
        """
        pass
```

#### 2. 字段配置定义

```python
# backend/app/config/import_configs.py

CHARGE_ITEM_IMPORT_CONFIG = {
    "fields": {
        "item_code": {
            "label": "项目编码",
            "required": True,
            "unique": True,
            "type": "string",
            "max_length": 100,
            "validators": [validate_item_code]
        },
        "item_name": {
            "label": "项目名称",
            "required": True,
            "type": "string",
            "max_length": 255
        },
        "item_category": {
            "label": "项目分类",
            "required": False,
            "type": "string",
            "max_length": 100
        },
        "unit_price": {
            "label": "单价",
            "required": False,
            "type": "string",
            "max_length": 50,
            "validators": [validate_price]
        }
    },
    "default_mapping": {
        # 常见的列名自动映射
        "项目编码": "item_code",
        "编码": "item_code",
        "code": "item_code",
        "项目名称": "item_name",
        "名称": "item_name",
        "name": "item_name",
        "分类": "item_category",
        "category": "item_category",
        "单价": "unit_price",
        "price": "unit_price"
    }
}

DIMENSION_ITEM_IMPORT_CONFIG = {
    "fields": {
        "item_code": {
            "label": "收费项目编码",
            "required": True,
            "type": "string"
        }
    },
    "default_mapping": {
        "项目编码": "item_code",
        "编码": "item_code",
        "code": "item_code"
    }
}
```

### 前端架构

#### 1. 通用导入组件

```vue
<!-- frontend/src/components/ExcelImport.vue -->

<template>
  <el-dialog v-model="visible" title="批量导入" width="900px">
    <!-- 步骤条 -->
    <el-steps :active="currentStep" align-center>
      <el-step title="上传文件" />
      <el-step title="字段映射" />
      <el-step title="数据预览" />
      <el-step title="导入结果" />
    </el-steps>

    <!-- 步骤1: 上传文件 -->
    <div v-if="currentStep === 0">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx,.xls"
      >
        <el-icon><UploadFilled /></el-icon>
        <div>点击或拖拽文件到此处上传</div>
        <template #tip>
          <div>支持 .xlsx 和 .xls 格式</div>
        </template>
      </el-upload>
      <el-button @click="downloadTemplate">下载导入模板</el-button>
    </div>

    <!-- 步骤2: 字段映射 -->
    <div v-if="currentStep === 1">
      <el-table :data="mappingData" border>
        <el-table-column label="Excel列名" prop="excelColumn" />
        <el-table-column label="系统字段" width="250">
          <template #default="{ row }">
            <el-select v-model="row.systemField" placeholder="请选择">
              <el-option label="不导入" value="" />
              <el-option
                v-for="field in systemFields"
                :key="field.value"
                :label="field.label"
                :value="field.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="必填" width="80">
          <template #default="{ row }">
            <el-tag v-if="isRequired(row.systemField)" type="danger">
              必填
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="示例数据">
          <template #default="{ row }">
            {{ row.sampleData }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 步骤3: 数据预览 -->
    <div v-if="currentStep === 2">
      <el-alert
        title="请确认数据映射正确"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-table :data="previewData" border max-height="400">
        <el-table-column
          v-for="field in mappedFields"
          :key="field.value"
          :label="field.label"
          :prop="field.value"
        />
      </el-table>
      <div style="margin-top: 10px">
        共 {{ totalRows }} 条数据，预览前 {{ previewData.length }} 条
      </div>
    </div>

    <!-- 步骤4: 导入结果 -->
    <div v-if="currentStep === 3">
      <el-result
        :icon="importResult.success_count > 0 ? 'success' : 'error'"
        :title="`导入完成`"
      >
        <template #sub-title>
          <div>成功: {{ importResult.success_count }} 条</div>
          <div>失败: {{ importResult.failed_count }} 条</div>
        </template>
      </el-result>

      <!-- 失败记录 -->
      <div v-if="importResult.failed_count > 0">
        <el-divider />
        <h4>失败记录</h4>
        <el-table :data="importResult.failed_items" border max-height="300">
          <el-table-column label="行号" prop="row" width="80" />
          <el-table-column label="数据" prop="data" />
          <el-table-column label="失败原因" prop="reason" />
        </el-table>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <el-button v-if="currentStep > 0 && currentStep < 3" @click="prevStep">
        上一步
      </el-button>
      <el-button @click="visible = false">取消</el-button>
      <el-button
        v-if="currentStep < 2"
        type="primary"
        @click="nextStep"
        :disabled="!canNext"
      >
        下一步
      </el-button>
      <el-button
        v-if="currentStep === 2"
        type="primary"
        @click="executeImport"
        :loading="importing"
      >
        开始导入
      </el-button>
      <el-button v-if="currentStep === 3" type="primary" @click="visible = false">
        完成
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
// 组件逻辑
</script>
```

#### 2. 使用示例

```vue
<!-- 在 ChargeItems.vue 中使用 -->

<template>
  <div>
    <el-button @click="showImport = true">批量导入</el-button>
    
    <ExcelImport
      v-model="showImport"
      :import-config="chargeItemImportConfig"
      :api-endpoint="/charge-items/import"
      @success="handleImportSuccess"
    />
  </div>
</template>

<script setup>
import ExcelImport from '@/components/ExcelImport.vue'

const chargeItemImportConfig = {
  fields: [
    { value: 'item_code', label: '项目编码', required: true },
    { value: 'item_name', label: '项目名称', required: true },
    { value: 'item_category', label: '项目分类', required: false },
    { value: 'unit_price', label: '单价', required: false }
  ],
  templateUrl: '/api/v1/charge-items/template'
}
</script>
```

## API设计

### 1. 解析Excel文件

```
POST /api/v1/import/parse
Content-Type: multipart/form-data

Request:
- file: Excel文件

Response:
{
  "headers": ["项目编码", "项目名称", "分类", "单价"],
  "preview_data": [
    ["CK001", "血常规", "检验", "25.00"],
    ["CK002", "尿常规", "检验", "15.00"]
  ],
  "total_rows": 100,
  "suggested_mapping": {
    "项目编码": "item_code",
    "项目名称": "item_name",
    "分类": "item_category",
    "单价": "unit_price"
  }
}
```

### 2. 执行导入

```
POST /api/v1/charge-items/import
Content-Type: multipart/form-data

Request:
- file: Excel文件
- mapping: JSON字符串，如 {"项目编码": "item_code", ...}

Response:
{
  "success_count": 80,
  "failed_count": 20,
  "failed_items": [
    {
      "row": 5,
      "data": {"项目编码": "CK005", "项目名称": ""},
      "reason": "项目名称不能为空"
    }
  ]
}
```

### 3. 下载模板

```
GET /api/v1/charge-items/template

Response: Excel文件
- 包含表头
- 包含示例数据（1-2行）
- 包含字段说明（批注）
```

## 数据验证规则

### 1. 基础验证
- **必填字段**: 检查是否为空
- **唯一性**: 检查是否重复（数据库 + 当前导入数据）
- **数据类型**: 字符串、数字、日期等
- **长度限制**: 最大长度检查

### 2. 业务验证
- **格式验证**: 如价格格式、编码格式
- **关联验证**: 如外键是否存在
- **自定义规则**: 各模块特定的业务规则

### 3. 验证时机
- **映射阶段**: 检查必填字段是否都已映射
- **预览阶段**: 对预览数据进行快速验证
- **导入阶段**: 对所有数据进行完整验证

## 错误处理策略

### 1. 部分成功策略（推荐）
- 逐行导入，记录失败的行
- 成功的数据正常入库
- 失败的数据返回详细错误信息
- 用户可以修正后重新导入失败的数据

### 2. 全部成功策略
- 先验证所有数据
- 如果有任何错误，全部不导入
- 返回所有错误信息
- 用户修正后重新导入

## 性能优化

### 1. 大文件处理
- **分批处理**: 每次处理1000行
- **异步导入**: 大文件使用后台任务
- **进度反馈**: 实时显示导入进度

### 2. 数据库优化
- **批量插入**: 使用 bulk_insert
- **事务控制**: 合理使用事务
- **索引优化**: 确保唯一性检查高效

## 用户体验优化

### 1. 智能映射
- 根据列名自动匹配系统字段
- 支持中英文列名
- 支持常见别名

### 2. 友好提示
- 清晰的错误信息
- 字段说明和示例
- 导入进度显示

### 3. 模板下载
- 提供标准模板
- 包含示例数据
- 字段说明（Excel批注）

## 安全考虑

### 1. 文件安全
- 限制文件大小（如10MB）
- 限制文件类型（只允许Excel）
- 病毒扫描（可选）

### 2. 数据安全
- 权限检查
- SQL注入防护
- XSS防护

### 3. 性能保护
- 限制并发导入数量
- 超时控制
- 资源限制

## 复用性设计

### 1. 配置化
- 每个模块定义自己的字段配置
- 统一的导入流程
- 可扩展的验证规则

### 2. 组件化
- 通用的前端导入组件
- 通用的后端导入服务
- 可插拔的验证器

### 3. 标准化
- 统一的API接口
- 统一的响应格式
- 统一的错误码

## 实现优先级

### P0 - 核心功能
1. 文件上传和解析
2. 字段映射配置
3. 数据预览
4. 基础导入功能
5. 错误处理和展示

### P1 - 增强功能
1. 智能字段映射
2. 模板下载
3. 数据验证规则
4. 批量处理优化

### P2 - 高级功能
1. 异步导入（大文件）
2. 导入历史记录
3. 导入模板管理
4. 高级验证规则

## 技术选型

### 后端
- **Excel解析**: `openpyxl` (Python)
- **数据验证**: `pydantic`
- **异步任务**: `Celery` (可选，用于大文件)

### 前端
- **Excel解析**: `xlsx` (JavaScript，用于客户端预览)
- **文件上传**: Element Plus Upload
- **步骤条**: Element Plus Steps

## 总结

这个设计方案的核心优势：

1. **灵活性**: 支持用户自定义字段映射
2. **可复用性**: 一套代码支持多个模块
3. **用户友好**: 清晰的步骤和错误提示
4. **可扩展性**: 易于添加新的验证规则和功能
5. **性能优化**: 支持大文件和批量处理

您觉得这个设计方案如何？有什么需要调整或补充的地方吗？
