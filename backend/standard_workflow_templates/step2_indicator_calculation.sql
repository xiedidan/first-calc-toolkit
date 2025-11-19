-- ============================================================================
-- 步骤2: 指标工作量统计
-- ============================================================================
-- 功能: 从工作量统计表中提取各类指标数据,自动匹配到对应的维度
-- 
-- 输入参数(通过占位符):
--   {current_year_month} - 当期年月 (格式: YYYY-MM, 如: 2025-10)
--   {hospital_id}        - 医疗机构ID (从科室信息中获取)
--   {version_id}         - 模型版本ID
--
-- 输出: 直接插入到临时表 dimension_workload_temp
--   dimension_id   - 维度ID
--   department_id  - 科室ID
--   workload_value - 工作量数值
--
-- 数据来源:
--   workload_statistics - 工作量统计表(外部数据源)
--   departments         - 科室表(系统表)
--   model_nodes         - 模型节点表(系统表)
--
-- 算法说明:
--   1. 从 workload_statistics 表读取各类指标数据
--   2. 根据统计类型(stat_type)和级别(stat_level)匹配到对应的维度
--   3. 按科室汇总工作量
--   4. 插入到临时表供后续步骤使用
--
-- 注意: 
--   - 本步骤假设 workload_statistics 表的结构与测试数据一致
--   - 如果实际表结构不同,需要调整 SQL
--   - 维度匹配规则可以根据实际业务调整
-- ============================================================================

-- 创建临时表存储指标工作量
CREATE TEMP TABLE IF NOT EXISTS dimension_workload_temp (
    dimension_id INTEGER,
    department_id INTEGER,
    workload_value DECIMAL(20, 4)
);

-- 清空临时表
TRUNCATE TABLE dimension_workload_temp;

-- 插入护理床日数工作量
-- 匹配规则: 维度编码包含 'nursing' 或 '护理'
INSERT INTO dimension_workload_temp (dimension_id, department_id, workload_value)
SELECT 
    mn.id as dimension_id,
    d.id as department_id,
    SUM(ws.stat_value) as workload_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
CROSS JOIN model_nodes mn
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'nursing_days'
  AND d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
  AND mn.version_id = {version_id}
  AND mn.node_type = 'dimension'
  AND (mn.code LIKE '%nursing%' OR mn.name LIKE '%护理%')
GROUP BY mn.id, d.id;

-- 插入会诊工作量
-- 匹配规则: 维度编码包含 'consultation' 或 '会诊'
INSERT INTO dimension_workload_temp (dimension_id, department_id, workload_value)
SELECT 
    mn.id as dimension_id,
    d.id as department_id,
    SUM(ws.stat_value) as workload_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
CROSS JOIN model_nodes mn
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'consultation'
  AND d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
  AND mn.version_id = {version_id}
  AND mn.node_type = 'dimension'
  AND (mn.code LIKE '%consultation%' OR mn.name LIKE '%会诊%')
GROUP BY mn.id, d.id;

-- 返回结果供查看
SELECT 
    dimension_id,
    department_id,
    workload_value
FROM dimension_workload_temp
ORDER BY dimension_id, department_id;


-- ============================================================================
-- 扩展说明: 如何添加更多指标类型
-- ============================================================================
-- 如果需要处理更多类型的指标,可以在上面添加类似的 INSERT 语句
-- 
-- 示例: 添加 MDT 工作量统计
/*
INSERT INTO dimension_workload_temp (dimension_id, department_id, workload_value)
SELECT 
    mn.id as dimension_id,
    d.id as department_id,
    SUM(ws.stat_value) as workload_value
FROM workload_statistics ws
INNER JOIN departments d ON ws.department_code = d.his_code
CROSS JOIN model_nodes mn
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'mdt'  -- MDT 统计类型
  AND d.hospital_id = {hospital_id}
  AND d.is_active = TRUE
  AND mn.version_id = {version_id}
  AND mn.node_type = 'dimension'
  AND (mn.code LIKE '%mdt%' OR mn.name LIKE '%MDT%')
GROUP BY mn.id, d.id;
*/
--
-- 维度匹配规则说明:
--   - 通过维度的 code 或 name 字段进行模糊匹配
--   - 可以根据实际业务调整匹配规则
--   - 如果维度有明确的类型字段,可以使用精确匹配
--
-- 常见指标类型:
--   - nursing_days: 护理床日数
--   - consultation: 会诊工作量
--   - mdt: MDT 工作量
--   - icu_days: 重症监护床日数
--   - discharge: 出院人次
--   - emergency_observation: 门急诊留观
--
-- ============================================================================
