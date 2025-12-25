"""
更新成本直接扣减步骤的SQL，添加核算序列过滤
仿照工作量计算步骤，只计算允许核算的序列，其他序列置0
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 新的成本直接扣减SQL，添加了核算序列过滤
NEW_COST_DEDUCTION_SQL = """-- ============================================================================
-- 成本直接扣减
-- ============================================================================
-- 功能: 根据成本报表数据，计算成本维度的业务价值（负值扣减）
-- 算法: 业务价值 = -1 * 成本取值 * 维度权重
-- 成本维度映射:
--   - *-cost-hr (人员经费) -> personnel_cost
--   - *-cost-mat (不收费卫生材料费) -> material_cost
--   - *-cost-depr (折旧风险费) -> depreciation_cost
--   - *-cost-other (其他费用) -> other_cost
-- 核算序列过滤:
--   - 医生序列成本只计算允许核算医生序列的科室
--   - 护理序列成本只计算允许核算护理序列的科室
--   - 医技序列成本只计算允许核算医技序列的科室
-- ============================================================================

-- 医生序列成本扣减（只计算允许核算医生序列的科室）
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    CASE
        WHEN mn.code = 'dim-doc-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-doc-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-doc-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-doc-cost-other' THEN cr.other_cost
    END as workload,
    mn.weight,
    mn.weight as original_weight,
    -1 * CASE
        WHEN mn.code = 'dim-doc-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-doc-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-doc-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-doc-cost-other' THEN cr.other_cost
    END * COALESCE(mn.weight, 0) as value,
    NOW() as created_at
FROM model_nodes mn
CROSS JOIN departments d
JOIN cost_reports cr ON cr.department_code = d.accounting_unit_code
    AND cr.period = '{period}'
    AND cr.hospital_id = {hospital_id}
WHERE mn.version_id = {version_id}
    AND mn.code IN ('dim-doc-cost-hr', 'dim-doc-cost-mat', 'dim-doc-cost-depr', 'dim-doc-cost-other')
    AND d.hospital_id = {hospital_id}
    AND d.is_active = true
    AND '医生' = ANY(d.accounting_sequences);

-- 护理序列成本扣减（只计算允许核算护理序列的科室）
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    CASE
        WHEN mn.code = 'dim-nur-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-nur-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-nur-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-nur-cost-other' THEN cr.other_cost
    END as workload,
    mn.weight,
    mn.weight as original_weight,
    -1 * CASE
        WHEN mn.code = 'dim-nur-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-nur-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-nur-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-nur-cost-other' THEN cr.other_cost
    END * COALESCE(mn.weight, 0) as value,
    NOW() as created_at
FROM model_nodes mn
CROSS JOIN departments d
JOIN cost_reports cr ON cr.department_code = d.accounting_unit_code
    AND cr.period = '{period}'
    AND cr.hospital_id = {hospital_id}
WHERE mn.version_id = {version_id}
    AND mn.code IN ('dim-nur-cost-hr', 'dim-nur-cost-mat', 'dim-nur-cost-depr', 'dim-nur-cost-other')
    AND d.hospital_id = {hospital_id}
    AND d.is_active = true
    AND '护理' = ANY(d.accounting_sequences);

-- 医技序列成本扣减（只计算允许核算医技序列的科室）
INSERT INTO calculation_results (
    task_id, node_id, department_id, node_type, node_name, node_code,
    parent_id, workload, weight, original_weight, value, created_at
)
SELECT
    '{task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    CASE
        WHEN mn.code = 'dim-tech-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-tech-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-tech-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-tech-cost-other' THEN cr.other_cost
    END as workload,
    mn.weight,
    mn.weight as original_weight,
    -1 * CASE
        WHEN mn.code = 'dim-tech-cost-hr' THEN cr.personnel_cost
        WHEN mn.code = 'dim-tech-cost-mat' THEN cr.material_cost
        WHEN mn.code = 'dim-tech-cost-depr' THEN cr.depreciation_cost
        WHEN mn.code = 'dim-tech-cost-other' THEN cr.other_cost
    END * COALESCE(mn.weight, 0) as value,
    NOW() as created_at
FROM model_nodes mn
CROSS JOIN departments d
JOIN cost_reports cr ON cr.department_code = d.accounting_unit_code
    AND cr.period = '{period}'
    AND cr.hospital_id = {hospital_id}
WHERE mn.version_id = {version_id}
    AND mn.code IN ('dim-tech-cost-hr', 'dim-tech-cost-mat', 'dim-tech-cost-depr', 'dim-tech-cost-other')
    AND d.hospital_id = {hospital_id}
    AND d.is_active = true
    AND '医技' = ANY(d.accounting_sequences);

-- 返回插入记录数
SELECT COUNT(*) as inserted_count FROM calculation_results WHERE task_id = '{task_id}' AND node_code LIKE '%-cost-%';"""


def update_cost_deduction_step():
    """更新成本直接扣减步骤的SQL"""
    workflow_id = 33
    step_id = 133  # 成本直接扣减步骤
    
    with engine.connect() as conn:
        # 验证步骤存在
        result = conn.execute(text("""
            SELECT id, name, workflow_id FROM calculation_steps 
            WHERE id = :step_id AND workflow_id = :workflow_id
        """), {"step_id": step_id, "workflow_id": workflow_id})
        step = result.fetchone()
        
        if not step:
            print(f"错误: 未找到步骤 ID={step_id}, workflow_id={workflow_id}")
            return False
        
        print(f"找到步骤: ID={step.id}, 名称={step.name}")
        
        # 更新SQL
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql, updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": NEW_COST_DEDUCTION_SQL, "step_id": step_id})
        conn.commit()
        
        # 验证更新
        result = conn.execute(text("""
            SELECT LENGTH(code_content) as sql_length,
                   code_content LIKE '%accounting_sequences%' as has_filter
            FROM calculation_steps WHERE id = :step_id
        """), {"step_id": step_id})
        verify = result.fetchone()
        
        print(f"更新完成:")
        print(f"  - SQL长度: {verify.sql_length} 字符")
        print(f"  - 包含核算序列过滤: {verify.has_filter}")
        
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("更新成本直接扣减步骤 - 添加核算序列过滤")
    print("=" * 60)
    
    success = update_cost_deduction_step()
    
    if success:
        print("\n✓ 更新成功！")
        print("\n变更说明:")
        print("  - 医生序列成本: 只计算 accounting_sequences 包含 '医生' 的科室")
        print("  - 护理序列成本: 只计算 accounting_sequences 包含 '护理' 的科室")
        print("  - 医技序列成本: 只计算 accounting_sequences 包含 '医技' 的科室")
    else:
        print("\n✗ 更新失败")
