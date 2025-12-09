-- 验证步骤95修复效果

-- 1. 检查JOIN字段是否正确
SELECT '=== 步骤95的JOIN字段 ===' as info;
SELECT 
    id,
    name,
    CASE 
        WHEN code_content LIKE '%d.accounting_unit_code%' THEN 'accounting_unit_code (正确)'
        WHEN code_content LIKE '%d.his_code%' THEN 'his_code (错误)'
        ELSE '未知'
    END as join_field
FROM calculation_steps
WHERE id = 95;

-- 2. 测试匹配效果（使用2025-10数据）
SELECT '=== 匹配科室数量对比 ===' as info;
SELECT 
    'accounting_unit_code匹配' as method,
    COUNT(DISTINCT d.id) as matched_departments
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
WHERE ws.stat_month = '2025-10'
  AND d.hospital_id = 1

UNION ALL

SELECT 
    'his_code匹配（旧方法）' as method,
    COUNT(DISTINCT d.id) as matched_departments
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE ws.stat_month = '2025-10'
  AND d.hospital_id = 1;

-- 3. 验证BHL01能否正确匹配
SELECT '=== BHL01匹配验证 ===' as info;
SELECT 
    d.his_code,
    d.accounting_unit_code,
    COUNT(DISTINCT ws.stat_type) as stat_type_count,
    SUM(ws.stat_value) as total_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
WHERE ws.stat_month = '2025-10'
  AND d.hospital_id = 1
  AND ws.department_code = 'BHL01'
GROUP BY d.his_code, d.accounting_unit_code;

-- 4. 统计各维度类型的匹配情况
SELECT '=== 各维度类型匹配统计 ===' as info;
SELECT 
    CASE 
        WHEN ws.stat_type LIKE 'dim-nur-bed%' THEN 'dim-nur-bed (护理床日)'
        WHEN ws.stat_type LIKE 'dim-nur-trans%' THEN 'dim-nur-trans (出入转院)'
        WHEN ws.stat_type LIKE 'dim-nur-op%' THEN 'dim-nur-op (手术管理)'
        WHEN ws.stat_type LIKE 'dim-nur-or%' THEN 'dim-nur-or (手术室护理)'
        ELSE '其他'
    END as dimension_group,
    COUNT(DISTINCT d.id) as matched_departments,
    COUNT(*) as total_records,
    SUM(ws.stat_value) as total_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code
WHERE ws.stat_month = '2025-10'
  AND d.hospital_id = 1
  AND (
    ws.stat_type LIKE 'dim-nur-bed%'
    OR ws.stat_type LIKE 'dim-nur-trans%'
    OR ws.stat_type LIKE 'dim-nur-op%'
    OR ws.stat_type LIKE 'dim-nur-or%'
  )
GROUP BY dimension_group
ORDER BY dimension_group;
