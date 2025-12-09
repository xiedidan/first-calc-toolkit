"""
生成科室收入数据和收入基准数据
1. 从 charge_details 统计各科室的当期总收入
2. 基于当期收入，随机上下浮动10%生成收入基准
"""
import random
from decimal import Decimal
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

HOSPITAL_ID = 1
YEAR_MONTH = "2025-10"
VERSION_ID = 23
VERSION_NAME = "2025年迭代版-宁波眼科v1.4"

def generate_revenue_data():
    """生成收入数据"""
    with engine.connect() as conn:
        print("1. 从 charge_details 统计各科室的当期总收入...")
        
        # 统计各科室收入
        result = conn.execute(text("""
            SELECT 
                cd.prescribing_dept_code as dept_code,
                d.his_name as dept_name,
                SUM(cd.amount) as total_revenue
            FROM charge_details cd
            JOIN departments d ON cd.prescribing_dept_code = d.his_code
            WHERE cd.charge_time >= :start_date
              AND cd.charge_time < DATE :end_date + INTERVAL '1 day'
              AND d.hospital_id = :hospital_id
              AND d.is_active = TRUE
            GROUP BY cd.prescribing_dept_code, d.his_name
            HAVING SUM(cd.amount) > 0
            ORDER BY cd.prescribing_dept_code
        """), {
            "start_date": f"{YEAR_MONTH}-01",
            "end_date": f"{YEAR_MONTH}-31",
            "hospital_id": HOSPITAL_ID
        })
        
        revenues = result.fetchall()
        print(f"   找到 {len(revenues)} 个科室有收入数据")
        
        if not revenues:
            print("   ⚠ 没有找到收入数据，请检查 charge_details 表")
            return
        
        # 2. 插入科室收入数据
        print("\n2. 插入科室收入数据...")
        revenue_records = []
        for dept_code, dept_name, revenue in revenues:
            revenue_records.append({
                "hospital_id": HOSPITAL_ID,
                "year_month": YEAR_MONTH,
                "department_code": dept_code,
                "department_name": dept_name,
                "revenue": revenue
            })
        
        insert_revenue_sql = text("""
            INSERT INTO department_revenues 
            (hospital_id, year_month, department_code, department_name, revenue, created_at, updated_at)
            VALUES 
            (:hospital_id, :year_month, :department_code, :department_name, :revenue, NOW(), NOW())
            ON CONFLICT (hospital_id, year_month, department_code)
            DO UPDATE SET
                department_name = EXCLUDED.department_name,
                revenue = EXCLUDED.revenue,
                updated_at = NOW()
        """)
        
        conn.execute(insert_revenue_sql, revenue_records)
        conn.commit()
        print(f"   ✓ 插入了 {len(revenue_records)} 条收入记录")
        
        # 3. 生成收入基准数据（基于当期收入随机浮动±10%）
        # 注意：收入基准使用核算单元代码，而不是HIS代码
        print("\n3. 生成收入基准数据...")
        
        # 先获取HIS代码到核算单元代码的映射
        result = conn.execute(text("""
            SELECT his_code, accounting_unit_code, his_name
            FROM departments
            WHERE hospital_id = :hospital_id
              AND is_active = TRUE
              AND accounting_unit_code IS NOT NULL
        """), {"hospital_id": HOSPITAL_ID})
        
        his_to_accounting = {row[0]: (row[1], row[2]) for row in result.fetchall()}
        
        benchmark_records = []
        for dept_code, dept_name, revenue in revenues:
            # 获取核算单元代码
            if dept_code in his_to_accounting:
                accounting_code, accounting_name = his_to_accounting[dept_code]
                
                # 随机浮动±10%
                fluctuation = random.uniform(-0.10, 0.10)
                benchmark_revenue = float(revenue) * (1 + fluctuation)
                
                benchmark_records.append({
                    "hospital_id": HOSPITAL_ID,
                    "department_code": accounting_code,  # 使用核算单元代码
                    "department_name": accounting_name,
                    "version_id": VERSION_ID,
                    "version_name": VERSION_NAME,
                    "benchmark_revenue": round(Decimal(str(benchmark_revenue)), 2)
                })
            else:
                print(f"   ⚠ 科室 {dept_code} ({dept_name}) 没有核算单元代码，跳过")
        
        insert_benchmark_sql = text("""
            INSERT INTO revenue_benchmarks 
            (hospital_id, department_code, department_name, version_id, version_name, 
             benchmark_revenue, created_at, updated_at)
            VALUES 
            (:hospital_id, :department_code, :department_name, :version_id, :version_name,
             :benchmark_revenue, NOW(), NOW())
            ON CONFLICT (hospital_id, department_code, version_id)
            DO UPDATE SET
                department_name = EXCLUDED.department_name,
                version_name = EXCLUDED.version_name,
                benchmark_revenue = EXCLUDED.benchmark_revenue,
                updated_at = NOW()
        """)
        
        conn.execute(insert_benchmark_sql, benchmark_records)
        conn.commit()
        print(f"   ✓ 插入了 {len(benchmark_records)} 条收入基准记录")
        
        # 4. 验证数据
        print("\n4. 验证数据...")
        
        # 验证收入数据
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as count,
                MIN(revenue) as min_revenue,
                MAX(revenue) as max_revenue,
                AVG(revenue) as avg_revenue
            FROM department_revenues
            WHERE hospital_id = :hospital_id
              AND year_month = :year_month
        """), {"hospital_id": HOSPITAL_ID, "year_month": YEAR_MONTH})
        
        row = result.fetchone()
        print(f"   科室收入: {row[0]}条记录")
        print(f"   范围: {float(row[1]):.2f} - {float(row[2]):.2f}")
        print(f"   平均: {float(row[3]):.2f}")
        
        # 验证收入基准数据
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as count,
                MIN(benchmark_revenue) as min_benchmark,
                MAX(benchmark_revenue) as max_benchmark,
                AVG(benchmark_revenue) as avg_benchmark
            FROM revenue_benchmarks
            WHERE hospital_id = :hospital_id
              AND version_id = :version_id
        """), {"hospital_id": HOSPITAL_ID, "version_id": VERSION_ID})
        
        row = result.fetchone()
        print(f"\n   收入基准: {row[0]}条记录")
        print(f"   范围: {float(row[1]):.2f} - {float(row[2]):.2f}")
        print(f"   平均: {float(row[3]):.2f}")
        
        # 对比收入和基准
        print("\n5. 对比收入和基准（前10个科室）...")
        result = conn.execute(text("""
            SELECT 
                dr.department_name,
                dr.revenue,
                rb.benchmark_revenue,
                (rb.benchmark_revenue - dr.revenue) / dr.revenue * 100 as diff_pct
            FROM department_revenues dr
            JOIN departments d ON 
                dr.department_code = d.his_code
                AND dr.hospital_id = d.hospital_id
            JOIN revenue_benchmarks rb ON 
                rb.hospital_id = d.hospital_id
                AND rb.department_code = d.accounting_unit_code
                AND rb.version_id = :version_id
            WHERE dr.hospital_id = :hospital_id
              AND dr.year_month = :year_month
            ORDER BY dr.department_name
            LIMIT 10
        """), {
            "hospital_id": HOSPITAL_ID,
            "year_month": YEAR_MONTH,
            "version_id": VERSION_ID
        })
        
        print(f"   {'科室':<20} {'当期收入':<15} {'收入基准':<15} {'差异%':<10}")
        print("   " + "-" * 65)
        for row in result:
            print(f"   {row[0]:<20} {float(row[1]):<15.2f} {float(row[2]):<15.2f} {float(row[3]):<10.2f}%")

if __name__ == "__main__":
    try:
        generate_revenue_data()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
