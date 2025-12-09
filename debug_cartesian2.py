"""
深入诊断笛卡尔积问题
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

TASK_ID = '83289d5f-df1f-4739-afdb-5aa76934eb2a'

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    # 获取任务的版本ID
    result = conn.execute(text("""
        SELECT model_version_id FROM calculation_tasks WHERE task_id = :task_id
    """), {"task_id": TASK_ID})
    version_id = result.fetchone().model_version_id
    
    print("=" * 80)
    print("1. 检查 charge_details 全表数据")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT business_type, COUNT(*) as cnt, SUM(amount) as total
        FROM charge_details
        GROUP BY business_type
    """))
    for row in result:
        print(f"  {row.business_type}: {row.cnt} 条, 金额: {row.total}")
    
    print("\n" + "=" * 80)
    print("2. 模拟完整的 step2 查询，检查 JOIN 结果")
    print("=" * 80)
    
    # 检查一个具体的维度和科室组合
    result = conn.execute(text(f"""
        WITH RECURSIVE dimension_hierarchy AS (
            SELECT 
                mn.id as dimension_id,
                mn.code as dimension_code,
                mn.name as dimension_name,
                mn.parent_id,
                mn.version_id,
                CAST(mn.name AS TEXT) as path_names,
                1 as level
            FROM model_nodes mn
            WHERE mn.version_id = {version_id}
              AND mn.node_type = 'sequence'
            
            UNION ALL
            
            SELECT 
                mn.id,
                mn.code,
                mn.name,
                mn.parent_id,
                mn.version_id,
                dh.path_names || '/' || mn.name,
                dh.level + 1
            FROM model_nodes mn
            INNER JOIN dimension_hierarchy dh ON mn.parent_id = dh.dimension_id
            WHERE mn.node_type = 'dimension'
              AND mn.version_id = {version_id}
        ),
        dimension_business_type AS (
            SELECT 
                dimension_id,
                dimension_code,
                dimension_name,
                path_names,
                CASE
                    WHEN path_names LIKE '医生/门诊%' OR path_names LIKE '医生序列/门诊%' THEN '门诊'
                    WHEN path_names LIKE '医生/住院%' OR path_names LIKE '医生序列/住院%' THEN '住院'
                    WHEN path_names LIKE '医生/手术/门诊%' OR path_names LIKE '医生序列/手术/门诊%' THEN '门诊'
                    WHEN path_names LIKE '医生/手术/住院%' OR path_names LIKE '医生序列/手术/住院%' THEN '住院'
                    WHEN path_names LIKE '护理/病区%' OR path_names LIKE '护理序列/病区%' THEN '住院'
                    WHEN path_names LIKE '护理/非病区%' OR path_names LIKE '护理序列/非病区%' THEN '门诊'
                    ELSE NULL
                END as business_type
            FROM dimension_hierarchy
        ),
        dimension_mappings AS (
            SELECT DISTINCT
                dbt.dimension_id,
                dbt.business_type,
                dim.item_code
            FROM dimension_item_mappings dim
            INNER JOIN dimension_business_type dbt ON dim.dimension_code = dbt.dimension_code
            WHERE dim.hospital_id = 1
        ),
        charge_data AS (
            SELECT 
                cd.prescribing_dept_code,
                cd.item_code,
                cd.business_type,
                SUM(cd.amount) as total_amount,
                SUM(cd.quantity) as total_quantity,
                COUNT(DISTINCT cd.patient_id) as patient_count
            FROM charge_details cd
            WHERE cd.charge_time >= '2025-10-01'
              AND cd.charge_time < '2025-11-01'
              AND cd.prescribing_dept_code IN (
                  SELECT his_code 
                  FROM departments 
                  WHERE hospital_id = 1 
                    AND is_active = TRUE
              )
            GROUP BY cd.prescribing_dept_code, cd.item_code, cd.business_type
        )
        -- 检查 CT检查 维度的 JOIN 结果
        SELECT 
            dm.dimension_id,
            dm.business_type as dim_business_type,
            dm.item_code,
            cd.prescribing_dept_code,
            cd.business_type as charge_business_type,
            cd.total_amount
        FROM dimension_mappings dm
        LEFT JOIN charge_data cd ON dm.item_code = cd.item_code
            AND (
                dm.business_type IS NULL
                OR dm.business_type = cd.business_type
            )
        WHERE dm.dimension_id = 1366  -- CT检查
        LIMIT 20
    """))
    rows = list(result)
    print(f"  CT检查(id=1366) 的 JOIN 结果: {len(rows)} 条")
    for row in rows:
        print(f"    dim_type={row.dim_business_type}, item={row.item_code}, dept={row.prescribing_dept_code}, charge_type={row.charge_business_type}, amount={row.total_amount}")
    
    print("\n" + "=" * 80)
    print("3. 检查 CT检查 的映射项目数")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT COUNT(DISTINCT item_code) as item_count
        FROM dimension_item_mappings
        WHERE dimension_code = 'dim-tech-exam-ct'
    """))
    row = result.fetchone()
    print(f"  CT检查 映射了 {row.item_count} 个项目")
    
    print("\n" + "=" * 80)
    print("4. 检查 charge_data 中 CT检查 相关项目的数据")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT 
            cd.prescribing_dept_code,
            cd.item_code,
            cd.business_type,
            SUM(cd.amount) as total_amount
        FROM charge_details cd
        WHERE cd.charge_time >= '2025-10-01'
          AND cd.charge_time < '2025-11-01'
          AND cd.item_code IN (
              SELECT item_code FROM dimension_item_mappings WHERE dimension_code = 'dim-tech-exam-ct'
          )
        GROUP BY cd.prescribing_dept_code, cd.item_code, cd.business_type
        ORDER BY cd.prescribing_dept_code, cd.item_code
        LIMIT 20
    """))
    rows = list(result)
    print(f"  charge_data 中 CT检查 相关数据: {len(rows)} 条")
    for row in rows:
        print(f"    dept={row.prescribing_dept_code}, item={row.item_code}, type={row.business_type}, amount={row.total_amount}")
