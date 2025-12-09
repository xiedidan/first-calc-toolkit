-- ============================================================================
-- 步骤1: 数据准备 - 从源表生成收费明细
-- ============================================================================
-- 功能: 从门诊和住院收费明细表(TB_MZ_SFMXB, TB_ZY_SFMXB)提取数据
--       转换并插入到统一的收费明细表(charge_details)
-- 
-- 输入参数(通过占位符):
--   {hospital_id}   - 医疗机构ID (用于数据隔离,如果需要)
--   {task_id}       - 任务ID (用于日志追踪)
--
-- 输出: 插入到 charge_details 表
--   patient_id           - 患者ID (来自BRZSY)
--   prescribing_dept_code - 开单科室代码 (来自KDKSBM)
--   item_code            - 收费项目编码 (来自MXXMBM)
--   item_name            - 收费项目名称 (来自MXXMMC)
--   amount               - 金额 (来自MXXMSSJE-实收金额)
--   quantity             - 数量 (来自MXXMSL)
--   charge_time          - 收费时间 (来自FYFSSJ)
--   business_type        - 业务类别 (门诊/住院)
--
-- 数据来源:
--   TB_MZ_SFMXB - 门诊收费明细表 (外部数据源)
--   TB_ZY_SFMXB - 住院收费明细表 (外部数据源)
--
-- 注意事项:
--   1. 每次执行前会清空 charge_details 表的现有数据
--   2. 不处理退费标志(TFBZ)和修改标志(XGBZ)
--   3. 使用实收金额(MXXMSSJE)而非应收金额
--   4. 不在此步骤进行时间范围过滤(由后续步骤处理)
-- ============================================================================

-- 第1步: 清空现有数据
-- 建议每次执行前清除,避免数据重复
TRUNCATE TABLE charge_details;

-- 第2步: 从门诊收费明细表插入数据
-- 业务类别标记为 '门诊'
INSERT INTO charge_details (
    patient_id,
    prescribing_dept_code,
    item_code,
    item_name,
    amount,
    quantity,
    charge_time,
    business_type,
    created_at
)
SELECT 
    "BRZSY" as patient_id,
    "KDKSBM" as prescribing_dept_code,
    "MXXMBM" as item_code,
    "MXXMMC" as item_name,
    COALESCE("MXXMSSJE", 0) as amount,
    COALESCE("MXXMSL", 0) as quantity,
    "FYFSSJ" as charge_time,
    '门诊' as business_type,
    NOW() as created_at
FROM "TB_MZ_SFMXB"
WHERE "BRZSY" IS NOT NULL
  AND "KDKSBM" IS NOT NULL
  AND "MXXMBM" IS NOT NULL
  AND "FYFSSJ" IS NOT NULL;

-- 第3步: 从住院收费明细表插入数据
-- 业务类别标记为 '住院'
INSERT INTO charge_details (
    patient_id,
    prescribing_dept_code,
    item_code,
    item_name,
    amount,
    quantity,
    charge_time,
    business_type,
    created_at
)
SELECT 
    "BRZSY" as patient_id,
    "KDKSBM" as prescribing_dept_code,
    "MXXMBM" as item_code,
    "MXXMMC" as item_name,
    COALESCE("MXXMSSJE", 0) as amount,
    COALESCE("MXXMSL", 0) as quantity,
    "FYFSSJ" as charge_time,
    '住院' as business_type,
    NOW() as created_at
FROM "TB_ZY_SFMXB"
WHERE "BRZSY" IS NOT NULL
  AND "KDKSBM" IS NOT NULL
  AND "MXXMBM" IS NOT NULL
  AND "FYFSSJ" IS NOT NULL;

-- 第4步: 返回统计信息
SELECT 
    business_type,
    COUNT(*) as record_count,
    COUNT(DISTINCT patient_id) as patient_count,
    COUNT(DISTINCT prescribing_dept_code) as dept_count,
    COUNT(DISTINCT item_code) as item_count,
    SUM(amount) as total_amount,
    SUM(quantity) as total_quantity,
    MIN(charge_time) as earliest_charge,
    MAX(charge_time) as latest_charge
FROM charge_details
GROUP BY business_type
ORDER BY business_type;

-- 返回总记录数
SELECT COUNT(*) as total_inserted_count FROM charge_details;

-- ============================================================================
-- 数据验证建议
-- ============================================================================
-- 执行后建议检查:
-- 1. 记录数是否符合预期 (门诊 + 住院)
-- 2. 业务类别分布是否合理
-- 3. 时间范围是否覆盖所需周期
-- 4. 科室代码和项目编码是否有效
-- 5. 金额和数量是否有异常值
--
-- 常见问题排查:
-- - 如果记录数为0: 检查源表是否有数据,字段名是否正确
-- - 如果金额异常: 检查是否使用了正确的金额字段(实收vs应收)
-- - 如果科室不匹配: 检查科室编码映射关系
-- ============================================================================
