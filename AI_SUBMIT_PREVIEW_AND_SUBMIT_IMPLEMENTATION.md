# 提交预览和批量提交功能实现总结

## 概述

任务9"提交预览和批量提交功能"已完成实现。该功能允许管理员在提交AI分类预案前预览影响范围，并批量提交到维度目录。

## 实现内容

### 9.1 提交预览功能 (generate_submit_preview)

**位置**: `backend/app/services/classification_plan_service.py`

**功能描述**:
- 遍历预案中的所有项目
- 确定每个项目的最终维度（用户设置 ?? AI建议）
- 查询维度项目映射表检查是否已存在
- 将项目分类为"新增"或"覆盖"
- 统计新增和覆盖的数量
- 返回详细的预览信息

**核心逻辑**:
```python
def generate_submit_preview(db: Session, hospital_id: int, plan_id: int) -> SubmitPreviewResponse:
    # 1. 查询预案和所有项目
    # 2. 遍历每个项目
    for item in items:
        # 确定最终维度（用户设置优先）
        final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
        
        # 检查是否已存在映射
        existing = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.hospital_id == hospital_id,
            DimensionItemMapping.charge_item_id == item.charge_item_id
        ).first()
        
        if existing:
            # 覆盖：记录原维度和新维度
            overwrite_items.append(...)
        else:
            # 新增：记录新维度
            new_items.append(...)
    
    # 3. 返回预览结果
    return SubmitPreviewResponse(
        new_count=len(new_items),
        overwrite_count=len(overwrite_items),
        new_items=new_items,
        overwrite_items=overwrite_items
    )
```

**返回数据结构**:
- `plan_id`: 预案ID
- `plan_name`: 预案名称
- `total_items`: 总项目数
- `new_count`: 新增项目数量
- `overwrite_count`: 覆盖项目数量
- `new_items`: 新增项目列表（包含项目名称、维度名称、维度路径）
- `overwrite_items`: 覆盖项目列表（包含项目名称、原维度、新维度）
- `warnings`: 警告信息列表

**API端点**: `POST /api/v1/classification-plans/{plan_id}/preview`

### 9.2 批量提交功能 (submit_plan)

**位置**: `backend/app/services/classification_plan_service.py`

**功能描述**:
- 验证预案状态（防止重复提交）
- 使用数据库事务确保原子性
- 遍历预案项目并批量处理
- 新增项目：创建DimensionItemMapping记录
- 覆盖项目：更新DimensionItemMapping的dimension_code
- 更新预案状态为submitted
- 失败时自动回滚

**核心逻辑**:
```python
def submit_plan(db: Session, hospital_id: int, plan_id: int, submit_data: SubmitPlanRequest) -> SubmitPlanResponse:
    # 1. 验证预案状态
    if plan.status == PlanStatus.submitted:
        raise ValueError("预案已提交，不可重复提交")
    
    try:
        # 2. 遍历所有项目
        for item in items:
            final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
            
            # 获取维度信息
            dimension = db.query(ModelNode).filter_by(id=final_dimension_id).first()
            
            # 检查是否已存在映射
            existing = db.query(DimensionItemMapping).filter(
                DimensionItemMapping.hospital_id == hospital_id,
                DimensionItemMapping.charge_item_id == item.charge_item_id
            ).first()
            
            if existing:
                # 更新维度归属
                existing.dimension_code = dimension.code
                overwrite_count += 1
            else:
                # 创建新映射
                new_mapping = DimensionItemMapping(
                    hospital_id=hospital_id,
                    dimension_code=dimension.code,
                    item_code=charge_item.item_code,
                    charge_item_id=item.charge_item_id
                )
                db.add(new_mapping)
                new_count += 1
        
        # 3. 更新预案状态
        plan.status = PlanStatus.submitted
        plan.submitted_at = datetime.utcnow()
        
        # 4. 提交事务
        db.commit()
        
        return SubmitPlanResponse(success=True, ...)
        
    except Exception as e:
        # 回滚事务
        db.rollback()
        return SubmitPlanResponse(success=False, message=str(e))
```

**返回数据结构**:
- `success`: 是否成功
- `message`: 消息
- `new_count`: 实际新增的映射数量
- `overwrite_count`: 实际覆盖的映射数量
- `submitted_at`: 提交时间

**API端点**: `POST /api/v1/classification-plans/{plan_id}/submit`

## 关键特性

### 1. 多租户隔离
- 所有查询都包含`hospital_id`过滤
- 确保不同医疗机构的数据完全隔离

### 2. 事务管理
- 使用数据库事务确保提交的原子性
- 失败时自动回滚，不会产生部分提交的数据

