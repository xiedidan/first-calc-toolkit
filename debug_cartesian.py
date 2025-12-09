"""
诊断笛卡尔积问题
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
    print("=" * 80)
    print(f"1. 检查任务 {TASK_ID} 的基本信息")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT task_id, model_version_id, period, status, created_at
        FROM calculation_tasks
        WHERE task_id = :task_id
    """), {"task_id": TASK_ID})
    row = result.fetchone()
    if row:
        print(f"  版本ID: {row.model_version_id}, 周期: {row.period}, 状态: {row.status}")
    
    print("\n" + "=" * 80)
    print("2. 检查计算结果记录数")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT 
            node_type,
            COUNT(*) as record_count,
            COUNT(DISTINCT node_id) as unique_nodes,
            COUNT(DISTINCT department_id) as unique_depts
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY node_type
    """), {"task_id": TASK_ID})
    for row in result:
        print(f"  {row.node_type}: {row.record_count} 条记录, {row.unique_nodes} 个唯一节点, {row.unique_depts} 个唯一科室")
    
    print("\n" + "=" * 80)
    print("3. 检查是否有重复的 (node_id, department_id) 组合")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT node_id, department_id, node_name, COUNT(*) as cnt
        FROM calculation_results
        WHERE task_id = :task_id
        GROUP BY node_id, department_id, node_name
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 20
    """), {"task_id": TASK_ID})
    rows = list(result)
    if rows:
        print(f"  发现 {len(rows)} 个重复组合:")
        for row in rows:
            print(f"    node_id={row.node_id}, dept_id={row.department_id}, name={row.node_name}, count={row.cnt}")
    else:
        print("  没有发现重复的 (node_id, department_id) 组合")
    
    print("\n" + "=" * 80)
    print("4. 检查 dimension_item_mappings 是否有重复")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT dimension_code, item_code, COUNT(*) as cnt
        FROM dimension_item_mappings
        GROUP BY dimension_code, item_code
        HAVING COUNT(*) > 1
        LIMIT 10
    """))
    rows = list(result)
    if rows:
        print(f"  发现 {len(rows)} 个重复的映射:")
        for row in rows:
            print(f"    dimension_code={row.dimension_code}, item_code={row.item_code}, count={row.cnt}")
    else:
        print("  没有发现重复的映射")
    
    print("\n" + "=" * 80)
    print("5. 检查某个重复节点的详细数据")
    print("=" * 80)
    # 获取一个重复的例子
    result = conn.execute(text("""
        SELECT node_id, department_id, node_name, workload, value
        FROM calculation_results
        WHERE task_id = :task_id
          AND (node_id, department_id) IN (
              SELECT node_id, department_id
              FROM calculation_results
              WHERE task_id = :task_id
              GROUP BY node_id, department_id
              HAVING COUNT(*) > 1
              LIMIT 1
          )
        ORDER BY node_id, department_id
    """), {"task_id": TASK_ID})
    rows = list(result)
    if rows:
        print(f"  重复记录示例 (node_id={rows[0].node_id}, dept_id={rows[0].department_id}):")
        for row in rows:
            print(f"    workload={row.workload}, value={row.value}")
    
    print("\n" + "=" * 80)
    print("6. 检查 dimension_business_type 是否有重复 (使用任务的版本ID)")
    print("=" * 80)
    # 获取任务的版本ID
    result = conn.execute(text("""
        SELECT model_version_id FROM calculation_tasks WHERE task_id = :task_id
    """), {"task_id": TASK_ID})
    version_id = result.fetchone().model_version_id
    print(f"  任务使用的版本ID: {version_id}")
    
    # 模拟 dimension_business_type CTE 的查询
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
        )
        SELECT dimension_code, COUNT(*) as cnt
        FROM dimension_hierarchy
        GROUP BY dimension_code
        HAVING COUNT(*) > 1
        LIMIT 10
    """))
    rows = list(result)
    if rows:
        print(f"  发现 {len(rows)} 个重复的维度代码:")
        for row in rows:
            print(f"    dimension_code={row.dimension_code}, count={row.cnt}")
    else:
        print("  没有发现重复的维度代码")
    
    print("\n" + "=" * 80)
    print("7. 检查 dimension_mappings CTE 是否有重复")
    print("=" * 80)
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
        )
        SELECT dimension_id, item_code, COUNT(*) as cnt
        FROM dimension_mappings
        GROUP BY dimension_id, item_code
        HAVING COUNT(*) > 1
        LIMIT 10
    """))
    rows = list(result)
    if rows:
        print(f"  发现 {len(rows)} 个重复的 (dimension_id, item_code):")
        for row in rows:
            print(f"    dimension_id={row.dimension_id}, item_code={row.item_code}, count={row.cnt}")
    else:
        print("  没有发现重复的 (dimension_id, item_code)")


    print("\n" + "=" * 80)
    print("8. 检查 charge_data 是否有重复的业务类别")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT 
            prescribing_dept_code,
            item_code,
            business_type,
            COUNT(*) as record_count,
            SUM(amount) as total_amount
        FROM charge_details
        WHERE charge_time >= '2025-10-01'
          AND charge_time < '2025-11-01'
        GROUP BY prescribing_dept_code, item_code, business_type
        HAVING COUNT(*) > 1
        LIMIT 10
    """))
    rows = list(result)
    if rows:
        print(f"  charge_data 中有多条记录的组合:")
        for row in rows:
            print(f"    dept={row.prescribing_dept_code}, item={row.item_code}, type={row.business_type}, count={row.record_count}")
    else:
        print("  charge_data 按 (dept, item, business_type) 分组后没有重复")
    
    print("\n" + "=" * 80)
    print("9. 检查 charge_details 中的业务类别分布")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT business_type, COUNT(*) as cnt
        FROM charge_details
        WHERE charge_time >= '2025-10-01'
          AND charge_time < '2025-11-01'
        GROUP BY business_type
    """))
    for row in result:
        print(f"  {row.business_type}: {row.cnt} 条")
    
    print("\n" + "=" * 80)
    print("10. 检查 JOIN 条件是否导致笛卡尔积")
    print("=" * 80)
    # 检查一个具体的例子
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
        )
        SELECT dimension_id, dimension_code, dimension_name, business_type, path_names
        FROM dimension_business_type
        WHERE dimension_code = 'dim-tech-exam-ct'
    """))
    rows = list(result)
    print(f"  CT检查维度的业务类别:")
    for row in rows:
        print(f"    id={row.dimension_id}, code={row.dimension_code}, business_type={row.business_type}")
        print(f"    path={row.path_names}")
