"""
添加手术室护理维度计算到工作流31步骤2
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接 - 使用远程数据库
DATABASE_URL = 'postgresql://root:root@47.108.227.254:50016/hospital_value'
engine = create_engine(DATABASE_URL)

# 手术室护理维度的SQL（添加到步骤2的末尾）
nursing_or_sql = """
-- ============================================================================
-- Part 3: 手术室护理维度 (从workload_statistics统计)
-- ============================================================================
-- 注意: workload_statistics中的stat_type使用简化代码 (dim-nur-or-*)
--       需要映射到model_nodes中的完整代码 (dim-nur-proc-or-*)

-- 12. 大手术护理 (dim-nur-proc-or-large)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-proc-or-large' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-large'
  AND d.is_active = TRUE;

-- 13. 中手术护理 (dim-nur-proc-or-mid)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-proc-or-mid' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-mid'
  AND d.is_active = TRUE;

-- 14. 小手术护理 (dim-nur-proc-or-tiny)
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
INNER JOIN model_nodes mn ON mn.code = 'dim-nur-proc-or-tiny' AND mn.version_id = {version_id}
INNER JOIN departments d ON ws.department_code = d.accounting_unit_code AND d.hospital_id = {hospital_id}
WHERE ws.stat_month = '{current_year_month}'
  AND ws.stat_type = 'dim-nur-or-tiny'
  AND d.is_active = TRUE;
"""

def main():
    print("添加手术室护理维度计算到工作流31步骤2...")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. 获取当前步骤2的SQL
        try:
            result = conn.execute(text("""
                SELECT id, code_content 
                FROM calculation_steps 
                WHERE workflow_id = 31 AND sort_order = 2.00
            """))
            rows = result.fetchall()
            print(f"查询返回 {len(rows)} 行")
            
            if not rows or len(rows) == 0:
                print("❌ 未找到工作流31的步骤2")
                # 尝试查看所有步骤
                result2 = conn.execute(text("SELECT id, workflow_id, name, sort_order FROM calculation_steps WHERE workflow_id = 31"))
                all_steps = result2.fetchall()
                print(f"工作流31的所有步骤: {all_steps}")
                return
        except Exception as e:
            print(f"❌ 查询错误: {e}")
            import traceback
            traceback.print_exc()
            return
        
        row = rows[0]
        step_id = row[0]
        current_sql = row[1]
        
        print(f"✓ 找到步骤ID: {step_id}")
        print(f"✓ 当前SQL长度: {len(current_sql)} 字符")
        
        # 2. 检查是否已经包含手术室护理维度
        if 'dim-nur-proc-or-large' in current_sql:
            print("⚠ 步骤2已包含手术室护理维度计算，跳过")
            return
        
        # 3. 追加手术室护理维度的SQL
        updated_sql = current_sql.rstrip() + "\n\n" + nursing_or_sql
        
        print(f"✓ 更新后SQL长度: {len(updated_sql)} 字符")
        
        # 4. 更新步骤
        conn.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql,
                updated_at = NOW()
            WHERE id = :step_id
        """), {"sql": updated_sql, "step_id": step_id})
        
        conn.commit()
        
        print("✓ 成功添加手术室护理维度计算")
        print("\n添加的维度:")
        print("  - dim-nur-proc-or-large (大手术护理) - 权重 1200")
        print("  - dim-nur-proc-or-mid (中手术护理) - 权重 400")
        print("  - dim-nur-proc-or-tiny (小手术护理) - 权重 20")
        print("\n数据来源: workload_statistics 表")
        print("  - stat_type: dim-nur-or-large/mid/tiny")
        print("  - 通过 department_code 关联科室")

if __name__ == "__main__":
    main()
