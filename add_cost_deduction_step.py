"""
添加成本直接扣减步骤到计算流程ID33

成本直接扣减算法：
业务价值 = -1 * 该维度成本取值 * 该维度权重

成本维度映射关系：
- dim-doc-cost-hr (人员经费) -> cost_reports.personnel_cost
- dim-doc-cost-mat (不收费卫生材料费) -> cost_reports.material_cost
- dim-doc-cost-depr (折旧风险费) -> cost_reports.depreciation_cost
- dim-doc-cost-other (其他费用) -> cost_reports.other_cost
- 同理适用于 dim-nur-cost-* 和 dim-tech-cost-*
"""

import os
from sqlalchemy import create_engine, text
from datetime import datetime

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

# 成本直接扣减SQL模板
COST_DEDUCTION_SQL = """-- ============================================================================
-- 成本直接扣减
-- ============================================================================
-- 功能: 根据成本报表数据，计算成本维度的业务价值（负值扣减）
-- 算法: 业务价值 = -1 * 成本取值 * 维度权重
-- 成本维度映射:
--   - *-cost-hr (人员经费) -> personnel_cost
--   - *-cost-mat (不收费卫生材料费) -> material_cost
--   - *-cost-depr (折旧风险费) -> depreciation_cost
--   - *-cost-other (其他费用) -> other_cost
-- ============================================================================

-- 医生序列成本扣减
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
    AND d.is_active = true;

-- 护理序列成本扣减
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
    AND d.is_active = true;

-- 医技序列成本扣减
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
    AND d.is_active = true;

-- 返回插入记录数
SELECT COUNT(*) as inserted_count FROM calculation_results WHERE task_id = '{task_id}' AND node_code LIKE '%-cost-%';
"""

def add_cost_deduction_step():
    """添加成本直接扣减步骤"""
    workflow_id = 33
    
    with engine.connect() as conn:
        # 1. 先调整现有步骤的sort_order，为新步骤腾出位置
        # 医技业务价值计算是sort_order=3，新步骤放在3.5
        # 业务导向调整是4，业务价值汇总是5
        
        # 检查是否已存在成本扣减步骤
        result = conn.execute(text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = :workflow_id AND name = '成本直接扣减'
        """), {"workflow_id": workflow_id})
        existing = result.fetchone()
        
        if existing:
            print(f"成本直接扣减步骤已存在 (id={existing[0]})，更新SQL内容...")
            conn.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :sql, updated_at = NOW()
                WHERE id = :step_id
            """), {"sql": COST_DEDUCTION_SQL, "step_id": existing[0]})
            conn.commit()
            print("SQL内容已更新")
            return
        
        # 2. 将sort_order >= 4的步骤后移1位
        print("调整现有步骤顺序...")
        conn.execute(text("""
            UPDATE calculation_steps 
            SET sort_order = sort_order + 1, updated_at = NOW()
            WHERE workflow_id = :workflow_id AND sort_order >= 4
        """), {"workflow_id": workflow_id})
        
        # 3. 插入新步骤，sort_order = 4（在医技业务价值计算之后）
        print("插入成本直接扣减步骤...")
        conn.execute(text("""
            INSERT INTO calculation_steps (
                workflow_id, name, description, code_type, code_content, 
                sort_order, is_enabled, created_at, updated_at
            ) VALUES (
                :workflow_id, 
                '成本直接扣减',
                '根据成本报表数据，计算成本维度的业务价值（负值扣减）。算法：业务价值 = -1 * 成本取值 * 维度权重',
                'sql',
                :sql,
                4.00,
                true,
                NOW(),
                NOW()
            )
        """), {"workflow_id": workflow_id, "sql": COST_DEDUCTION_SQL})
        
        conn.commit()
        print("成本直接扣减步骤添加成功！")
        
        # 4. 显示更新后的步骤列表
        result = conn.execute(text("""
            SELECT id, name, sort_order 
            FROM calculation_steps 
            WHERE workflow_id = :workflow_id 
            ORDER BY sort_order
        """), {"workflow_id": workflow_id})
        
        print("\n更新后的步骤列表:")
        print("-" * 50)
        for row in result:
            print(f"  {row[2]:.2f} - {row[1]} (id={row[0]})")

if __name__ == "__main__":
    add_cost_deduction_step()
