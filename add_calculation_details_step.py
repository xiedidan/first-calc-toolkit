"""
为工作流添加 calculation_details 生成步骤

这个步骤应该在维度计算步骤之前执行，生成核算明细数据
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# SQL 模板 - 生成 calculation_details
CALCULATION_DETAILS_SQL = """
-- ============================================================================
-- 生成核算明细表 (calculation_details)
-- ============================================================================
-- 将 charge_details 按维度和项目聚合，用于支持下钻功能
-- 统计逻辑：
--   - 诊断维度 (dim-doc-*-eval-*): 使用开单科室 (prescribing_dept_code)
--   - 其他所有维度: 使用执行科室 (executing_dept_code)
-- ============================================================================

-- 清理旧数据
DELETE FROM calculation_details WHERE task_id = '{task_id}';

-- 1. 医生序列 - 诊断维度（使用开单科室）
INSERT INTO calculation_details (
    hospital_id, task_id, department_id, department_code,
    node_id, node_code, node_name, parent_id,
    item_code, item_name, item_category,
    business_type, amount, quantity, period, created_at
)
SELECT 
    {hospital_id} as hospital_id,
    '{task_id}' as task_id,
    d.id as department_id,
    cd.prescribing_dept_code as department_code,
    mn.id as node_id,
    mn.code as node_code,
    mn.name as node_name,
    mn.parent_id,
    cd.item_code,
    cd.item_name,
    ci.item_category,
    cd.business_type,
    SUM(cd.amount) as amount,
    SUM(cd.quantity) as quantity,
    '{year_month}' as period,
    NOW()
FROM charge_details cd
JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
    AND dim.hospital_id = {hospital_id}
JOIN model_nodes mn ON dim.dimension_code = mn.code 
    AND mn.version_id = {version_id}
JOIN departments d ON cd.prescribing_dept_code = d.his_code 
    AND d.hospital_id = {hospital_id}
LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
    AND ci.hospital_id = {hospital_id}
WHERE cd.year_month = '{year_month}'
AND (mn.code LIKE 'dim-doc-in-eval-%' OR mn.code LIKE 'dim-doc-out-eval-%')
AND (
    (mn.code LIKE 'dim-doc-in-%' AND cd.business_type = '住院')
    OR (mn.code LIKE 'dim-doc-out-%' AND cd.business_type = '门诊')
)
GROUP BY d.id, cd.prescribing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
         cd.item_code, cd.item_name, ci.item_category, cd.business_type;

-- 2. 医生序列 - 非诊断维度（使用执行科室）
INSERT INTO calculation_details (
    hospital_id, task_id, department_id, department_code,
    node_id, node_code, node_name, parent_id,
    item_code, item_name, item_category,
    business_type, amount, quantity, period, created_at
)
SELECT 
    {hospital_id} as hospital_id,
    '{task_id}' as task_id,
    d.id as department_id,
    cd.executing_dept_code as department_code,
    mn.id as node_id,
    mn.code as node_code,
    mn.name as node_name,
    mn.parent_id,
    cd.item_code,
    cd.item_name,
    ci.item_category,
    cd.business_type,
    SUM(cd.amount) as amount,
    SUM(cd.quantity) as quantity,
    '{year_month}' as period,
    NOW()
FROM charge_details cd
JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
    AND dim.hospital_id = {hospital_id}
JOIN model_nodes mn ON dim.dimension_code = mn.code 
    AND mn.version_id = {version_id}
JOIN departments d ON cd.executing_dept_code = d.his_code 
    AND d.hospital_id = {hospital_id}
LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
    AND ci.hospital_id = {hospital_id}
WHERE cd.year_month = '{year_month}'
AND mn.code LIKE 'dim-doc-%'
AND mn.code NOT LIKE 'dim-doc-in-eval-%'
AND mn.code NOT LIKE 'dim-doc-out-eval-%'
AND (
    (mn.code LIKE 'dim-doc-in-%' AND cd.business_type = '住院')
    OR (mn.code LIKE 'dim-doc-out-%' AND cd.business_type = '门诊')
    OR (mn.code LIKE 'dim-doc-sur-in-%' AND cd.business_type = '住院')
    OR (mn.code LIKE 'dim-doc-sur-out-%' AND cd.business_type = '门诊')
)
GROUP BY d.id, cd.executing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
         cd.item_code, cd.item_name, ci.item_category, cd.business_type;

-- 3. 医技序列（使用执行科室，不区分门诊住院）
INSERT INTO calculation_details (
    hospital_id, task_id, department_id, department_code,
    node_id, node_code, node_name, parent_id,
    item_code, item_name, item_category,
    business_type, amount, quantity, period, created_at
)
SELECT 
    {hospital_id} as hospital_id,
    '{task_id}' as task_id,
    d.id as department_id,
    cd.executing_dept_code as department_code,
    mn.id as node_id,
    mn.code as node_code,
    mn.name as node_name,
    mn.parent_id,
    cd.item_code,
    cd.item_name,
    ci.item_category,
    cd.business_type,
    SUM(cd.amount) as amount,
    SUM(cd.quantity) as quantity,
    '{year_month}' as period,
    NOW()
FROM charge_details cd
JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
    AND dim.hospital_id = {hospital_id}
JOIN model_nodes mn ON dim.dimension_code = mn.code 
    AND mn.version_id = {version_id}
