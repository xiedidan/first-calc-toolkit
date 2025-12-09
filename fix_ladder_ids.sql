-- 修复orientation_adjustment_details表中缺失的ladder_id
UPDATE orientation_adjustment_details oad
SET 
    ladder_id = ol.id,
    ladder_lower_limit = ol.lower_limit,
    ladder_upper_limit = ol.upper_limit
FROM orientation_ladders ol
WHERE oad.orientation_rule_id = ol.rule_id
  AND oad.hospital_id = ol.hospital_id
  AND oad.orientation_type = 'benchmark_ladder'
  AND oad.orientation_ratio IS NOT NULL
  AND (ol.lower_limit IS NULL OR oad.orientation_ratio >= ol.lower_limit)
  AND (ol.upper_limit IS NULL OR oad.orientation_ratio < ol.upper_limit)
  AND oad.ladder_id IS NULL;

-- 查看更新结果
SELECT 
    COUNT(*) as total_updated,
    COUNT(DISTINCT orientation_rule_id) as rules_updated,
    COUNT(DISTINCT department_id) as depts_updated
FROM orientation_adjustment_details
WHERE ladder_id IS NOT NULL;
