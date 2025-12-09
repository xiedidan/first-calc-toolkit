"""
添加手术管理维度计算到工作流31步骤2
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = 'postgresql://root:root@47.108.227.254:50016/hospital_value'
engine = create_engine(DATABASE_URL)

# 手术管理维度的SQL
nursing_op_sql = """
-- ============================================================================
-- Part 4: 手术管理维度 (从workload_statistics统计)
-- ============================================================================

-- 15. 乙级手术管理 (dim-nur-op-3)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-3' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-op-3'
  AND d.is_active = TRUE;

-- 16. 甲级手术管理 (dim-nur-op-4)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-4' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-op-4'
  AND d.is_active = TRUE;

-- 17. 学科手术管理 (dim-nur-op-acad)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-acad' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-op-acad'
  AND d.is_active = TRUE;

-- 18. 其他级别手术管理 (dim-nur-op-other)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-op-other' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-op-other'
  AND d.is_active = TRUE;
"""

def main():
    print("添加手术管理维度计算到工作流31步骤2...")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. 获取当前步骤2的SQL
        result = conn.execute(text("""
            SELECT cs.id, cs.code_content, w.version_id
            FROM calculation_steps cs
            INNER JOIN calculation_workflows w ON cs.workflow_id = w.id
            WHERE w.id = 31 AND cs.sort_order = 2.00
        """))
        row = result.fetchone()
        
        if not row:
            print("❌ 未找到工作流31的步骤2")
            return
        
        step_id = row[0]
        current_sql = row[1]
        version_id = row[2]
        
        print(f"✓ 找到步骤ID: {step_id}")
        print(f"✓ 版本ID: {version_id}")
        print(f"✓ 当前SQL长度: {len(current_sql)} 字符")
        
        # 2. 检查版本中的手术管理维度
        result = conn.execute(text("""
            SELECT code, name, weight
            FROM model_nodes
            WHERE version_id = :version_id
              AND code IN ('dim-nur-op-3', 'dim-nur-op-4', 'dim-nur-op-acad', 'dim-nur-op-other')
            ORDER BY code
        """), {"version_id": version_id})
        
        nodes = result.fetchall()
        if not nodes:
            print(f"❌ 版本{version_id}中没有找到手术管理维度节点")
            return
        
        print(f"\n✓ 找到{len(nodes)}个手术管理维度:")
        for node in nodes:
            print(f"  - {node[1]} ({node[0]}): 权重={node[2]}")
        
        # 3. 检查workload_statistics中的数据
        result = conn.execute(text("""
            SELECT stat_type, COUNT(DISTINCT department_code) as dept_count, SUM(stat_value) as total_value
            FROM workload_statistics
            WHERE stat_month = '2025-10'
              AND stat_type IN ('dim-nur-op-3', 'dim-nur-op-4', 'dim-nur-op-acad', 'dim-nur-op-other')
            GROUP BY stat_type
            ORDER BY stat_type
        """))
        
        data_rows = result.fetchall()
        if data_rows:
            print(f"\n✓ workload_statistics中的数据 (2025-10):")
            for row in data_rows:
                print(f"  - {row[0]}: {row[1]}个科室, 总工作量={row[2]}")
        else:
            print("\n⚠ workload_statistics中没有手术管理数据")
        
        # 4. 检查是否已经包含手术管理维度
        if 'dim-nur-op-3' in current_sql:
            print("\n⚠ 步骤2已包含手术管理维度计算，跳过")
            return
        
        # 5. 追加手术管理维度的SQL
        updated_sql = current_sql.rstrip() + "\n\n" + nursing_op_sql
        
        print(f"\n✓ 更新后SQL长度: {len(updated_sql)} 字符")
        
        # 6. 更新步骤
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": updated_sql, "step_id": step_id})
        
        conn.commit()
        
        print("\n✅ 成功添加手术管理维度计算")
        print("\n添加的维度:")
        print("  - dim-nur-op-3 (乙级手术管理)")
        print("  - dim-nur-op-4 (甲级手术管理)")
        print("  - dim-nur-op-acad (学科手术管理)")
        print("  - dim-nur-op-other (其他级别手术管理)")
        print("\n数据来源: workload_statistics 表")
        print("  - stat_type: dim-nur-op-3/4/acad/other")
        print("  - 通过 department_code 关联科室")
        print("\n⚠ 注意: 需要重新运行计算任务才能看到手术管理数据")

if __name__ == "__main__":
    main()
