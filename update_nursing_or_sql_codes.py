"""
更新步骤118的SQL，将手术室护理维度代码从完整代码改为简化代码
dim-nur-proc-or-* → dim-nur-or-*
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = 'postgresql://root:root@47.108.227.254:50016/hospital_value'
engine = create_engine(DATABASE_URL)

def main():
    print("更新步骤118的手术室护理维度代码...")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. 获取当前SQL
        result = conn.execute(text("""
            SELECT id, code_content
            FROM calculation_steps
            WHERE workflow_id = 31 AND sort_order = 2.00
        """))
        row = result.fetchone()
        
        if not row:
            print("❌ 未找到步骤118")
            return
        
        step_id = row[0]
        current_sql = row[1]
        
        print(f"✓ 找到步骤ID: {step_id}")
        print(f"✓ 当前SQL长度: {len(current_sql)} 字符")
        
        # 2. 替换代码
        # 将 dim-nur-proc-or-* 替换为 dim-nur-or-*
        updated_sql = current_sql.replace(
            "mn.code = 'dim-nur-proc-or-large'",
            "mn.code = 'dim-nur-or-large'"
        ).replace(
            "mn.code = 'dim-nur-proc-or-mid'",
            "mn.code = 'dim-nur-or-mid'"
        ).replace(
            "mn.code = 'dim-nur-proc-or-tiny'",
            "mn.code = 'dim-nur-or-tiny'"
        )
        
        # 检查是否有变化
        if updated_sql == current_sql:
            print("\n⚠ SQL中没有找到需要替换的代码")
            print("   搜索: dim-nur-proc-or-large/mid/tiny")
            return
        
        print(f"\n✓ 更新后SQL长度: {len(updated_sql)} 字符")
        print("\n替换内容:")
        print("  dim-nur-proc-or-large → dim-nur-or-large")
        print("  dim-nur-proc-or-mid   → dim-nur-or-mid")
        print("  dim-nur-proc-or-tiny  → dim-nur-or-tiny")
        
        # 3. 更新步骤
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": updated_sql, "step_id": step_id})
        
        conn.commit()
        
        print("\n✅ 成功更新SQL代码")
        print("\n⚠ 注意: 需要重新运行计算任务才能看到手术室护理数据")

if __name__ == "__main__":
    main()
