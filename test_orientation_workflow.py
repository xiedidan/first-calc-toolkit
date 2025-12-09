"""
测试包含业务导向调整的标准计算流程
"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 创建数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_workflow_structure():
    """测试工作流结构"""
    print("=" * 80)
    print("测试工作流结构")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # 查询工作流
        result = db.execute(text("""
            SELECT id, name, version_id, is_active
            FROM calculation_workflows
            WHERE name = '标准计算流程-含业务导向'
            ORDER BY id DESC
            LIMIT 1
        """))
        workflow = result.fetchone()
        
        if not workflow:
            print("❌ 未找到工作流")
            return False
        
        print(f"✓ 工作流ID: {workflow[0]}")
        print(f"✓ 工作流名称: {workflow[1]}")
        print(f"✓ 版本ID: {workflow[2]}")
        print(f"✓ 是否激活: {workflow[3]}")
        
        # 查询步骤
        result = db.execute(text("""
            SELECT id, name, sort_order, code_type, data_source_id, is_enabled
            FROM calculation_steps
            WHERE workflow_id = :workflow_id
            ORDER BY sort_order
        """), {"workflow_id": workflow[0]})
        
        steps = result.fetchall()
        print(f"\n✓ 步骤数量: {len(steps)}")
        print("\n步骤详情:")
        for step in steps:
            print(f"  {step[2]}: {step[1]} (数据源: {step[4]}, 启用: {step[5]})")
        
        # 验证步骤3a是否包含导向调整逻辑
        result = db.execute(text("""
            SELECT code_content
            FROM calculation_steps
            WHERE workflow_id = :workflow_id
              AND name = '业务导向调整'
        """), {"workflow_id": workflow[0]})
        
        step3a = result.fetchone()
        if step3a:
            sql_content = step3a[0]
            if 'orientation_values' in sql_content and 'orientation_ratios' in sql_content:
                print("\n✓ 步骤3a包含业务导向调整逻辑")
            else:
                print("\n❌ 步骤3a缺少业务导向调整逻辑")
                return False
        else:
            print("\n❌ 未找到业务导向调整步骤")
            return False
        
        return True
        
    finally:
        db.close()


def test_orientation_values_table():
    """测试orientation_values表是否存在"""
    print("\n" + "=" * 80)
    print("测试orientation_values表")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # 检查表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'orientation_values'
            )
        """))
        
        exists = result.fetchone()[0]
        if not exists:
            print("❌ orientation_values表不存在")
            return False
        
        print("✓ orientation_values表存在")
        
        # 检查表结构
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'orientation_values'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"\n✓ 字段数量: {len(columns)}")
        print("\n字段详情:")
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  {col[0]}: {col[1]} ({nullable})")
        
        # 检查索引
        result = db.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'orientation_values'
        """))
        
        indexes = result.fetchall()
        print(f"\n✓ 索引数量: {len(indexes)}")
        
        # 检查约束
        result = db.execute(text("""
            SELECT conname, contype
            FROM pg_constraint
            WHERE conrelid = 'orientation_values'::regclass
        """))
        
        constraints = result.fetchall()
        print(f"✓ 约束数量: {len(constraints)}")
        
        return True
        
    finally:
        db.close()


def test_model_relationships():
    """测试模型关系"""
    print("\n" + "=" * 80)
    print("测试模型关系")
    print("=" * 80)
    
    try:
        from app.models import OrientationValue, OrientationRule, Hospital
        
        print("✓ OrientationValue模型导入成功")
        print("✓ OrientationRule模型导入成功")
        print("✓ Hospital模型导入成功")
        
        # 检查关系属性
        if hasattr(OrientationValue, 'orientation_rule'):
            print("✓ OrientationValue.orientation_rule关系存在")
        else:
            print("❌ OrientationValue.orientation_rule关系不存在")
            return False
        
        if hasattr(OrientationValue, 'hospital'):
            print("✓ OrientationValue.hospital关系存在")
        else:
            print("❌ OrientationValue.hospital关系不存在")
            return False
        
        if hasattr(OrientationRule, 'orientation_values'):
            print("✓ OrientationRule.orientation_values关系存在")
        else:
            print("❌ OrientationRule.orientation_values关系不存在")
            return False
        
        if hasattr(Hospital, 'orientation_values'):
            print("✓ Hospital.orientation_values关系存在")
        else:
            print("❌ Hospital.orientation_values关系不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 模型导入失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("业务导向计算流程测试")
    print("=" * 80 + "\n")
    
    results = []
    
    # 测试1: 工作流结构
    results.append(("工作流结构", test_workflow_structure()))
    
    # 测试2: orientation_values表
    results.append(("orientation_values表", test_orientation_values_table()))
    
    # 测试3: 模型关系
    results.append(("模型关系", test_model_relationships()))
    
    # 输出总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！业务导向计算流程已成功部署。")
        print("\n下一步:")
        print("1. 准备导向实际值数据（由ETL工程师导入到orientation_values表）")
        print("2. 在前端配置导向规则、基准值和阶梯")
        print("3. 在模型节点中关联导向规则")
        print("4. 创建计算任务并验证导向调整效果")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
