import sys
import time
sys.path.insert(0, 'backend')
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult
from app.tasks.calculation_tasks import execute_calculation_task

# 创建任务
db = SessionLocal()
try:
    # 生成任务ID
    import uuid
    from datetime import datetime
    
    task_id = str(uuid.uuid4())
    
    print("=" * 60)
    print("创建计算任务")
    print("=" * 60)
    print(f"任务ID: {task_id}")
    print(f"版本ID: 1 (2025年标准版)")
    print(f"流程ID: 22 (标准计算流程)")
    print(f"月份: 2025-01")
    
    # 创建任务记录
    db_task = CalculationTask(
        task_id=task_id,
        model_version_id=1,
        workflow_id=22,
        period="2025-01",
        status="pending",
        description="API测试-标准计算流程验证",
        created_by=1,
        created_at=datetime.now()
    )
    db.add(db_task)
    db.commit()
    
    print(f"\n[OK] 任务记录已创建")
    
    # 同步执行任务（用于测试）
    print(f"\n开始执行计算任务...")
    print("-" * 60)
    
    try:
        execute_calculation_task(
            task_id=task_id,
            model_version_id=1,
            workflow_id=22,
            department_ids=None,
            period="2025-01"
        )
        
        # 等待一下让任务完成
        time.sleep(2)
        
        # 查询任务状态
        db.expire_all()
        task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
        
        print("\n" + "=" * 60)
        print("任务执行结果")
        print("=" * 60)
        print(f"状态: {task.status}")
        if task.completed_at:
            print(f"完成时间: {task.completed_at}")
        if task.error_message:
            print(f"错误信息: {task.error_message}")
        
        # 查询结果数量
        result_count = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id
        ).count()
        print(f"\n生成结果记录数: {result_count}")
        
        if result_count > 0:
            # 显示部分结果
            sample_results = db.query(CalculationResult).filter(
                CalculationResult.task_id == task_id
            ).limit(5).all()
            
            print(f"\n前5条结果示例:")
            print("-" * 60)
            for r in sample_results:
                print(f"科室ID: {r.department_id}, 节点: {r.node_name}, 类型: {r.node_type}, 价值: {r.value}")
        
        print("\n" + "=" * 60)
        if task.status == "completed":
            print("[SUCCESS] 标准计算流程测试成功!")
        elif task.status == "failed":
            print("[FAILED] 标准计算流程测试失败")
        else:
            print(f"[INFO] 任务状态: {task.status}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
finally:
    db.close()
