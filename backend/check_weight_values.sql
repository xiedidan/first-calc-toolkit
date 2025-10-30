-- 检查计算结果中的权重值是否与模型节点中的权重一致

-- 1. 查看某个任务的计算结果中的权重值
SELECT 
    cr.node_id,
    cr.node_name,
    cr.node_type,
    cr.weight AS result_weight,
    mn.weight AS model_weight,
    CASE 
        WHEN cr.weight = mn.weight THEN '一致'
        WHEN cr.weight IS NULL AND mn.weight IS NULL THEN '都为空'
        ELSE '不一致'
    END AS comparison
FROM calculation_results cr
LEFT JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = 'report-2025-10-20251030151533'  -- 替换为实际的task_id
    AND cr.department_id = 3  -- 替换为实际的department_id
    AND cr.node_type = 'dimension'  -- 只看维度节点
ORDER BY cr.node_id;

-- 2. 查看模型节点的权重设置
SELECT 
    id,
    name,
    code,
    node_type,
    is_leaf,
    weight,
    unit
FROM model_nodes
WHERE version_id = (
    SELECT model_version_id 
    FROM calculation_tasks 
    WHERE task_id = 'report-2025-10-20251030151533'
)
ORDER BY sort_order;

-- 3. 检查是否有权重不一致的情况
SELECT 
    cr.task_id,
    cr.node_id,
    cr.node_name,
    cr.weight AS result_weight,
    mn.weight AS model_weight,
    ABS(COALESCE(cr.weight, 0) - COALESCE(mn.weight, 0)) AS difference
FROM calculation_results cr
LEFT JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = 'report-2025-10-20251030151533'
    AND cr.department_id = 3
    AND cr.node_type = 'dimension'
    AND (
        (cr.weight IS NULL AND mn.weight IS NOT NULL)
        OR (cr.weight IS NOT NULL AND mn.weight IS NULL)
        OR ABS(COALESCE(cr.weight, 0) - COALESCE(mn.weight, 0)) > 0.0001
    );
