"""
更新计算流程32的科室代码使用规则
- 医生诊断维度：使用开单科室代码（prescribing_dept_code）
- 其他所有维度：使用执行科室代码（executing_dept_code）
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 医生业务价值计算 - Step 123
DOCTOR_SQL = """-- ============================================================================
-- 医生业务价值计算
-- ============================================================================
-- 功能: 统计医生序列各末级维度的工作量和业务价值
--
-- 科室代码使用规则:
--   - 诊断类维度(dim-doc-*-diag*, dim-doc-*-eval*): 使用开单科室(prescribing_dept_code)
--   - 其他维度(诊察、治疗、手术、病例): 使用执行科室(executing_dept_code)
-- ============================================================================

-- 1. 门诊-诊察类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-diag%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 2. 门诊-诊断类维度 (使用开单科室 - 诊断归开单科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-eval%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

print("开始更新计算流程32...")

DOCTOR_SQL += """
-- 3. 门诊-治疗类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-tr%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 住院-诊察类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-diag%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 住院-病例价值 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, COUNT(DISTINCT cd.patient_id) as workload, mn.weight,
    mn.weight as original_weight, COUNT(DISTINCT cd.patient_id) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN model_nodes mn ON mn.code = 'dim-doc-in-case' AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

DOCTOR_SQL += """
-- 6. 住院-诊断类维度 (使用开单科室 - 诊断归开单科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-eval%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 7. 住院-治疗类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-tr%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 8. 手术-门诊类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-out%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

DOCTOR_SQL += """
-- 9. 手术-住院类维度 (使用执行科室)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医生' = ANY(d.accounting_sequences)
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-in%'
  AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count
FROM calculation_results
WHERE task_id = '{task_id}'
  AND node_type = 'dimension'
  AND (node_code LIKE 'dim-doc-out%' OR node_code LIKE 'dim-doc-in%' OR node_code LIKE 'dim-doc-sur%');
"""

# 护理业务价值计算 - Step 124 (全部使用执行科室)
NURSING_SQL = """-- ============================================================================
-- 护理业务价值计算
-- ============================================================================
-- 功能: 统计护理序列各末级维度的工作量和业务价值
-- 科室代码使用规则: 全部使用执行科室(executing_dept_code)
-- ============================================================================

-- Part 1: 从charge_details统计的护理维度 (全部使用执行科室)

-- 1. 基础护理 (dim-nur-base)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-base' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

NURSING_SQL += """
-- 2. 医护协同治疗 (dim-nur-collab)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-collab' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 3. 甲级护理治疗 (dim-nur-tr-a)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-a' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 乙级护理治疗 (dim-nur-tr-b)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-b' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 丙级护理治疗 (dim-nur-tr-c)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-c' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 6. 其他护理 (dim-nur-other)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '护理' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-other' AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

NURSING_SQL += """
-- Part 2: 从workload_statistics统计的护理维度 (使用accounting_unit_code)

-- 7. 甲级床日护理 (dim-nur-bed-3)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT 
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-bed-3' AND d.is_active = TRUE;

-- 8. 乙级床日护理 (dim-nur-bed-4)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT 
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-bed-4' AND d.is_active = TRUE;

-- 9. 丙级床日护理 (dim-nur-bed-5)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-bed-5' AND d.is_active = TRUE;

-- 10. 普通入院护理 (dim-nur-trans-in)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-trans-in' AND d.is_active = TRUE;

-- 11. 日间护理 (dim-nur-trans-intraday)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-trans-intraday' AND d.is_active = TRUE;

-- 12. 普通出院护理 (dim-nur-trans-out)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-trans-out' AND d.is_active = TRUE;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results WHERE task_id = '{task_id}' AND node_type = 'dimension' AND node_code LIKE 'dim-nur%';
"""

NURSING_SQL += """
-- Part 3: 手术室护理维度 (从workload_statistics统计)

-- 13. 大手术护理 (dim-nur-or-large)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-large' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-or-large' AND d.is_active = TRUE;

-- 14. 中手术护理 (dim-nur-or-mid)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-mid' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-or-mid' AND d.is_active = TRUE;

-- 15. 小手术护理 (dim-nur-or-tiny)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-tiny' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-or-tiny' AND d.is_active = TRUE;

-- Part 4: 手术管理维度 (从workload_statistics统计)

-- 16. 乙级手术管理 (dim-nur-op-3)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-3' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-op-3' AND d.is_active = TRUE;

-- 17. 甲级手术管理 (dim-nur-op-4)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-4' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-op-4' AND d.is_active = TRUE;

-- 18. 学科手术管理 (dim-nur-op-acad)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-acad' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-op-acad' AND d.is_active = TRUE;

-- 19. 其他级别手术管理 (dim-nur-op-other)
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, ws.stat_value as workload, mn.weight,
    mn.weight as original_weight, ws.stat_value * mn.weight as value, NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-other' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}' AND ws.stat_type = 'dim-nur-op-other' AND d.is_active = TRUE;
"""

# 医技业务价值计算 - Step 125 (全部使用执行科室)
TECH_SQL = """-- ============================================================================
-- 医技业务价值计算
-- ============================================================================
-- 功能: 统计医技序列各末级维度的工作量和业务价值
-- 科室代码使用规则: 全部使用执行科室(executing_dept_code)
-- ============================================================================

-- 量表检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-scale' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 眼科检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-ophth' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- CT检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-ct' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

TECH_SQL += """
-- 超声检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-us' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 内窥镜检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-endo' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- X线检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-xray' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 其他检查
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-exam-other' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

TECH_SQL += """
-- 临床免疫学检验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-immu' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 临床血液学检验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-blood' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 临床化学检验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-chem' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 临床体液检验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-fluid' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 分子病理学技术与诊断
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-molecular' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 其他化验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-other' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 临床微生物与寄生虫学检验
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-lab-micro' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
"""

TECH_SQL += """
-- 全身麻醉
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-ana-general' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 部位麻醉
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-ana-regional' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 麻醉中监测
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-ana-mon' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 其他麻醉
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id, mn.id as node_id, d.id as department_id,
    'dimension' as node_type, mn.name as node_name, mn.code as node_code,
    mn.parent_id as parent_id, SUM(cd.amount) as workload, mn.weight,
    mn.weight as original_weight, SUM(cd.amount) * mn.weight as value, NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.executing_dept_code = d.his_code AND d.hospital_id = {hospital_id} AND '医技' = ANY(d.accounting_sequences)
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-tech-ana-other' AND mn.is_leaf = TRUE AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results WHERE task_id = '{task_id}' AND node_type = 'dimension' AND node_code LIKE 'dim-tech%';
"""

# 执行更新
def update_workflow32():
    with engine.connect() as conn:
        # 更新医生业务价值计算 (Step 123)
        print("更新Step 123 - 医生业务价值计算...")
        result = conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql, updated_at = NOW()
            WHERE id = 123
        """), {"sql": DOCTOR_SQL})
        print(f"  影响行数: {result.rowcount}")
        
        # 更新护理业务价值计算 (Step 124)
        print("更新Step 124 - 护理业务价值计算...")
        result = conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql, updated_at = NOW()
            WHERE id = 124
        """), {"sql": NURSING_SQL})
        print(f"  影响行数: {result.rowcount}")
        
        # 更新医技业务价值计算 (Step 125)
        print("更新Step 125 - 医技业务价值计算...")
        result = conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql, updated_at = NOW()
            WHERE id = 125
        """), {"sql": TECH_SQL})
        print(f"  影响行数: {result.rowcount}")
        
        conn.commit()
        print("\n更新完成!")
        
        # 验证更新
        print("\n验证更新结果:")
        for step_id in [123, 124, 125]:
            result = conn.execute(text("""
                SELECT name, 
                       CASE WHEN code_content LIKE '%executing_dept_code%' THEN 'YES' ELSE 'NO' END as has_executing,
                       CASE WHEN code_content LIKE '%prescribing_dept_code%' THEN 'YES' ELSE 'NO' END as has_prescribing,
                       LENGTH(code_content) as sql_length
                FROM calculation_steps WHERE id = :id
            """), {"id": step_id})
            row = result.fetchone()
            print(f"  Step {step_id} ({row[0]}): executing={row[1]}, prescribing={row[2]}, length={row[3]}")

if __name__ == "__main__":
    update_workflow32()
