"""
为计算流程ID34添加学科规则调整步骤

步骤说明:
- 在步骤5（业务导向调整）之后、步骤6（业务价值汇总）之前插入新步骤
- 新步骤6: 学科规则调整 - 根据学科规则系数调整维度的业务价值
- 原步骤6（业务价值汇总）改为步骤7
"""
import os
import sys
from decimal import Decimal

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库连接
DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# 学科规则调整步骤的SQL
DISCIPLINE_RULE_STEP_SQL = """
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


def add_discipline_rule_step():
    """添加学科规则调整步骤到流程34"""
    session = Session()
    
    try:
        # 1. 检查流程34是否存在
        result = session.execute(text(
            "SELECT id, name FROM calculation_workflows WHERE id = 34"
        ))
        workflow = result.fetchone()
        if not workflow:
            print("错误: 流程ID 34 不存在")
            return False
        print(f"找到流程: {workflow.name}")
        
        # 2. 查看当前步骤
        result = session.execute(text("""
            SELECT id, name, sort_order 
            FROM calculation_steps 
            WHERE workflow_id = 34 
            ORDER BY sort_order
        """))
        steps = result.fetchall()
        print("\n当前步骤:")
        for step in steps:
            print(f"  ID={step.id}, sort_order={step.sort_order}, name={step.name}")
        
        # 3. 检查是否已存在学科规则调整步骤
        result = session.execute(text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = 34 AND name = '学科规则调整'
        """))
        existing = result.fetchone()
        if existing:
            print(f"\n学科规则调整步骤已存在 (ID={existing.id})，跳过创建")
            return True
        
        # 4. 将原步骤6（业务价值汇总，sort_order=6.00）改为步骤7
        print("\n将业务价值汇总步骤的sort_order从6.00改为7.00...")
        session.execute(text("""
            UPDATE calculation_steps 
            SET sort_order = 7.00 
            WHERE workflow_id = 34 AND sort_order = 6.00
        """))
        
        # 5. 插入新的步骤6（学科规则调整）
        # 获取其他步骤使用的数据源ID
        result = session.execute(text("""
            SELECT data_source_id FROM calculation_steps 
            WHERE workflow_id = 34 AND data_source_id IS NOT NULL 
            LIMIT 1
        """))
        data_source_row = result.fetchone()
        data_source_id = data_source_row.data_source_id if data_source_row else None
        
        print(f"插入学科规则调整步骤 (sort_order=6.00, data_source_id={data_source_id})...")
        session.execute(text("""
            INSERT INTO calculation_steps (
                workflow_id, name, description, code_type, code_content, 
                sort_order, is_enabled, created_at, updated_at, data_source_id
            ) VALUES (
                34, 
                '学科规则调整', 
                '根据学科规则系数调整维度的业务价值（weight和value字段）',
                'sql',
                :sql_content,
                6.00,
                true,
                NOW(),
                NOW(),
                :data_source_id
            )
        """), {"sql_content": DISCIPLINE_RULE_STEP_SQL, "data_source_id": data_source_id})
        
        session.commit()
        
        # 6. 验证结果
        result = session.execute(text("""
            SELECT id, name, sort_order 
            FROM calculation_steps 
            WHERE workflow_id = 34 
            ORDER BY sort_order
        """))
        steps = result.fetchall()
        print("\n更新后的步骤:")
        for step in steps:
            print(f"  ID={step.id}, sort_order={step.sort_order}, name={step.name}")
        
        print("\n✓ 学科规则调整步骤添加成功!")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    add_discipline_rule_step()
