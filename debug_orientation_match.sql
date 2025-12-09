-- 调试导向匹配问题
-- 任务ID: 793a6c10-3de2-4e28-addc-d1603a122f8f

-- 1. 检查calculation_results中的科室
SELECT DISTINCT 
    d.id as dept_id,
    d.his_code,
    d.accounting_unit_code,
    d.his_name
FROM calculation_results cr
INNER JOIN departments d ON cr.department_id = d.id
WHERE cr.task_id = '793a6c10-3de2-4e28-addc-d1603a122f8f'
  AND d.accounting_unit_code IS NOT NULL
ORDER BY d.accounting_unit_code
LIMIT 10;

-- 2. 检查orientation_values中的科室
SELECT DISTINCT 
    department_code,
    COUNT(*) as rule_count
FROM orientation_values
WHERE year_month = '2025-10'
  AND hospital_id = 1
GROUP BY department_code
ORDER BY department_code
LIMIT 10;

-- 3. 测试关联
SELECT 
    d.accounting_unit_code as dept_code_from_cr,
    ov.department_code as dept_code_from_ov,
    ov.actual_value,
    CASE 
        WHEN ov.department_code IS NULL THEN '未匹配'
        ELSE '已匹配'
    END as match_status
FROM calculation_results cr
INNER JOIN departments d ON cr.department_id = d.id
LEFT JOIN orientation_values ov 
    ON d.accounting_unit_code = ov.department_code
    AND ov.year_month = '2025-10'
    AND ov.hospital_id = 1
WHERE cr.task_id = '793a6c10-3de2-4e28-addc-d1603a122f8f'
  AND d.accounting_unit_code IS NOT NULL
LIMIT 10;
