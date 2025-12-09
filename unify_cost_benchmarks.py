"""
统一成本基准值
将同一科室、同一维度的基准值统一为医生序列的取值
例如：护理-成本-人员经费 和 医技-成本-人员经费 都使用 医生-成本-人员经费 的值
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

VERSION_ID = 23
HOSPITAL_ID = 1

# 维度映射：将护理和医技的维度代码映射到医生的维度代码
DIMENSION_MAPPING = {
    # 人员经费
    'dim-nur-cost-hr': 'dim-doc-cost-hr',
    'dim-tech-cost-hr': 'dim-doc-cost-hr',
    # 其他费用
    'dim-nur-cost-other': 'dim-doc-cost-other',
    'dim-tech-cost-other': 'dim-doc-cost-other',
    # 不收费卫生材料费
    'dim-nur-cost-mat': 'dim-doc-cost-mat',
    'dim-tech-cost-mat': 'dim-doc-cost-mat',
    # 折旧（风险）费
    'dim-nur-cost-depr': 'dim-doc-cost-depr',
    'dim-tech-cost-depr': 'dim-doc-cost-depr',
}

def unify_benchmarks():
    """统一成本基准值"""
    with engine.connect() as conn:
        print("开始统一成本基准值...")
        
        # 对每个需要统一的维度进行处理
        total_updated = 0
        for target_dim, source_dim in DIMENSION_MAPPING.items():
            print(f"\n处理维度: {target_dim} -> {source_dim}")
            
            # 更新SQL：将目标维度的基准值更新为源维度（医生）的基准值
            update_sql = text("""
                UPDATE cost_benchmarks target
                SET benchmark_value = source.benchmark_value,
                    updated_at = NOW()
                FROM cost_benchmarks source
                WHERE target.hospital_id = :hospital_id
                  AND target.version_id = :version_id
                  AND target.dimension_code = :target_dim
                  AND source.hospital_id = :hospital_id
                  AND source.version_id = :version_id
                  AND source.dimension_code = :source_dim
                  AND target.department_code = source.department_code
                  AND target.benchmark_value != source.benchmark_value
            """)
            
            result = conn.execute(update_sql, {
                "hospital_id": HOSPITAL_ID,
                "version_id": VERSION_ID,
                "target_dim": target_dim,
                "source_dim": source_dim
            })
            
            updated_count = result.rowcount
            total_updated += updated_count
            print(f"  更新了 {updated_count} 条记录")
        
        conn.commit()
        print(f"\n✓ 统一完成，共更新 {total_updated} 条记录")
        
        # 验证结果：检查同一科室、同一类型维度的基准值是否一致
        print("\n验证结果（抽样检查）：")
        verify_sql = text("""
            SELECT 
                cb1.department_code,
                cb1.department_name,
                cb1.dimension_code as doc_dim,
                cb1.benchmark_value as doc_value,
                cb2.dimension_code as nur_dim,
                cb2.benchmark_value as nur_value,
                cb3.dimension_code as tech_dim,
                cb3.benchmark_value as tech_value,
                CASE 
                    WHEN cb1.benchmark_value = cb2.benchmark_value 
                     AND cb1.benchmark_value = cb3.benchmark_value 
                    THEN '✓ 一致'
                    ELSE '✗ 不一致'
                END as status
            FROM cost_benchmarks cb1
            LEFT JOIN cost_benchmarks cb2 ON 
                cb1.department_code = cb2.department_code 
                AND cb1.hospital_id = cb2.hospital_id
                AND cb1.version_id = cb2.version_id
                AND cb2.dimension_code = 'dim-nur-cost-hr'
            LEFT JOIN cost_benchmarks cb3 ON 
                cb1.department_code = cb3.department_code 
                AND cb1.hospital_id = cb3.hospital_id
                AND cb1.version_id = cb3.version_id
                AND cb3.dimension_code = 'dim-tech-cost-hr'
            WHERE cb1.hospital_id = :hospital_id
              AND cb1.version_id = :version_id
              AND cb1.dimension_code = 'dim-doc-cost-hr'
            ORDER BY cb1.department_code
            LIMIT 5
        """)
        
        result = conn.execute(verify_sql, {
            "hospital_id": HOSPITAL_ID,
            "version_id": VERSION_ID
        })
        
        print(f"\n{'科室':<15} {'医生值':<12} {'护理值':<12} {'医技值':<12} {'状态'}")
        print("-" * 70)
        for row in result:
            doc_val = float(row[3]) if row[3] else 0
            nur_val = float(row[5]) if row[5] else 0
            tech_val = float(row[7]) if row[7] else 0
            print(f"{row[1]:<15} {doc_val:<12.2f} {nur_val:<12.2f} {tech_val:<12.2f} {row[8]}")

if __name__ == "__main__":
    try:
        unify_benchmarks()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
