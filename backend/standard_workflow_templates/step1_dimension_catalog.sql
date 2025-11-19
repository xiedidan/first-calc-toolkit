-- ============================================================================
-- 步骤1: 维度目录统计
-- ============================================================================
-- 功能: 根据维度-收费项目映射关系,从收费明细表中统计各维度的工作量
-- 
-- 输入参数(通过占位符):
--   {current_year_month} - 当期年月 (格式: YYYY-MM, 如: 2025-10)
--   {hospital_id}        - 医疗机构ID (从科室信息中获取)
--   {start_date}         - 开始日期 (当月第一天, 如: 2025-10-01)
--   {end_date}           - 结束日期 (当月最后一天, 如: 2025-10-31)
--
-- 输出字段:
--   dimension_id           - 维度ID
--   department_id          - 科室ID
--   workload_amount        - 工作量金额
--   workload_quantity      - 工作量数量
--   workload_patient_count - 患者人次
--
-- 数据来源:
--   dimension_item_mappings - 维度-收费项目映射表(系统表)
--   charge_details          - 收费明细表(外部数据源)
--   departments             - 科室表(系统表)
--   model_nodes             - 模型节点表(系统表)
-- ============================================================================

WITH dimension_mappings AS (
    -- 第1步: 获取维度-收费项目映射关系
    -- 从dimension_item_mappings表获取映射,并关联model_nodes确保维度属于当前活动版本
    SELECT DISTINCT
        mn.id as dimension_id,
        dim.item_code
    FROM dimension_item_mappings dim
    INNER JOIN model_nodes mn ON dim.dimension_code = mn.code
    INNER JOIN model_versions mv ON mn.version_id = mv.id
    WHERE dim.hospital_id = {hospital_id}
      AND mv.hospital_id = {hospital_id}
      AND mv.is_active = TRUE
      AND mn.node_type = 'dimension'  -- 只选择维度节点
),


charge_data AS (
    -- 第2步: 从收费明细表提取指定周期的数据并汇总
    -- 按开单科室和收费项目汇总金额、数量、患者人次
    SELECT 
        cd.prescribing_dept_code,
        cd.item_code,
        SUM(cd.amount) as total_amount,
        SUM(cd.quantity) as total_quantity,
        COUNT(DISTINCT cd.patient_id) as patient_count
    FROM charge_details cd
    WHERE cd.charge_time >= '{start_date}'
      AND cd.charge_time < DATE '{end_date}' + INTERVAL '1 day'  -- 包含结束日期当天
      AND cd.prescribing_dept_code IN (
          -- 只统计参与评估的科室
          SELECT his_code 
          FROM departments 
          WHERE hospital_id = {hospital_id} 
            AND is_active = TRUE
      )
    GROUP BY cd.prescribing_dept_code, cd.item_code
)


-- 第3步: 关联映射和收费数据,按维度和科室汇总工作量
SELECT 
    dm.dimension_id,
    d.id as department_id,
    COALESCE(SUM(cd.total_amount), 0) as workload_amount,
    COALESCE(SUM(cd.total_quantity), 0) as workload_quantity,
    COALESCE(SUM(cd.patient_count), 0) as workload_patient_count
FROM dimension_mappings dm
LEFT JOIN charge_data cd ON dm.item_code = cd.item_code
LEFT JOIN departments d ON cd.prescribing_dept_code = d.his_code
WHERE d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
GROUP BY dm.dimension_id, d.id
HAVING SUM(cd.total_amount) > 0  -- 只返回有工作量的记录
ORDER BY dm.dimension_id, d.id;

-- ============================================================================
-- 使用说明:
-- 1. 此SQL会自动处理一个收费项目属于多个维度的情况
-- 2. 使用LEFT JOIN确保即使某些维度没有收费数据也能返回(金额为0)
-- 3. HAVING子句过滤掉没有工作量的记录,减少结果集大小
-- 4. 占位符会在执行时自动替换:
--    {start_date} -> 当月第一天 (如: 2025-10-01)
--    {end_date} -> 当月最后一天 (如: 2025-10-31)
--    {hospital_id} -> 医疗机构ID (如: 1)
-- ============================================================================
