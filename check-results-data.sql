-- 检查 calculation_results 表的数据
SELECT 
    task_id,
    node_id,
    node_type,
    node_name,
    parent_id,
    department_id,
    workload,
    weight,
    value
FROM calculation_results
ORDER BY task_id DESC, department_id, node_type, node_id
LIMIT 20;
