-- 测试workload_statistics的stat_type与model_nodes的code匹配

-- 1. 查看workload_statistics中的stat_type
SELECT '=== workload_statistics中的stat_type ===' as info;
SELECT DISTINCT stat_type, COUNT(*) as count
FROM workload_statistics
GROUP BY stat_type
ORDER BY stat_type;

-- 2. 查看model_nodes中匹配的维度code
SELECT '=== model_nodes中匹配的维度code ===' as info;
SELECT DISTINCT code, name, COUNT(*) as count
FROM model_nodes
WHERE node_type = 'dimension'
  AND (
    code LIKE 'dim-nur-bed%'
    OR code LIKE 'dim-nur-trans%'
    OR code LIKE 'dim-nur-op%'
    OR code LIKE 'dim-nur-or%'
  )
GROUP BY code, name
ORDER BY code;

-- 3. 测试匹配关系
SELECT '=== stat_type与code的匹配关系 ===' as info;
SELECT 
    ws.stat_type,
    mn.code,
    mn.name,
    COUNT(DISTINCT ws.department_code) as dept_count,
    SUM(ws.stat_value) as total_value
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code
WHERE mn.node_type = 'dimension'
  AND (
    mn.code LIKE 'dim-nur-bed%'
    OR mn.code LIKE 'dim-nur-trans%'
    OR mn.code LIKE 'dim-nur-op%'
    OR mn.code LIKE 'dim-nur-or%'
  )
GROUP BY ws.stat_type, mn.code, mn.name
ORDER BY ws.stat_type;

-- 4. 检查未匹配的stat_type
SELECT '=== 未匹配的stat_type ===' as info;
SELECT DISTINCT ws.stat_type
FROM workload_statistics ws
WHERE ws.stat_type LIKE 'dim-nur-%'
  AND NOT EXISTS (
    SELECT 1 FROM model_nodes mn
    WHERE mn.code = ws.stat_type
      AND mn.node_type = 'dimension'
  )
ORDER BY ws.stat_type;
