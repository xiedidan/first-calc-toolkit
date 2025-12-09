#!/usr/bin/env python3
"""
更新数据库中已有工作流步骤的SQL代码，添加original_weight字段
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text

# 从环境变量读取数据库连接
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://root:root@47.108.227.254:50016/hospital_value')

def update_workflow_steps():
    """更新数据库中的工作流步骤"""
    engine = create_engine(DATABASE_URL)
    
    # 需要更新的步骤：中文名称 -> 文件路径
    step_files = {
        '维度目录统计': 'standard_workflow_templates/step2_dimension_catalog.sql',
        '指标计算-护理床日数': 'standard_workflow_templates/step3b_indicator_calculation.sql',
        '业务价值汇总': 'standard_workflow_templates/step5_value_aggregation.sql',
    }
    
    updated_count = 0
    
    with engine.connect() as conn:
        for step_name, file_path in step_files.items():
            # 读取更新后的SQL文件
            sql_file = Path(file_path)
            if not sql_file.exists():
                print(f"✗ 文件不存在: {file_path}")
                continue
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                new_sql_content = f.read()
            
            # 更新数据库中的步骤（通过name精确匹配）
            result = conn.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :new_content,
                    updated_at = NOW()
                WHERE code_type = 'sql' 
                  AND name = :step_name
                RETURNING id, name
            """), {
                'new_content': new_sql_content,
                'step_name': step_name
            })
            
            updated_rows = result.fetchall()
            if updated_rows:
                for row in updated_rows:
                    print(f"✓ 已更新步骤 ID={row[0]}: {row[1]}")
                    updated_count += 1
            else:
                print(f"- 未找到匹配的步骤: {step_name}")
        
        # 提交事务
        conn.commit()
    
    print(f"\n总计更新了 {updated_count} 个步骤")
    return updated_count

if __name__ == '__main__':
    try:
        count = update_workflow_steps()
        if count > 0:
            print("\n✓ 工作流步骤更新成功！")
        else:
            print("\n⚠ 没有找到需要更新的步骤")
    except Exception as e:
        print(f"\n✗ 更新失败: {e}")
        import traceback
        traceback.print_exc()