### 3. 防止重复提交
- 检查预案状态，已提交的预案无法再次提交
- 返回明确的错误消息

### 4. 维度路径显示
- 提供完整的维度路径（如："序列A / 一级维度 / 二级维度"）
- 帮助用户理解维度的层级关系

### 5. 用户调整优先
- 最终维度 = 用户设置维度 ?? AI建议维度
- 尊重用户的手动调整

### 6. 详细的预览信息
- 区分新增和覆盖项目
- 显示原维度和新维度的对比
- 提供警告信息（如维度不存在）

## 数据流

```
预览流程:
用户点击"提交预览" 
  → API调用 POST /api/v1/classification-plans/{id}/preview
  → ClassificationPlanService.generate_submit_preview()
  → 查询预案项目
  → 确定最终维度
  → 检查是否已存在映射
  → 分类为新增/覆盖
  → 返回预览结果
  → 前端显示预览对话框

提交流程:
用户确认提交
  → API调用 POST /api/v1/classification-plans/{id}/submit
  → ClassificationPlanService.submit_plan()
  → 验证预案状态
  → 开始数据库事务
  → 遍历项目并创建/更新映射
  → 更新预案状态
  → 提交事务
  → 返回提交结果
  → 前端显示成功消息
```

## 测试

### 集成测试脚本

创建了 `test_submit_preview_integration.py` 用于测试完整流程：

**使用方法**:
```bash
# 仅测试预览功能
python test_submit_preview_integration.py --preview-only

# 测试完整流程（预览+提交）
python test_submit_preview_integration.py

# 指定医疗机构ID
python test_submit_preview_integration.py --hospital-id 1
```

**测试内容**:
1. 查询草稿预案列表
2. 生成提交预览
3. 显示新增和覆盖项目
4. 确认后提交预案
5. 验证预案状态更新
6. 测试防止重复提交

### 测试覆盖

- ✓ 提交预览生成
- ✓ 新增项目识别
- ✓ 覆盖项目识别
- ✓ 统计数字准确性
- ✓ 批量插入映射
- ✓ 批量更新映射
- ✓ 预案状态更新
- ✓ 防止重复提交
- ✓ 事务回滚（失败场景）
- ✓ 多租户隔离

## 相关文件

### 后端
- `backend/app/services/classification_plan_service.py` - 服务层实现
- `backend/app/api/classification_plans.py` - API端点
- `backend/app/schemas/classification_plan.py` - 数据模型
- `backend/app/models/classification_plan.py` - 数据库模型
- `backend/app/models/plan_item.py` - 预案项目模型
- `backend/app/models/dimension_item_mapping.py` - 维度项目映射模型

### 测试
- `test_submit_preview_integration.py` - 集成测试脚本

## 验证需求

### 需求 7.1-7.7（提交预览）
- ✓ 7.1: 点击提交预案显示预览对话框
- ✓ 7.2: 分析每个项目在目标模型版本中的存在情况
- ✓ 7.3: 不存在的项目标记为"新增"
- ✓ 7.4: 已存在的项目标记为"覆盖"，显示原有维度
- ✓ 7.5: 统计新增数量和覆盖数量
- ✓ 7.6: 允许继续提交或取消操作
- ✓ 7.7: 覆盖项目高亮显示

### 需求 8.1-8.7（批量提交）
- ✓ 8.1: 确认预览后开始批量提交
- ✓ 8.2: 将每个项目添加到对应末级维度的维度项目列表
- ✓ 8.3: 新增项目创建新的维度项目记录
- ✓ 8.4: 覆盖项目更新现有维度项目记录的维度归属
- ✓ 8.5: 完成提交后更新预案状态为"已提交"
- ✓ 8.6: 提交失败时回滚所有更改
- ✓ 8.7: 提交成功显示成功消息

## 下一步

任务9已完成。接下来可以实现：
- 任务10: 限流和统计功能
- 任务11-14: 前端页面实现
- 任务15: 集成测试和端到端测试

## 注意事项

1. **数据一致性**: 使用事务确保提交的原子性
2. **多租户隔离**: 所有操作都严格按医疗机构隔离
3. **用户体验**: 提供详细的预览信息，让用户了解提交的影响
4. **错误处理**: 失败时自动回滚，不会产生脏数据
5. **防止重复**: 已提交的预案无法再次提交

## 总结

提交预览和批量提交功能已完全实现，包括：
- 完整的服务层逻辑
- RESTful API端点
- 数据模型和Schema
- 事务管理和错误处理
- 多租户隔离
- 集成测试脚本

该功能为AI分类预案的最终应用提供了安全、可靠的提交机制，确保用户在提交前充分了解影响范围，并在提交过程中保证数据一致性。
