"""
修复 cost_values 表
1. 删除刚才生成的测试数据（人员经费、其他费用）
2. 修正 dimension_name 字段，使其与 dimension_code 对应的 model_nodes.name 一致
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

HOSPITAL_ID = 1
YEAR_MONTH = "2025-10"

def fix_cost_values():
    """修复成本值数据"""
    with engine.connect() as conn:
        # 1. 删除刚才生成的测试数据
        print("1. 删除测试数据（人员经费、其他费用）...")
        delete_sql = text("""
            DELETE FROM cost_values
            WHERE hospital_id = :hospital_id
              AND year_month = :year_month
              AND dimension_name IN ('人员经费', '其他费用')
        """)
        
        result = conn.execute(delete_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        deleted_count = result.rowcount
        conn.commit()
        print(f"   ✓ 删除了 {deleted_count} 条测试数据")
        
        # 2. 查看当前的 dimension_name 和 dimension_code
        print("\n2. 检查当前数据...")
        check_sql = text("""
            SELECT DISTINCT dimension_code, dimension_name
            FROM cost_values
            WHERE hospital_id = :hospital_id
              AND year_month = :year_month
            ORDER BY dimension_code
        """)
        
        result = conn.execute(check_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        
        print("   当前的维度代码和名称：")
        for row in result:
            print(f"   {row[0]:<20} -> {row[1]}")
        
        # 3. 从 model_nodes 获取正确的维度名称并更新
        print("\n3. 修正 dimension_name 字段...")
        update_sql = text("""
            UPDATE cost_values cv
            SET dimension_name = mn.name,
                updated_at = NOW()
            FROM model_nodes mn
            JOIN model_versions mv ON mn.version_id = mv.id
            WHERE cv.dimension_code = mn.code
              AND mn.node_type = 'dimension'
              AND mv.hospital_id = :hospital_id
              AND mv.is_active = TRUE
              AND cv.hospital_id = :hospital_id
              AND cv.year_month = :year_month
              AND cv.dimension_name != mn.name
        """)
        
        result = conn.execute(update_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        updated_count = result.rowcount
        conn.commit()
        print(f"   ✓ 更新了 {updated_count} 条记录")
        
        # 4. 验证修正结果
        print("\n4. 验证修正结果...")
        verify_sql = text("""
            SELECT DISTINCT 
                cv.dimension_code, 
                cv.dimension_name,
                mn.name as correct_name,
                CASE 
                    WHEN cv.dimension_name = mn.name THEN '✓ 正确'
                    ELSE '✗ 不匹配'
                END as status
            FROM cost_values cv
            LEFT JOIN model_nodes mn ON 
                cv.dimension_code = mn.code 
                AND mn.node_type = 'dimension'
            LEFT JOIN model_versions mv ON 
                mn.version_id = mv.id
                AND mv.hospital_id = :hospital_id
                AND mv.is_active = TRUE
            WHERE cv.hospital_id = :hospital_id
              AND cv.year_month = :year_month
            ORDER BY cv.dimension_code
        """)
        
        result = conn.execute(verify_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        
        print(f"   {'维度代码':<20} {'当前名称':<15} {'正确名称':<15} {'状态'}")
        print("   " + "-" * 70)
        for row in result:
            print(f"   {row[0]:<20} {row[1]:<15} {row[2] or 'N/A':<15} {row[3]}")
        
        # 5. 统计最终数据
        print("\n5. 最终数据统计...")
        stats_sql = text("""
            SELECT 
                dimension_name,
                COUNT(*) as count,
                MIN(cost_value) as min_val,
                MAX(cost_value) as max_val,
                AVG(cost_value) as avg_val
            FROM cost_values
            WHERE hospital_id = :hospital_id
              AND year_month = :year_month
            GROUP BY dimension_name
            ORDER BY dimension_name
        """)
        
        result = conn.execute(stats_sql, {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH
        })
        
        print(f"   {'维度名称':<15} {'记录数':<10} {'最小值':<12} {'最大值':<12} {'平均值':<12}")
        print("   " + "-" * 70)
        for row in result:
            print(f"   {row[0]:<15} {row[1]:<10} {float(row[2]):<12.2f} {float(row[3]):<12.2f} {float(row[4]):<12.2f}")

if __name__ == "__main__":
    try:
        fix_cost_values()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
