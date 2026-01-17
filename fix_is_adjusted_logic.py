#!/usr/bin/env python
"""
修复导向调整步骤中 is_adjusted 的判断逻辑

问题：当 adjustment_intensity = 1 时，adjusted_weight = original_weight，
      实际上权重没有变化，但 is_adjusted 仍然显示为 TRUE

修复：只有当 adjustment_intensity 存在且不等于 1 时才标记为已调整
"""

import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def fix_is_adjusted_logic():
    """修复数据库中导向调整步骤的 is_adjusted 判断逻辑"""
    
    print(f"连接数据库: {DATABASE_URL[:50]}...")
    
    with engine.connect() as conn:
        # 查找包含导向调整的步骤
        result = conn.execute(text("""
            SELECT id, workflow_id, name, code_content
            FROM calculation_steps
            WHERE code_content LIKE '%is_adjusted%'
              AND code_content LIKE '%orientation_adjustment%'
        """))
        
        steps = result.fetchall()
        print(f"找到 {len(steps)} 个包含 is_adjusted 的导向调整步骤")
        
        updated_count = 0
        for step in steps:
            step_id = step.id
            workflow_id = step.workflow_id
            name = step.name
            sql = step.code_content
            
            print(f"\n处理步骤 {step_id} (工作流 {workflow_id}): {name}")
            
            # 检查是否需要修复
            if "adjustment_intensity != 1" in sql or "adjustment_intensity = 1 THEN FALSE" in sql:
                print("  已包含修复逻辑，跳过")
                continue
            
            original_sql = sql
            
            # 修复模式1: (la.adjustment_intensity IS NOT NULL) as is_adjusted
            old_pattern1 = "(la.adjustment_intensity IS NOT NULL) as is_adjusted"
            new_pattern1 = "(la.adjustment_intensity IS NOT NULL AND la.adjustment_intensity != 1) as is_adjusted"
            
            if old_pattern1 in sql:
                sql = sql.replace(old_pattern1, new_pattern1)
                print(f"  修复模式1")
            
            # 修复模式2: CASE WHEN ... ELSE TRUE END as is_adjusted
            # 需要在 ELSE TRUE 前添加 WHEN adjustment_intensity = 1 THEN FALSE
            old_pattern2 = "WHEN lm.adjustment_intensity IS NULL THEN FALSE\n            ELSE TRUE\n        END as is_adjusted"
            new_pattern2 = "WHEN lm.adjustment_intensity IS NULL THEN FALSE\n            WHEN lm.adjustment_intensity = 1 THEN FALSE  -- 管控力度为1时实际未调整\n            ELSE TRUE\n        END as is_adjusted"
            
            if old_pattern2 in sql:
                sql = sql.replace(old_pattern2, new_pattern2)
                print(f"  修复模式2")
            
            # 检查是否有变化
            if sql == original_sql:
                print("  未找到匹配的模式，跳过")
                continue
            
            # 更新数据库
            conn.execute(text("""
                UPDATE calculation_steps
                SET code_content = :sql
                WHERE id = :step_id
            """), {"sql": sql, "step_id": step_id})
            
            updated_count += 1
            print(f"  ✓ 已更新")
        
        conn.commit()
        print(f"\n完成！共更新 {updated_count} 个步骤")

if __name__ == "__main__":
    fix_is_adjusted_logic()
