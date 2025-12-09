INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code, parent_id, 
    workload, weight, original_weight, value, created_at
)
SELECT 
    '10ac82e7-94ac-4baf-b79b-7d0e3f248297', 
    mn.id, 
    d.id, 
    'dimension', 
    mn.name, 
    mn.code, 
    mn.parent_id, 
    SUM(ws.stat_value), 
    mn.weight, 
    mn.weight, 
    SUM(ws.stat_value) * mn.weight, 
    NOW()
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE ws.stat_month = '2025-10'
  AND mn.version_id = 23
  AND mn.node_type = 'dimension'
  AND d.hospital_id = 1
  AND d.is_active = TRUE
  AND (mn.code LIKE 'dim-nur-bed%' OR mn.code LIKE 'dim-nur-trans%' OR mn.code LIKE 'dim-nur-op%' OR mn.code LIKE 'dim-nur-or%')
  AND d.sort_order = 999.00
  AND NOT EXISTS (
    SELECT 1 FROM calculation_results cr
    WHERE cr.task_id = '10ac82e7-94ac-4baf-b79b-7d0e3f248297'
      AND cr.department_id = d.id
      AND cr.node_id = mn.id
  )
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;
