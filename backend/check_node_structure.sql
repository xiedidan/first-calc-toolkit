-- 检查模型节点的层级结构

-- 1. 查看所有节点及其父子关系
SELECT 
    n.id,
    n.name,
    n.code,
    n.node_type,
    n.parent_id,
    p.name as parent_name,
    p.node_type as parent_type,
    n.weight,
    n.business_guide
FROM model_nodes n
LEFT JOIN model_nodes p ON n.parent_id = p.id
WHERE n.version_id = (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1)
ORDER BY n.parent_id NULLS FIRST, n.sort_order;

-- 2. 查看序列节点（顶层）
SELECT 
    id,
    name,
    code,
    node_type,
    parent_id
FROM model_nodes
WHERE version_id = (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1)
  AND node_type = 'sequence'
ORDER BY sort_order;

-- 3. 查看维度节点及其层级
WITH RECURSIVE node_path AS (
    -- 基础：序列节点（顶层）
    SELECT 
        id,
        name,
        code,
        node_type,
        parent_id,
        0 as level,
        CAST(name AS TEXT) as path
    FROM model_nodes
    WHERE version_id = (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1)
      AND parent_id IS NULL
    
    UNION ALL
    
    -- 递归：子节点
    SELECT 
        n.id,
        n.name,
        n.code,
        n.node_type,
        n.parent_id,
        np.level + 1,
        np.path || ' > ' || n.name
    FROM model_nodes n
    INNER JOIN node_path np ON n.parent_id = np.id
    WHERE n.version_id = (SELECT id FROM model_versions WHERE is_active = TRUE LIMIT 1)
)
SELECT 
    level,
    id,
    name,
    code,
    node_type,
    parent_id,
    path
FROM node_path
ORDER BY path;

-- 4. 查看某个科室的计算结果
SELECT 
    cr.node_id,
    cr.node_name,
    cr.node_type,
    cr.parent_id,
    cr.workload,
    cr.weight,
    cr.value,
    cr.ratio,
    mn.name as model_node_name,
    mn.business_guide
FROM calculation_results cr
LEFT JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.task_id = (
    SELECT task_id 
    FROM calculation_tasks 
    WHERE status = 'completed' 
    ORDER BY created_at DESC 
    LIMIT 1
)
AND cr.department_id = (
    SELECT id 
    FROM departments 
    WHERE is_active = TRUE 
    LIMIT 1
)
ORDER BY cr.node_type, cr.parent_id, cr.node_id
LIMIT 20;