JOIN departments d ON cd.executing_dept_code = d.his_code 
    AND d.hospital_id = {hospital_id}
LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
    AND ci.hospital_id = {hospital_id}
WHERE cd.year_month = '{year_month}'
AND mn.code LIKE 'dim-tech-%'
GROUP BY d.id, cd.executing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
         cd.item_code, cd.item_name, ci.item_category, cd.business_type;

-- 4. 护理序列 - 收费类维度（使用执行科室，不区分门诊住院）
-- 注意：工作量统计维度（床日、出入转院、手术管理、手术室护理、监护）不生成明细
INSERT INTO calculation_details (
    hospital_id, task_id, department_id, department_code,
    node_id, node_code, node_name, parent_id,
    item_code, item_name, item_category,
    business_type, amount, quantity, period, created_at
)
SELECT 
    {hospital_id} as hospital_id,
    '{task_id}' as task_id,
    d.id as department_id,
    cd.executing_dept_code as department_code,
    mn.id as node_id,
    mn.code as node_code,
    mn.name as node_name,
    mn.parent_id,
    cd.item_code,
    cd.item_name,
    ci.item_category,
    cd.business_type,
    SUM(cd.amount) as amount,
    SUM(cd.quantity) as quantity,
    '{year_month}' as period,
    NOW()
FROM charge_details cd
JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
    AND dim.hospital_id = {hospital_id}
JOIN model_nodes mn ON dim.dimension_code = mn.code 
    AND mn.version_id = {version_id}
JOIN departments d ON cd.executing_dept_code = d.his_code 
    AND d.hospital_id = {hospital_id}
LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
    AND ci.hospital_id = {hospital_id}
WHERE cd.year_month = '{year_month}'
AND mn.code LIKE 'dim-nur-%'
AND mn.code NOT LIKE 'dim-nur-bed%'
AND mn.code NOT LIKE 'dim-nur-trans%'
AND mn.code NOT LIKE 'dim-nur-op%'
AND mn.code NOT LIKE 'dim-nur-or%'
AND mn.code NOT LIKE 'dim-nur-mon%'
GROUP BY d.id, cd.executing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
         cd.item_code, cd.item_name, ci.item_category, cd.business_type;

-- 返回插入记录数
SELECT COUNT(*) as inserted_count FROM calculation_details WHERE task_id = '{task_id}';
"""


def add_step_to_workflow(workflow_id: int, sort_order: float = 0.5):
    """
    为指定工作流添加 calculation_details 生成步骤
    
    Args:
        workflow_id: 工作流ID
        sort_order: 步骤排序（默认0.5，在第一个步骤之前）
    """
    with engine.connect() as conn:
        # 检查工作流是否存在
        result = conn.execute(text(
            "SELECT id, name FROM calculation_workflows WHERE id = :id"
        ), {"id": workflow_id})
        workflow = result.fetchone()
        
        if not workflow:
            print(f"错误：工作流 {workflow_id} 不存在")
            return False
        
        print(f"工作流: {workflow[1]} (ID: {workflow[0]})")
        
        # 检查是否已存在该步骤
        result = conn.execute(text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = :workflow_id AND name = '生成核算明细'
        """), {"workflow_id": workflow_id})
        
        if result.fetchone():
            print("该工作流已存在'生成核算明细'步骤，跳过")
            return True
        
        # 插入新步骤
        conn.execute(text("""
            INSERT INTO calculation_steps (
                workflow_id, name, description, code_type, code_content, 
                sort_order, is_enabled, created_at, updated_at
            ) VALUES (
                :workflow_id, 
                '生成核算明细',
                '生成 calculation_details 表，用于支持维度下钻功能',
                'sql',
                :code_content,
                :sort_order,
                true,
                NOW(),
                NOW()
            )
        """), {
            "workflow_id": workflow_id,
            "code_content": CALCULATION_DETAILS_SQL,
            "sort_order": sort_order
        })
        conn.commit()
        
        print(f"成功添加步骤，sort_order = {sort_order}")
        return True


def list_workflows():
    """列出所有工作流"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT w.id, w.name, w.version_id, 
                   (SELECT COUNT(*) FROM calculation_steps WHERE workflow_id = w.id) as step_count
            FROM calculation_workflows w
            ORDER BY w.id DESC
            LIMIT 20
        """))
        
        print("\n可用的工作流:")
        print(f"{'ID':<5} {'名称':<40} {'版本ID':<10} {'步骤数':<10}")
        print("-" * 70)
        for row in result:
            print(f"{row[0]:<5} {row[1]:<40} {row[2]:<10} {row[3]:<10}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="为工作流添加 calculation_details 生成步骤")
    parser.add_argument("--workflow-id", type=int, help="工作流ID")
    parser.add_argument("--sort-order", type=float, default=0.5, help="步骤排序（默认0.5）")
    parser.add_argument("--list", action="store_true", help="列出所有工作流")
    
    args = parser.parse_args()
    
    if args.list:
        list_workflows()
    elif args.workflow_id:
        add_step_to_workflow(args.workflow_id, args.sort_order)
    else:
        print("用法:")
        print("  python add_calculation_details_step.py --list")
        print("  python add_calculation_details_step.py --workflow-id 31 --sort-order 0.5")
        list_workflows()
