"""
添加业务导向调整和业务价值汇总步骤到计算流程31

从计算流程30移植步骤111(业务导向调整)和步骤116(业务价值汇总)到流程31
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 数据库连接 - 直接使用远程数据库
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)

def main():
    """添加业务导向调整和业务价值汇总步骤"""
    
    with engine.begin() as conn:
        # 检查工作流31是否存在
        check_workflow = text("""
            SELECT id, name FROM calculation_workflows WHERE id = 31
        """)
        workflow = conn.execute(check_workflow).fetchone()
        
        if not workflow:
            print("❌ 工作流31不存在")
            return
        
        print(f"✓ 找到工作流: {workflow.name}")
        
        # 检查步骤是否已存在
        check_steps = text("""
            SELECT id, name, sort_order 
            FROM calculation_steps 
            WHERE workflow_id = 31 
            ORDER BY sort_order
        """)
        existing_steps = conn.execute(check_steps).fetchall()
        
        print(f"\n当前流程31的步骤:")
        for step in existing_steps:
            print(f"  - {step.name} (sort_order: {step.sort_order})")
        
        # 检查是否已有步骤4和5
        has_step4 = any(s.sort_order == 4.00 for s in existing_steps)
        has_step5 = any(s.sort_order == 5.00 for s in existing_steps)
        
        if has_step4 or has_step5:
            print(f"\n⚠️  步骤4或5已存在，是否覆盖？(y/n)")
            response = input().strip().lower()
            if response != 'y':
                print("取消操作")
                return
            
            # 删除现有步骤
            if has_step4:
                conn.execute(text("DELETE FROM calculation_steps WHERE workflow_id = 31 AND sort_order = 4.00"))
                print("✓ 已删除现有步骤4")
            if has_step5:
                conn.execute(text("DELETE FROM calculation_steps WHERE workflow_id = 31 AND sort_order = 5.00"))
                print("✓ 已删除现有步骤5")
        
        # 从流程30获取步骤111和116的SQL
        get_step111 = text("""
            SELECT code_content FROM calculation_steps WHERE id = 111
        """)
        step111_sql = conn.execute(get_step111).scalar()
        
        get_step116 = text("""
            SELECT code_content FROM calculation_steps WHERE id = 116
        """)
        step116_sql = conn.execute(get_step116).scalar()
        
        if not step111_sql or not step116_sql:
            print("❌ 无法获取源步骤的SQL")
            return
        
        print(f"\n✓ 已获取源步骤SQL (步骤111: {len(step111_sql)} 字符, 步骤116: {len(step116_sql)} 字符)")
        
        # 插入步骤4: 业务导向调整
        insert_step4 = text("""
            INSERT INTO calculation_steps (
                workflow_id,
                name,
                description,
                code_type,
                sort_order,
                code_content,
                created_at,
                updated_at
            ) VALUES (
                31,
                '业务导向调整',
                '根据业务导向规则调整维度的学科业务价值（weight字段）',
                'sql',
                4.00,
                :sql_content,
                NOW(),
                NOW()
            )
        """)
        
        conn.execute(insert_step4, {"sql_content": step111_sql})
        print("✓ 已添加步骤4: 业务导向调整")
        
        # 插入步骤5: 业务价值汇总
        insert_step5 = text("""
            INSERT INTO calculation_steps (
                workflow_id,
                name,
                description,
                code_type,
                sort_order,
                code_content,
                created_at,
                updated_at
            ) VALUES (
                31,
                '业务价值汇总',
                '根据模型结构和权重,自下而上汇总各科室的业务价值',
                'sql',
                5.00,
                :sql_content,
                NOW(),
                NOW()
            )
        """)
        
        conn.execute(insert_step5, {"sql_content": step116_sql})
        print("✓ 已添加步骤5: 业务价值汇总")
        
        # 验证添加结果
        verify_steps = text("""
            SELECT id, name, sort_order, LENGTH(code_content) as sql_length
            FROM calculation_steps 
            WHERE workflow_id = 31 
            ORDER BY sort_order
        """)
        final_steps = conn.execute(verify_steps).fetchall()
        
        print(f"\n✓ 流程31的最终步骤:")
        for step in final_steps:
            print(f"  - {step.name} (sort_order: {step.sort_order}, SQL长度: {step.sql_length})")
        
        print("\n" + "="*80)
        print("✓ 步骤添加完成!")
        print("="*80)
        print("\n⚠️  注意事项:")
        print("1. 步骤4(业务导向调整)需要以下数据:")
        print("   - orientation_values: 导向实际值")
        print("   - orientation_benchmarks: 导向基准值")
        print("   - orientation_ladders: 导向阶梯")
        print("   - model_nodes.orientation_rule_ids: 维度节点的导向规则配置")
        print("")
        print("2. 步骤5(业务价值汇总)会:")
        print("   - 从calculation_results读取维度数据(步骤1-3的输出)")
        print("   - 使用调整后的weight字段(步骤4的输出)")
        print("   - 递归汇总到序列节点")
        print("   - 将序列节点数据插入回calculation_results")
        print("")
        print("3. 流程31的特点:")
        print("   - 步骤1-3直接插入叶子维度节点到calculation_results")
        print("   - 步骤4调整这些维度节点的weight字段")
        print("   - 步骤5补充所有中间层级和序列节点")
        print("")
        print("4. 与流程30的区别:")
        print("   - 流程30: Step2插入维度 -> Step3调整 -> Step4汇总")
        print("   - 流程31: Step1-3插入维度 -> Step4调整 -> Step5汇总")
        print("   - SQL模板完全兼容,无需修改")

if __name__ == "__main__":
    main()
