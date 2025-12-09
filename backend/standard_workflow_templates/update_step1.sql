UPDATE calculation_steps SET code_content = '-- ============================================================================
-- 步骤1: 维度目录统计
-- ============================================================================
-- 功能: 根据维度-收费项目映射关系,从收费明细表中统计各维度的工作量
--       根据维度的层级结构自动判断业务类别(门诊/住院)
-- 
-- 输入参数(通过占位符):
--   {current_year_month} - 当期年月 (格式: YYYY-MM, 如: 2025-10)
--   {hospital_id}        - 医疗机构ID (从科室信息中获取)
--   {start_date}         - 开始日期 (当月第一天, 如: 2025-10-01)
--   {end_date}           - 结束日期 (当月最后一天, 如: 2025-10-31)
--   {version_id}         - 模型版本ID
--
-- 输出字段:
--   dimension_id           - 维度ID
--   department_id          - 科室ID
--   workload_amount        - 工作量金额
--   workload_quantity      - 工作量数量
--   workload_patient_count - 患者人次
--
-- 数据来源:
--   dimension_item_mappings - 维度-收费项目映射表(系统表)
--   charge_details          - 收费明细表(外部数据源)
--   departments             - 科室表(系统表)
--   model_nodes             - 模型节点表(系统表)
--
-- 业务类别判断规则:
--   1. 医生序列-门诊: 只统计门诊业务
--   2. 医生序列-住院: 只统计住院业务
--   3. 医生序列-手术-门诊: 只统计门诊业务
--   4. 医生序列-手术-住院: 只统计住院业务
--   5. 护理序列-病区: 只统计住院业务
--   6. 护理序列-非病区: 只统计非住院业务(门诊、急诊等)
--   7. 医技序列: 不区分门诊住院,统计全部业务
-- ============================================================================

WITH RECURSIVE dimension_hierarchy AS (
    -- 第1步: 构建维度层级结构,用于判断业务类别
    -- 获取所有维度节点及其祖先路径(从序列节点开始向下递归)
    SELECT 
        mn.id as dimension_id,
        mn.code as dimension_code,
        mn.name as dimension_name,
        mn.parent_id,
        CAST(mn.name AS TEXT) as path_names,  -- 显式转换为TEXT类型
        1 as level
    FROM model_nodes mn
    INNER JOIN model_versions mv ON mn.version_id = mv.id
    WHERE mv.hospital_id = {hospital_id}
      AND mv.is_active = TRUE
      AND mn.node_type = ''sequence''  -- 从序列节点开始
    
    UNION ALL
    
    SELECT 
        mn.id,
        mn.code,
        mn.name,
        mn.parent_id,
        dh.path_names || ''/'' || mn.name,
        dh.level + 1
    FROM model_nodes mn
    INNER JOIN dimension_hierarchy dh ON mn.parent_id = dh.dimension_id
    WHERE mn.node_type = ''dimension''  -- 只递归维度节点
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
            WHEN path_names LIKE ''医生序列/门诊%'' THEN ''门诊''
            -- 医生序列-住院 (不含手术)
            WHEN path_names LIKE ''医生序列/住院%'' THEN ''住院''
            -- 医生序列-手术-门诊
            WHEN path_names LIKE ''医生序列/手术/门诊%'' THEN ''门诊''
            -- 医生序列-手术-住院
            WHEN path_names LIKE ''医生序列/手术/住院%'' THEN ''住院''
            -- 护理序列-病区
            WHEN path_names LIKE ''护理序列/病区%'' THEN ''住院''
            -- 护理序列-非病区
            WHEN path_names LIKE ''护理序列/非病区%'' THEN ''门诊''
            -- 医技序列或其他: 不区分
            ELSE NULL
        END as business_type
    FROM dimension_hierarchy
),

dimension_mappings AS (
    -- 第3步: 获取维度-收费项目映射关系,并关联业务类别
    SELECT DISTINCT
        dbt.dimension_id,
        dbt.business_type,
        dim.item_code
    FROM dimension_item_mappings dim
    INNER JOIN dimension_business_type dbt ON dim.dimension_code = dbt.dimension_code
    WHERE dim.hospital_id = {hospital_id}
),


