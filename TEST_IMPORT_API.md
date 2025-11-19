# 模型版本导入API测试

## 问题诊断

API返回422错误，可能的原因：

1. **当前用户没有hospital_id** - 最可能的原因
   - `get_current_hospital_id_or_raise()` 会抛出异常
   - 需要确保当前登录用户有hospital_id

2. **参数验证失败** - 不太可能
   - skip和limit都有默认值
   - search是可选的

## 解决方案

### 方案1：确保用户有hospital_id

检查当前登录用户是否有hospital_id：

```sql
SELECT id, username, hospital_id FROM users WHERE username = 'your_username';
```

如果hospital_id为NULL，需要更新：

```sql
UPDATE users 
SET hospital_id = (SELECT id FROM hospitals LIMIT 1)
WHERE username = 'your_username';
```

### 方案2：修改API使其更健壮

如果用户没有hospital_id，可以返回空列表而不是抛出异常：

```python
@router.get("/importable", response_model=ImportableVersionListResponse)
def get_importable_versions(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取可导入的模型版本列表（其他医疗机构的版本）"""
    try:
        # 获取当前医疗机构ID
        current_hospital_id = get_current_hospital_id_or_raise()
    except HTTPException:
        # 如果用户没有hospital_id，返回空列表
        return {"total": 0, "items": []}
    
    # ... 其余代码
```

## 测试步骤

1. 检查当前用户的hospital_id
2. 如果为NULL，更新用户的hospital_id
3. 重新测试API
4. 如果还有问题，查看后端详细日志

## 预期行为

- 如果当前医疗机构只有一个，应该返回空列表（因为没有其他医疗机构）
- 如果有多个医疗机构，应该返回其他医疗机构的版本列表
