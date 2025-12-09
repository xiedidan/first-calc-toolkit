"""
测试业务导向调整SQL
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 使用最新的任务ID
task_id = 'b0ee9e80-7fa5-44f7-b98d-d6ca4dc92d6a'
version_id = 12
year_month = '2025-10'

print("=" * 80)
print("测试业务导向调整SQL")
print("=" * 80)

with engine.connect() as conn:
    # 先清理测试数据
    print("\n1. 清理旧的测试数据...")
    conn.execute(text("""
        DELETE FROM orientation_adjustment_details WHERE task_id = :task_id
    """), {"task_id": task_id})
    conn.commit()
    
    # 测试SQL（分步执行）
    print("\n2. 测试CTE: orientation_ratios...")
    result = conn.execute(text("""
        WITH orientation_ratios AS (
            SELECT 
                ov.department_code,
                ov.orientation_rule_id,
                ov.actual_value,
                ob.benchmark_value,
                CASE 
                    WHEN ob.benchmark_value = 0 THEN NULL
                    ELSE ov.actual_value / ob.benchmark_value
                END as orientation_ratio
            FROM orientation_values ov
            INNER JOIN orientation_benchmarks ob 
                ON ov.orientation_rule_id = ob.rule_id
                AND ov.department_code = ob.department_code
                AND ov.hospital_id = ob.hospital_id
            WHERE ov.year_month = :year_month
              AND ov.hospital_id = (SELECT hospital_id FROM model_versions WHERE id = :version_id)
        )
        SELECT COUNT(*) as count FROM orientation_ratios
    """), {"year_month": year_month, "version_id": version_id})
    print(f"   导向比例记录数: {result.fetchone()[0]}")
    
    print("\n3. 测试CTE: ladder_adjustments...")
    result = conn.execute(text("""
        WITH orientation_ratios AS (
            SELECT 
                ov.department_code,
                ov.orientation_rule_id,
                ov.actual_value,
                ob.benchmark_value,
                CASE 
                    WHEN ob.benchmark_value = 0 THEN NULL
                    ELSE ov.actual_value / ob.benchmark_value
                END as orientation_ratio
            FROM orientation_values ov
            INNER JOIN orientation_benchmarks ob 
                ON ov.orientation_rule_id = ob.rule_id
                AND ov.department_code = ob.department_code
                AND ov.hospital_id = ob.hospital_id
            WHERE ov.year_month = :year_month
              AND ov.hospital_id = (SELECT hospital_id FROM model_versions WHERE id = :version_id)
        ),
        ladder_adjustments AS (
            SELECT 
                oratio.department_code,
                oratio.orientation_rule_id,
                oratio.orientation_ratio,
                ol.adjustment_intensity
            FROM orientation_ratios oratio
            INNER JOIN orientation_ladders ol
                ON oratio.orientation_rule_id = ol.rule_id
            WHERE oratio.orientation_ratio IS NOT NULL
              AND (ol.lower_limit IS NULL OR oratio.orientation_ratio >= ol.lower_limit)
              AND (ol.upper_limit IS NULL OR oratio.orientation_ratio < ol.upper_limit)
              AND ol.hospital_id = (SELECT hospital_id FROM model_versions WHERE id = :version_id)
        )
        SELECT COUNT(*) as count FROM ladder_adjustments
    """), {"year_month": year_month, "version_id": version_id})
    print(f"   阶梯匹配记录数: {result.fetchone()[0]}")
    
    print("\n4. 测试CTE: all_node_rules...")
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT node_id) as unique_nodes,
            COUNT(DISTINCT orientation_rule_id) as unique_rules
        FROM (
            SELECT 
                cr.node_id,
                UNNEST(mn.orientation_rule_ids) as orientation_rule_id
            FROM calculation_results cr
            INNER JOIN model_nodes mn ON cr.node_id = mn.id
            WHERE cr.task_id = :task_id
              AND cr.node_type = 'dimension'
              AND mn.orientation_rule_ids IS NOT NULL
              AND array_length(mn.orientation_rule_ids, 1) > 0
        ) sub
    """), {"task_id": task_id})
    row = result.fetchone()
    print(f"   节点-规则展开记录数: {row.total_records}")
    print(f"   唯一节点数: {row.unique_nodes}")
    print(f"   唯一规则数: {row.unique_rules}")
    
    print("\n5. 执行完整SQL...")
    sql = open('backend/standard_workflow_templates/step3a_orientation_adjustment.sql', 'r', encoding='utf-8').read()
    
    # 替换占位符
    sql = sql.replace('{task_id}', task_id)
    sql = sql.replace('{version_id}', str(version_id))
    sql = sql.replace('{year_month}', year_month)
    
    try:
        result = conn.execute(text(sql))
        conn.commit()
        print("   ✓ SQL执行成功")
        
        # 检查结果
        result = conn.execute(text("""
            SELECT COUNT(*) FROM orientation_adjustment_details WHERE task_id = :task_id
        """), {"task_id": task_id})
        detail_count = result.fetchone()[0]
        print(f"\n6. 业务导向过程表记录数: {detail_count}")
        
        if detail_count > 0:
            result = conn.execute(text("""
                SELECT 
                    department_name,
                    node_name,
                    orientation_rule_name,
                    is_adjusted,
                    adjustment_reason
                FROM orientation_adjustment_details
                WHERE task_id = :task_id
                LIMIT 5
            """), {"task_id": task_id})
            
            print("\n示例数据:")
            for row in result:
                print(f"  {row.department_name} - {row.node_name} - {row.orientation_rule_name}")
                print(f"    调整: {row.is_adjusted}, 原因: {row.adjustment_reason}")
        
    except Exception as e:
        print(f"   ✗ SQL执行失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
