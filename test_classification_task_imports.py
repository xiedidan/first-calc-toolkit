"""
测试分类任务服务和API的导入和基本结构
"""
import sys
sys.path.insert(0, 'backend')

print("测试1: 导入服务模块...")
try:
    from app.services.classification_task_service import ClassificationTaskService
    print("✅ ClassificationTaskService 导入成功")
    
    # 检查方法是否存在
    methods = [
        'create_task',
        'get_tasks',
        'get_task_detail',
        'delete_task',
        'continue_task',
        'get_task_progress',
        'get_task_logs',
    ]
    
    for method in methods:
        if hasattr(ClassificationTaskService, method):
            print(f"  ✅ 方法 {method} 存在")
        else:
            print(f"  ❌ 方法 {method} 不存在")
            
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试2: 导入API模块...")
try:
    from app.api import classification_tasks
    print("✅ classification_tasks API 导入成功")
    
    # 检查router是否存在
    if hasattr(classification_tasks, 'router'):
        print("  ✅ router 存在")
        
        # 检查路由数量
        routes = classification_tasks.router.routes
        print(f"  ✅ 共有 {len(routes)} 个路由")
        
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if hasattr(route.methods, '__iter__') else []
                print(f"    - {methods} {route.path}")
    else:
        print("  ❌ router 不存在")
        
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试3: 检查Schema...")
try:
    from app.schemas.classification_task import (
        ClassificationTaskCreate,
        ClassificationTaskResponse,
        ClassificationTaskListResponse,
        TaskProgressResponse,
        TaskLogResponse,
        ContinueTaskResponse,
    )
    print("✅ 所有Schema导入成功")
    
    schemas = [
        'ClassificationTaskCreate',
        'ClassificationTaskResponse',
        'ClassificationTaskListResponse',
        'TaskProgressResponse',
        'TaskLogResponse',
        'ContinueTaskResponse',
    ]
    
    for schema in schemas:
        print(f"  ✅ {schema}")
        
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试4: 检查模型...")
try:
    from app.models.classification_task import ClassificationTask, TaskStatus
    from app.models.classification_plan import ClassificationPlan
    from app.models.plan_item import PlanItem
    from app.models.task_progress import TaskProgress
    from app.models.api_usage_log import APIUsageLog
    
    print("✅ 所有模型导入成功")
    
    models = [
        'ClassificationTask',
        'ClassificationPlan',
        'PlanItem',
        'TaskProgress',
        'APIUsageLog',
    ]
    
    for model in models:
        print(f"  ✅ {model}")
        
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n测试5: 检查Celery任务...")
try:
    from app.tasks.classification_tasks import classify_items_task, continue_classification_task
    print("✅ Celery任务导入成功")
    print(f"  ✅ classify_items_task")
    print(f"  ✅ continue_classification_task")
        
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("所有导入测试完成！")
print("="*60)
