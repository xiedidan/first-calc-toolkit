-- ============================================================================
-- 步骤3a: 业务导向调整（含明细记录）
-- ============================================================================
-- 功能: 根据业务导向规则调整维度的学科业务价值，并记录完整的计算过程
-- 
-- 输入参数(通过占位符):
--   {task_id}    - 计算任务ID
--   {version_id} - 模型版本ID
--   {year_month} - 计算年月(格式: YYYY-MM)
--
-- 输出: 
--   1. 更新 calculation_results 表中维度节点的 weight 字段
--   2. 插入 orientation_adjustment_details 表记录完整计算过程
-- ============================================================================

-- 第1步: 插入调整明细记录
INSERT INTO orientation_adjustment_details (
    task_id,
    hospital_id,
    year_month,
    department_id,
    department_code,
    department_name,
    node_id,
    node_code,
    node_name,
    orientation_rule_id,
    orientation_rule_name,
    orientation_type,
    actual_value,
    benchmark_value,
    orientation_ratio,
    ladder_id,
    ladder_lower_limit,
    ladder_upper_limit,
    adjustment_intensity,
    original_weight,
    adjusted_weight,
    is_adjusted,
    adjustment_reason,
    created_at
)
WITH base_data AS (
    -- 获取所有需要处理的维度节点（配置了导向规则的）
    -- 使用 UNNEST 展开 orientation_rule_ids 数组，为每个规则创建一条记录
    SELECT 
        '{task_id}'::VARCHAR as task_id,
        mv.hospital_id,
        '{year_month}'::VARCHAR as year_month,
        cr.department_id,
        d.his_code as department_code,
        d.his_name as department_name,
        cr.node_id,
        mn.code as node_code,
        mn.name as node_name,
        UNNEST(mn.orientation_rule_ids) as orientation_rule_id,
        orule.name as orientation_rule_name,
        orule.category::text as orientation_type,
        mn.weight as original_weight
    FROM calculation_results cr
    INNER JOIN model_nodes mn ON cr.node_id = mn.id
    INNER JOIN departments d ON cr.department_id = d.id
    INNER JOIN model_versions mv ON mn.version_id = mv.id
    LEFT JOIN orientation_rules orule ON orule.id = ANY(mn.orientation_rule_ids) AND orule.hospital_id = mv.hospital_id
    WHERE cr.task_id = '{task_id}'
      AND cr.node_type = 'dimension'
      AND mn.orientation_rule_ids IS NOT NULL
      AND array_length(mn.orientation_rule_ids, 1) > 0
      AND mn.version_id = {version_id}
),

orientation_data AS (
    -- 关联导向实际值和基准值
    SELECT 
        bd.*,
        ov.actual_value,
        ob.benchmark_value,
        CASE 
            WHEN ob.benchmark_value IS NULL THEN NULL
            WHEN ob.benchmark_value = 0 THEN NULL
            ELSE ov.actual_value / ob.benchmark_value
        END as orientation_ratio
    FROM base_data bd
    LEFT JOIN orientation_values ov 
        ON bd.orientation_rule_id = ov.orientation_rule_id
        AND bd.department_code = ov.department_code
        AND bd.hospital_id = ov.hospital_id
        AND bd.year_month = ov.year_month
    LEFT JOIN orientation_benchmarks ob
        ON bd.orientation_rule_id = ob.rule_id
        AND bd.department_code = ob.department_code
        AND bd.hospital_id = ob.hospital_id
),

ladder_match AS (
    -- 匹配阶梯（仅基准阶梯型）
    SELECT 
        od.*,
        ol.id as ladder_id,
        ol.lower_limit as ladder_lower_limit,
        ol.upper_limit as ladder_upper_limit,
        ol.adjustment_intensity
    FROM orientation_data od
    LEFT JOIN orientation_ladders ol
        ON od.orientation_rule_id = ol.rule_id
        AND od.hospital_id = ol.hospital_id
        AND od.orientation_type = 'benchmark_ladder'
        AND od.orientation_ratio IS NOT NULL
        AND (ol.lower_limit IS NULL OR od.orientation_ratio >= ol.lower_limit)
        AND (ol.upper_limit IS NULL OR od.orientation_ratio < ol.upper_limit)
),

