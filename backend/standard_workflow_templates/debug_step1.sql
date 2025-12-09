-- ============================================================================
-- Step1 调试 SQL
-- ============================================================================
-- 用于排查 step1 返回 0 行数据的问题
-- 
-- 使用方法：
--   1. 替换占位符为实际值
--   2. 逐步执行每个查询
--   3. 找出哪一步返回了 0 行
-- ============================================================================

-- 替换这些占位符：
-- {hospital_id} = 1
-- {start_date} = '2025-10-01'
-- {end_date} = '2025-10-31'

-- ============================================================================
-- 第1步：检查维度-收费项目映射
-- ============================================================================
SELECT 
    '第1步：维度-收费项目映射' as step,
    COUNT(*) as count
FROM dimension_item_mappings dim
WHERE dim.hospital_id = 1;

-- 查看具体数据
SELECT 
    dim.dimension_code,
    dim.item_code,
    COUNT(*) as mapping_count
FROM dimension_item_mappings dim
WHERE dim.hospital_id = 1
GROUP BY dim.dimension_code, dim.item_code
LIMIT 10;

-- ============================================================================
-- 第2步：检查模型节点
-- ============================================================================
SELECT 
    '第2步：模型节点' as step,
    COUNT(*) as count
FROM model_nodes mn
INNER JOIN model_versions mv ON mn.version_id = mv.id
WHERE mv.hospital_id = 1
  AND mv.is_active = TRUE
  AND mn.node_type = 'dimension';

-- 查看具体数据
SELECT 
    mn.id,
    mn.code,
    mn.name,
    mn.node_type
FROM model_nodes mn
INNER JOIN model_versions mv ON mn.version_id = mv.id
WHERE mv.hospital_id = 1
  AND mv.is_active = TRUE
  AND mn.node_type = 'dimension'
LIMIT 10;

-- ============================================================================
-- 第3步：检查维度映射和模型节点的关联
-- ============================================================================
SELECT 
    '第3步：维度映射 JOIN 模型节点' as step,
    COUNT(*) as count
FROM dimension_item_mappings dim
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code
INNER JOIN model_versions mv ON mn.version_id = mv.id
WHERE dim.hospital_id = 1
  AND mv.hospital_id = 1
  AND mv.is_active = TRUE
  AND mn.node_type = 'dimension';

-- 查看具体数据
SELECT 
    dim.dimension_code,
    mn.code as node_code,
    mn.name as node_name,
    dim.item_code
FROM dimension_item_mappings dim
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code
INNER JOIN model_versions mv ON mn.version_id = mv.id
WHERE dim.hospital_id = 1
  AND mv.hospital_id = 1
  AND mv.is_active = TRUE
  AND mn.node_type = 'dimension'
LIMIT 10;

-- ============================================================================
-- 第4步：检查收费明细数据
-- ============================================================================
SELECT 
    '第4步：收费明细数据' as step,
    COUNT(*) as count
FROM charge_details cd
WHERE cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day';

-- 查看具体数据
SELECT 
    cd.prescribing_dept_code,
    cd.item_code,
    cd.amount,
    cd.quantity,
    cd.charge_time
FROM charge_details cd
WHERE cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day'
LIMIT 10;

-- ============================================================================
-- 第5步：检查科室数据
-- ============================================================================
SELECT 
    '第5步：科室数据' as step,
    COUNT(*) as count
FROM departments d
WHERE d.hospital_id = 1
  AND d.is_active = TRUE;

-- 查看具体数据
SELECT 
    d.id,
    d.his_code,
    d.his_name,
    d.is_active
FROM departments d
WHERE d.hospital_id = 1
  AND d.is_active = TRUE
LIMIT 10;

-- ============================================================================
-- 第6步：检查收费明细和科室的关联
-- ============================================================================
SELECT 
    '第6步：收费明细 JOIN 科室' as step,
    COUNT(*) as count
FROM charge_details cd
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code
WHERE cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day'
  AND d.hospital_id = 1
  AND d.is_active = TRUE;

-- 查看具体数据
SELECT 
    cd.prescribing_dept_code,
    d.his_code,
    d.his_name,
    cd.item_code,
    cd.amount
FROM charge_details cd
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code
WHERE cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day'
  AND d.hospital_id = 1
  AND d.is_active = TRUE
LIMIT 10;

-- ============================================================================
-- 第7步：检查完整的关联（维度映射 + 收费明细 + 科室）
-- ============================================================================
SELECT 
    '第7步：完整关联' as step,
    COUNT(*) as count
FROM dimension_item_mappings dim
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code
INNER JOIN model_versions mv ON mn.version_id = mv.id
LEFT JOIN charge_details cd ON dim.item_code = cd.item_code
LEFT JOIN departments d ON cd.prescribing_dept_code = d.his_code
WHERE dim.hospital_id = 1
  AND mv.hospital_id = 1
  AND mv.is_active = TRUE
  AND mn.node_type = 'dimension'
  AND cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day'
  AND d.hospital_id = 1
  AND d.is_active = TRUE;

-- ============================================================================
-- 第8步：检查维度映射的 item_code 和收费明细的 item_code 是否匹配
-- ============================================================================
-- 查看维度映射中的 item_code
SELECT 
    'dimension_item_mappings 中的 item_code' as source,
    item_code
FROM dimension_item_mappings
WHERE hospital_id = 1
LIMIT 10;

-- 查看收费明细中的 item_code
SELECT 
    'charge_details 中的 item_code' as source,
    DISTINCT item_code
FROM charge_details
WHERE charge_time >= '2025-10-01'
  AND charge_time < DATE '2025-10-31' + INTERVAL '1 day'
LIMIT 10;

-- 检查是否有交集
SELECT 
    '有交集的 item_code' as info,
    COUNT(DISTINCT dim.item_code) as count
FROM dimension_item_mappings dim
INNER JOIN charge_details cd ON dim.item_code = cd.item_code
WHERE dim.hospital_id = 1
  AND cd.charge_time >= '2025-10-01'
  AND cd.charge_time < DATE '2025-10-31' + INTERVAL '1 day';
