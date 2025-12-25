"""
修复学科规则调整步骤的SQL语法
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 修复后的SQL
FIXED_SQL = """
-- ============================================================================
-- 步骤6: 学科规则调整
-- ============================================================================
-- 功能: 根据学科规则系数调整维度的业务价值（weight和value字段）
--
-- 输入参数(通过占位符):
--   {task_id}    - 计算任务ID
--   {version_id} - 模型版本ID
--   {hospital_id} - 医疗机构ID
--
-- 算法说明:
--   1. 从 discipline_rules 表获取科室-维度的规则系数
--   2. 调整后的 weight = 原 weight * rule_coefficient
--   3. 调整后的 value = 原 value * rule_coefficient
--
-- 输出: 更新 calculation_results 表中匹配的维度节点的 weight 和 value 字段
-- ============================================================================

-- 第1步: 更新 calculation_results 表中的 weight 和 value 字段
-- 注意: PostgreSQL UPDATE...FROM 语法中，FROM子句的表不能用JOIN引用被更新表
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
  AND dr.department_code = d.his_code
  AND dr.dimension_code = mn.code;

-- 返回更新的记录数
SELECT COUNT(*) as updated_count
FROM calculation_results cr
INNER JOIN departments d ON cr.department_id = d.id
INNER JOIN model_nodes mn ON cr.node_id = mn.id
INNER JOIN discipline_rules dr 
    ON dr.department_code = d.his_code 
    AND dr.dimension_code = mn.code
    AND dr.version_id = {version_id}
    AND dr.hospital_id = {hospital_id}
WHERE cr.task_id = '{task_id}'
  AND cr.node_type = 'dimension';

-- ============================================================================
-- 使用说明:
-- ============================================================================
-- 1. 此步骤在Step5（业务导向调整）之后、Step7（价值汇总）之前执行
-- 2. 只调整在 discipline_rules 表中配置了规则的科室-维度组合
-- 3. 未配置规则的科室-维度保持原值不变
-- 4. 调整后的权重和价值会影响Step7的价值汇总结果
-- 5. 占位符会在执行时自动替换:
--    {task_id} -> 计算任务ID
--    {version_id} -> 模型版本ID
--    {hospital_id} -> 医疗机构ID
-- ============================================================================
"""


def fix_sql():
    session = Session()
    try:
        # 更新步骤140的SQL
        session.execute(text("""
            UPDATE calculation_steps 
            SET code_content = :sql_content,
                updated_at = NOW()
            WHERE id = 140
        """), {"sql_content": FIXED_SQL})
        
        session.commit()
        print("✓ 已更新步骤140的SQL")
        
        # 验证
        result = session.execute(text(
            "SELECT LEFT(code_content, 200) as preview FROM calculation_steps WHERE id = 140"
        ))
        row = result.fetchone()
        print(f"\nSQL预览:\n{row.preview}")
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    fix_sql()
