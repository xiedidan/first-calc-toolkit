"""
检查业务导向调整明细表为什么是空的
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 配置
WORKFLOW_ID = 26  # 流程 ID

print("=" * 80)
print("检查业务导向调整明细")
print("=" * 80)

with engine.connect() as conn:
    # 1. 查找流程信息
    print(f"\n步骤1: 查找流程 {WORKFLOW_ID} 的信息...")
    
    workflow_query = text("""
        SELECT cw.id, cw.name, cw.version_id, mv.hospital_id
        FROM calculation_workflows cw
        INNER JOIN model_versions mv ON cw.version_id = mv.id
        WHERE cw.id = :workflow_id;
    """)
    
    workflow = conn.execute(workflow_query, {'workflow_id': WORKFLOW_ID}).fetchone()
    
    if not workflow:
        print(f"❌ 未找到流程 {WORKFLOW_ID}")
        exit(1)
    
    print(f"✓ 流程: {workflow[1]}")
    print(f"  版本ID: {workflow[2]}")
    print(f"  医疗机构ID: {workflow[3]}")
    
    version_id = workflow[2]
    hospital_id = workflow[3]
    
    # 2. 查找最近的计算任务
    print(f"\n步骤2: 查找最近的计算任务...")
    
    task_query = text("""
        SELECT task_id, status, period, created_at
        FROM calculation_tasks
        WHERE workflow_id = :workflow_id
        ORDER BY created_at DESC
        LIMIT 5;
    """)
    
    tasks = conn.execute(task_query, {'workflow_id': WORKFLOW_ID}).fetchall()
    
    if not tasks:
        print("❌ 未找到计算任务")
        exit(1)
    
    print(f"✓ 找到 {len(tasks)} 个最近的任务:")
    for t in tasks:
        print(f"  - {t[0]}: {t[1]} ({t[2]}) - {t[3]}")
    
    latest_task_id = tasks[0][0]
    period = tasks[0][2]
    
    # 3. 检查是否有配置导向规则的维度
    print(f"\n步骤3: 检查模型中配置了导向规则的维度...")
    
    oriented_nodes_query = text("""
        SELECT mn.id, mn.code, mn.name, mn.orientation_rule_id, orule.name as rule_name
        FROM model_nodes mn
        INNER JOIN orientation_rules orule ON mn.orientation_rule_id = orule.id
        WHERE mn.version_id = :version_id
          AND mn.orientation_rule_id IS NOT NULL
        ORDER BY mn.name
        LIMIT 10;
    """)
    
    oriented_nodes = conn.execute(oriented_nodes_query, {'version_id': version_id}).fetchall()
    
    if not oriented_nodes:
        print("❌ 模型中没有配置导向规则的维度")
        print("   需要在模型节点管理中为维度配置导向规则")
        exit(1)
    
    print(f"✓ 找到 {len(oriented_nodes)} 个配置了导向规则的维度:")
    for node in oriented_nodes[:5]:
        print(f"  - {node[2]} (code: {node[1]}) -> 规则: {node[4]}")
    
    # 4. 检查导向实际值数据
    print(f"\n步骤4: 检查导向实际值数据...")
    
    values_query = text("""
        SELECT ov.orientation_rule_id, orule.name, COUNT(*) as count
        FROM orientation_values ov
        INNER JOIN orientation_rules orule ON ov.orientation_rule_id = orule.id
        WHERE ov.hospital_id = :hospital_id
          AND ov.year_month = :period
        GROUP BY ov.orientation_rule_id, orule.name;
    """)
    
    values = conn.execute(values_query, {
        'hospital_id': hospital_id,
        'period': period
    }).fetchall()
    
    if not values:
        print(f"❌ 没有 {period} 的导向实际值数据")
        print("   需要在业务导向管理中录入实际值")
    else:
        print(f"✓ 找到 {len(values)} 个导向规则的实际值:")
        for v in values:
            print(f"  - {v[1]}: {v[2]} 条记录")
    
    # 5. 检查导向基准值数据
    print(f"\n步骤5: 检查导向基准值数据...")
    
    benchmarks_query = text("""
        SELECT ob.rule_id, orule.name, COUNT(*) as count
        FROM orientation_benchmarks ob
        INNER JOIN orientation_rules orule ON ob.rule_id = orule.id
        WHERE ob.hospital_id = :hospital_id
        GROUP BY ob.rule_id, orule.name;
    """)
    
    benchmarks = conn.execute(benchmarks_query, {'hospital_id': hospital_id}).fetchall()
    
    if not benchmarks:
        print("❌ 没有导向基准值数据")
        print("   需要在业务导向管理中配置基准值")
    else:
        print(f"✓ 找到 {len(benchmarks)} 个导向规则的基准值:")
        for b in benchmarks:
            print(f"  - {b[1]}: {b[2]} 条记录")
    
    # 6. 检查导向阶梯数据
    print(f"\n步骤6: 检查导向阶梯数据...")
    
    ladders_query = text("""
        SELECT ol.rule_id, orule.name, COUNT(*) as count
        FROM orientation_ladders ol
        INNER JOIN orientation_rules orule ON ol.rule_id = orule.id
        WHERE ol.hospital_id = :hospital_id
        GROUP BY ol.rule_id, orule.name;
    """)
    
    ladders = conn.execute(ladders_query, {'hospital_id': hospital_id}).fetchall()
    
    if not ladders:
        print("❌ 没有导向阶梯数据")
        print("   需要在业务导向管理中配置阶梯")
    else:
        print(f"✓ 找到 {len(ladders)} 个导向规则的阶梯:")
        for l in ladders:
            print(f"  - {l[1]}: {l[2]} 条记录")
    
    # 7. 检查调整明细表
    print(f"\n步骤7: 检查调整明细表...")
    
    details_query = text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN is_adjusted THEN 1 ELSE 0 END) as adjusted,
               SUM(CASE WHEN NOT is_adjusted THEN 1 ELSE 0 END) as not_adjusted
        FROM orientation_adjustment_details
        WHERE task_id = :task_id;
    """)
    
    details = conn.execute(details_query, {'task_id': latest_task_id}).fetchone()
    
    if details[0] == 0:
        print(f"❌ 任务 {latest_task_id} 的调整明细表为空")
        print("\n可能的原因:")
        print("  1. 步骤3a未执行或执行失败")
        print("  2. 模型中没有配置导向规则的维度")
        print("  3. 没有导向实际值或基准值数据")
    else:
        print(f"✓ 找到 {details[0]} 条调整明细:")
        print(f"  - 已调整: {details[1]}")
        print(f"  - 未调整: {details[2]}")
        
        # 查看未调整原因
        if details[2] > 0:
            reasons_query = text("""
                SELECT adjustment_reason, COUNT(*) as count
                FROM orientation_adjustment_details
                WHERE task_id = :task_id
                  AND is_adjusted = FALSE
                GROUP BY adjustment_reason;
            """)
            
            reasons = conn.execute(reasons_query, {'task_id': latest_task_id}).fetchall()
            
            print(f"\n  未调整原因:")
            for r in reasons:
                print(f"    - {r[0]}: {r[1]} 条")
    
    # 8. 检查 calculation_results 中配置了导向的维度
    print(f"\n步骤8: 检查计算结果中配置了导向的维度...")
    
    results_query = text("""
        SELECT COUNT(DISTINCT cr.node_id) as node_count,
               COUNT(*) as result_count
        FROM calculation_results cr
        INNER JOIN model_nodes mn ON cr.node_id = mn.id
        WHERE cr.task_id = :task_id
          AND cr.node_type = 'dimension'
          AND mn.orientation_rule_id IS NOT NULL;
    """)
    
    results = conn.execute(results_query, {'task_id': latest_task_id}).fetchone()
    
    print(f"✓ 计算结果中有 {results[0]} 个配置了导向的维度")
    print(f"  共 {results[1]} 条记录（跨所有科室）")

print("\n" + "=" * 80)
print("检查完成!")
print("=" * 80)