final_calculation AS (
    -- 计算最终调整结果
    SELECT 
        lm.*,
        CASE 
            WHEN lm.adjustment_intensity IS NOT NULL 
            THEN lm.original_weight * lm.adjustment_intensity
            ELSE NULL
        END as adjusted_weight,
        CASE 
            WHEN lm.actual_value IS NULL THEN FALSE
            WHEN lm.benchmark_value IS NULL THEN FALSE
            WHEN lm.benchmark_value = 0 THEN FALSE
            WHEN lm.adjustment_intensity IS NULL THEN FALSE
            ELSE TRUE
        END as is_adjusted,
        CASE 
            WHEN lm.actual_value IS NULL THEN '缺少导向实际值'
            WHEN lm.benchmark_value IS NULL THEN '缺少导向基准值'
            WHEN lm.benchmark_value = 0 THEN '基准值为0'
            WHEN lm.adjustment_intensity IS NULL THEN '未匹配到阶梯'
            ELSE NULL
        END as adjustment_reason
    FROM ladder_match lm
)
SELECT 
    task_id,
    hospital_id,
    year_month,
    department_id,
    department_code,
    department_name,
    node_id,
    node_code,
    node_name,
    orientation_rule_id,
    orientation_rule_name,
    orientation_type,
    actual_value,
    benchmark_value,
    orientation_ratio,
    ladder_id,
    ladder_lower_limit,
    ladder_upper_limit,
    adjustment_intensity,
    original_weight,
    adjusted_weight,
    is_adjusted,
    adjustment_reason,
    NOW() as created_at
FROM final_calculation;

-- 第2步: 更新 calculation_results 表中的 weight 字段
UPDATE calculation_results cr
SET weight = oad.adjusted_weight
FROM orientation_adjustment_details oad
WHERE cr.task_id = oad.task_id
  AND cr.department_id = oad.department_id
  AND cr.node_id = oad.node_id
  AND oad.is_adjusted = TRUE
  AND oad.adjusted_weight IS NOT NULL;

-- 返回统计信息
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN is_adjusted THEN 1 ELSE 0 END) as adjusted_count,
    SUM(CASE WHEN NOT is_adjusted THEN 1 ELSE 0 END) as not_adjusted_count,
    COUNT(DISTINCT department_id) as department_count,
    COUNT(DISTINCT node_id) as node_count,
    COUNT(DISTINCT orientation_rule_id) as rule_count
FROM orientation_adjustment_details
WHERE task_id = '{task_id}';

-- ============================================================================
-- 表结构说明:
-- ============================================================================
-- orientation_adjustment_details 表记录了每个维度节点的完整调整过程:
--
-- 1. 基础信息: task_id, hospital_id, year_month, department, node, rule
-- 2. 输入值: actual_value(实际值), benchmark_value(基准值)
-- 3. 中间计算: orientation_ratio(导向比例 = 实际值/基准值)
-- 4. 阶梯匹配: ladder_id, ladder_lower_limit, ladder_upper_limit, adjustment_intensity
-- 5. 最终结果: original_weight, adjusted_weight, is_adjusted, adjustment_reason
--
-- 通过这张表可以完整追溯每个维度的调整过程，便于:
-- - 问题诊断: 为什么某个维度没有被调整？
-- - 结果验证: 调整力度是否正确？
-- - 数据展示: 在前端展示完整的计算过程
-- ============================================================================

-- ============================================================================
-- 使用说明:
-- ============================================================================
-- 1. 此步骤在Step2（维度统计）之后、Step4（价值汇总）之前执行
-- 2. 会为所有配置了导向规则的维度节点创建明细记录
-- 3. 只有 is_adjusted=TRUE 的记录会实际更新 calculation_results
-- 4. 未调整的记录会在 adjustment_reason 中说明原因
-- 5. 占位符会在执行时自动替换:
--    {task_id} -> 计算任务ID
--    {version_id} -> 模型版本ID
--    {year_month} -> 计算年月(如: 2025-11)
-- ============================================================================

-- ============================================================================
-- 查询示例:
-- ============================================================================
-- 1. 查看某个任务的所有调整明细:
--    SELECT * FROM orientation_adjustment_details WHERE task_id = 'xxx';
--
-- 2. 查看某个科室的调整情况:
--    SELECT * FROM orientation_adjustment_details 
--    WHERE task_id = 'xxx' AND department_code = 'xxx';
--
-- 3. 查看未调整的记录及原因:
--    SELECT department_name, node_name, adjustment_reason
--    FROM orientation_adjustment_details 
--    WHERE task_id = 'xxx' AND is_adjusted = FALSE;
--
-- 4. 查看调整前后对比:
--    SELECT department_name, node_name, 
--           original_weight, adjusted_weight,
--           (adjusted_weight - original_weight) as weight_change,
--           adjustment_intensity
--    FROM orientation_adjustment_details 
--    WHERE task_id = 'xxx' AND is_adjusted = TRUE;
-- ============================================================================
