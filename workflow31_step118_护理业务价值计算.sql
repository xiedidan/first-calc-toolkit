-- ============================================================================
-- 护理业务价值计算
-- ============================================================================
-- 功能: 统计护理序列各末级维度的工作量和业务价值
-- 
-- 输入参数:
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 数据来源:
--   Part 1: charge_details + dimension_item_mappings (收费明细统计)
--   Part 2: workload_statistics (工作量统计表)
--
-- 维度分类:
--   从charge_details统计: 基础护理、医护协同治疗、甲/乙/丙级护理治疗、其他护理
--   从workload_statistics统计: 床日护理(甲/乙/丙级)、出入转院(入院/日间/出院)
-- ============================================================================

-- ============================================================================
-- Part 1: 从charge_details统计的护理维度
-- ============================================================================

-- 1. 基础护理 (dim-nur-base)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-base'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 2. 医护协同治疗 (dim-nur-collab)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-collab'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 3. 甲级护理治疗 (dim-nur-tr-a)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-a'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 乙级护理治疗 (dim-nur-tr-b)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-b'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 丙级护理治疗 (dim-nur-tr-c)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-c'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 6. 其他护理 (dim-nur-other)
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
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-other'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- ============================================================================
-- Part 2: 从workload_statistics统计的护理维度
-- ============================================================================
-- 注意: workload_statistics中的department_code是核算单元代码，需要通过departments表关联

-- 7. 甲级床日护理 (dim-nur-bed-3)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-3'
  AND d.is_active = TRUE;

-- 8. 乙级床日护理 (dim-nur-bed-4)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-4'
  AND d.is_active = TRUE;

-- 9. 丙级床日护理 (dim-nur-bed-5)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-5'
  AND d.is_active = TRUE;

-- 10. 普通入院护理 (dim-nur-trans-in)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-in'
  AND d.is_active = TRUE;

-- 11. 日间护理 (dim-nur-trans-intraday)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-intraday'
  AND d.is_active = TRUE;

-- 12. 普通出院护理 (dim-nur-trans-out)
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
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-out'
  AND d.is_active = TRUE;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_type = 'dimension'
  AND node_code LIKE 'dim-nur%';
