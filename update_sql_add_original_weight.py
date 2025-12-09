#!/usr/bin/env python3
"""
批量更新SQL模板，在INSERT calculation_results时添加original_weight字段
"""
import re
from pathlib import Path

def update_sql_file(filepath):
    """更新单个SQL文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 模式1: INSERT后面的字段列表（添加original_weight）
    pattern1 = r'(INSERT INTO calculation_results \(\s*task_id,\s*node_id,\s*department_id,\s*node_type,\s*node_name,\s*node_code,\s*parent_id,\s*workload,\s*weight,)\s*(value,\s*created_at\s*\))'
    replacement1 = r'\1\n    original_weight,\n    \2'
    
    # 模式2: SELECT后面的值列表（添加mn.weight as original_weight）
    pattern2 = r'(\s+mn\.weight,)\s*(\n\s+(?:COALESCE\()?SUM\([^)]+\)(?:\))?[^,]*\s+\*\s+mn\.weight as value,)'
    replacement2 = r'\1\n    mn.weight as original_weight,\2'
    
    # 应用替换
    new_content = re.sub(pattern1, replacement1, content)
    new_content = re.sub(pattern2, replacement2, new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# 需要更新的文件列表
files_to_update = [
    'backend/standard_workflow_templates/step3b_indicator_calculation.sql',
    'backend/standard_workflow_templates/step5_value_aggregation.sql',
]

updated_count = 0
for filepath in files_to_update:
    path = Path(filepath)
    if path.exists():
        if update_sql_file(path):
            print(f"✓ 已更新: {filepath}")
            updated_count += 1
        else:
            print(f"- 无需更新: {filepath}")
    else:
        print(f"✗ 文件不存在: {filepath}")

print(f"\n总计更新了 {updated_count} 个文件")
