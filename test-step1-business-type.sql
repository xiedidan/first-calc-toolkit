-- 测试步骤1 SQL（包含业务类别区分）
-- 使用实际参数替换占位符

WITH RECURSIVE dimension_hierarchy AS (
    -- 第1步: 构建维度层级结构,用于判断业务类别
    SELECT 
        mn.id as dimension_id,
        mn.code as dimension_code,
        mn.name as dimension_name,
        mn.parent_id,
        CAST(mn.name AS TEXT) as path_names,
        1 as level
    FROM model_nodes mn
    INNER JOIN model_versions mv ON mn.version_id = mv.id
    WHERE mv.hospital_id = 1
      AND mv.is_active = TRUE
      AND mn.node_type = 'sequence'
    
    UNION ALL
    
    SELECT 
        mn.id,
        mn.code,
        mn.name,
        mn.parent_id,
        dh.path_names || '/' || mn.name,
        dh.level + 1
    FROM model_nodes mn
    INNER JOIN dimension_hierarchy dh ON mn.parent_id = dh.dimension_id
    WHERE mn.node_type = 'dimension'
),

dimension_business_type AS (
    -- 第2步: 根据维度路径判断业务类别
    SELECT 
        dimension_id,
        dimension_code,
        dimension_name,
        path_names,
        CASE
            WHEN path_names LIKE '医生序列/门诊%' THEN '门诊'
            WHEN path_names LIKE '医生序列/住院%' THEN '住院'
            WHEN path_names LIKE '医生序列/手术/门诊%' THEN '门诊'
            WHEN path_names LIKE '医生序列/手术/住院%' THEN '住院'
            WHEN path_names LIKE '护理序列/病区%' THEN '住院'
            WHEN path_names LIKE '护理序列/非病区%' THEN '门诊'
            ELSE NULL
        END as business_type
    FROM dimension_hierarchy
),

dimension_mappings AS (
    -- 第3步: 获取维度-收费项目映射关系
    SELECT DISTINCT
        dbt.dimension_id,
        dbt.business_type,
        dim.item_code
    FROM dimension_item_mappings dim
    INNER JOIN dimension_business_type dbt ON dim.dimension_code = dbt.dimension_code
    WHERE dim.hospital_id = 1
)

-- 查看结果（前20条）
SELECT 
    dm.dimension_id,
    dbt.dimension_name,
    dbt.path_names,
    dm.business_type,
    COUNT(dm.item_code) as item_count
FROM dimension_mappings dm
INNER JOIN dimension_business_type dbt ON dm.dimension_id = dbt.dimension_id
GROUP BY dm.dimension_id, dbt.dimension_name, dbt.path_names, dm.business_type
ORDER BY dbt.path_names
LIMIT 20;
