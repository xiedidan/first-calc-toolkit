"""
创建参考价值表
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"

engine = create_engine(DATABASE_URL)

# 分开执行每个语句
statements = [
    """
    CREATE TABLE IF NOT EXISTS reference_values (
        id SERIAL PRIMARY KEY,
        hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
        period VARCHAR(7) NOT NULL,
        department_code VARCHAR(50) NOT NULL,
        department_name VARCHAR(100) NOT NULL,
        reference_value NUMERIC(18, 4) NOT NULL,
        doctor_reference_value NUMERIC(18, 4),
        nurse_reference_value NUMERIC(18, 4),
        tech_reference_value NUMERIC(18, 4),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_reference_values_hospital_id ON reference_values(hospital_id)",
    "CREATE INDEX IF NOT EXISTS ix_reference_values_period ON reference_values(period)",
    "CREATE INDEX IF NOT EXISTS ix_reference_values_department_code ON reference_values(department_code)",
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'uq_reference_value_hospital_period_dept') THEN
            CREATE UNIQUE INDEX uq_reference_value_hospital_period_dept 
            ON reference_values(hospital_id, period, department_code);
        END IF;
    END $$
    """
]

with engine.connect() as conn:
    for statement in statements:
        try:
            conn.execute(text(statement))
            conn.commit()
            print(f"OK: {statement[:60].strip()}...")
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")

print("Done!")
