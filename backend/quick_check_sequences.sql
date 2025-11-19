-- 快速检查序列名称和数据

-- 1. 查看模型中的序列节点
SELECT 
    id,
    name,
    code,
    node_type,
    sort_order
FROM model_nodes
WHERE version_id = (SELECT id FROM model_versions WHERE is_active = true)
    AND node_type = 'sequence'
ORDER BY sort_order;

-- 2. 查看计算结果中的序列数据（最新任务，科室ID=3）
SELECT 
    cr.node_id,
    cr.node_name,
    cr.value,
    CASE 
        WHEN cr.node_name LIKE '%医生%' OR cr.node_name LIKE '%医疗%' OR cr.node_name LIKE '%医师%' THEN '医生序列'
        WHEN cr.node_name LIKE '%护理%' OR cr.node_name LIKE '%护士%' THEN '护理序列'
        WHEN cr.node_name LIKE '%医技%' OR cr.node_name LIKE '%技师%' THEN '医技序列'
        ELSE '未识别'
    END AS sequence_type
FROM calculation_results cr
WHERE cr.task_id = (
    SELECT task_id 
    FROM calculation_tasks 
    WHERE status = 'completed' 
    ORDER BY completed_at DESC 
    LIMIT 1
)
    AND cr.department_id = 3
    AND cr.node_type = 'sequence'
ORDER BY cr.node_id;

-- 3. 查看汇总表数据（最新任务，科室ID=3）
SELECT 
    task_id,
    department_id,
    doctor_value,
    nurse_value,
    tech_value,
    total_value
FROM calculation_summaries
WHERE task_id = (
    SELECT task_id 
    FROM calculation_tasks 
    WHERE status = 'completed' 
    ORDER BY completed_at DESC 
    LIMIT 1
)
    AND department_id = 3;

-- 4. 对比序列结果和汇总表（检查是否一致）
WITH sequence_totals AS (
    SELECT 
        SUM(CASE 
            WHEN cr.node_name LIKE '%医生%' OR cr.node_name LIKE '%医疗%' OR cr.node_name LIKE '%医师%' 
            THEN cr.value ELSE 0 
        END) AS doctor_total,
        SUM(CASE 
            WHEN cr.node_name LIKE '%护理%' OR cr.node_name LIKE '%护士%' 
            THEN cr.value ELSE 0 
        END) AS nurse_total,
        SUM(CASE 
            WHEN cr.node_name LIKE '%医技%' OR cr.node_name LIKE '%技师%' 
            THEN cr.value ELSE 0 
        END) AS tech_total
    FROM calculation_results cr
    WHERE cr.task_id = (
        SELECT task_id 
        FROM calculation_tasks 
        WHERE status = 'completed' 
        ORDER BY completed_at DESC 
        LIMIT 1
    )
        AND cr.department_id = 3
        AND cr.node_type = 'sequence'
)
SELECT 
    '序列结果' AS source,
    st.doctor_total AS doctor_value,
    st.nurse_total AS nurse_value,
    st.tech_total AS tech_value,
    (st.doctor_total + st.nurse_total + st.tech_total) AS total_value
FROM sequence_totals st
UNION ALL
SELECT 
    '汇总表' AS source,
    cs.doctor_value,
    cs.nurse_value,
    cs.tech_value,
    cs.total_value
FROM calculation_summaries cs
WHERE cs.task_id = (
    SELECT task_id 
    FROM calculation_tasks 
    WHERE status = 'completed' 
    ORDER BY completed_at DESC 
    LIMIT 1
)
    AND cs.department_id = 3;
