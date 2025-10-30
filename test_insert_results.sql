-- ============================================
-- 计算结果测试数据插入脚本（简化版）
-- 用于测试报表功能
-- ============================================
-- 
-- 使用说明：
-- 1. 确保模型中已有节点数据
-- 2. 在计算流程中创建一个 SQL 步骤
-- 3. 复制此脚本到代码编辑器
-- 4. 选择数据源（系统数据库）
-- 5. 创建计算任务（可选择科室或不选）
-- 6. 执行任务，自动生成测试数据
--
-- 参数说明：
-- {task_id} - 自动获取当前任务ID
-- {period} - 自动获取计算周期
-- {department_code} - 自动获取科室代码（批量模式时为空）
-- ============================================

-- 为每个科室和每个叶子节点生成随机的计算结果
INSERT INTO calculation_results (
    task_id, 
    department_id, 
    node_id, 
    node_name, 
    node_code, 
    node_type,
    parent_id, 
    workload, 
    weight, 
    value, 
    ratio, 
    created_at
)
SELECT 
    '{task_id}',
    d.id,
    n.id,
    n.name,
    n.code,
    n.node_type,
    n.parent_id,
    -- 工作量：根据节点类型生成不同范围的随机数
    CASE 
        WHEN n.node_type = 'dimension' THEN (100 + random() * 900) * (0.5 + random())
        ELSE NULL
    END,
    -- 权重：根据节点类型生成不同范围的随机数
    CASE 
        WHEN n.node_type = 'dimension' THEN 20 + random() * 80
        ELSE NULL
    END,
    -- 价值：根据节点类型生成不同范围的随机数
    CASE 
        WHEN n.node_type = 'sequence' THEN (30000 + random() * 70000) * (0.5 + random())
        WHEN n.node_type = 'dimension' THEN (5000 + random() * 45000) * (0.5 + random())
        ELSE (1000 + random() * 9000) * (0.5 + random())
    END,
    -- 占比：维度节点生成随机占比
    CASE 
        WHEN n.node_type = 'dimension' THEN 10 + random() * 40
        ELSE NULL
    END,
    NOW()
FROM departments d
CROSS JOIN model_nodes n
WHERE ('{department_code}' = '' OR d.his_code = '{department_code}')
  AND d.is_active = TRUE
  AND n.node_type IN ('sequence', 'dimension')
ORDER BY d.sort_order, n.id
LIMIT CASE WHEN '{department_code}' = '' THEN 200 ELSE 10 END;

-- 生成汇总数据
INSERT INTO calculation_summaries (
    task_id, 
    department_id,
    doctor_value, 
    doctor_ratio,
    nurse_value, 
    nurse_ratio,
    tech_value, 
    tech_ratio,
    total_value, 
    created_at
)
SELECT 
    '{task_id}',
    dept_id,
    COALESCE(doctor_value, 0),
    CASE WHEN total_value > 0 THEN (COALESCE(doctor_value, 0) / total_value * 100) ELSE 0 END,
    COALESCE(nurse_value, 0),
    CASE WHEN total_value > 0 THEN (COALESCE(nurse_value, 0) / total_value * 100) ELSE 0 END,
    COALESCE(tech_value, 0),
    CASE WHEN total_value > 0 THEN (COALESCE(tech_value, 0) / total_value * 100) ELSE 0 END,
    COALESCE(total_value, 0),
    NOW()
FROM (
    SELECT 
        cr.department_id as dept_id,
        SUM(CASE WHEN n.name LIKE '%医生%' AND cr.node_type = 'sequence' THEN cr.value ELSE 0 END) as doctor_value,
        SUM(CASE WHEN n.name LIKE '%护理%' AND cr.node_type = 'sequence' THEN cr.value ELSE 0 END) as nurse_value,
        SUM(CASE WHEN n.name LIKE '%医技%' AND cr.node_type = 'sequence' THEN cr.value ELSE 0 END) as tech_value,
        SUM(CASE WHEN cr.node_type = 'sequence' THEN cr.value ELSE 0 END) as total_value
    FROM calculation_results cr
    JOIN model_nodes n ON n.id = cr.node_id
    WHERE cr.task_id = '{task_id}'
    GROUP BY cr.department_id
) summary_data
WHERE total_value > 0
ON CONFLICT (task_id, department_id) 
DO UPDATE SET
    doctor_value = EXCLUDED.doctor_value,
    doctor_ratio = EXCLUDED.doctor_ratio,
    nurse_value = EXCLUDED.nurse_value,
    nurse_ratio = EXCLUDED.nurse_ratio,
    tech_value = EXCLUDED.tech_value,
    tech_ratio = EXCLUDED.tech_ratio,
    total_value = EXCLUDED.total_value;

-- 返回统计信息
SELECT 
    '{task_id}' as task_id,
    '{period}' as period,
    CASE WHEN '{department_code}' = '' THEN '批量模式' ELSE '单科室模式' END as mode,
    '{department_code}' as department_filter,
    COUNT(DISTINCT department_id) as department_count,
    COUNT(*) FILTER (WHERE node_type = 'sequence') as sequence_count,
    COUNT(*) FILTER (WHERE node_type = 'dimension') as dimension_count,
    COUNT(*) as total_records,
    ROUND(SUM(value)::numeric, 2) as total_value,
    '测试数据生成成功' as status
FROM calculation_results
WHERE task_id = '{task_id}';
