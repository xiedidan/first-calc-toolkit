-- 测试业务类别判断逻辑
-- 此脚本用于验证维度层级结构和业务类别判断是否正确

-- 假设 hospital_id = 1, version_id = 1

WITH RECURSIVE dimension_hierarchy AS (
    -- 第1步: 构建维度层级结构,用于判断业务类别
    -- 获取所有维度节点及其祖先路径(从序列节点开始向下递归)
    SELECT 
        mn.id as dimension_id,
        mn.code as dimension_code,
        mn.name as dimension_name,
        mn.parent_id,
        mn.name as path_names,
        1 as level
    FROM model_nodes mn
    INNER JOIN model_versions mv ON mn.version_id = mv.id
    WHERE mv.hospital_id = 1
      AND mv.is_active = TRUE
      AND mn.node_type = 'sequence'  -- 从序列节点开始
    
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
    WHERE mn.node_type = 'dimension'  -- 只递归维度节点
),

dimension_business_type AS (
    -- 第2步: 根据维度路径判断业务类别
    -- 路径格式: 序列名称/一级维度/二级维度/...
    SELECT 
        dimension_id,
        dimension_code,
        dimension_name,
        path_names,
        CASE
            -- 医生序列-门诊 (不含手术)
            WHEN path_names LIKE '医生序列/门诊%' THEN '门诊'
            -- 医生序列-住院 (不含手术)
            WHEN path_names LIKE '医生序列/住院%' THEN '住院'
            -- 医生序列-手术-门诊
            WHEN path_names LIKE '医生序列/手术/门诊%' THEN '门诊'
            -- 医生序列-手术-住院
            WHEN path_names LIKE '医生序列/手术/住院%' THEN '住院'
            -- 护理序列-病区
            WHEN path_names LIKE '护理序列/病区%' THEN '住院'
            -- 护理序列-非病区
            WHEN path_names LIKE '护理序列/非病区%' THEN '门诊'
            -- 医技序列或其他: 不区分
            ELSE NULL
        END as business_type
    FROM dimension_hierarchy
)

-- 查看所有维度及其业务类别判断结果
SELECT 
    dimension_code,
    dimension_name,
    path_names,
    business_type,
    CASE 
        WHEN business_type IS NULL THEN '不区分'
        ELSE business_type
    END as business_type_display
FROM dimension_business_type
ORDER BY path_names;
