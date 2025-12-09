"""
修复版本26的手术室护理维度计算
版本26使用简化代码 (dim-nur-or-*) 而不是完整代码 (dim-nur-proc-or-*)
"""
from sqlalchemy import create_engine, text

# 数据库连接
DATABASE_URL = 'postgresql://root:root@47.108.227.254:50016/hospital_value'
engine = create_engine(DATABASE_URL)

# 手术室护理维度的SQL（使用简化代码）
nursing_or_sql = """
-- ============================================================================
-- Part 3: 手术室护理维度 (从workload_statistics统计)
-- ============================================================================
-- 注意: 版本26使用简化代码 (dim-nur-or-*)，与workload_statistics中的代码一致

-- 12. 大手术护理 (dim-nur-or-large)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-large' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-large'
  AND d.is_active = TRUE;

-- 13. 中手术护理 (dim-nur-or-mid)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-mid' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-mid'
  AND d.is_active = TRUE;

-- 14. 小手术护理 (dim-nur-or-tiny)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-or-tiny' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-tiny'
  AND d.is_active = TRUE;
"""

def main():
    print("修复版本26的手术室护理维度计算...")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. 检查工作流31的步骤2
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
        
        # 2. 检查版本中的手术室护理维度代码
        result = conn.execute(text("""
            SELECT code, name, weight
            FROM model_nodes
            WHERE version_id = :version_id
              AND code LIKE 'dim-nur-or-%'
              AND code IN ('dim-nur-or-large', 'dim-nur-or-mid', 'dim-nur-or-tiny')
            ORDER BY code
        """), {"version_id": version_id})
        
        nodes = result.fetchall()
        if not nodes:
            print(f"❌ 版本{version_id}中没有找到手术室护理维度节点")
            print("   预期代码: dim-nur-or-large, dim-nur-or-mid, dim-nur-or-tiny")
            return
        
        print(f"\n✓ 找到{len(nodes)}个手术室护理维度:")
        for node in nodes:
            print(f"  - {node[1]} ({node[0]}): 权重={node[2]}")
        
        # 3. 检查是否已经包含手术室护理维度
        if 'dim-nur-or-large' in current_sql:
            print("\n⚠ 步骤2已包含手术室护理维度计算，跳过")
            return
        
        # 4. 追加手术室护理维度的SQL
        updated_sql = current_sql.rstrip() + "\n\n" + nursing_or_sql
        
        print(f"\n✓ 更新后SQL长度: {len(updated_sql)} 字符")
        
        # 5. 更新步骤
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": updated_sql, "step_id": step_id})
        
        conn.commit()
        
        print("\n✅ 成功添加手术室护理维度计算")
        print("\n添加的维度:")
        print("  - dim-nur-or-large (大手术护理)")
        print("  - dim-nur-or-mid (中手术护理)")
        print("  - dim-nur-or-tiny (小手术护理)")
        print("\n数据来源: workload_statistics 表")
        print("  - stat_type: dim-nur-or-large/mid/tiny")
        print("  - 通过 department_code 关联科室")
        print("\n⚠ 注意: 需要重新运行计算任务才能看到手术室护理数据")

if __name__ == "__main__":
    main()