charge_data AS (
    -- 第4步: 从收费明细表提取指定周期的数据并汇总
    -- 按开单科室、收费项目和业务类别汇总金额、数量、患者人次
    SELECT 
        cd.prescribing_dept_code,
        cd.item_code,
        cd.business_type,
        SUM(cd.amount) as total_amount,
        SUM(cd.quantity) as total_quantity,
        COUNT(DISTINCT cd.patient_id) as patient_count
    FROM charge_details cd
    WHERE cd.charge_time >= ''{start_date}''
      AND cd.charge_time < DATE ''{end_date}'' + INTERVAL ''1 day''  -- 包含结束日期当天
      AND cd.prescribing_dept_code IN (
          -- 只统计参与评估的科室
          SELECT his_code 
          FROM departments 
          WHERE hospital_id = {hospital_id} 
            AND is_active = TRUE
      )
    GROUP BY cd.prescribing_dept_code, cd.item_code, cd.business_type
)


-- 第5步: 关联映射和收费数据,按维度和科室汇总工作量,并插入到calculation_results表
-- 关键: 根据维度的业务类别筛选对应的收费明细
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
    value,
    created_at
)
SELECT 
    ''{task_id}'' as task_id,
    dm.dimension_id as node_id,
    d.id as department_id,
    ''dimension'' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    COALESCE(SUM(cd.total_amount), 0) as workload,
    mn.weight,
    COALESCE(SUM(cd.total_amount), 0) * mn.weight as value,
    NOW() as created_at
FROM dimension_mappings dm
LEFT JOIN charge_data cd ON dm.item_code = cd.item_code
    -- 关键条件: 业务类别匹配
    AND (
        dm.business_type IS NULL  -- 维度不区分业务类别(如医技)
        OR dm.business_type = cd.business_type  -- 业务类别匹配
    )
LEFT JOIN departments d ON cd.prescribing_dept_code = d.his_code
INNER JOIN model_nodes mn ON dm.dimension_id = mn.id
WHERE d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
GROUP BY dm.dimension_id, d.id, mn.name, mn.code, mn.parent_id, mn.weight
HAVING SUM(cd.total_amount) > 0;  -- 只插入有工作量的记录

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results WHERE task_id = ''{task_id}'';

-- ============================================================================
-- 使用说明:
-- 1. 此SQL会自动根据维度的层级结构判断业务类别(门诊/住院)
-- 2. 医生序列的门诊和住院维度会分别统计对应业务类别的收费明细
-- 3. 护理序列的病区和非病区维度会分别统计住院和非住院业务
-- 4. 医技序列不区分业务类别,统计全部收费明细
-- 5. 使用LEFT JOIN确保即使某些维度没有收费数据也能返回(金额为0)
-- 6. HAVING子句过滤掉没有工作量的记录,减少结果集大小
-- 7. 占位符会在执行时自动替换:
--    {start_date} -> 当月第一天 (如: 2025-10-01)
--    {end_date} -> 当月最后一天 (如: 2025-10-31)
--    {hospital_id} -> 医疗机构ID (如: 1)
--    {version_id} -> 模型版本ID (如: 1)
-- ============================================================================

-- ============================================================================
-- 业务类别判断示例:
-- ============================================================================
-- 假设模型结构如下:
--   医生序列
--     ├─ 门诊 (一级维度)
--     │   ├─ 诊察费 (末级维度) -> 只统计门诊业务
--     │   └─ 检查费 (末级维度) -> 只统计门诊业务
--     ├─ 住院 (一级维度)
--     │   ├─ 床位费 (末级维度) -> 只统计住院业务
--     │   └─ 治疗费 (末级维度) -> 只统计住院业务
--     └─ 手术 (一级维度)
--         ├─ 门诊 (二级维度)
--         │   └─ 门诊手术费 (末级维度) -> 只统计门诊业务
--         └─ 住院 (二级维度)
--             └─ 住院手术费 (末级维度) -> 只统计住院业务
--   护理序列
--     ├─ 病区 (一级维度)
--     │   └─ 护理费 (末级维度) -> 只统计住院业务
--     └─ 非病区 (一级维度)
--         └─ 门诊护理费 (末级维度) -> 只统计非住院业务
--   医技序列
--     ├─ 检验 (一级维度)
--     │   └─ 血常规 (末级维度) -> 统计全部业务(门诊+住院)
--     └─ 影像 (一级维度)
--         └─ CT (末级维度) -> 统计全部业务(门诊+住院)
-- ============================================================================
', updated_at = NOW() WHERE id = 62;
