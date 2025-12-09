# 智能导入功能修复总结

## 问题描述

用户在调用智能导入预览 API 时遇到 400 错误：
```
请求 URL: http://127.0.0.1:3000/api/v1/dimension-items/smart-import/preview
请求方法: POST
状态代码: 400 Bad Request
响应: {"detail":"'' is not in list"}
```

## 根本原因分析

经过详细分析，发现了以下严重的多租户隔离问题：

### 1. 缺少 hospital_id 参数传递
- `generate_preview()` 方法没有接收 `hospital_id` 参数
- `execute_import()` 方法没有接收 `hospital_id` 参数

### 2. 数据查询未隔离
- 查询收费项目时未按 `hospital_id` 过滤
- 查询已存在映射时未按 `hospital_id` 过滤
- 可能导致跨医疗机构的数据泄露

### 3. 数据创建违反约束
- 创建 `DimensionItemMapping` 时未设置 `hospital_id` 字段
- 违反数据库 NOT NULL 约束，导致插入失败

### 4. 空值处理不完善
- 某些字段可能为 `None`，导致 Pydantic 验证失败

## 已实施的修复

### 1. 添加 hospital_id 参数

**backend/app/services/dimension_import_service.py**

```python
# generate_preview 方法
@classmethod
def generate_preview(
    cls,
    session_id: str,
    value_mapping: List[Dict[str, Any]],
    db: Session,
    hospital_id: int  # 新增参数
) -> Dict[str, Any]:
    ...

# execute_import 方法
@classmethod
def execute_import(
    cls,
    session_id: str,
    confirmed_items: Optional[List[Dict[str, Any]]],
    db: Session,
    hospital_id: int  # 新增参数
) -> Dict[str, Any]:
    ...
```

### 2. 数据查询添加医疗机构过滤

```python
# 查询收费项目
all_charge_items_by_code = {
    item.item_code: item 
    for item in db.query(ChargeItem)
    .filter(ChargeItem.hospital_id == hospital_id)  # 添加过滤
    .all()
}

# 查询已存在映射
existing_mappings = set()
for mapping in db.query(DimensionItemMapping)
    .filter(DimensionItemMapping.hospital_id == hospital_id)  # 添加过滤
    .all():
    existing_mappings.add((mapping.dimension_code, mapping.item_code))
```

### 3. 创建映射时设置 hospital_id

```python
# 创建新映射
mapping = DimensionItemMapping(
    hospital_id=hospital_id,  # 设置医疗机构ID
    dimension_code=item["dimension_code"],
    item_code=item["item_code"]
)
```

### 4. 空值保护

```python
preview_items.append({
    "item_code": item_code or "",
    "item_name": item_name or "",
    "dimension_code": dim_code or "",
    "dimension_name": dimension.name or "",
    "dimension_path": dimension_path or "",
    "source": source_type or "",
    "source_value": source_value or "",
    "status": status or "",
    "message": message or ""
})
```

### 5. API 层传递 hospital_id

**backend/app/api/dimension_items.py**

```python
@router.post("/smart-import/preview", response_model=SmartImportPreviewResponse)
def smart_import_preview(
    request: SmartImportPreviewRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第三步：生成导入预览"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = DimensionImportService.generate_preview(
            session_id=request.session_id,
            value_mapping=request.value_mapping,
            db=db,
            hospital_id=hospital_id  # 传递参数
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")

@router.post("/smart-import/execute", response_model=SmartImportExecuteResponse)
def smart_import_execute(
    request: SmartImportExecuteRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """执行导入"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    try:
        result = DimensionImportService.execute_import(
            session_id=request.session_id,
            confirmed_items=request.confirmed_items,
            db=db,
            hospital_id=hospital_id  # 传递参数
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行导入失败: {str(e)}")
```

## 测试验证

### 前置条件
1. 后端服务正在运行
2. 前端已登录并激活医疗机构
3. 前端请求头包含有效的 `X-Hospital-ID`

### 测试步骤
1. 上传包含维度映射的 Excel 文件
2. 完成字段映射和唯一值提取
3. 为每个值选择对应的维度
4. 点击"下一步"生成预览
5. 检查预览数据是否正确显示
6. 执行导入
7. 验证数据是否正确保存到数据库

### 预期结果
- ✅ 预览 API 返回 200 状态码
- ✅ 预览数据正确显示收费项目和维度信息
- ✅ 导入成功，数据正确保存
- ✅ 所有数据都正确关联到当前医疗机构
- ✅ 不同医疗机构的数据完全隔离

## 安全性改进

修复后的代码确保了：
1. **数据隔离**：所有查询和操作都限定在当前医疗机构范围内
2. **数据完整性**：所有创建的记录都包含必需的 `hospital_id` 字段
3. **访问控制**：用户只能访问和修改自己医疗机构的数据

## 注意事项

1. 前端必须在所有请求中包含 `X-Hospital-ID` 请求头
2. 如果未激活医疗机构，API 会返回 400 错误："请先激活医疗机构"
3. 智能导入的会话数据存储在内存中，生产环境应考虑使用 Redis
4. 导入操作会覆盖已存在的映射关系（同一医疗机构内）

## 相关文件

- `backend/app/api/dimension_items.py` - API 路由
- `backend/app/services/dimension_import_service.py` - 业务逻辑
- `backend/app/models/dimension_item_mapping.py` - 数据模型
- `backend/app/schemas/dimension_item.py` - 数据验证
- `frontend/src/components/DimensionSmartImport.vue` - 前端组件
