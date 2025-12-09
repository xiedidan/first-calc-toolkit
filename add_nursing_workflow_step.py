"""
为医生业务价值计算流程(ID=31)添加护理业务价值计算步骤
"""
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.data_source import DataSource


def add_nursing_step():
    """为工作流31添加护理业务价值计算步骤"""
    db = SessionLocal()
    
    try:
        workflow_id = 31
        
        # 检查工作流是否存在
        workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
        if not workflow:
            print(f"错误: 工作流 {workflow_id} 不存在")
            return
        
        print(f"找到工作流: {workflow.name} (ID: {workflow_id})")
        
        # 获取默认数据源
        data_source = db.query(DataSource).filter(DataSource.is_default == True).first()
        if not data_source:
            data_source = db.query(DataSource).filter(DataSource.is_enabled == True).first()
        
        if not data_source:
            print("错误: 没有可用的数据源")
            return
        
        print(f"使用数据源: {data_source.name} (ID: {data_source.id})")
        
        # 检查是否已存在护理步骤
        existing = db.query(CalculationStep).filter(
            CalculationStep.workflow_id == workflow_id,
            CalculationStep.name == "护理业务价值计算"
        ).first()
        
        if existing:
            print(f"步骤已存在 (ID: {existing.id})，是否删除并重建？(y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                db.delete(existing)
                db.commit()
                print("已删除旧步骤")
            else:
                print("取消操作")
                return
        
        # 创建护理业务价值计算步骤SQL
        # 分为两部分：从charge_details统计的维度 和 从workload_statistics取值的维度
        step_sql = """-- ============================================================================
-- 护理业务价值计算
-- ============================================================================
-- 功能: 统计护理序列各末级维度的工作量和业务价值
-- 
-- 输入参数:
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 数据来源:
--   Part 1: charge_details + dimension_item_mappings (收费明细统计)
--   Part 2: workload_statistics (工作量统计表)
--
-- 维度分类:
--   从charge_details统计: 基础护理、医护协同治疗、甲/乙/丙级护理治疗、其他护理
--   从workload_statistics统计: 床日护理(甲/乙/丙级)、出入转院(入院/日间/出院)
-- ============================================================================

-- ============================================================================
-- Part 1: 从charge_details统计的护理维度
-- ============================================================================

-- 1. 基础护理 (dim-nur-base)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-base'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 2. 医护协同治疗 (dim-nur-collab)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-collab'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 3. 甲级护理治疗 (dim-nur-tr-a)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-a'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 乙级护理治疗 (dim-nur-tr-b)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-b'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 丙级护理治疗 (dim-nur-tr-c)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-tr-c'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 6. 其他护理 (dim-nur-other)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    SUM(cd.amount) as workload,
    mn.weight,
    mn.weight as original_weight,
    SUM(cd.amount) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code AND dim.hospital_id = {hospital_id}
INNER JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code = 'dim-nur-other'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- ============================================================================
-- Part 2: 从workload_statistics统计的护理维度
-- ============================================================================
-- 注意: workload_statistics中的department_code是核算单元代码，需要通过departments表关联

-- 7. 甲级床日护理 (dim-nur-bed-3)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-3'
  AND d.is_active = TRUE;

-- 8. 乙级床日护理 (dim-nur-bed-4)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-4'
  AND d.is_active = TRUE;

-- 9. 丙级床日护理 (dim-nur-bed-5)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-bed-5'
  AND d.is_active = TRUE;

-- 10. 普通入院护理 (dim-nur-trans-in)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-in'
  AND d.is_active = TRUE;

-- 11. 日间护理 (dim-nur-trans-intraday)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-intraday'
  AND d.is_active = TRUE;

-- 12. 普通出院护理 (dim-nur-trans-out)
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
    mn.id as node_id,
    d.id as department_id,
    'dimension' as node_type,
    mn.name as node_name,
    mn.code as node_code,
    mn.parent_id as parent_id,
    ws.stat_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ws.stat_value * mn.weight as value,
    NOW() as created_at
FROM workload_statistics ws
INNER JOIN model_nodes mn ON ws.stat_type = mn.code AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-trans-out'
  AND d.is_active = TRUE;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_type = 'dimension'
  AND node_code LIKE 'dim-nur%';
"""
        
        # 创建步骤
        step = CalculationStep(
            workflow_id=workflow_id,
            name="护理业务价值计算",
            description="统计护理序列各末级维度的工作量和业务价值，包括基础护理、床日护理、出入转院、护理治疗等",
            code_type="sql",
            code_content=step_sql,
            data_source_id=data_source.id,
            sort_order=2.00,
            is_enabled=True
        )
        db.add(step)
        db.commit()
        
        print(f"\n✓ 步骤创建成功!")
        print(f"  步骤ID: {step.id}")
        print(f"  步骤名称: {step.name}")
        print(f"  排序: {step.sort_order}")
        print(f"\n可以在前端的「计算流程管理」中查看和测试此步骤")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    add_nursing_step()
