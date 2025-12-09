-- 测试步骤95现在能否正确处理BHL01的数据

-- 模拟步骤95的查询（不插入，只查看结果）
SELECT 
    d.his_code,
    d.id as department_id,
    mn.code as node_code,
    mn.name as node_name,
    SUM(ws.stat_value) as workload,
    mn.weight,
    SUM(ws.stat_value) * mn.weight as value
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE ws.stat_month = '2025-11'
  AND mn.version_id = 23
  AND mn.node_type = 'dimension'
  AND d.hospital_id = 1
  AND d.is_active = TRUE
  AND (
    mn.code LIKE 'dim-nur-bed%'
    OR mn.code LIKE 'dim-nur-trans%'
    OR mn.code LIKE 'dim-nur-op%'
    OR mn.code LIKE 'dim-nur-or%'
  )
  AND d.his_code = 'BHL01'  -- 只看BHL01
GROUP BY mn.id, d.id, d.his_code, mn.code, mn.name, mn.weight
ORDER BY mn.code;
