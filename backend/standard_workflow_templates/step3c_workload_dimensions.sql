-- ============================================================================
-- 步骤3c: 工作量维度统计
-- ============================================================================
-- 功能: 从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量
-- 
-- 输入参数(通过占位符):
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM, 如: 2025-10)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 输出: 直接插入到 calculation_results 表
--
-- 数据来源:
--   workload_statistics - 工作量统计表(外部数据源)
--   departments         - 科室表(系统表)
--   model_nodes         - 模型节点表(系统表)
--
-- 算法说明:
--   1. 从 workload_statistics 表读取各类工作量数据
--   2. 根据统计类型(stat_type)匹配到对应的维度(通过code)
--   3. 按科室汇总工作量
--   4. 插入到 calculation_results 表
--
-- 支持的维度类型:
--   - dim-nur-bed: 护理床日（及其子维度）
--   - dim-nur-trans: 出入转院（及其子维度）
--   - dim-nur-op: 手术管理（及其子维度）
--   - dim-nur-or: 手术室护理（及其子维度）
--
-- 匹配规则: workload_statistics.stat_type 直接对应 model_nodes.code
-- ============================================================================

-- 统一插入: 通过stat_type直接匹配维度code
-- 注意: workload_statistics.department_code 对应 departments.accounting_unit_code (核算单元代码)
INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_type,
    node_name,
    node_code,
    parent_id,
    workload,
    weight,
    original_weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(ws.stat_value) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(ws.stat_value) * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
WHERE ws.stat_month = '{current_year_month}'
  AND mn.version_id = {version_id}
  AND mn.node_type = 'dimension'
  AND d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
  AND (
    mn.code LIKE 'dim-nur-bed%'
    OR mn.code LIKE 'dim-nur-trans%'
    OR mn.code LIKE 'dim-nur-op%'
    OR mn.code LIKE 'dim-nur-or%'
  )
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_type = 'dimension'
  AND (
    node_code LIKE 'dim-nur-bed%'
    OR node_code LIKE 'dim-nur-trans%'
    OR node_code LIKE 'dim-nur-op%'
    OR node_code LIKE 'dim-nur-or%'
  );
