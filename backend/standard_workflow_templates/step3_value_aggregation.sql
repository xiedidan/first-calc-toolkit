-- ============================================================================
-- 步骤3: 业务价值汇总
-- ============================================================================
-- 功能: 根据模型结构和权重,自下而上汇总各科室的业务价值
-- 
-- 输入参数(通过占位符):
--   {task_id}    - 计算任务ID
--   {version_id} - 模型版本ID
--
-- 输出字段:
--   task_id            - 任务ID
--   department_id      - 科室ID
--   doctor_value       - 医生序列价值
--   nursing_value      - 护理序列价值
--   medical_tech_value - 医技序列价值
--   total_value        - 科室总价值
--
-- 数据来源:
--   model_nodes         - 模型节点表(系统表)
--   calculation_results - 计算结果表(系统表)
--
-- 算法说明:
--   1. 加载模型结构(树形结构)
--   2. 加载维度计算结果
--   3. 根据权重类型计算维度得分
--   4. 自下而上递归汇总父节点得分
--   5. 提取序列得分和科室总价值
-- ============================================================================

WITH RECURSIVE model_structure AS (
    -- 第1步: 加载模型结构
    -- 获取指定版本的所有节点,包含层级关系、权重、权重类型
    SELECT 
        id as node_id,
        parent_id,
        name as node_name,
        node_type,
        calc_type,
        weight,
        sort_order,
        0 as level  -- 根节点层级为0
    FROM model_nodes
    WHERE version_id = {version_id}
      AND parent_id IS NULL  -- 从根节点开始
    
    UNION ALL
    
    -- 递归获取子节点
    SELECT 
        mn.id,
        mn.parent_id,
        mn.name,
        mn.node_type,
        mn.calc_type,
        mn.weight,
        mn.sort_order,
        ms.level + 1
    FROM model_nodes mn
    INNER JOIN model_structure ms ON mn.parent_id = ms.node_id
    WHERE mn.version_id = {version_id}
),


dimension_results AS (
    -- 第2步: 加载维度计算结果
    -- 从calculation_results表获取指定任务的所有维度计算结果
    SELECT 
        cr.node_id as dimension_id,
        cr.department_id,
        cr.workload,
        ms.weight,
        ms.node_name
    FROM calculation_results cr
    INNER JOIN model_structure ms ON cr.node_id = ms.node_id
    WHERE cr.task_id = '{task_id}'
      AND ms.node_type = 'dimension'  -- 只选择维度节点
),


dimension_scores AS (
    -- 第3步: 计算维度得分
    -- 根据权重类型(百分比或固定值)计算每个维度的得分
    -- 百分比权重: 得分 = 工作量 × 权重
    -- 固定值权重: 得分 = 工作量 × 单价
    SELECT 
        dr.dimension_id,
        dr.department_id,
        dr.workload,
        dr.weight,
        -- 简化处理: 统一使用 工作量 × 权重 计算得分
        -- 实际应用中,可以根据calc_type区分百分比和固定值
        COALESCE(dr.workload * dr.weight, 0) as score
    FROM dimension_results dr
),


node_hierarchy AS (
    -- 第4步: 构建节点层级关系（递归获取所有祖先节点）
    -- 基础情况: 维度节点本身
    SELECT 
        ds.dimension_id as leaf_node_id,
        ds.dimension_id as ancestor_node_id,
        ds.department_id,
        ds.score,
        ms.parent_id,
        ms.node_name,
        ms.level,
        0 as depth
    FROM dimension_scores ds
    INNER JOIN model_structure ms ON ds.dimension_id = ms.node_id
    
    UNION ALL
    
    -- 递归情况: 获取父节点
    SELECT 
        nh.leaf_node_id,
        ms.node_id as ancestor_node_id,
        nh.department_id,
        nh.score,
        ms.parent_id,
        ms.node_name,
        ms.level,
        nh.depth + 1
    FROM node_hierarchy nh
    INNER JOIN model_structure ms ON nh.parent_id = ms.node_id
    WHERE nh.parent_id IS NOT NULL
),

aggregated_scores AS (
    -- 第5步: 汇总每个节点的得分（所有子孙节点的得分之和）
    SELECT 
        ancestor_node_id as node_id,
        department_id,
        node_name,
        level,
        SUM(score) as score
    FROM node_hierarchy
    GROUP BY ancestor_node_id, department_id, node_name, level
)


-- 第6步: 提取序列得分并计算科室总价值
SELECT 
    '{task_id}' as task_id,
    department_id,
    -- 提取医生序列价值 (假设序列名称包含'医生'或'doctor')
    COALESCE(MAX(CASE 
        WHEN node_name LIKE '%医生%' OR node_name LIKE '%doctor%' 
        THEN score 
    END), 0) as doctor_value,
    -- 提取护理序列价值 (假设序列名称包含'护理'或'nursing')
    COALESCE(MAX(CASE 
        WHEN node_name LIKE '%护理%' OR node_name LIKE '%nursing%' 
        THEN score 
    END), 0) as nursing_value,
    -- 提取医技序列价值 (假设序列名称包含'医技'或'medical')
    COALESCE(MAX(CASE 
        WHEN node_name LIKE '%医技%' OR node_name LIKE '%medical%' 
        THEN score 
    END), 0) as medical_tech_value,
    -- 计算科室总价值 (所有序列得分之和)
    COALESCE(SUM(score), 0) as total_value
FROM aggregated_scores
WHERE level = 1  -- 只选择序列级别的节点(假设序列在第1层)
GROUP BY department_id
ORDER BY department_id;

-- ============================================================================
-- 使用说明:
-- ============================================================================
-- 1. 此SQL实现了自下而上的汇总算法
-- 2. 序列识别基于节点名称的模糊匹配,可能需要根据实际情况调整
-- 3. 如果模型结构不同,需要调整level的值和序列识别逻辑
-- 4. 占位符会在执行时自动替换:
--    {task_id} -> 计算任务ID (如: task_20251113_001)
--    {version_id} -> 模型版本ID (如: 123)
-- ============================================================================

-- ============================================================================
-- 注意事项:
-- ============================================================================
-- 1. 权重类型处理:
--    - 当前简化为统一使用 工作量 × 权重
--    - 实际应用中可能需要区分百分比权重和固定值权重
--    - 可以在dimension_scores CTE中添加CASE语句处理不同权重类型
--
-- 2. 序列识别:
--    - 当前使用节点名称模糊匹配识别序列
--    - 更可靠的方法是在model_nodes表中添加sequence_type字段
--    - 或者使用固定的parent_id来识别序列节点
--
-- 3. 层级假设:
--    - 当前假设序列在第1层(level=1)
--    - 如果模型结构不同,需要调整WHERE level = 1的条件
--    - 可以通过查询model_structure确认实际层级
-- ============================================================================
