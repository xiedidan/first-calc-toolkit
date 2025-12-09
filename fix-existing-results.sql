-- ============================================================================
-- 修复现有 calculation_results 数据的缺失字段
-- ============================================================================
-- 用途: 为已经插入的记录补充 node_code 和 parent_id 字段
-- 使用场景: 在更新SQL模板之前已经运行过计算任务
-- ============================================================================

-- 显示修复前的统计
SELECT 
    '修复前统计' as stage,
    COUNT(*) as total_records,
    COUNT(node_code) as has_node_code,
    COUNT(parent_id) as has_parent_id,
    COUNT(*) - COUNT(node_code) as missing_node_code,
    COUNT(*) - COUNT(parent_id) as missing_parent_id
FROM calculation_results
WHERE node_type = 'dimension';

-- 从 model_nodes 补充缺失的字段
UPDATE calculation_results cr
SET 
    node_code = mn.code,
    parent_id = mn.parent_id
FROM model_nodes mn
WHERE cr.node_id = mn.id
  AND cr.node_type = 'dimension'
  AND (cr.node_code IS NULL OR cr.parent_id IS NULL);

-- 显示修复后的统计
SELECT 
    '修复后统计' as stage,
    COUNT(*) as total_records,
    COUNT(node_code) as has_node_code,
    COUNT(parent_id) as has_parent_id,
    COUNT(*) - COUNT(node_code) as missing_node_code,
    COUNT(*) - COUNT(parent_id) as missing_parent_id
FROM calculation_results
WHERE node_type = 'dimension';

-- 显示修复的记录数
SELECT 
    '修复完成' as message,
    COUNT(*) as updated_records
FROM calculation_results cr
INNER JOIN model_nodes mn ON cr.node_id = mn.id
WHERE cr.node_type = 'dimension';

-- 验证: 显示一些修复后的记录
SELECT 
    id,
    task_id,
    node_name,
    node_code,
    parent_id,
    node_type,
    workload,
    value
FROM calculation_results 
WHERE node_type = 'dimension'
ORDER BY id DESC
LIMIT 10;
