"""
创建科室收入表和科室收入基准表
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

def create_tables():
    """创建表"""
    with engine.connect() as conn:
        # 创建科室收入表
        print("创建科室收入表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS department_revenues (
                id SERIAL PRIMARY KEY,
                hospital_id INTEGER NOT NULL,
                year_month VARCHAR(7) NOT NULL,
                department_code VARCHAR(50) NOT NULL,
                department_name VARCHAR(100) NOT NULL,
                revenue NUMERIC(20, 2) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_dept_revenue_hospital_month_dept UNIQUE (hospital_id, year_month, department_code)
            )
        """))
        print("  ✓ department_revenues 表已创建")
        
        # 创建科室收入基准表
        print("\n创建科室收入基准表...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS revenue_benchmarks (
                id SERIAL PRIMARY KEY,
                hospital_id INTEGER NOT NULL,
                department_code VARCHAR(50) NOT NULL,
                department_name VARCHAR(100) NOT NULL,
                version_id INTEGER NOT NULL,
                version_name VARCHAR(200) NOT NULL,
                benchmark_revenue NUMERIC(20, 2) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_revenue_benchmark_hospital_dept_version UNIQUE (hospital_id, department_code, version_id),
                CONSTRAINT fk_revenue_benchmarks_version FOREIGN KEY (version_id) REFERENCES model_versions(id) ON DELETE CASCADE
            )
        """))
        print("  ✓ revenue_benchmarks 表已创建")
        
        conn.commit()
        print("\n✓ 所有表创建完成")

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
