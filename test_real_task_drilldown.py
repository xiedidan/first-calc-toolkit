"""
使用真实计算任务测试 calculation_details 下钻功能
"""
import os
import sys
sys.path.insert(0, 'backend')

import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# API 配置
BASE_URL = "http://localhost:8000/api/v1"

# 使用真实的计算任务
real_task_id = '428b13dc-e6ff-44ad-b970-41334f3743ee'  # 2025-10 完成的任务

print("=" * 60)
print("使用真实任务测试下钻功能")
print("=" * 60)

with engine.connect() as conn:
    # 1. 获取任务信息
    result = conn.execute(text("""
        SELECT ct.task_id, ct.period, ct.model_version_id, mv.hospital_id
        FROM calculation_tasks ct
        JOIN model_versions mv ON ct.model_version_id = mv.id
        WHERE ct.task_id = :task_id
    """), {"task_id": real_task_id})
    task_info = result.fetchone()
    
    if not task_info:
        print(f"错误：任务 {real_task_id} 不存在")
        sys.exit(1)
    
    task_id = task_info[0]
    period = task_info[1]
    version_id = task_info[2]
    hospital_id = task_info[3]
    year_month = period  # 格式已经是 YYYY-MM
    
    print(f"\n任务信息:")
    print(f"  task_id: {task_id}")
    print(f"  period: {period}")
    print(f"  version_id: {version_id}")
    print(f"  hospital_id: {hospital_id}")
    
    # 2. 检查是否已有 calculation_details 数据
    result = conn.execute(text("""
        SELECT COUNT(*) FROM calculation_details WHERE task_id = :task_id
    """), {"task_id": task_id})
    existing_count = result.scalar()
    
    print(f"\n现有 calculation_details 记录: {existing_count}")
    
    if existing_count == 0:
        print("\n生成 calculation_details 数据...")
        
        # 清理旧数据（如果有）
        conn.execute(text("DELETE FROM calculation_details WHERE task_id = :task_id"), {"task_id": task_id})
        
        # 1. 医生序列 - 诊断维度（使用开单科室）
        print("  插入医生序列诊断维度...")
        result = conn.execute(text("""
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
        """), {
            "hospital_id": hospital_id,
            "task_id": task_id,
            "version_id": version_id,
            "year_month": year_month
        })
        print(f"    插入 {result.rowcount} 条")
        
        # 2. 医生序列 - 非诊断维度（使用执行科室）
        print("  插入医生序列非诊断维度...")
        result = conn.execute(text("""
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
        """), {
            "hospital_id": hospital_id,
            "task_id": task_id,
            "version_id": version_id,
            "year_month": year_month
        })
        print(f"    插入 {result.rowcount} 条")
        
        # 3. 医技序列
        print("  插入医技序列维度...")
        result = conn.execute(text("""
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
        """), {
            "hospital_id": hospital_id,
            "task_id": task_id,
            "version_id": version_id,
            "year_month": year_month
        })
        print(f"    插入 {result.rowcount} 条")
        
        # 4. 护理序列 - 收费类维度
        print("  插入护理序列收费类维度...")
        result = conn.execute(text("""
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
        """), {
            "hospital_id": hospital_id,
            "task_id": task_id,
            "version_id": version_id,
            "year_month": year_month
        })
        print(f"    插入 {result.rowcount} 条")
        
        conn.commit()
        
        # 统计总数
        result = conn.execute(text("""
            SELECT COUNT(*) FROM calculation_details WHERE task_id = :task_id
        """), {"task_id": task_id})
        total = result.scalar()
        print(f"\n总计生成 {total} 条 calculation_details 记录")
    
    # 3. 获取一个有数据的维度用于测试
    result = conn.execute(text("""
        SELECT DISTINCT cr.node_id, cr.node_code, cr.node_name, cr.department_id
        FROM calculation_results cr
        WHERE cr.task_id = :task_id
        AND cr.node_type = 'dimension'
        AND cr.node_code LIKE 'dim-doc-sur-in-%'
        AND NOT EXISTS (
            SELECT 1 FROM calculation_results cr2 
            WHERE cr2.task_id = cr.task_id 
            AND cr2.department_id = cr.department_id 
            AND cr2.parent_id = cr.node_id
        )
        LIMIT 1
    """), {"task_id": task_id})
    row = result.fetchone()
    
    if row:
        test_node_id = row[0]
        test_node_code = row[1]
        test_node_name = row[2]
        test_dept_id = row[3]
        
        print(f"\n测试维度: {test_node_code} ({test_node_name})")
        print(f"测试科室ID: {test_dept_id}")
        
        # 4. 测试 API
        print("\n测试下钻 API...")
        try:
            # 登录
            login_resp = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if login_resp.status_code == 200:
                token = login_resp.json().get("access_token")
                headers = {
                    "X-Hospital-ID": str(hospital_id),
                    "Authorization": f"Bearer {token}"
                }
                
                # 测试下钻
                drilldown_url = f"{BASE_URL}/analysis-reports/dimension-drilldown"
                params = {
                    "task_id": task_id,
                    "department_id": test_dept_id,
                    "node_id": test_node_id
                }
                
                resp = requests.get(drilldown_url, params=params, headers=headers)
                
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"  ✓ 下钻查询成功!")
                    print(f"    维度名称: {data.get('dimension_name')}")
                    print(f"    项目数量: {len(data.get('items', []))}")
                    print(f"    总金额: {data.get('total_amount')}")
                    
                    # 显示前3个项目
                    items = data.get('items', [])[:3]
                    if items:
                        print(f"    前3个项目:")
                        for item in items:
                            print(f"      - {item['item_code']}: {item['item_name'][:20]}... 金额:{item['amount']}")
                else:
                    print(f"  ✗ 下钻查询失败: {resp.status_code}")
                    print(f"    响应: {resp.text[:300]}")
            else:
                print(f"  登录失败: {login_resp.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("  无法连接到后端服务")
            print("  请确保后端服务运行在 localhost:8000")
    else:
        print("未找到可测试的维度")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
