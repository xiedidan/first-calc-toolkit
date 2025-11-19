-- 检查科室汇总表数据
-- 找出最新的任务

-- 1. 查看最新的任务
SELECT 
    task_id,
    period,
    status,
    created_at
FROM calculation_tasks
ORDER BY created_at DESC
LIMIT 5;

-- 2. 查看某个任务的所有计算结果（替换task_id）
-- SELECT 
--     node_type,
--     node_id,
--     node_name,
--     parent_id,
--     workload,
--     weight,
--     value,
--     ratio
-- FROM calculation_results
-- WHERE task_id = 'YOUR_TASK_ID_HERE'
--   AND department_id = 1
-- ORDER BY node_type, node_id;

-- 3. 查看序列数据
-- SELECT 
--     node_id,
--     node_name,
--     value
-- FROM calculation_results
-- WHERE task_id = 'YOUR_TASK_ID_HERE'
--   AND department_id = 1
--   AND node_type = 'sequence'
-- ORDER BY node_id;

-- 4. 查看维度数据（按parent_id分组）
-- SELECT 
--     parent_id,
--     node_id,
--     node_name,
--     workload,
--     weight,
--     value
-- FROM calculation_results
-- WHERE task_id = 'YOUR_TASK_ID_HERE'
--   AND department_id = 1
--   AND node_type = 'dimension'
-- ORDER BY parent_id, node_id;

-- 5. 查看汇总表数据
-- SELECT 
--     d.his_code,
--     d.his_name,
--     cs.doctor_value,
--     cs.doctor_ratio,
--     cs.nurse_value,
--     cs.nurse_ratio,
--     cs.tech_value,
--     cs.tech_ratio,
--     cs.total_value
-- FROM calculation_summaries cs
-- JOIN departments d ON cs.department_id = d.id
-- WHERE cs.task_id = 'YOUR_TASK_ID_HERE'
-- ORDER BY cs.total_value DESC;

-- 6. 验证序列价值汇总（按序列统计维度价值）
-- WITH RECURSIVE dimension_tree AS (
--     -- 找出所有序列
--     SELECT 
--         node_id as seq_id,
--         node_name as seq_name,
--         node_id,
--         parent_id,
--         value
--     FROM calculation_results
--     WHERE task_id = 'YOUR_TASK_ID_HERE'
--       AND department_id = 1
--       AND node_type = 'sequence'
--     
--     UNION ALL
--     
--     -- 递归找出所有子维度
--     SELECT 
--         dt.seq_id,
--         dt.seq_name,
--         cr.node_id,
--         cr.parent_id,
--         cr.value
--     FROM calculation_results cr
--     JOIN dimension_tree dt ON cr.parent_id = dt.node_id
--     WHERE cr.task_id = 'YOUR_TASK_ID_HERE'
--       AND cr.department_id = 1
--       AND cr.node_type = 'dimension'
-- )
-- SELECT 
--     seq_id,
--     seq_name,
--     COUNT(*) as dimension_count,
--     SUM(value) as total_value
-- FROM dimension_tree
-- WHERE node_id != seq_id  -- 排除序列本身
-- GROUP BY seq_id, seq_name
-- ORDER BY seq_id;

-- 7. 检查模型节点结构
SELECT 
    node_type,
    id,
    name,
    code,
    parent_id,
    weight,
    sort_order
FROM model_nodes
WHERE version_id = (
    SELECT model_version_id 
    FROM calculation_tasks 
    ORDER BY created_at DESC 
    LIMIT 1
)
ORDER BY node_type, sort_order, id;
