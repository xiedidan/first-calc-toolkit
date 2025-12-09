-- ============================================================================
-- 步骤4: 业务价值汇总
-- ============================================================================
-- 功能: 根据模型结构和权重,自下而上汇总各科室的业务价值,并将序列节点数据插入到 calculation_results
-- 
-- 输入参数(通过占位符):
--   {task_id}    - 计算任务ID
--   {version_id} - 模型版本ID
--
-- 输出: 将序列节点的汇总数据插入到 calculation_results 表
--   task_id       - 任务ID
--   node_id       - 序列节点ID
--   department_id - 科室ID
--   node_type     - 节点类型 (sequence)
--   node_name     - 序列名称
--   node_code     - 序列编码
--   parent_id     - 父节点ID
--   value         - 序列价值（从子维度汇总而来）
--
-- 数据来源:
--   model_nodes         - 模型节点表(系统表)
--   calculation_results - 计算结果表(系统表，读取维度数据)
--
-- 算法说明:
--   1. 加载模型结构(树形结构)
--   2. 加载维度计算结果（Step1/Step2的输出）
--   3. 根据权重类型计算维度得分
--   4. 自下而上递归汇总父节点得分
--   5. 将序列节点的汇总数据插入到 calculation_results 表
-- ============================================================================

WITH RECURSIVE model_structure AS (
    -- 第1步: 加载模型结构
    -- 获取指定版本的所有节点,包含层级关系、权重、权重类型
    SELECT 
        id as node_id,
        parent_id,
        code,
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
        mn.code,
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
    -- 关键: 使用cr.weight（已被Step 3a调整）而不是ms.weight（原始值）
    SELECT 
        cr.node_id as dimension_id,
        cr.department_id,
        cr.workload,
        cr.weight,  -- 使用调整后的权重
        cr.original_weight,  -- 保存原始权重
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


-- 第6步: 将汇总数据插入到 calculation_results 表
-- 插入所有非叶子节点（序列节点 + 中间层级的维度节点）
INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_type,
    node_name,
    node_code,
    parent_id,
    workload,
    weight,
    original_weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    agg.node_id,
    agg.department_id,
    ms.node_type,
    agg.node_name,
    ms.code as node_code,
    ms.parent_id,
    0 as workload,  -- 非叶子节点的工作量为0（由子节点汇总而来）
    ms.weight,
    NULL as original_weight,  -- 非叶子节点不需要original_weight（值是汇总来的）
    agg.score as value,
    NOW() as created_at
FROM aggregated_scores agg
INNER JOIN model_structure ms ON agg.node_id = ms.node_id
WHERE agg.score > 0  -- 只插入有价值的记录
  AND agg.node_id NOT IN (
      -- 排除已经存在的叶子维度节点（Step1/2已插入）
      SELECT node_id 
      FROM calculation_results 
      WHERE task_id = '{task_id}'
  );

-- 返回插入的记录数（统计新插入的序列和中间维度节点）
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND workload = 0;  -- 非叶子节点的workload为0

-- ============================================================================
-- 使用说明:
-- ============================================================================
-- 1. 此SQL实现了自下而上的汇总算法
-- 2. 从 calculation_results 表读取维度数据（Step1/Step2的输出）
-- 3. 递归汇总到序列节点，并将序列数据插入回 calculation_results 表
-- 4. 报表查询时可以直接从 calculation_results 表读取序列和维度数据
-- 5. 占位符会在执行时自动替换:
--    {task_id} -> 计算任务ID (如: 124694a7-3f17-4ff3-831e-5e7efb6febe2)
--    {version_id} -> 模型版本ID (如: 1)
-- ============================================================================

-- ============================================================================
-- 注意事项:
-- ============================================================================
-- 1. 权重类型处理:
--    - 当前简化为统一使用 工作量 × 权重
--    - 实际应用中可能需要区分百分比权重和固定值权重
--    - 可以在dimension_scores CTE中添加CASE语句处理不同权重类型
--
-- 2. 数据流向:
--    - Step1/Step2: 插入维度节点数据到 calculation_results
--    - Step3: 汇总并插入序列节点数据到 calculation_results
--    - 报表查询: 从 calculation_results 读取序列节点，递归汇总显示
--
-- 3. 序列识别:
--    - 通过 node_type = 'sequence' 精确识别序列节点
--    - 不依赖节点名称的模糊匹配
-- ============================================================================
