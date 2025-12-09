-- 创建参考价值表
-- 用于存储各科室每月的参考价值数据

CREATE TABLE IF NOT EXISTS reference_values (
    id SERIAL PRIMARY KEY,
    hospital_id INTEGER NOT NULL REFERENCES hospitals(id) ON DELETE CASCADE,
    period VARCHAR(7) NOT NULL,  -- 年月，格式：YYYY-MM
    department_code VARCHAR(50) NOT NULL,  -- 科室代码
    department_name VARCHAR(100) NOT NULL,  -- 科室名称
    reference_value NUMERIC(18, 4) NOT NULL,  -- 参考总价值
    doctor_reference_value NUMERIC(18, 4),  -- 医生参考价值（可为空）
    nurse_reference_value NUMERIC(18, 4),  -- 护理参考价值（可为空）
    tech_reference_value NUMERIC(18, 4),  -- 医技参考价值（可为空）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_reference_values_hospital_id ON reference_values(hospital_id);
CREATE INDEX IF NOT EXISTS ix_reference_values_period ON reference_values(period);
CREATE INDEX IF NOT EXISTS ix_reference_values_department_code ON reference_values(department_code);

-- 创建唯一约束：同一医院、同一月份、同一科室只能有一条记录
CREATE UNIQUE INDEX IF NOT EXISTS uq_reference_value_hospital_period_dept 
ON reference_values(hospital_id, period, department_code);

-- 添加表注释
COMMENT ON TABLE reference_values IS '参考价值表';
COMMENT ON COLUMN reference_values.hospital_id IS '医疗机构ID';
COMMENT ON COLUMN reference_values.period IS '年月，格式：YYYY-MM';
COMMENT ON COLUMN reference_values.department_code IS '科室代码';
COMMENT ON COLUMN reference_values.department_name IS '科室名称';
COMMENT ON COLUMN reference_values.reference_value IS '参考总价值';
COMMENT ON COLUMN reference_values.doctor_reference_value IS '医生参考价值';
COMMENT ON COLUMN reference_values.nurse_reference_value IS '护理参考价值';
COMMENT ON COLUMN reference_values.tech_reference_value IS '医技参考价值';
