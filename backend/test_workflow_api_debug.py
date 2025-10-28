"""
测试计算流程API - 调试版本
"""
import sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

# 添加项目路径
sys.path.insert(0, '.')

from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.model_version import ModelVersion
from app.config import settings

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)

def test_get_workflows():
    """测试获取计算流程列表"""
    print("=" * 60)
    print("测试获取计算流程列表")
    print("=" * 60)
    
    try:
        with Session(engine) as db:
            # 检查表是否存在
            print("\n1. 检查数据库表...")
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"数据库中的表: {tables}")
            
            if 'calculation_workflows' not in tables:
                print("❌ calculation_workflows 表不存在！")
                return
            
            if 'model_versions' not in tables:
                print("❌ model_versions 表不存在！")
                return
            
            print("✓ 所需表都存在")
            
            # 检查是否有数据
            print("\n2. 检查数据...")
            version_count = db.query(ModelVersion).count()
            workflow_count = db.query(CalculationWorkflow).count()
            print(f"模型版本数量: {version_count}")
            print(f"计算流程数量: {workflow_count}")
            
            # 尝试查询
            print("\n3. 尝试查询计算流程...")
            query = db.query(CalculationWorkflow).options(joinedload(CalculationWorkflow.version))
            items = query.all()
            
            print(f"查询到 {len(items)} 条记录")
            
            # 处理每条记录
            print("\n4. 处理记录...")
            for item in items:
                print(f"\n流程 ID: {item.id}")
                print(f"  名称: {item.name}")
                print(f"  版本ID: {item.version_id}")
                
                # 尝试访问版本
                try:
                    if item.version:
                        print(f"  版本名称: {item.version.name}")
                        item.version_name = item.version.name
                    else:
                        print(f"  版本: None")
                        item.version_name = None
                except Exception as e:
                    print(f"  ❌ 访问版本时出错: {e}")
                    traceback.print_exc()
                
                # 获取步骤数量
                try:
                    step_count = db.query(func.count(CalculationStep.id)).filter(
                        CalculationStep.workflow_id == item.id
                    ).scalar()
                    print(f"  步骤数量: {step_count}")
                    item.step_count = step_count
                except Exception as e:
                    print(f"  ❌ 获取步骤数量时出错: {e}")
                    traceback.print_exc()
            
            print("\n✓ 测试完成")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_get_workflows()
