"""
修复汇总SQL，支持负值维度（如成本）
将 WHERE agg.score > 0 改为 WHERE agg.score != 0
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

def fix_aggregation_sql():
    """修复汇总SQL"""
    with engine.connect() as conn:
        # 获取当前的SQL
        result = conn.execute(text("""
            SELECT id, code_content 
            FROM calculation_steps 
            WHERE id IN (85, 89)
        """))
        
        for row in result:
            step_id = row[0]
            old_sql = row[1]
            
            # 检查是否包含需要修改的条件
            if 'WHERE agg.score > 0' in old_sql:
                print(f"\n步骤 {step_id} 需要修改")
                
                # 替换条件
                new_sql = old_sql.replace(
                    'WHERE agg.score > 0  -- 只插入有价值的记录',
                    'WHERE agg.score != 0  -- 只插入有价值的记录（包括负值）'
                )
                
                # 如果没有注释，也尝试替换
                if new_sql == old_sql:
                    new_sql = old_sql.replace(
                        'WHERE agg.score > 0',
                        'WHERE agg.score != 0'
                    )
                
                if new_sql != old_sql:
                    # 更新SQL
                    conn.execute(text("""
                        UPDATE calculation_steps
                        SET code_content = :new_sql,
                            updated_at = NOW()
                        WHERE id = :step_id
                    """), {"new_sql": new_sql, "step_id": step_id})
                    
                    print(f"  ✓ 步骤 {step_id} 已更新")
                else:
                    print(f"  ⚠ 步骤 {step_id} 未找到匹配的条件")
            else:
                print(f"\n步骤 {step_id} 不需要修改")
        
        conn.commit()
        print("\n✓ 修复完成")

if __name__ == "__main__":
    try:
        fix_aggregation_sql()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
