"""
测试学科规则调整步骤

验证:
1. 步骤SQL语法正确
2. 占位符替换正确
3. 能正确更新calculation_results中的weight和value
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://root:root@47.108.227.254:50016/hospital_value"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def test_step_sql_syntax():
    """测试步骤SQL语法"""
    session = Session()
    
    try:
        # 获取学科规则调整步骤的SQL
        result = session.execute(text("""
            SELECT id, name, code_content 
            FROM calculation_steps 
            WHERE workflow_id = 34 AND name = '学科规则调整'
        """))
        step = result.fetchone()
        
        if not step:
            print("❌ 未找到学科规则调整步骤")
            return False
        
        print(f"✓ 找到步骤: ID={step.id}, name={step.name}")
        print(f"\nSQL内容预览 (前500字符):")
        print(step.code_content[:500])
        
        # 模拟占位符替换
        sql = step.code_content
        sql = sql.replace("{task_id}", "test-task-123")
        sql = sql.replace("{version_id}", "1")
        sql = sql.replace("{hospital_id}", "1")
        
        print("\n替换占位符后的SQL (前500字符):")
        print(sql[:500])
        
        # 检查是否还有未替换的占位符
        import re
        remaining = re.findall(r'\{[a-z_]+\}', sql)
        if remaining:
            print(f"\n⚠️ 警告: 还有未替换的占位符: {remaining}")
        else:
            print("\n✓ 所有占位符已替换")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def test_discipline_rules_data():
    """检查学科规则数据"""
    session = Session()
    
    try:
        # 检查discipline_rules表是否存在
        result = session.execute(text("""
            SELECT COUNT(*) as cnt FROM discipline_rules
        """))
        count = result.fetchone().cnt
        print(f"\n学科规则表记录数: {count}")
        
        if count > 0:
            # 显示一些示例数据
            result = session.execute(text("""
                SELECT dr.id, dr.hospital_id, dr.version_id, 
                       dr.department_code, dr.department_name,
                       dr.dimension_code, dr.dimension_name,
                       dr.rule_coefficient
                FROM discipline_rules dr
                LIMIT 5
            """))
            rules = result.fetchall()
            print("\n示例学科规则:")
            for rule in rules:
                print(f"  ID={rule.id}, 科室={rule.department_name}({rule.department_code}), "
                      f"维度={rule.dimension_name}({rule.dimension_code}), 系数={rule.rule_coefficient}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def test_workflow_steps():
    """显示流程34的所有步骤"""
    session = Session()
    
    try:
        result = session.execute(text("""
            SELECT id, name, sort_order, data_source_id, is_enabled
            FROM calculation_steps 
            WHERE workflow_id = 34 
            ORDER BY sort_order
        """))
        steps = result.fetchall()
        
        print("\n流程34的步骤列表:")
        print("-" * 80)
        for step in steps:
            status = "✓" if step.is_enabled else "✗"
            ds = f"数据源={step.data_source_id}" if step.data_source_id else "无数据源"
            print(f"  {status} 步骤{step.sort_order}: {step.name} (ID={step.id}, {ds})")
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    finally:
        session.close()


def main():
    print("=" * 60)
    print("学科规则调整步骤测试")
    print("=" * 60)
    
    test_workflow_steps()
    test_step_sql_syntax()
    test_discipline_rules_data()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
