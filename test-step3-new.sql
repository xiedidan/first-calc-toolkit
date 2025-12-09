-- 测试新的 Step3 SQL
-- 使用任务 124694a7-3f17-4ff3-831e-5e7efb6febe2 的数据

WITH RECURSIVE model_structure AS (
    -- 第1步: 加载模型结构
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
    WHERE version_id = 1
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
    WHERE mn.version_id = 1
),

dimension_results AS (
    -- 第2步: 加载维度计算结果
    SELECT 
        cr.node_id as dimension_id,
        cr.department_id,
        cr.workload,
        ms.weight,
        ms.node_name
    FROM calculation_results cr
    INNER JOIN model_structure ms ON cr.node_id = ms.node_id
    WHERE cr.task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'
      AND ms.node_type = 'dimension'
),

dimension_scores AS (
    -- 第3步: 计算维度得分
    SELECT 
        dr.dimension_id,
        dr.department_id,
        dr.workload,
        dr.weight,
        COALESCE(dr.workload * dr.weight, 0) as score
    FROM dimension_results dr
),

node_hierarchy AS (
    -- 第4步: 构建节点层级关系
    SELECT 
        ds.dimension_id as leaf_node_id,
        ds.dimension_id as ancestor_node_id,
        ds.department_id,
        ds.score,
        ms.parent_id,
        ms.node_name,
        ms.level,
        0 as depth
    FROM dimension_scores ds
    INNER JOIN model_structure ms ON ds.dimension_id = ms.node_id
    
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
    -- 第5步: 汇总每个节点的得分
    SELECT 
        ancestor_node_id as node_id,
        department_id,
        node_name,
        level,
        SUM(score) as score
    FROM node_hierarchy
    GROUP BY ancestor_node_id, department_id, node_name, level
)

-- 第6步: 查看序列节点的汇总结果（预览，不实际插入）
SELECT 
    agg.node_id,
    agg.department_id,
    ms.node_type,
    agg.node_name,
    ms.code as node_code,
    ms.parent_id,
    agg.score as value
FROM aggregated_scores agg
INNER JOIN model_structure ms ON agg.node_id = ms.node_id
WHERE ms.node_type = 'sequence'
  AND agg.score > 0
ORDER BY agg.department_id, agg.node_id
LIMIT 20;
