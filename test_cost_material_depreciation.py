"""
测试成本维度计算：不收费卫生材料费和折旧（风险）费
"""
import psycopg2
import uuid

conn = psycopg2.connect(
    host="47.108.227.254",
    port=50016,
    user="root",
    password="root",
    database="hospital_value"
)

cursor = conn.cursor()

# 生成测试任务ID
test_task_id = f"test-cost-mat-{uuid.uuid4().hex[:8]}"
print(f"测试任务ID: {test_task_id}")

# 测试SQL
sql = f"""
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
    '{test_task_id}' as task_id,
    mn.id as node_id,
    d.id as department_id,
    mn.code as node_code,
    mn.name as node_name,
    'dimension' as node_type,
    mn.parent_id,
    (dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value as workload,
    mn.weight,
    mn.weight as original_weight,
    ((dr.revenue * cb.benchmark_value / rb.benchmark_revenue) - cv.cost_value) * mn.weight as value,
    NOW() as created_at
FROM cost_values cv
JOIN departments d ON 
    cv.dept_code = d.accounting_unit_code 
    AND d.hospital_id = 1
    AND d.is_active = TRUE
JOIN department_revenues dr ON
    dr.hospital_id = 1
    AND dr.year_month = '2025-10'
    AND dr.department_code = d.his_code
JOIN model_nodes mn ON 
    cv.dimension_code = mn.code 
    AND mn.node_type = 'dimension'
JOIN model_versions mv ON 
    mn.version_id = mv.id
    AND mv.hospital_id = 1
    AND mv.is_active = TRUE
JOIN cost_benchmarks cb ON
    cb.hospital_id = 1
    AND cb.version_id = mv.id
    AND cb.department_code = d.accounting_unit_code
    AND cb.dimension_code = cv.dimension_code
JOIN revenue_benchmarks rb ON
    rb.hospital_id = 1
    AND rb.version_id = mv.id
    AND rb.department_code = d.accounting_unit_code
WHERE cv.hospital_id = 1
    AND cv.year_month = '2025-10'
    AND cv.dimension_code IN (
        'dim-doc-cost-mat', 'dim-nur-cost-mat', 'dim-tech-cost-mat',
        'dim-doc-cost-depr', 'dim-nur-cost-depr', 'dim-tech-cost-depr'
    )
    AND rb.benchmark_revenue > 0;
"""

try:
    print("\n执行成本维度计算SQL...")
    cursor.execute(sql)
    conn.commit()
    print(f"✓ SQL执行成功，插入了 {cursor.rowcount} 条记录")
    
    # 查询插入的结果
    cursor.execute("""
        SELECT 
            d.his_name as dept_name,
            cr.node_name,
            cr.workload,
            cr.weight,
            cr.value
        FROM calculation_results cr
        JOIN departments d ON cr.department_id = d.id
        WHERE cr.task_id = %s
        ORDER BY d.his_name, cr.node_name
        LIMIT 10
    """, (test_task_id,))
    
    results = cursor.fetchall()
    
    if results:
        print(f"\n前10条结果：")
        print(f"{'科室':<20} {'维度':<20} {'工作量':<15} {'权重':<10} {'价值':<15}")
        print("-" * 85)
        for row in results:
            dept_name, node_name, workload, weight, value = row
            workload_val = float(workload) if workload else 0
            weight_val = float(weight) if weight else 0
            value_val = float(value) if value else 0
            print(f"{dept_name:<20} {node_name:<20} {workload_val:<15.2f} {weight_val:<10.4f} {value_val:<15.2f}")
    
    # 清理测试数据
    print(f"\n清理测试数据...")
    cursor.execute("DELETE FROM calculation_results WHERE task_id = %s", (test_task_id,))
    conn.commit()
    print("✓ 测试数据已清理")
    
except Exception as e:
    print(f"✗ SQL执行失败: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    cursor.close()
    conn.close()
