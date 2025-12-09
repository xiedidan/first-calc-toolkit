-- 检查workload_statistics与departments表的科室代码不匹配问题

-- 1. workload_statistics中存在但departments中不存在的科室
SELECT '=== workload_statistics中存在但departments中不存在的科室 ===' as info;
SELECT 
    ws.department_code,
    COUNT(DISTINCT ws.stat_type) as stat_type_count,
    SUM(ws.stat_value) as total_value
FROM workload_statistics ws
WHERE NOT EXISTS (
    SELECT 1 FROM departments d 
    WHERE d.his_code = ws.department_code
)
GROUP BY ws.department_code
ORDER BY ws.department_code;

-- 2. departments中存在的科室
SELECT '=== departments表中存在的科室 ===' as info;
SELECT 
    his_code,
    hospital_id,
    is_active
FROM departments
WHERE hospital_id = 1
ORDER BY his_code;

-- 3. 匹配成功的科室（有workload_statistics数据且在departments中存在）
SELECT '=== 匹配成功的科室 ===' as info;
SELECT 
    d.his_code,
    d.hospital_id,
    COUNT(DISTINCT ws.stat_type) as stat_type_count,
    SUM(ws.stat_value) as total_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
WHERE d.hospital_id = 1
GROUP BY d.his_code, d.hospital_id
ORDER BY d.his_code;

-- 4. 建议：需要添加到departments表的科室
SELECT '=== 建议添加到departments表的科室 ===' as info;
SELECT DISTINCT
    ws.department_code as his_code,
    '需要添加' as action
FROM workload_statistics ws
WHERE NOT EXISTS (
    SELECT 1 FROM departments d 
    WHERE d.his_code = ws.department_code
)
ORDER BY ws.department_code;
