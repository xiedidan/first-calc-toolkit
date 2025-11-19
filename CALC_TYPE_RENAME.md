# 算法类型命名统一 - 修改说明

## 📋 修改内容

### 字段名称修改
- **"计算类型"** → **"算法类型"**

### 取值修改
- **"统计型"** (statistical) → **"指标"**
- **"计算型"** (calculational) → **"目录"**

## 🎯 修改范围

### 1. 前端代码 (`frontend/src/views/ModelNodes.vue`)

#### 表格列标题
```vue
<!-- 修改前 -->
<el-table-column label="计算类型" width="100" align="center">

<!-- 修改后 -->
<el-table-column label="算法类型" width="100" align="center">
```

#### 表格显示标签
```vue
<!-- 修改前 -->
<el-tag>统计型</el-tag>
<el-tag>计算型</el-tag>

<!-- 修改后 -->
<el-tag>指标</el-tag>
<el-tag>目录</el-tag>
```

#### 表单标签
```vue
<!-- 修改前 -->
<el-form-item label="计算类型" prop="calc_type">
  <el-option label="统计型" value="statistical" />
  <el-option label="计算型" value="calculational" />
</el-form-item>

<!-- 修改后 -->
<el-form-item label="算法类型" prop="calc_type">
  <el-option label="指标" value="statistical" />
  <el-option label="目录" value="calculational" />
</el-form-item>
```

#### 验证提示
```typescript
// 修改前
message: '请选择计算类型'

// 修改后
message: '请选择算法类型'
```

### 2. 后端代码

#### API错误提示 (`backend/app/api/model_nodes.py`)
```python
# 修改前
detail="末级维度必须指定计算类型"

# 修改后
detail="末级维度必须指定算法类型"
```

#### Schema注释 (`backend/app/schemas/model_node.py`)
```python
# 修改前
calc_type: Optional[str] = Field(None, description="计算类型(statistical/calculational)")
calc_type: Optional[str] = Field(None, description="计算类型")

# 修改后
calc_type: Optional[str] = Field(None, description="算法类型(statistical=指标/calculational=目录)")
calc_type: Optional[str] = Field(None, description="算法类型")
```

#### Model注释 (`backend/app/models/model_node.py`)
```python
# 修改前
calc_type = Column(String(20), comment="计算类型(statistical/calculational)")

# 修改后
calc_type = Column(String(20), comment="算法类型(statistical=指标/calculational=目录)")
```

## 📊 数据映射关系

| 界面显示 | 数据库值 | 说明 |
|---------|---------|------|
| 指标 | statistical | 原"统计型"，表示可直接统计的指标 |
| 目录 | calculational | 原"计算型"，表示需要计算的目录项 |

## 🔄 数据兼容性

### 数据库层面
- ✅ **无需数据迁移**
- ✅ 数据库存储的值不变（statistical/calculational）
- ✅ 只是界面显示文本的变化

### API层面
- ✅ **API接口不变**
- ✅ 请求和响应的字段值不变
- ✅ 只是注释和错误提示的变化

### 前端层面
- ✅ **TypeScript类型定义不变**
- ✅ 数据处理逻辑不变
- ✅ 只是显示文本的变化

## 📝 术语对照表

### 修改前
```
字段名: 计算类型 (calc_type)
取值:
  - statistical: 统计型
  - calculational: 计算型
```

### 修改后
```
字段名: 算法类型 (calc_type)
取值:
  - statistical: 指标
  - calculational: 目录
```

## 🎨 界面效果

### 表格列
```
修改前: | 计算类型 |
        | 统计型   |
        | 计算型   |

修改后: | 算法类型 |
        | 指标     |
        | 目录     |
```

### 表单下拉框
```
修改前: 计算类型 [请选择 ▼]
        - 统计型
        - 计算型

修改后: 算法类型 [请选择 ▼]
        - 指标
        - 目录
```

### 验证提示
```
修改前: "请选择计算类型"
        "末级维度必须指定计算类型"

修改后: "请选择算法类型"
        "末级维度必须指定算法类型"
```

## 📁 修改的文件

### 代码文件
1. `frontend/src/views/ModelNodes.vue` - 前端界面
2. `backend/app/api/model_nodes.py` - API接口
3. `backend/app/schemas/model_node.py` - Schema定义
4. `backend/app/models/model_node.py` - 数据模型

### 文档文件（需要更新）
- `系统设计文档.md`
- `API设计文档.md`
- `MODEL_NODE_VALIDATION.md`
- `VALIDATION_SUMMARY.md`
- 其他相关文档

## ✅ 验证检查

### 前端验证
- [x] 表格列标题显示"算法类型"
- [x] 表格单元格显示"指标"或"目录"
- [x] 表单标签显示"算法类型"
- [x] 下拉选项显示"指标"和"目录"
- [x] 验证提示显示"请选择算法类型"

### 后端验证
- [x] API错误提示显示"算法类型"
- [x] Schema注释更新为"算法类型"
- [x] Model注释更新为"算法类型"

### 功能验证
- [x] 创建节点功能正常
- [x] 编辑节点功能正常
- [x] 数据保存和读取正常
- [x] 验证规则正常工作

## 💡 注意事项

1. **数据库无需变更**
   - 存储的值仍然是 statistical/calculational
   - 只是界面显示的文本变化

2. **API兼容性**
   - API接口完全兼容
   - 前端发送的值不变
   - 后端返回的值不变

3. **用户体验**
   - 新术语更符合业务场景
   - "指标"和"目录"更直观易懂
   - "算法类型"更准确描述字段含义

4. **文档同步**
   - 需要更新相关设计文档
   - 需要更新API文档
   - 需要更新用户手册

## 📅 更新日志

**2025-10-23**
- ✅ 统一修改"计算类型"为"算法类型"
- ✅ 统一修改"统计型"为"指标"
- ✅ 统一修改"计算型"为"目录"
- ✅ 更新前端界面显示
- ✅ 更新后端注释和提示
- ✅ 创建修改说明文档
- ⏳ 待更新相关设计文档
