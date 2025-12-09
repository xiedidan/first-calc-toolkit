-- ============================================================================
-- 医生业务价值计算
-- ============================================================================
-- 功能: 统计医生序列各末级维度的工作量和业务价值
-- 
-- 输入参数:
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 数据来源:
--   charge_details           - 收费明细表
--   dimension_item_mappings  - 维度项目映射表
--   departments              - 科室表
--   model_nodes              - 模型节点表
--
-- 算法说明:
--   1. 门诊-诊察: 统计门诊诊察类收费金额
--   2. 门诊-诊断: 统计门诊诊断类收费金额（检查化验、中草药、治疗手术）
--   3. 住院-诊察: 统计住院诊察类收费金额
--   4. 住院-病例价值: 按住院病例数统计，每例50元
--   5. 住院-诊断: 统计住院诊断类收费金额
--   6. 手术-门诊: 统计门诊手术类收费金额
--   7. 手术-住院: 统计住院手术类收费金额
-- ============================================================================

-- 1. 门诊-诊察类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-diag%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 2. 门诊-诊断类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-eval%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 3. 门诊-治疗类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-tr%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 住院-诊察类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-diag%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 住院-病例价值 (按病例数统计，每例50元)
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
    COUNT(DISTINCT cd.patient_id) as workload,
    mn.weight,
    mn.weight as original_weight,
    COUNT(DISTINCT cd.patient_id) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN model_nodes mn ON mn.code = 'dim-doc-in-case' AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 6. 住院-诊断类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-eval%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 7. 住院-治疗类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-tr%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 8. 手术-门诊类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-out%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 9. 手术-住院类维度
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
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-in%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, d.accounting_unit_code, mn.name, mn.code, mn.parent_id, mn.weight;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_type = 'dimension'
  AND (
    node_code LIKE 'dim-doc-out%'
    OR node_code LIKE 'dim-doc-in%'
    OR node_code LIKE 'dim-doc-sur%'
  );
