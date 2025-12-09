-- 创建科室收入表
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
);

COMMENT ON TABLE department_revenues IS '科室收入表';
COMMENT ON COLUMN department_revenues.year_month IS '年月，格式：YYYY-MM';
COMMENT ON COLUMN department_revenues.department_code IS '科室代码';
COMMENT ON COLUMN department_revenues.department_name IS '科室名称';
COMMENT ON COLUMN department_revenues.revenue IS '收入金额';

-- 创建科室收入基准表
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
);

COMMENT ON TABLE revenue_benchmarks IS '科室收入基准表';
COMMENT ON COLUMN revenue_benchmarks.department_code IS '科室代码';
COMMENT ON COLUMN revenue_benchmarks.department_name IS '科室名称';
COMMENT ON COLUMN revenue_benchmarks.version_id IS '模型版本ID';
COMMENT ON COLUMN revenue_benchmarks.version_name IS '模型版本名称';
COMMENT ON COLUMN revenue_benchmarks.benchmark_revenue IS '基准收入';
