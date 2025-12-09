-- 添加workload_statistics中存在但departments表中缺失的科室
-- 注意: 这些科室将被添加到hospital_id=1，并设置为激活状态

INSERT INTO departments (his_code, his_name, hospital_id, is_active, created_at, updated_at)
SELECT DISTINCT
    ws.department_code,
    ws.department_code as his_name,  -- 暂时使用科室代码作为名称
    1 as hospital_id,
    TRUE as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM workload_statistics ws
WHERE NOT EXISTS (
    SELECT 1 FROM departments d 
    WHERE d.his_code = ws.department_code
      AND d.hospital_id = 1
)
ORDER BY ws.department_code
ON CONFLICT (hospital_id, his_code) DO NOTHING;

-- 显示添加的科室
SELECT 
    his_code,
    hospital_id,
    is_active,
    created_at
FROM departments
WHERE his_code IN (
    SELECT DISTINCT department_code 
    FROM workload_statistics
)
ORDER BY his_code;
