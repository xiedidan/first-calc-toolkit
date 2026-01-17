"""检查工作流39的成本计算步骤"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # 1. 查看工作流39的基本信息
    print("=" * 80)
    print("1. 工作流39基本信息")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT id, name, description FROM calculation_workflows WHERE id = 39
    """))
    for row in result:
        print(f"  ID: {row[0]}, 名称: {row[1]}, 描述: {row[2]}")
    
    # 2. 查看成本相关的步骤
    print("\n" + "=" * 80)
    print("2. 成本相关步骤")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT id, sort_order, name, description
        FROM calculation_steps 
        WHERE workflow_id = 39 
          AND (name LIKE '%成本%' OR name LIKE '%cost%' OR description LIKE '%成本%')
        ORDER BY sort_order
    """))
    steps = list(result)
    for row in steps:
        print(f"  步骤ID: {row[0]}, 序号: {row[1]}, 名称: {row[2]}")
        print(f"    描述: {row[3]}")
    
    # 3. 查看成本步骤的SQL
    print("\n" + "=" * 80)
    print("3. 成本步骤SQL详情")
    print("=" * 80)
    for step in steps:
        step_id = step[0]
        result = conn.execute(text("""
            SELECT code_content FROM calculation_steps WHERE id = :step_id
        """), {"step_id": step_id})
        sql = result.fetchone()
        if sql and sql[0]:
            print(f"\n--- 步骤 {step_id}: {step[2]} ---")
            print(sql[0][:3000])
            if len(sql[0]) > 3000:
                print("... (SQL过长，已截断)")
    
    # 4. 查看cost_values表中的数据样本
    print("\n" + "=" * 80)
    print("4. cost_values表数据样本 (2025-01)")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT dept_code, dept_name, dimension_code, dimension_name, cost_value
        FROM cost_values 
        WHERE hospital_id = 1 AND year_month = '2025-01'
        ORDER BY dept_name, dimension_code
        LIMIT 20
    """))
    for row in result:
        print(f"  {row[0]:<10} {row[1]:<15} {row[2]:<20} {row[3]:<10} {float(row[4]):>12,.2f}")
    
    # 5. 检查最近一个任务的成本计算结果
    print("\n" + "=" * 80)
    print("5. 最近任务的成本维度结果")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT ct.task_id, ct.year_month, ct.status
        FROM calculation_tasks ct
        WHERE ct.workflow_id = 39
        ORDER BY ct.created_at DESC
        LIMIT 1
    """))
    task = result.fetchone()
    if task:
        task_id = task[0]
        year_month = task[1]
        print(f"  任务ID: {task_id[:30]}..., 年月: {year_month}, 状态: {task[2]}")
        
        # 查看成本维度的计算结果
        result = conn.execute(text("""
            SELECT cr.department_name, mn.name as node_name, cr.value
            FROM calculation_results cr
            JOIN model_nodes mn ON cr.node_id = mn.id
            WHERE cr.task_id = :task_id
              AND mn.name LIKE '%成本%'
            ORDER BY cr.department_name, mn.name
            LIMIT 30
        """), {"task_id": task_id})
        rows = list(result)
        if rows:
            print(f"\n  成本维度计算结果 (共 {len(rows)} 条):")
            for row in rows:
                print(f"    {row[0]:<15} {row[1]:<20} {float(row[2]) if row[2] else 0:>12,.2f}")
        else:
            print("  未找到成本维度的计算结果")
    
    # 6. 检查成本步骤SQL中的关键JOIN条件
    print("\n" + "=" * 80)
    print("6. 检查cost_values与departments的关联")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT cv.dept_code, cv.dept_name, d.accounting_unit_code, d.accounting_unit_name
        FROM cost_values cv
        LEFT JOIN departments d ON cv.dept_code = d.accounting_unit_code AND d.hospital_id = cv.hospital_id
        WHERE cv.hospital_id = 1 AND cv.year_month = '2025-01'
        ORDER BY cv.dept_name
        LIMIT 15
    """))
    print("  cost_values.dept_code 与 departments.accounting_unit_code 匹配情况:")
    for row in result:
        match = "✓" if row[2] else "✗"
        print(f"    {match} {row[0]:<10} {row[1]:<15} -> {row[2] or 'NULL':<10} {row[3] or 'NULL'}")
