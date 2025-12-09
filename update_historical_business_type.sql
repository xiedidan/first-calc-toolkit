-- ============================================================================
-- 更新历史数据的业务类别
-- ============================================================================
-- 功能: 根据业务规则为历史收费明细数据填充 business_type 字段
-- 
-- 使用方法:
--   1. 根据实际业务规则修改下面的判断条件
--   2. 在测试环境验证SQL正确性
--   3. 执行: psql -h <host> -U <user> -d <database> -f update_historical_business_type.sql
--
-- 注意事项:
--   1. 此脚本会修改现有数据，请务必先备份
--   2. 建议分批执行，避免长时间锁表
--   3. 根据实际业务规则调整判断条件
-- ============================================================================

-- 显示当前状态
SELECT 
    business_type,
    COUNT(*) as record_count,
    SUM(amount) as total_amount
FROM charge_details
GROUP BY business_type
ORDER BY business_type NULLS FIRST;

-- ============================================================================
-- 方案1: 根据就诊类型判断（如果 charge_details 表有 visit_type 字段）
-- ============================================================================
-- 如果收费明细表中有 visit_type 字段，可以根据就诊类型判断

-- 更新门诊业务
-- UPDATE charge_details 
-- SET business_type = '门诊'
-- WHERE business_type IS NULL
-- AND visit_type IN ('门诊', '急诊', '体检');

-- 更新住院业务
-- UPDATE charge_details 
-- SET business_type = '住院'
-- WHERE business_type IS NULL
-- AND visit_type IN ('住院', '留观');

-- ============================================================================
-- 方案2: 根据收费项目类别判断
-- ============================================================================
-- 某些收费项目明确属于门诊或住院

-- 更新门诊业务（根据收费项目名称）
-- UPDATE charge_details 
-- SET business_type = '门诊'
-- WHERE business_type IS NULL
-- AND (
--     item_name LIKE '%门诊%'
--     OR item_name LIKE '%挂号%'
--     OR item_name LIKE '%诊察%'
-- );

-- 更新住院业务（根据收费项目名称）
-- UPDATE charge_details 
-- SET business_type = '住院'
-- WHERE business_type IS NULL
-- AND (
--     item_name LIKE '%床位%'
--     OR item_name LIKE '%住院%'
--     OR item_name LIKE '%护理费%'
-- );

-- ============================================================================
-- 方案3: 根据科室判断
-- ============================================================================
-- 某些科室主要是门诊或住院

-- 更新门诊科室的业务
-- UPDATE charge_details 
-- SET business_type = '门诊'
-- WHERE business_type IS NULL
-- AND prescribing_dept_code IN (
--     '门诊部', '急诊科', '体检中心'
--     -- 添加更多门诊科室编码
-- );

-- 更新住院科室的业务
-- UPDATE charge_details 
-- SET business_type = '住院'
-- WHERE business_type IS NULL
-- AND prescribing_dept_code IN (
--     '内科病区', '外科病区', 'ICU'
--     -- 添加更多住院科室编码
-- );

-- ============================================================================
-- 方案4: 默认值处理
-- ============================================================================
-- 对于无法判断的记录，可以设置默认值或保持为空

-- 将剩余记录设置为门诊（如果门诊业务占多数）
-- UPDATE charge_details 
-- SET business_type = '门诊'
-- WHERE business_type IS NULL;

-- 或者保持为空，等待人工处理
-- （不执行任何操作）

-- ============================================================================
-- 验证更新结果
-- ============================================================================

-- 显示更新后的统计
SELECT 
    business_type,
    COUNT(*) as record_count,
    SUM(amount) as total_amount,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER () * 100, 2) as percentage
FROM charge_details
GROUP BY business_type
ORDER BY business_type NULLS FIRST;

-- 显示仍为空的记录数
SELECT 
    COUNT(*) as null_count,
    ROUND(COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM charge_details) * 100, 2) as null_percentage
FROM charge_details
WHERE business_type IS NULL;

-- 按科室统计业务类别分布
SELECT 
    prescribing_dept_code,
    business_type,
    COUNT(*) as record_count,
    SUM(amount) as total_amount
FROM charge_details
GROUP BY prescribing_dept_code, business_type
ORDER BY prescribing_dept_code, business_type;

-- ============================================================================
-- 建议的更新策略
-- ============================================================================
-- 1. 优先使用方案1（根据就诊类型），这是最准确的方法
-- 2. 如果没有就诊类型字段，使用方案2（根据收费项目）
-- 3. 方案3（根据科室）可以作为补充
-- 4. 最后使用方案4处理剩余记录
-- 5. 建议分批执行，每次更新一部分数据，避免长时间锁表
-- 6. 每次更新后验证结果，确保符合预期
-- ============================================================================
