-- ============================================================================
-- 创建测试数据表 (PostgreSQL 版本)
-- ============================================================================

-- 1. 收费明细表
DROP TABLE IF EXISTS charge_details CASCADE;
CREATE TABLE charge_details (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    prescribing_dept_code VARCHAR(50) NOT NULL,
    item_code VARCHAR(100) NOT NULL,
    item_name VARCHAR(200),
    amount DECIMAL(20, 4) NOT NULL DEFAULT 0,
    quantity DECIMAL(20, 4) NOT NULL DEFAULT 0,
    charge_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_charge_details_dept ON charge_details(prescribing_dept_code);
CREATE INDEX idx_charge_details_item ON charge_details(item_code);
CREATE INDEX idx_charge_details_time ON charge_details(charge_time);

-- 2. 工作量统计表
DROP TABLE IF EXISTS workload_statistics CASCADE;
CREATE TABLE workload_statistics (
    id SERIAL PRIMARY KEY,
    department_code VARCHAR(50) NOT NULL,
    stat_month VARCHAR(7) NOT NULL,
    stat_type VARCHAR(50) NOT NULL,
    stat_level VARCHAR(50),
    stat_value DECIMAL(20, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workload_dept ON workload_statistics(department_code);
CREATE INDEX idx_workload_month ON workload_statistics(stat_month);
CREATE INDEX idx_workload_type ON workload_statistics(stat_type);

-- ============================================================================
-- 插入测试数据
-- ============================================================================

-- 收费明细测试数据
INSERT INTO charge_details (patient_id, prescribing_dept_code, item_code, item_name, amount, quantity, charge_time)
VALUES
    ('P001', 'NK', 'ITEM001', '血常规', 25.00, 1, '2025-10-15 10:30:00'),
    ('P001', 'NK', 'ITEM002', '尿常规', 15.00, 1, '2025-10-15 10:35:00'),
    ('P002', 'NK', 'ITEM001', '血常规', 25.00, 1, '2025-10-16 09:20:00'),
    ('P002', 'NK', 'ITEM003', 'CT检查', 300.00, 1, '2025-10-16 14:00:00'),
    ('P003', 'NK', 'ITEM004', '心电图', 50.00, 1, '2025-10-17 11:00:00'),
    ('P004', 'WK', 'ITEM001', '血常规', 25.00, 1, '2025-10-15 08:00:00'),
    ('P004', 'WK', 'ITEM005', '手术费', 5000.00, 1, '2025-10-15 10:00:00'),
    ('P005', 'WK', 'ITEM003', 'CT检查', 300.00, 1, '2025-10-16 15:30:00'),
    ('P005', 'WK', 'ITEM006', '麻醉费', 800.00, 1, '2025-10-16 16:00:00'),
    ('P006', 'EK', 'ITEM001', '血常规', 25.00, 1, '2025-10-18 09:00:00'),
    ('P006', 'EK', 'ITEM002', '尿常规', 15.00, 1, '2025-10-18 09:10:00'),
    ('P007', 'EK', 'ITEM007', '疫苗接种', 120.00, 1, '2025-10-19 10:00:00');

-- 工作量统计测试数据
INSERT INTO workload_statistics (department_code, stat_month, stat_type, stat_level, stat_value)
VALUES
    ('NK', '2025-10', 'nursing_days', '一级护理', 50),
    ('NK', '2025-10', 'nursing_days', '二级护理', 120),
    ('NK', '2025-10', 'nursing_days', '三级护理', 80),
    ('WK', '2025-10', 'nursing_days', '一级护理', 80),
    ('WK', '2025-10', 'nursing_days', '二级护理', 150),
    ('WK', '2025-10', 'nursing_days', '特级护理', 20),
    ('EK', '2025-10', 'nursing_days', '一级护理', 30),
    ('EK', '2025-10', 'nursing_days', '二级护理', 60),
    ('NK', '2025-10', 'consultation', '发起', 15),
    ('NK', '2025-10', 'consultation', '参与', 25),
    ('WK', '2025-10', 'consultation', '发起', 20),
    ('WK', '2025-10', 'consultation', '参与', 30);

-- ============================================================================
-- 验证数据
-- ============================================================================

SELECT '=== 收费明细汇总 ===' as info;
SELECT 
    prescribing_dept_code,
    COUNT(*) as record_count,
    COUNT(DISTINCT patient_id) as patient_count,
    SUM(amount) as total_amount
FROM charge_details
WHERE charge_time >= '2025-10-01' AND charge_time < '2025-11-01'
GROUP BY prescribing_dept_code
ORDER BY prescribing_dept_code;

SELECT '=== 工作量统计 ===' as info;
SELECT 
    department_code,
    stat_type,
    stat_level,
    stat_value
FROM workload_statistics
WHERE stat_month = '2025-10'
ORDER BY department_code, stat_type, stat_level;
