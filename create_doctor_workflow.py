"""
创建医生业务价值计算流程
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
from app.models.model_version import ModelVersion


def create_doctor_workflow():
    """创建医生业务价值计算流程"""
    db = SessionLocal()
    
    try:
        # 参数配置
        version_id = 26  # 模型版本ID
        
        # 调试：查看所有版本
        all_versions = db.query(ModelVersion).all()
        print(f"数据库中共有 {len(all_versions)} 个版本:")
        for v in all_versions:
            print(f"  - ID: {v.id}, 名称: {v.name}, 医院ID: {v.hospital_id}")
        
        # 检查版本是否存在
        version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
        if not version:
            print(f"\n错误: 模型版本 {version_id} 不存在")
            return
        
        print(f"找到模型版本: {version.name} (ID: {version_id})")
        
        # 获取默认数据源
        data_source = db.query(DataSource).filter(DataSource.is_default == True).first()
        if not data_source:
            data_source = db.query(DataSource).filter(DataSource.is_enabled == True).first()
        
        if not data_source:
            print("错误: 没有可用的数据源")
            return
        
        print(f"使用数据源: {data_source.name} (ID: {data_source.id})")
        
        # 检查是否已存在同名流程
        existing = db.query(CalculationWorkflow).filter(
            CalculationWorkflow.version_id == version_id,
            CalculationWorkflow.name == "医生业务价值计算流程"
        ).first()
        
        if existing:
            print(f"流程已存在 (ID: {existing.id})，是否删除并重建？(y/n)")
            choice = input().strip().lower()
            if choice == 'y':
                db.delete(existing)
                db.commit()
                print("已删除旧流程")
            else:
                print("取消操作")
                return
        
        # 创建计算流程
        workflow = CalculationWorkflow(
            version_id=version_id,
            name="医生业务价值计算流程",
            description="统计医生序列各维度的工作量和业务价值，包括门诊、住院、手术三大类",
            is_active=True
        )
        db.add(workflow)
        db.flush()  # 获取workflow.id
        
        print(f"创建流程: {workflow.name} (ID: {workflow.id})")
        
        # 创建步骤1: 医生业务价值计算
        step1_sql = """-- ============================================================================
-- 医生业务价值计算
-- ============================================================================
-- 功能: 统计医生序列各末级维度的工作量和业务价值
-- 
-- 输入参数:
--   {task_id}            - 计算任务ID
--   {current_year_month} - 当期年月 (格式: YYYY-MM)
--   {hospital_id}        - 医疗机构ID
--   {version_id}         - 模型版本ID
--
-- 数据来源:
--   charge_details           - 收费明细表
--   dimension_item_mappings  - 维度项目映射表
--   departments              - 科室表
--   model_nodes              - 模型节点表
--
-- 算法说明:
--   1. 门诊-诊察: 统计门诊诊察类收费金额
--   2. 门诊-诊断: 统计门诊诊断类收费金额（检查化验、中草药、治疗手术）
--   3. 住院-诊察: 统计住院诊察类收费金额
--   4. 住院-病例价值: 按住院病例数统计，每例50元
--   5. 住院-诊断: 统计住院诊断类收费金额
--   6. 手术-门诊: 统计门诊手术类收费金额
--   7. 手术-住院: 统计住院手术类收费金额
-- ============================================================================

-- 1. 门诊-诊察类维度
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
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-diag%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 2. 门诊-诊断类维度
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
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-eval%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 3. 门诊-治疗类维度
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
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-out-tr%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 4. 住院-诊察类维度
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
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-diag%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 5. 住院-病例价值 (按病例数统计，每例50元)
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
    COUNT(DISTINCT cd.patient_id) as workload,
    mn.weight,
    mn.weight as original_weight,
    COUNT(DISTINCT cd.patient_id) * mn.weight as value,
    NOW() as created_at
FROM charge_details cd
INNER JOIN model_nodes mn ON mn.code = 'dim-doc-in-case' AND mn.version_id = {version_id}
INNER JOIN departments d ON cd.prescribing_dept_code = d.his_code AND d.hospital_id = {hospital_id}
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 6. 住院-诊断类维度
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
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-eval%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 7. 住院-治疗类维度
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
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-in-tr%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 8. 手术-门诊类维度
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
WHERE cd.business_type = '门诊'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-out%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 9. 手术-住院类维度
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
WHERE cd.business_type = '住院'
  AND TO_CHAR(cd.charge_time, 'YYYY-MM') = '{current_year_month}'
  AND mn.code LIKE 'dim-doc-sur-in%'
  AND mn.is_leaf = TRUE
  AND d.is_active = TRUE
GROUP BY mn.id, d.id, mn.name, mn.code, mn.parent_id, mn.weight;

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count 
FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_type = 'dimension'
  AND (
    node_code LIKE 'dim-doc-out%'
    OR node_code LIKE 'dim-doc-in%'
    OR node_code LIKE 'dim-doc-sur%'
  );
"""
        
        step1 = CalculationStep(
            workflow_id=workflow.id,
            name="医生业务价值计算",
            description="统计医生序列各末级维度的工作量和业务价值，包括门诊诊察/诊断/治疗、住院诊察/病例/诊断/治疗、手术门诊/住院",
            code_type="sql",
            code_content=step1_sql,
            data_source_id=data_source.id,
            sort_order=1.00,
            is_enabled=True
        )
        db.add(step1)
        
        print(f"创建步骤: {step1.name}")
        
        # 提交事务
        db.commit()
        
        print("\n✓ 流程创建成功!")
        print(f"  流程ID: {workflow.id}")
        print(f"  流程名称: {workflow.name}")
        print(f"  步骤数量: 1")
        print(f"\n可以在前端的「计算流程管理」中查看和测试此流程")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_doctor_workflow()
