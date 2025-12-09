"""
通过API创建计算任务并监控执行状态 - 使用2025-11数据
"""
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
    print("创建计算任务 - 测试标准计算流程")
    print("=" * 60)
    print(f"任务ID: {task_id}")
    print(f"版本ID: 1 (2025年标准版)")
    print(f"流程ID: 22 (标准计算流程)")
    print(f"月份: 2025-11")
    
    # 创建任务记录
    db_task = CalculationTask(
        task_id=task_id,
        model_version_id=1,
        workflow_id=22,
        period="2025-11",
        status="pending",
        description="API测试-标准计算流程验证-2025年11月数据",
        created_by=1,
        created_at=datetime.now()
    )
    db.add(db_task)
    db.commit()
    
    print(f"\n[OK] 任务记录已创建")
    
    # 使用Celery异步执行
    print(f"\n提交Celery任务...")
    print("-" * 60)
    
    try:
        # 使用.delay()方法异步执行
        celery_result = execute_calculation_task.delay(
            task_id=task_id,
            model_version_id=1,
            workflow_id=22,
            department_ids=None,
            period="2025-11"
        )
        
        print(f"Celery任务ID: {celery_result.id}")
        print(f"任务已提交，等待执行...")
        
        # 轮询任务状态
        max_wait = 60  # 最多等待60秒
        wait_interval = 3  # 每3秒查询一次
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            # 刷新数据库会话
            db.expire_all()
            task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
            
            print(f"[{elapsed}s] 状态: {task.status}", end="")
            if task.progress:
                print(f", 进度: {task.progress}%", end="")
            print()
            
            if task.status in ["completed", "failed", "cancelled"]:
                break
        
        # 查询最终状态
        db.expire_all()
        task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
        
        print("\n" + "=" * 60)
        print("任务执行结果")
        print("=" * 60)
        print(f"状态: {task.status}")
        if task.started_at:
            print(f"开始时间: {task.started_at}")
        if task.completed_at:
            print(f"完成时间: {task.completed_at}")
            duration = (task.completed_at - task.started_at).total_seconds()
            print(f"执行耗时: {duration:.2f}秒")
        if task.error_message:
            print(f"错误信息: {task.error_message}")
        
        # 查询结果数量
        result_count = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id
        ).count()
        print(f"\n生成结果记录数: {result_count}")
        
        if result_count > 0:
            # 按节点类型统计
            from sqlalchemy import func
            type_stats = db.query(
                CalculationResult.node_type,
                func.count(CalculationResult.id).label('count')
            ).filter(
                CalculationResult.task_id == task_id
            ).group_by(CalculationResult.node_type).all()
            
            print(f"\n按节点类型统计:")
            for node_type, count in type_stats:
                print(f"  {node_type}: {count} 条")
            
            # 显示部分结果
            sample_results = db.query(CalculationResult).filter(
                CalculationResult.task_id == task_id
            ).order_by(CalculationResult.node_type, CalculationResult.department_id).limit(10).all()
            
            print(f"\n前10条结果示例:")
            print("-" * 80)
            for r in sample_results:
                print(f"科室ID: {r.department_id:3d} | 类型: {r.node_type:10s} | 节点: {r.node_name:20s} | 价值: {r.value}")
        
        print("\n" + "=" * 60)
        if task.status == "completed" and result_count > 0:
            print("[SUCCESS] 标准计算流程测试成功!")
            print(f"任务ID: {task_id}")
        elif task.status == "completed" and result_count == 0:
            print("[WARNING] 任务完成但未生成结果数据")
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
