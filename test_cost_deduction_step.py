"""
测试成本直接扣减步骤
"""

import os
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

def test_cost_deduction():
    """测试成本扣减SQL"""
    
    # 测试参数
    task_id = "test-cost-deduction-001"
    version_id = 28
    hospital_id = 1
    period = "2025-10"
    
    with engine.connect() as conn:
        # 1. 清理测试数据
        conn.execute(text("DELETE FROM calculation_results WHERE task_id = :task_id"), 
                    {"task_id": task_id})
        conn.commit()
        
        # 2. 检查成本报表数据
        print("=== 成本报表数据样例 ===")
        result = conn.execute(text("""
            SELECT department_code, department_name, 
                   personnel_cost, material_cost, depreciation_cost, other_cost
            FROM cost_reports 
            WHERE hospital_id = :hospital_id AND period = :period
            LIMIT 3
        """), {"hospital_id": hospital_id, "period": period})
        for row in result:
            print(f"  {row[0]} {row[1]}: 人员={row[2]}, 材料={row[3]}, 折旧={row[4]}, 其他={row[5]}")
        
        # 3. 检查成本维度节点
        print("\n=== 成本维度节点 ===")
        result = conn.execute(text("""
            SELECT code, name, weight FROM model_nodes 
            WHERE version_id = :version_id AND code LIKE '%-cost-%'
            ORDER BY code
        """), {"version_id": version_id})
        for row in result:
            print(f"  {row[0]}: {row[1]} (权重={row[2]})")
        
        # 4. 执行成本扣减SQL（医生序列）
        print("\n=== 执行医生序列成本扣减 ===")
        sql = """
        INSERT INTO calculation_results (
            task_id, node_id, department_id, node_type, node_name, node_code,
            parent_id, workload, weight, original_weight, value, created_at
        )
        SELECT
            :task_id as task_id,
            mn.id as node_id,
            d.id as department_id,
            'dimension' as node_type,
            mn.name as node_name,
            mn.code as node_code,
            mn.parent_id as parent_id,
            CASE 
                WHEN mn.code = 'dim-doc-cost-hr' THEN cr.personnel_cost
                WHEN mn.code = 'dim-doc-cost-mat' THEN cr.material_cost
                WHEN mn.code = 'dim-doc-cost-depr' THEN cr.depreciation_cost
                WHEN mn.code = 'dim-doc-cost-other' THEN cr.other_cost
            END as workload,
            mn.weight,
            mn.weight as original_weight,
            -1 * CASE 
                WHEN mn.code = 'dim-doc-cost-hr' THEN cr.personnel_cost
                WHEN mn.code = 'dim-doc-cost-mat' THEN cr.material_cost
                WHEN mn.code = 'dim-doc-cost-depr' THEN cr.depreciation_cost
                WHEN mn.code = 'dim-doc-cost-other' THEN cr.other_cost
            END * COALESCE(mn.weight, 0) as value,
            NOW() as created_at
        FROM model_nodes mn
        CROSS JOIN departments d
        JOIN cost_reports cr ON cr.department_code = d.accounting_unit_code 
            AND cr.period = :period
            AND cr.hospital_id = :hospital_id
        WHERE mn.version_id = :version_id
            AND mn.code IN ('dim-doc-cost-hr', 'dim-doc-cost-mat', 'dim-doc-cost-depr', 'dim-doc-cost-other')
            AND d.hospital_id = :hospital_id
            AND d.is_active = true
        """
        result = conn.execute(text(sql), {
            "task_id": task_id,
            "version_id": version_id,
            "hospital_id": hospital_id,
            "period": period
        })
        print(f"  插入 {result.rowcount} 条记录")
        conn.commit()
        
        # 5. 查看计算结果
        print("\n=== 计算结果样例 ===")
        result = conn.execute(text("""
            SELECT cr.node_code, cr.node_name, d.his_name as dept_name,
                   cr.workload, cr.weight, cr.value
            FROM calculation_results cr
            JOIN departments d ON d.id = cr.department_id
            WHERE cr.task_id = :task_id
            ORDER BY cr.node_code, d.his_name
            LIMIT 12
        """), {"task_id": task_id})
        
        print(f"{'节点代码':<25} {'节点名称':<15} {'科室':<15} {'成本额':>15} {'权重':>8} {'业务价值':>15}")
        print("-" * 100)
        for row in result:
            print(f"{row[0]:<25} {row[1]:<15} {row[2]:<15} {float(row[3]):>15,.2f} {float(row[4]):>8.4f} {float(row[5]):>15,.2f}")
        
        # 6. 统计汇总
        print("\n=== 统计汇总 ===")
        result = conn.execute(text("""
            SELECT node_code, COUNT(*) as dept_count, 
                   SUM(workload) as total_cost, SUM(value) as total_value
            FROM calculation_results
            WHERE task_id = :task_id
            GROUP BY node_code
            ORDER BY node_code
        """), {"task_id": task_id})
        
        for row in result:
            print(f"  {row[0]}: {row[1]}个科室, 总成本={float(row[2]):,.2f}, 总扣减={float(row[3]):,.2f}")
        
        # 7. 清理测试数据
        conn.execute(text("DELETE FROM calculation_results WHERE task_id = :task_id"), 
                    {"task_id": task_id})
        conn.commit()
        print("\n测试数据已清理")

if __name__ == "__main__":
    test_cost_deduction()
