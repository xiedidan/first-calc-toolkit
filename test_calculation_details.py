"""
测试 calculation_details 生成逻辑
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 测试参数
hospital_id = 1
version_id = 24  # 使用实际的版本ID
task_id = 'test-calc-details-001'
year_month = '2025-10'

print("=" * 60)
print("测试 calculation_details 生成")
print("=" * 60)

with engine.connect() as conn:
    # 清理测试数据
    conn.execute(text("DELETE FROM calculation_details WHERE task_id = :task_id"), {"task_id": task_id})
    conn.commit()
    
    # 1. 医生序列 - 诊断维度（使用开单科室）
    print("\n1. 插入医生序列诊断维度（使用开单科室）...")
    sql_doctor_eval = text("""
        INSERT INTO calculation_details (
            hospital_id, task_id, department_id, department_code,
            node_id, node_code, node_name, parent_id,
            item_code, item_name, item_category,
            business_type, amount, quantity, period, created_at
        )
        SELECT 
            :hospital_id as hospital_id,
            :task_id as task_id,
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
            :year_month as period,
            NOW()
        FROM charge_details cd
        JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
            AND dim.hospital_id = :hospital_id
        JOIN model_nodes mn ON dim.dimension_code = mn.code 
            AND mn.version_id = :version_id
        JOIN departments d ON cd.prescribing_dept_code = d.his_code 
            AND d.hospital_id = :hospital_id
        LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
            AND ci.hospital_id = :hospital_id
        WHERE cd.year_month = :year_month
        AND (mn.code LIKE 'dim-doc-in-eval-%' OR mn.code LIKE 'dim-doc-out-eval-%')
        AND (
            (mn.code LIKE 'dim-doc-in-%' AND cd.business_type = '住院')
            OR (mn.code LIKE 'dim-doc-out-%' AND cd.business_type = '门诊')
        )
        GROUP BY d.id, cd.prescribing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
                 cd.item_code, cd.item_name, ci.item_category, cd.business_type
    """)
    result = conn.execute(sql_doctor_eval, {
        "hospital_id": hospital_id,
        "task_id": task_id,
        "version_id": version_id,
        "year_month": year_month
    })
    print(f"   插入 {result.rowcount} 条记录")
    conn.commit()
    
    # 2. 医生序列 - 非诊断维度（使用执行科室）
    print("\n2. 插入医生序列非诊断维度（使用执行科室）...")
    sql_doctor_other = text("""
        INSERT INTO calculation_details (
            hospital_id, task_id, department_id, department_code,
            node_id, node_code, node_name, parent_id,
            item_code, item_name, item_category,
            business_type, amount, quantity, period, created_at
        )
        SELECT 
            :hospital_id as hospital_id,
            :task_id as task_id,
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
            :year_month as period,
            NOW()
        FROM charge_details cd
        JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
            AND dim.hospital_id = :hospital_id
        JOIN model_nodes mn ON dim.dimension_code = mn.code 
            AND mn.version_id = :version_id
        JOIN departments d ON cd.executing_dept_code = d.his_code 
            AND d.hospital_id = :hospital_id
        LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
            AND ci.hospital_id = :hospital_id
        WHERE cd.year_month = :year_month
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
                 cd.item_code, cd.item_name, ci.item_category, cd.business_type
    """)
    result = conn.execute(sql_doctor_other, {
        "hospital_id": hospital_id,
        "task_id": task_id,
        "version_id": version_id,
        "year_month": year_month
    })
    print(f"   插入 {result.rowcount} 条记录")
    conn.commit()
    
    # 3. 医技序列（使用执行科室，不区分门诊住院）
    print("\n3. 插入医技序列维度（使用执行科室）...")
    sql_tech = text("""
        INSERT INTO calculation_details (
            hospital_id, task_id, department_id, department_code,
            node_id, node_code, node_name, parent_id,
            item_code, item_name, item_category,
            business_type, amount, quantity, period, created_at
        )
        SELECT 
            :hospital_id as hospital_id,
            :task_id as task_id,
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
            :year_month as period,
            NOW()
        FROM charge_details cd
        JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
            AND dim.hospital_id = :hospital_id
        JOIN model_nodes mn ON dim.dimension_code = mn.code 
            AND mn.version_id = :version_id
        JOIN departments d ON cd.executing_dept_code = d.his_code 
            AND d.hospital_id = :hospital_id
        LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
            AND ci.hospital_id = :hospital_id
        WHERE cd.year_month = :year_month
        AND mn.code LIKE 'dim-tech-%'
        GROUP BY d.id, cd.executing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
                 cd.item_code, cd.item_name, ci.item_category, cd.business_type
    """)
    result = conn.execute(sql_tech, {
        "hospital_id": hospital_id,
        "task_id": task_id,
        "version_id": version_id,
        "year_month": year_month
    })
    print(f"   插入 {result.rowcount} 条记录")
    conn.commit()
    
    # 4. 护理序列 - 收费类维度（使用执行科室，不区分门诊住院）
    print("\n4. 插入护理序列收费类维度（使用执行科室）...")
    sql_nurse = text("""
        INSERT INTO calculation_details (
            hospital_id, task_id, department_id, department_code,
            node_id, node_code, node_name, parent_id,
            item_code, item_name, item_category,
            business_type, amount, quantity, period, created_at
        )
        SELECT 
            :hospital_id as hospital_id,
            :task_id as task_id,
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
            :year_month as period,
            NOW()
        FROM charge_details cd
        JOIN dimension_item_mappings dim ON cd.item_code = dim.item_code 
            AND dim.hospital_id = :hospital_id
        JOIN model_nodes mn ON dim.dimension_code = mn.code 
            AND mn.version_id = :version_id
        JOIN departments d ON cd.executing_dept_code = d.his_code 
            AND d.hospital_id = :hospital_id
        LEFT JOIN charge_items ci ON cd.item_code = ci.item_code 
            AND ci.hospital_id = :hospital_id
        WHERE cd.year_month = :year_month
        AND mn.code LIKE 'dim-nur-%'
        AND mn.code NOT LIKE 'dim-nur-bed%'
        AND mn.code NOT LIKE 'dim-nur-trans%'
        AND mn.code NOT LIKE 'dim-nur-op%'
        AND mn.code NOT LIKE 'dim-nur-or%'
        AND mn.code NOT LIKE 'dim-nur-mon%'
        GROUP BY d.id, cd.executing_dept_code, mn.id, mn.code, mn.name, mn.parent_id,
                 cd.item_code, cd.item_name, ci.item_category, cd.business_type
    """)
    result = conn.execute(sql_nurse, {
        "hospital_id": hospital_id,
        "task_id": task_id,
        "version_id": version_id,
        "year_month": year_month
    })
    print(f"   插入 {result.rowcount} 条记录")
    conn.commit()
    
    # 统计结果
    print("\n" + "=" * 60)
    print("统计结果")
    print("=" * 60)
    
    result = conn.execute(text("""
        SELECT 
            CASE 
                WHEN node_code LIKE 'dim-doc-in-eval-%' OR node_code LIKE 'dim-doc-out-eval-%' THEN '医生-诊断'
                WHEN node_code LIKE 'dim-doc-%' THEN '医生-其他'
                WHEN node_code LIKE 'dim-tech-%' THEN '医技'
                WHEN node_code LIKE 'dim-nur-%' THEN '护理'
                ELSE '其他'
            END as category,
            COUNT(DISTINCT node_code) as dimension_count,
            COUNT(DISTINCT item_code) as item_count,
            COUNT(*) as record_count,
            SUM(amount) as total_amount
        FROM calculation_details
        WHERE task_id = :task_id
        GROUP BY 1
        ORDER BY 1
    """), {"task_id": task_id})
    
    print(f"\n{'类别':<15} {'维度数':<10} {'项目数':<10} {'记录数':<10} {'总金额':<15}")
    print("-" * 60)
    for row in result:
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<15}")
    
    # 按科室统计
    print("\n按科室统计（Top 10）:")
    result = conn.execute(text("""
        SELECT 
            department_code,
            COUNT(DISTINCT node_code) as dimension_count,
            COUNT(*) as record_count,
            SUM(amount) as total_amount
        FROM calculation_details
        WHERE task_id = :task_id
        GROUP BY department_code
        ORDER BY total_amount DESC
        LIMIT 10
    """), {"task_id": task_id})
    
    print(f"\n{'科室代码':<15} {'维度数':<10} {'记录数':<10} {'总金额':<15}")
    print("-" * 50)
    for row in result:
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<10} {row[3]:<15}")
    
    # 测试下钻查询
    print("\n" + "=" * 60)
    print("测试下钻查询")
    print("=" * 60)
    
    # 找一个有数据的维度
    result = conn.execute(text("""
        SELECT node_id, node_code, node_name, department_id, department_code
        FROM calculation_details
        WHERE task_id = :task_id
        AND node_code LIKE 'dim-doc-sur-in-%'
        LIMIT 1
    """), {"task_id": task_id})
    row = result.fetchone()
    
    if row:
        test_node_id = row[0]
        test_node_code = row[1]
        test_dept_id = row[3]
        test_dept_code = row[4]
        
        print(f"\n测试维度: {test_node_code} ({row[2]})")
        print(f"测试科室: {test_dept_code} (ID: {test_dept_id})")
        
        # 下钻查询
        result = conn.execute(text("""
            SELECT 
                item_code,
                item_name,
                item_category,
                business_type,
                SUM(amount) as total_amount,
                SUM(quantity) as total_quantity
            FROM calculation_details
            WHERE task_id = :task_id
            AND department_id = :department_id
            AND node_id = :node_id
            GROUP BY item_code, item_name, item_category, business_type
            ORDER BY total_amount DESC
            LIMIT 10
        """), {
            "task_id": task_id,
            "department_id": test_dept_id,
            "node_id": test_node_id
        })
        
        print(f"\n{'项目编码':<15} {'项目名称':<20} {'金额':<15} {'数量':<10}")
        print("-" * 60)
        for row in result:
            name = (row[1] or '')[:18]
            print(f"{row[0]:<15} {name:<20} {row[4]:<15} {row[5]:<10}")
    else:
        print("未找到手术维度数据")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
