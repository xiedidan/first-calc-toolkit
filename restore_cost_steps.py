"""
恢复成本维度计算步骤的正确SQL
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 成本维度计算SQL（人员经费和其他费用）
COST_DIMENSION_SQL = """
-- 成本维度计算：人员经费和其他费用
-- 算法：成本值 * weight * -1
-- 只处理人员经费和其他费用两个维度
-- 关键：通过 dimension_code 匹配，使用核算单元代码关联科室

INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_code,
    node_name,
    node_type,
    parent_id,
    workload,
    weight,
    original_weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    mn.code as node_code,
    mn.name as node_name,
    'dimension' as node_type,
    mn.parent_id,
    cv.cost_value * -1 as workload,  -- 成本值取负（成本是负向指标）
    mn.weight,
    mn.weight as original_weight,
    cv.cost_value * mn.weight * -1 as value,  -- 成本值 * 权重 * -1
    NOW() as created_at
FROM cost_values cv
JOIN departments d ON 
    cv.dept_code = d.accounting_unit_code 
    AND d.hospital_id = {hospital_id}
    AND d.is_active = TRUE
JOIN model_nodes mn ON 
    cv.dimension_code = mn.code 
    AND mn.node_type = 'dimension'
    AND mn.version_id = {version_id}
WHERE cv.hospital_id = {hospital_id}
    AND cv.year_month = '{year_month}'
    -- 通过 dimension_code 筛选成本维度
    AND cv.dimension_code IN (
        'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
        'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
    );

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_code IN (
      'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
      'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
  );
"""

# 成本维度计算-材料费和折旧费SQL
COST_MATERIAL_SQL = """
-- 成本维度计算：不收费卫生材料费和折旧（风险）费
-- 算法：维度价值 = ((当期科室总收入 * 成本基准 / 科室收入基准) - 当期成本) * weight
-- 数据来源：
--   department_revenues: 当期科室总收入
--   cost_benchmarks: 成本基准
--   revenue_benchmarks: 科室收入基准
--   cost_values: 当期成本

INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_code,
    node_name,
    node_type,
    parent_id,
    workload,
    weight,
    original_weight,
    value,
    created_at
)
SELECT 
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    mn.code as node_code,
    mn.name as node_name,
    'dimension' as node_type,
    mn.parent_id,
    -- workload = (当期收入 * 成本基准 / 收入基准) - 当期成本
    (dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value as workload,
    mn.weight,
    mn.weight as original_weight,
    -- value = workload * weight
    ((dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value) * mn.weight as value,
    NOW() as created_at
FROM cost_values cv
JOIN departments d ON 
    cv.dept_code = d.accounting_unit_code 
    AND d.hospital_id = {hospital_id}
    AND d.is_active = TRUE
JOIN department_revenues dr ON
    dr.hospital_id = {hospital_id}
    AND dr.year_month = '{year_month}'
    AND dr.department_code = d.his_code
JOIN model_nodes mn ON 
    cv.dimension_code = mn.code 
    AND mn.node_type = 'dimension'
    AND mn.version_id = {version_id}
JOIN cost_benchmarks cb ON
    cb.hospital_id = {hospital_id}
    AND cb.version_id = {version_id}
    AND cb.department_code = d.accounting_unit_code
    AND cb.dimension_code = cv.dimension_code
JOIN revenue_benchmarks rb ON
    rb.hospital_id = {hospital_id}
    AND rb.version_id = {version_id}
    AND rb.department_code = d.his_code
WHERE cv.hospital_id = {hospital_id}
    AND cv.year_month = '{year_month}'
    -- 只处理不收费卫生材料费和折旧（风险）费
    AND cv.dimension_code IN (
        'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
        'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
    )
    AND rb.benchmark_revenue > 0;  -- 避免除以零

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_code IN (
      'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
      'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
  );
"""

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print("=" * 80)
    print("1. 恢复'成本维度计算'步骤的SQL")
    print("=" * 80)
    result = conn.execute(text("""
        UPDATE calculation_steps 
        SET code_content = :sql
        WHERE name = '成本维度计算'
    """), {"sql": COST_DIMENSION_SQL.strip()})
    print(f"   更新了 {result.rowcount} 个步骤")
    
    print("\n" + "=" * 80)
    print("2. 恢复'成本维度计算-材料费和折旧费'步骤的SQL")
    print("=" * 80)
    result = conn.execute(text("""
        UPDATE calculation_steps 
        SET code_content = :sql
        WHERE name = '成本维度计算-材料费和折旧费'
    """), {"sql": COST_MATERIAL_SQL.strip()})
    print(f"   更新了 {result.rowcount} 个步骤")
    
    print("\n" + "=" * 80)
    print("3. 验证流程30的步骤")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cs.sort_order, 
               SUBSTRING(cs.code_content, 1, 80) as sql_preview
        FROM calculation_steps cs
        WHERE cs.workflow_id = 30
        ORDER BY cs.sort_order
    """))
    for row in result:
        print(f"   {row.sort_order}: {row.name} (ID={row.id})")
        print(f"      {row.sql_preview}...")
