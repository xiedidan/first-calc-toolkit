-- 测试ladder匹配逻辑
WITH base_data AS (
    SELECT 
        'test-ladder-match'::VARCHAR as task_id,
        mv.hospital_id,
        '2025-11'::VARCHAR as year_month,
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
    WHERE cr.task_id = 'b0ee9e80-7fa5-44f7-b98d-d6ca4dc92d6a'
      AND cr.node_type = 'dimension'
      AND mn.orientation_rule_ids IS NOT NULL
      AND array_length(mn.orientation_rule_ids, 1) > 0
      AND mn.version_id = 1
    LIMIT 5
),

orientation_data AS (
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
)

SELECT 
    department_code,
    node_code,
    orientation_rule_id,
    orientation_type,
    orientation_ratio,
    ladder_id,
    ladder_lower_limit,
    ladder_upper_limit,
    adjustment_intensity
FROM ladder_match;
