"""
添加成本维度计算步骤：不收费卫生材料费和折旧（风险）费
算法：维度价值 = ((当期科室总收入 * 成本基准 / 科室收入基准) - 当期成本) * weight
"""
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

WORKFLOW_IDS = [26, 27]
SORT_ORDER = 4.50  # 在成本维度计算(4.00)之后，业务价值汇总(5.00)之前
DATA_SOURCE_ID = 3  # 系统数据源

# SQL模板
SQL_TEMPLATE = """
-- 成本维度计算：不收费卫生材料费和折旧（风险）费
-- 算法：维度价值 = ((当期科室总收入 * 成本基准 / 科室收入基准) - 当期成本) * weight
-- 数据来源：
--   department_revenues: 当期科室总收入
--   cost_benchmarks: 成本基准
--   revenue_benchmarks: 科室收入基准
--   cost_values: 当期成本

INSERT INTO calculation_results (
    task_id,
    node_id,
    department_id,
    node_code,
    node_name,
    node_type,
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
    mn.code as node_code,
    mn.name as node_name,
    'dimension' as node_type,
    mn.parent_id,
    -- workload = (当期收入 * 成本基准 / 收入基准) - 当期成本
    (dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value as workload,
    mn.weight,
    mn.weight as original_weight,
    -- value = workload * weight
    ((dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value) * mn.weight as value,
    NOW() as created_at
FROM cost_values cv
JOIN departments d ON 
    cv.dept_code = d.accounting_unit_code 
    AND d.hospital_id = {hospital_id}
    AND d.is_active = TRUE
JOIN department_revenues dr ON
    dr.hospital_id = {hospital_id}
    AND dr.year_month = '{year_month}'
    AND dr.department_code = d.his_code
JOIN model_nodes mn ON 
    cv.dimension_code = mn.code 
    AND mn.node_type = 'dimension'
JOIN model_versions mv ON 
    mn.version_id = mv.id
    AND mv.hospital_id = {hospital_id}
    AND mv.is_active = TRUE
JOIN cost_benchmarks cb ON
    cb.hospital_id = {hospital_id}
    AND cb.version_id = mv.id
    AND cb.department_code = d.accounting_unit_code
    AND cb.dimension_code = cv.dimension_code
JOIN revenue_benchmarks rb ON
    rb.hospital_id = {hospital_id}
    AND rb.version_id = mv.id
    AND rb.department_code = d.his_code
WHERE cv.hospital_id = {hospital_id}
    AND cv.year_month = '{year_month}'
    -- 只处理不收费卫生材料费和折旧（风险）费
    AND cv.dimension_code IN (
        'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
        'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
    )
    AND rb.benchmark_revenue > 0;  -- 避免除以零

-- 返回插入的记录数
SELECT COUNT(*) as inserted_count FROM calculation_results 
WHERE task_id = '{task_id}' 
  AND node_code IN (
      'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
      'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
  );
"""

def get_step_config(workflow_id):
    """获取步骤配置"""
    return {
        "workflow_id": workflow_id,
        "name": "成本维度计算-材料费和折旧费",
        "description": "计算不收费卫生材料费和折旧（风险）费维度的价值",
        "code_type": "sql",
        "code_content": SQL_TEMPLATE.strip(),
        "sort_order": SORT_ORDER,
        "is_enabled": True,
        "data_source_id": DATA_SOURCE_ID
    }

def add_cost_material_depreciation_step():
    """添加成本维度计算步骤到多个工作流"""
    with engine.connect() as conn:
        for workflow_id in WORKFLOW_IDS:
            print(f"\n处理工作流 {workflow_id}...")
            step_config = get_step_config(workflow_id)
            
            # 检查是否已存在相同名称的步骤
            check_sql = text("""
                SELECT id, name, sort_order 
                FROM calculation_steps 
                WHERE workflow_id = :workflow_id 
                  AND name = :name
            """)
            result = conn.execute(check_sql, {
                "workflow_id": workflow_id,
                "name": step_config["name"]
            })
            existing = result.fetchone()
            
            if existing:
                print(f"  步骤已存在: ID={existing[0]}, 名称={existing[1]}, 排序={existing[2]}")
                # 自动更新
                update_sql = text("""
                    UPDATE calculation_steps
                    SET description = :description,
                        code_type = :code_type,
                        code_content = :code_content,
                        sort_order = :sort_order,
                        is_enabled = :is_enabled,
                        data_source_id = :data_source_id,
                        updated_at = NOW()
                    WHERE id = :step_id
                """)
                conn.execute(update_sql, {
                    **step_config,
                    "step_id": existing[0]
                })
                conn.commit()
                print(f"  ✓ 步骤已更新: ID={existing[0]}")
            else:
                # 插入新步骤
                insert_sql = text("""
                    INSERT INTO calculation_steps 
                    (workflow_id, name, description, code_type, code_content, 
                     sort_order, is_enabled, data_source_id, created_at, updated_at)
                    VALUES 
                    (:workflow_id, :name, :description, :code_type, :code_content,
                     :sort_order, :is_enabled, :data_source_id, NOW(), NOW())
                    RETURNING id
                """)
                result = conn.execute(insert_sql, step_config)
                step_id = result.fetchone()[0]
                conn.commit()
                print(f"  ✓ 步骤已创建: ID={step_id}")
            
            # 显示工作流中的所有步骤
            list_sql = text("""
                SELECT id, sort_order, name, description
                FROM calculation_steps
                WHERE workflow_id = :workflow_id
                ORDER BY sort_order
            """)
            result = conn.execute(list_sql, {"workflow_id": workflow_id})
            
            print(f"\n  工作流 {workflow_id} 的所有步骤:")
            print(f"  {'ID':<6} {'排序':<8} {'名称':<30} {'描述'}")
            print("  " + "-" * 90)
            for row in result:
                print(f"  {row[0]:<6} {float(row[1]):<8.2f} {row[2]:<30} {row[3] or ''}")

if __name__ == "__main__":
    try:
        add_cost_material_depreciation_step()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
