"""
测试AI分类任务
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models.classification_task import ClassificationTask, TaskStatus
from app.models.classification_plan import ClassificationPlan
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.ai_config import AIConfig
from app.models.model_version import ModelVersion
from app.models.charge_item import ChargeItem
from app.tasks.classification_tasks import classify_items_task, continue_classification_task


def test_task_structure():
    """测试任务结构和数据库连接"""
    db = SessionLocal()
    
    try:
        # 1. 检查是否有AI配置
        ai_configs = db.query(AIConfig).all()
        print(f"✓ 找到 {len(ai_configs)} 个AI配置")
        
        if ai_configs:
            config = ai_configs[0]
            print(f"  - 医疗机构ID: {config.hospital_id}")
            print(f"  - API端点: {config.api_endpoint}")
            print(f"  - 调用延迟: {config.call_delay}秒")
        
        # 2. 检查是否有分类任务
        tasks = db.query(ClassificationTask).all()
        print(f"\n✓ 找到 {len(tasks)} 个分类任务")
        
        if tasks:
            task = tasks[0]
            print(f"  - 任务ID: {task.id}")
            print(f"  - 任务名称: {task.task_name}")
            print(f"  - 状态: {task.status}")
            print(f"  - 收费类别: {task.charge_categories}")
            print(f"  - 总项目数: {task.total_items}")
            print(f"  - 已处理: {task.processed_items}")
            print(f"  - 失败: {task.failed_items}")
        
        # 3. 检查是否有预案
        plans = db.query(ClassificationPlan).all()
        print(f"\n✓ 找到 {len(plans)} 个分类预案")
        
        if plans:
            plan = plans[0]
            print(f"  - 预案ID: {plan.id}")
            print(f"  - 任务ID: {plan.task_id}")
            print(f"  - 状态: {plan.status}")
            
            # 检查预案项目
            items = db.query(PlanItem).filter(PlanItem.plan_id == plan.id).all()
            print(f"  - 预案项目数: {len(items)}")
            
            if items:
                # 统计各状态的项目数
                pending = sum(1 for i in items if i.processing_status == ProcessingStatus.pending)
                processing = sum(1 for i in items if i.processing_status == ProcessingStatus.processing)
                completed = sum(1 for i in items if i.processing_status == ProcessingStatus.completed)
                failed = sum(1 for i in items if i.processing_status == ProcessingStatus.failed)
                
                print(f"    - 待处理: {pending}")
                print(f"    - 处理中: {processing}")
                print(f"    - 已完成: {completed}")
                print(f"    - 失败: {failed}")
                
                # 显示前3个项目
                print(f"\n  前3个项目:")
                for item in items[:3]:
                    print(f"    - {item.charge_item_name}")
                    print(f"      状态: {item.processing_status}")
                    if item.ai_suggested_dimension_id:
                        print(f"      AI建议维度ID: {item.ai_suggested_dimension_id}")
                        print(f"      确信度: {item.ai_confidence}")
        
        # 4. 检查收费项目
        charge_items = db.query(ChargeItem).limit(5).all()
        print(f"\n✓ 数据库中有收费项目")
        print(f"  前5个收费项目:")
        for item in charge_items:
            print(f"    - {item.item_name} (类别: {item.item_category})")
        
        # 5. 检查模型版本
        versions = db.query(ModelVersion).all()
        print(f"\n✓ 找到 {len(versions)} 个模型版本")
        
        if versions:
            version = versions[0]
            print(f"  - 版本ID: {version.id}")
            print(f"  - 医疗机构ID: {version.hospital_id}")
        
        print("\n✓ 所有数据结构检查通过")
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_task_import():
    """测试任务模块导入"""
    try:
        from app.tasks.classification_tasks import classify_items_task, continue_classification_task
        print("✓ 成功导入分类任务模块")
        print(f"  - classify_items_task: {classify_items_task}")
        print(f"  - continue_classification_task: {continue_classification_task}")
        
        # 检查任务是否已注册到Celery
        from app.celery_app import celery_app
        registered_tasks = list(celery_app.tasks.keys())
        
        classification_tasks = [t for t in registered_tasks if 'classification' in t.lower()]
        print(f"\n✓ Celery中注册的分类任务:")
        for task in classification_tasks:
            print(f"  - {task}")
        
        if not classification_tasks:
            print("  ⚠ 警告: 没有找到注册的分类任务")
            print("  请确保Celery worker已重启")
        
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("AI分类任务测试")
    print("=" * 60)
    
    print("\n1. 测试任务模块导入")
    print("-" * 60)
    test_task_import()
    
    print("\n2. 测试数据库结构")
    print("-" * 60)
    test_task_structure()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n提示:")
    print("- 如果要实际执行分类任务，请确保:")
    print("  1. AI配置已正确设置（API端点和密钥）")
    print("  2. Celery worker正在运行")
    print("  3. Redis服务正在运行")
    print("- 可以通过API创建分类任务来触发异步处理")
