"""
添加学科规则应用步骤到计算流程

学科规则在业务导向调整之后、业务价值汇总之前应用
给维度业务价值乘以学科规则系数
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 学科规则应用步骤的 SQL
DISCIPLINE_RULE_SQL = """
-- 学科规则应用步骤
-- 在业务导向调整之后、业务价值汇总之前执行
-- 给维度业务价值乘以学科规则系数

-- 更新 calculation_results 中的 value 字段
-- 只更新有学科规则的维度
UPDATE calculation_results cr
SET value = cr.value * dr.rule_coefficient
FROM discipline_rules dr
JOIN departments d ON d.accounting_unit_code = dr.department_code 
    AND d.hospital_id = dr.hospital_id
JOIN model_nodes mn ON mn.code = dr.dimension_code 
    AND mn.version_id = dr.version_id
WHERE cr.task_id = '{task_id}'
  AND cr.department_id = d.id
  AND cr.node_id = mn.id
  AND dr.version_id = {version_id}
  AND dr.hospital_id = {hospital_id};

-- 返回更新的记录数
SELECT 
    COUNT(*) as updated_count,
    '学科规则应用完成' as message
FROM calculation_results cr
JOIN discipline_rules dr ON dr.version_id = {version_id} AND dr.hospital_id = {hospital_id}
JOIN departments d ON d.accounting_unit_code = dr.department_code 
    AND d.hospital_id = dr.hospital_id
    AND cr.department_id = d.id
JOIN model_nodes mn ON mn.code = dr.dimension_code 
    AND mn.version_id = dr.version_id
    AND cr.node_id = mn.id
WHERE cr.task_id = '{task_id}';
"""

def add_discipline_rule_step(workflow_id: int = 31, data_source_id: int = 3):
    """添加学科规则应用步骤"""
    session = Session()
    
    try:
        # 检查步骤是否已存在
        result = session.execute(text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = :workflow_id AND name = '学科规则应用'
        """), {"workflow_id": workflow_id})
        existing = result.fetchone()
        
        if existing:
            print(f"步骤已存在，ID: {existing[0]}")
            # 更新 SQL
            session.execute(text("""
                UPDATE calculation_steps 
                SET code_content = :code_content
                WHERE id = :step_id
            """), {
                "step_id": existing[0],
                "code_content": DISCIPLINE_RULE_SQL
            })
            session.commit()
            print("已更新步骤 SQL")
            return existing[0]
        
        # 获取业务价值汇总步骤的 sort_order
        result = session.execute(text("""
            SELECT sort_order FROM calculation_steps 
            WHERE workflow_id = :workflow_id AND name = '业务价值汇总'
        """), {"workflow_id": workflow_id})
        summary_step = result.fetchone()
        
        if not summary_step:
            print("未找到业务价值汇总步骤")
            return None
        
        summary_sort_order = float(summary_step[0])
        
        # 新步骤的 sort_order 在业务导向调整和业务价值汇总之间
        # 业务导向调整是 4.00，业务价值汇总是 5.00
        new_sort_order = 4.50
        
        # 插入新步骤
        result = session.execute(text("""
            INSERT INTO calculation_steps 
            (workflow_id, name, description, code_type, code_content, sort_order, is_enabled, data_source_id, created_at, updated_at)
            VALUES 
            (:workflow_id, '学科规则应用', '应用学科规则系数，调整维度业务价值', 'sql', :code_content, :sort_order, true, :data_source_id, NOW(), NOW())
            RETURNING id
        """), {
            "workflow_id": workflow_id,
            "code_content": DISCIPLINE_RULE_SQL,
            "sort_order": new_sort_order,
            "data_source_id": data_source_id
        })
        
        new_step_id = result.fetchone()[0]
        session.commit()
        
        print(f"已添加学科规则应用步骤，ID: {new_step_id}, sort_order: {new_sort_order}")
        return new_step_id
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()


def verify_step(workflow_id: int = 31):
    """验证步骤顺序"""
    session = Session()
    
    try:
        result = session.execute(text("""
            SELECT id, name, sort_order, is_enabled
            FROM calculation_steps 
            WHERE workflow_id = :workflow_id
            ORDER BY sort_order
        """), {"workflow_id": workflow_id})
        
        print("\n当前步骤顺序:")
        print("-" * 60)
        for row in result:
            enabled = "✓" if row[3] else "✗"
            print(f"  [{enabled}] {row[2]:5.2f} - {row[1]} (ID: {row[0]})")
        print("-" * 60)
        
    finally:
        session.close()


if __name__ == "__main__":
    print("添加学科规则应用步骤...")
    add_discipline_rule_step()
    verify_step()
