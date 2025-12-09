-- 测试成本维度的汇总
-- 检查为什么"成本"父节点没有被汇总

-- 1. 检查成本维度的叶子节点
SELECT 
    cr.node_id,
    mn.name as node_name,
    mn.parent_id,
    parent.name as parent_name,
    COUNT(*) as dept_count,
    SUM(cr.value) as total_value
FROM calculation_results cr
JOIN model_nodes mn ON cr.node_id = mn.id
LEFT JOIN model_nodes parent ON mn.parent_id = parent.id
WHERE cr.task_id = '89d58d96-26ab-4742-8792-13c20ec22043'
  AND mn.code IN ('dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr')
GROUP BY cr.node_id, mn.name, mn.parent_id, parent.name;

-- 2. 检查"成本"节点是否在 aggregated_scores 中
WITH RECURSIVE model_structure AS (
    SELECT 
        id as node_id,
        parent_id,
        code,
        name as node_name,
        node_type,
        calc_type,
        weight,
        sort_order,
        0 as level
    FROM model_nodes
    WHERE version_id = 23
      AND parent_id IS NULL
    
    UNION ALL
    
    SELECT 
        mn.id,
        mn.parent_id,
        mn.code,
        mn.name,
        mn.node_type,
        mn.calc_type,
        mn.weight,
        mn.sort_order,
        ms.level + 1
    FROM model_nodes mn
    INNER JOIN model_structure ms ON mn.parent_id = ms.node_id
    WHERE mn.version_id = 23
),

dimension_results AS (
    SELECT 
        cr.node_id as dimension_id,
        cr.department_id,
        cr.workload,
        cr.weight,
        cr.original_weight,
        ms.node_name,
        cr.value as score
    FROM calculation_results cr
    INNER JOIN model_structure ms ON cr.node_id = ms.node_id
    WHERE cr.task_id = '89d58d96-26ab-4742-8792-13c20ec22043'
      AND ms.node_type = 'dimension'
),

node_hierarchy AS (
    SELECT 
        dr.dimension_id as leaf_node_id,
        dr.dimension_id as ancestor_node_id,
        dr.department_id,
        dr.score,
        ms.parent_id,
        ms.node_name,
        ms.level,
        0 as depth
    FROM dimension_results dr
    INNER JOIN model_structure ms ON dr.dimension_id = ms.node_id
    
    UNION ALL
    
    SELECT 
        nh.leaf_node_id,
        ms.node_id as ancestor_node_id,
        nh.department_id,
        nh.score,
        ms.parent_id,
        ms.node_name,
        ms.level,
        nh.depth + 1
    FROM node_hierarchy nh
    INNER JOIN model_structure ms ON nh.parent_id = ms.node_id
    WHERE nh.parent_id IS NOT NULL
),

aggregated_scores AS (
    SELECT 
        ancestor_node_id as node_id,
        department_id,
        node_name,
        level,
        SUM(score) as score
    FROM node_hierarchy
    GROUP BY ancestor_node_id, department_id, node_name, level
)

SELECT 
    node_id,
    node_name,
    COUNT(*) as dept_count,
    SUM(score) as total_score
FROM aggregated_scores
WHERE node_name = '成本'
GROUP BY node_id, node_name;
