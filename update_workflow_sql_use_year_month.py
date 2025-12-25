"""
更新计算流程SQL，使用year_month字段替代TO_CHAR函数

优化效果：
- 避免每行数据都执行TO_CHAR函数转换
- 可以利用year_month字段上的索引
"""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)


def update_workflow_sql():
    """更新计算流程SQL"""
    with engine.connect() as conn:
        # 查找使用TO_CHAR的步骤
        result = conn.execute(text("""
            SELECT id, name, code_content 
            FROM calculation_steps 
            WHERE code_content LIKE '%TO_CHAR(cd.charge_time%'
            ORDER BY id
        """))
        
        steps = result.fetchall()
        print(f"找到 {len(steps)} 个需要更新的步骤")
        
        for step_id, name, sql in steps:
            print(f"\n更新步骤 {step_id}: {name}")
            
            # 替换TO_CHAR为year_month
            new_sql = sql.replace(
                "TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'",
                "cd.year_month = '{current_year_month}'"
            )
            
            # 检查是否有变化
            if new_sql == sql:
                print("  无需更新")
                continue
            
            # 更新数据库
            conn.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :sql, updated_at = NOW()
                WHERE id = :step_id
            """), {"sql": new_sql, "step_id": step_id})
            
            print("  已更新")
        
        conn.commit()
        print("\n所有步骤更新完成")


def verify_update():
    """验证更新结果"""
    with engine.connect() as conn:
        # 检查是否还有使用TO_CHAR的步骤
        result = conn.execute(text("""
            SELECT id, name 
            FROM calculation_steps 
            WHERE code_content LIKE '%TO_CHAR(cd.charge_time%'
        """))
        
        remaining = result.fetchall()
        if remaining:
            print(f"警告：还有 {len(remaining)} 个步骤使用TO_CHAR:")
            for step_id, name in remaining:
                print(f"  - {step_id}: {name}")
        else:
            print("验证通过：所有步骤已更新为使用year_month字段")
        
        # 检查使用year_month的步骤
        result = conn.execute(text("""
            SELECT id, name 
            FROM calculation_steps 
            WHERE code_content LIKE '%cd.year_month%'
        """))
        
        updated = result.fetchall()
        print(f"\n使用year_month字段的步骤 ({len(updated)} 个):")
        for step_id, name in updated:
            print(f"  - {step_id}: {name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_update()
    else:
        update_workflow_sql()
        print()
        verify_update()
