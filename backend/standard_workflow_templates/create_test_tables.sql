-- ============================================================================
-- 创建测试数据表
-- ============================================================================
-- 用途: 在测试环境中创建模拟的外部数据源表,用于验证标准计算流程
-- 
-- 使用方法:
--   1. 连接到外部数据源数据库
--   2. 执行本SQL文件创建测试表
--   3. 插入一些测试数据
--   4. 运行标准计算流程进行测试
-- ============================================================================

-- 1. 收费明细表 (charge_details)
-- 模拟HIS系统的收费明细数据
CREATE TABLE IF NOT EXISTS charge_details (
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

-- 添加列注释
COMMENT ON COLUMN charge_details.patient_id IS '患者ID';
COMMENT ON COLUMN charge_details.prescribing_dept_code IS '开单科室代码';
COMMENT ON COLUMN charge_details.item_code IS '收费项目编码';
COMMENT ON COLUMN charge_details.item_name IS '收费项目名称';
COMMENT ON COLUMN charge_details.amount IS '金额';
COMMENT ON COLUMN charge_details.quantity IS '数量';
COMMENT ON COLUMN charge_details.charge_time IS '收费时间';

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_charge_details_dept ON charge_details(prescribing_dept_code);
CREATE INDEX IF NOT EXISTS idx_charge_details_item ON charge_details(item_code);
CREATE INDEX IF NOT EXISTS idx_charge_details_time ON charge_details(charge_time);

-- 2. 工作量统计表 (workload_statistics)
-- 模拟护理、会诊等工作量统计数据
CREATE TABLE IF NOT EXISTS workload_statistics (
    id SERIAL PRIMARY KEY,
    department_code VARCHAR(50) NOT NULL,
    stat_month VARCHAR(7) NOT NULL,
    stat_type VARCHAR(50) NOT NULL,
    stat_level VARCHAR(50),
    stat_value DECIMAL(20, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加列注释
COMMENT ON COLUMN workload_statistics.department_code IS '科室代码';
COMMENT ON COLUMN workload_statistics.stat_month IS '统计月份(YYYY-MM)';
COMMENT ON COLUMN workload_statistics.stat_type IS '统计类型(nursing_days/consultation/mdt等)';
COMMENT ON COLUMN workload_statistics.stat_level IS '统计级别(一级护理/二级护理等)';
COMMENT ON COLUMN workload_statistics.stat_value IS '统计值';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_workload_dept ON workload_statistics(department_code);
CREATE INDEX IF NOT EXISTS idx_workload_month ON workload_statistics(stat_month);
CREATE INDEX IF NOT EXISTS idx_workload_type ON workload_statistics(stat_type);

-- ============================================================================
-- 插入测试数据
-- ============================================================================

-- 插入收费明细测试数据
INSERT INTO charge_details (patient_id, prescribing_dept_code, item_code, item_name, amount, quantity, charge_time)
VALUES
    -- 内科的收费数据
    ('P001', 'NK', 'ITEM001', '血常规', 25.00, 1, '2025-10-15 10:30:00'),
    ('P001', 'NK', 'ITEM002', '尿常规', 15.00, 1, '2025-10-15 10:35:00'),
    ('P002', 'NK', 'ITEM001', '血常规', 25.00, 1, '2025-10-16 09:20:00'),
    ('P002', 'NK', 'ITEM003', 'CT检查', 300.00, 1, '2025-10-16 14:00:00'),
    ('P003', 'NK', 'ITEM004', '心电图', 50.00, 1, '2025-10-17 11:00:00'),
    
    -- 外科的收费数据
    ('P004', 'WK', 'ITEM001', '血常规', 25.00, 1, '2025-10-15 08:00:00'),
    ('P004', 'WK', 'ITEM005', '手术费', 5000.00, 1, '2025-10-15 10:00:00'),
    ('P005', 'WK', 'ITEM003', 'CT检查', 300.00, 1, '2025-10-16 15:30:00'),
    ('P005', 'WK', 'ITEM006', '麻醉费', 800.00, 1, '2025-10-16 16:00:00'),
    
    -- 儿科的收费数据
    ('P006', 'EK', 'ITEM001', '血常规', 25.00, 1, '2025-10-18 09:00:00'),
    ('P006', 'EK', 'ITEM002', '尿常规', 15.00, 1, '2025-10-18 09:10:00'),
    ('P007', 'EK', 'ITEM007', '疫苗接种', 120.00, 1, '2025-10-19 10:00:00');

-- 插入工作量统计测试数据
INSERT INTO workload_statistics (department_code, stat_month, stat_type, stat_level, stat_value)
VALUES
    -- 内科护理床日数
    ('NK', '2025-10', 'nursing_days', '一级护理', 50),
    ('NK', '2025-10', 'nursing_days', '二级护理', 120),
    ('NK', '2025-10', 'nursing_days', '三级护理', 80),
    
    -- 外科护理床日数
    ('WK', '2025-10', 'nursing_days', '一级护理', 80),
    ('WK', '2025-10', 'nursing_days', '二级护理', 150),
    ('WK', '2025-10', 'nursing_days', '特级护理', 20),
    
    -- 儿科护理床日数
    ('EK', '2025-10', 'nursing_days', '一级护理', 30),
    ('EK', '2025-10', 'nursing_days', '二级护理', 60),
    
    -- 会诊工作量
    ('NK', '2025-10', 'consultation', '发起', 15),
    ('NK', '2025-10', 'consultation', '参与', 25),
    ('WK', '2025-10', 'consultation', '发起', 20),
    ('WK', '2025-10', 'consultation', '参与', 30);

-- ============================================================================
-- 验证数据
-- ============================================================================

-- 查看收费明细数据
SELECT 
    prescribing_dept_code,
    COUNT(*) as record_count,
    COUNT(DISTINCT patient_id) as patient_count,
    SUM(amount) as total_amount
FROM charge_details
WHERE charge_time >= '2025-10-01' AND charge_time < '2025-11-01'
GROUP BY prescribing_dept_code
ORDER BY prescribing_dept_code;

-- 查看工作量统计数据
SELECT 
    department_code,
    stat_type,
    stat_level,
    stat_value
FROM workload_statistics
WHERE stat_month = '2025-10'
ORDER BY department_code, stat_type, stat_level;

-- ============================================================================
-- 清理测试数据 (可选)
-- ============================================================================

-- 如果需要清理测试数据,取消下面的注释并执行:
-- DELETE FROM charge_details WHERE charge_time >= '2025-10-01' AND charge_time < '2025-11-01';
-- DELETE FROM workload_statistics WHERE stat_month = '2025-10';

-- 如果需要删除测试表,取消下面的注释并执行:
-- DROP TABLE IF EXISTS charge_details;
-- DROP TABLE IF EXISTS workload_statistics;
