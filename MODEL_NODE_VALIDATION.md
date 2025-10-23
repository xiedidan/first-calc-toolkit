# 模型节点表单验证规则

## 📋 验证规则说明

### 基础字段（所有节点必填）
- ✅ **节点名称** (`name`): 必填
- ✅ **节点编码** (`code`): 必填
- ✅ **节点类型** (`node_type`): 必填（序列/维度）

### 末级维度额外必填字段
当节点被标记为"末级维度"（`is_leaf = true`）时，以下字段变为必填：
- ✅ **计算类型** (`calc_type`): 必填（统计型/计算型）
- ✅ **权重/单价** (`weight`): 必填
- ✅ **单位** (`unit`): 必填
- ✅ **计算脚本** (`script`): 必填

### 可选字段
- ⭕ **排序序号** (`sort_order`): 可选，留空自动设置
- ⭕ **业务导向** (`business_guide`): 可选

## 💻 实现方式

### 动态验证规则
使用 Vue 的 `computed` 属性实现动态验证规则：

```typescript
const rules = computed<FormRules>(() => {
  const baseRules: FormRules = {
    name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
    code: [{ required: true, message: '请输入节点编码', trigger: 'blur' }],
    node_type: [{ required: true, message: '请选择节点类型', trigger: 'change' }]
  }
  
  // 如果是末级维度，添加额外的必填验证
  if (form.is_leaf) {
    baseRules.calc_type = [{ required: true, message: '请选择计算类型', trigger: 'change' }]
    baseRules.weight = [{ required: true, message: '请输入权重/单价', trigger: 'blur' }]
    baseRules.unit = [{ required: true, message: '请输入单位', trigger: 'blur' }]
    baseRules.script = [{ required: true, message: '请输入计算脚本', trigger: 'blur' }]
  }
  
  return baseRules
})
```

### 验证触发时机
- **blur**: 失去焦点时验证（输入框）
- **change**: 值改变时验证（下拉框、开关）

## 🎯 用户体验

### 场景1: 创建非末级节点
```
必填字段:
✅ 节点名称
✅ 节点编码
✅ 节点类型
⭕ 是否末级维度: 否

可以直接保存 ✓
```

### 场景2: 创建末级维度节点
```
必填字段:
✅ 节点名称
✅ 节点编码
✅ 节点类型
✅ 是否末级维度: 是
✅ 计算类型
✅ 权重/单价
✅ 单位
✅ 计算脚本

必须填写所有字段才能保存 ✓
```

### 场景3: 将非末级节点改为末级
```
1. 编辑一个非末级节点
2. 勾选"是否末级维度"
3. 表单自动显示额外字段
4. 这些字段变为必填
5. 必须填写完整才能保存
```

## ⚠️ 验证错误提示

### 基础字段
- "请输入节点名称"
- "请输入节点编码"
- "请选择节点类型"

### 末级维度字段
- "请选择计算类型"
- "请输入权重/单价"
- "请输入单位"
- "请输入计算脚本"

## 🔍 验证逻辑

### 前端验证
```typescript
// 提交表单时触发验证
await formRef.value.validate(async (valid) => {
  if (!valid) return  // 验证失败，阻止提交
  
  // 验证通过，继续提交
  // ...
})
```

### 后端验证（建议）
虽然前端已经做了验证，但建议在后端也添加相应的验证逻辑：

```python
# backend/app/api/model_nodes.py
def create_model_node(node_in: ModelNodeCreate, ...):
    # 如果是末级维度，验证必填字段
    if node_in.is_leaf:
        if not node_in.calc_type:
            raise HTTPException(400, "末级维度必须指定计算类型")
        if node_in.weight is None:
            raise HTTPException(400, "末级维度必须指定权重/单价")
        if not node_in.unit:
            raise HTTPException(400, "末级维度必须指定单位")
        if not node_in.script:
            raise HTTPException(400, "末级维度必须指定计算脚本")
```

## 📊 字段依赖关系

```
is_leaf (是否末级维度)
├─ false (非末级)
│  ├─ calc_type: 隐藏，不验证
│  ├─ weight: 隐藏，不验证
│  ├─ unit: 隐藏，不验证
│  ├─ business_guide: 隐藏，不验证
│  └─ script: 隐藏，不验证
│
└─ true (末级维度)
   ├─ calc_type: 显示，必填 ✓
   ├─ weight: 显示，必填 ✓
   ├─ unit: 显示，必填 ✓
   ├─ business_guide: 显示，可选
   └─ script: 显示，必填 ✓
```

## 🧪 测试场景

### 测试1: 创建非末级节点
1. 填写节点名称、编码、类型
2. 不勾选"是否末级维度"
3. 点击保存
4. ✅ 应该成功保存

### 测试2: 创建末级节点（缺少必填字段）
1. 填写节点名称、编码、类型
2. 勾选"是否末级维度"
3. 不填写计算类型、权重等
4. 点击保存
5. ❌ 应该显示验证错误，阻止保存

### 测试3: 创建末级节点（完整填写）
1. 填写节点名称、编码、类型
2. 勾选"是否末级维度"
3. 填写计算类型、权重、单位、脚本
4. 点击保存
5. ✅ 应该成功保存

### 测试4: 动态切换末级维度
1. 编辑一个节点
2. 切换"是否末级维度"开关
3. 观察表单字段显示/隐藏
4. 观察必填标记变化
5. ✅ 应该正确响应

## 💡 注意事项

1. **动态验证**
   - 验证规则使用 `computed` 实现
   - 当 `is_leaf` 改变时，验证规则自动更新

2. **用户提示**
   - 必填字段在标签旁显示红色星号
   - 验证失败时显示错误提示
   - 错误提示清晰明确

3. **表单重置**
   - 关闭对话框时重置表单
   - 重置验证状态

4. **有子节点的限制**
   - 如果节点有子节点，不能设为末级维度
   - 开关会被禁用
   - 显示提示文本

## 📝 更新日志

**2025-10-23**
- ✅ 添加末级维度字段的必填验证
- ✅ 实现动态验证规则
- ✅ 计算类型、权重/单价、单位、脚本必填
- ✅ 编写验证规则文档
