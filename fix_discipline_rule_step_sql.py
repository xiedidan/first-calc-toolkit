"""
修复学科规则步骤的SQL - 使用 accounting_unit_code 而不是 his_code
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 修正后的学科规则SQL
DISCIPLINE_RULE_SQL = """
-- ===========================================================================
-- 步骤: 学科规则调整
-- ===========================================================================
-- 功能: 根据学科规则系数调整维度的业务价值（weight和value字段）
--
-- 输入参数(通过占位符):
--   {task_id}    - 计算任务ID
--   {version_id} - 模型版本ID
--   {hospital_id} - 医疗机构ID
--
-- 算法说明:
--   1. 从 discipline_rules 表获取科室-维度的规则系数
--   2. 通过 accounting_unit_code 匹配科室（学科规则按核算单元配置）
--   3. 调整后的 weight = 原 weight * rule_coefficient
--   4. 调整后的 value = 原 value * rule_coefficient
--
-- 输出: 更新 calculation_results 表中匹配的维度节点的 weight 和 value 字段
-- ===========================================================================

-- 第1步: 更新 calculation_results 表中的 weight 和 value 字段
-- 注意: 使用 accounting_unit_code 匹配科室，因为学科规则是按核算单元配置的
UPDATE calculation_results cr
SET
    weight = cr.weight * dr.rule_coefficient,
    value = cr.value * dr.rule_coefficient
FROM discipline_rules dr, departments d, model_nodes mn
WHERE cr.task_id = '{task_id}'
  AND cr.node_type = 'dimension'
  AND cr.department_id = d.id
  AND cr.node_id = mn.id
  AND dr.version_id = {version_id}
  AND dr.hospital_id = {hospital_id}
  AND dr.department_code = d.accounting_unit_code
  AND dr.dimension_code = mn.code;

-- 返回更新的记录数
SELECT COUNT(*) as updated_count
FROM calculation_results cr
INNER JOIN departments d ON cr.department_id = d.id
INNER JOIN model_nodes mn ON cr.node_id = mn.id
INNER JOIN discipline_rules dr
    ON dr.department_code = d.accounting_unit_code
    AND dr.dimension_code = mn.code
    AND dr.version_id = {version_id}
    AND dr.hospital_id = {hospital_id}
WHERE cr.task_id = '{task_id}'
  AND cr.node_type = 'dimension';

-- ===========================================================================
-- 使用说明:
-- ===========================================================================
-- 1. 此步骤在业务导向调整之后、价值汇总之前执行
-- 2. 只调整在 discipline_rules 表中配置了规则的科室-维度组合
-- 3. 未配置规则的科室-维度保持原值不变
-- 4. 调整后的权重和价值会影响价值汇总结果
-- 5. 学科规则使用核算单元代码(accounting_unit_code)匹配科室
-- ===========================================================================
"""

def fix_discipline_rule_steps():
    """修复所有工作流中的学科规则步骤SQL"""
    session = Session()
    
    try:
        # 查找所有学科规则相关的步骤
        result = session.execute(text("""
            SELECT id, workflow_id, name, code_content
            FROM calculation_steps
            WHERE name LIKE '%学科规则%'
        """))
        
        steps = result.fetchall()
        print(f"找到 {len(steps)} 个学科规则步骤:")
        
        for step in steps:
            step_id, workflow_id, name, code_content = step
            print(f"  - ID: {step_id}, 工作流: {workflow_id}, 名称: {name}")
            
            # 检查是否使用了 his_code
            if 'his_code' in code_content:
                print(f"    [需要修复] 使用了 his_code，将更新为 accounting_unit_code")
                
                # 更新SQL
                session.execute(text("""
                    UPDATE calculation_steps
                    SET code_content = :code_content, updated_at = NOW()
                    WHERE id = :step_id
                """), {"step_id": step_id, "code_content": DISCIPLINE_RULE_SQL})
                
                print(f"    [已修复] 步骤 {step_id} 已更新")
            else:
                print(f"    [正常] 已使用 accounting_unit_code")
        
        session.commit()
        print("\n修复完成!")
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    fix_discipline_rule_steps()
