-- 补充BHL01等新添加科室的工作量维度数据到已完成的任务
-- 任务ID: 10ac82e7-94ac-4baf-b79b-7d0e3f248297
-- Period: 2025-10
-- Version: 23

-- 插入BHL01及其他新添加科室的工作量维度数据
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
    '10ac82e7-94ac-4baf-b79b-7d0e3f248297' as task_id,
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
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE ws.stat_month = '2025-10'
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
  -- 只处理新添加的科室（sort_order=999的）
  AND d.sort_order = 999.00
  -- 避免重复插入
  AND NOT EXISTS (
    SELECT 1 FROM calculation_results cr
    WHERE cr.task_id = '10ac82e7-94ac-4baf-b79b-7d0e3f248297'
      AND cr.department_id = d.id
      AND cr.node_id = mn.id
  )
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 显示插入的记录数
SELECT 
    d.his_code,
    COUNT(*) as inserted_count
FROM calculation_results cr
JOIN departments d ON cr.department_id = d.id
WHERE cr.task_id = '10ac82e7-94ac-4baf-b79b-7d0e3f248297'
  AND d.sort_order = 999.00
  AND cr.node_code LIKE 'dim-nur-%'
GROUP BY d.his_code
ORDER BY d.his_code;
