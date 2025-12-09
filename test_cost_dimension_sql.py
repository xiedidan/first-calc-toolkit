"""
测试成本维度计算SQL
直接执行SQL验证是否能正确插入数据
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
test_task_id = f"test-cost-{uuid.uuid4().hex[:8]}"
print(f"测试任务ID: {test_task_id}")

# 成本维度计算SQL
sql = f"""
-- 成本维度计算：人员经费和其他费用
-- 算法：成本值 * weight * -1
-- 只处理人员经费和其他费用两个维度

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
    0 as workload,  -- 成本维度不使用工作量
    mn.weight,
    mn.weight as original_weight,
    cv.cost_value * mn.weight * -1 as value,  -- 成本值 * 权重 * -1
    NOW() as created_at
FROM cost_values cv
JOIN departments d ON 
    cv.dept_code = d.accounting_unit_code 
    AND d.hospital_id = 1
    AND d.is_active = TRUE
JOIN model_nodes mn ON 
    cv.dimension_code = mn.code 
    AND mn.node_type = 'dimension'
JOIN model_versions mv ON 
    mn.version_id = mv.id
    AND mv.hospital_id = 1
    AND mv.is_active = TRUE
WHERE cv.hospital_id = 1
    AND cv.year_month = '2025-10'
    -- 通过 dimension_code 筛选成本维度
    AND cv.dimension_code IN (
        'dim-doc-cost-hr', 'dim-nur-cost-hr', 'dim-tech-cost-hr',
        'dim-doc-cost-other', 'dim-nur-cost-other', 'dim-tech-cost-other'
    );
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
        print(f"{'科室':<20} {'维度':<15} {'工作量':<12} {'权重':<10} {'价值':<15}")
        print("-" * 80)
        for row in results:
            dept_name, node_name, workload, weight, value = row
            workload_val = float(workload) if workload else 0
            weight_val = float(weight) if weight else 0
            value_val = float(value) if value else 0
            print(f"{dept_name:<20} {node_name:<15} {workload_val:<12.2f} {weight_val:<10.4f} {value_val:<15.2f}")
    
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
