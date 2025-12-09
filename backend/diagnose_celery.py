"""
诊断Celery任务执行问题
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask
from sqlalchemy import desc


def check_celery_connection():
    """检查Celery连接"""
    print("=" * 60)
    print("1. 检查Celery连接")
    print("=" * 60)
    
    try:
        # 检查broker连接
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✓ Celery broker连接正常")
            print(f"  活跃的worker数量: {len(stats)}")
            for worker_name, worker_stats in stats.items():
                print(f"  - Worker: {worker_name}")
                print(f"    进程数: {worker_stats.get('pool', {}).get('max-concurrency', 'N/A')}")
        else:
            print("✗ 没有检测到活跃的Celery worker")
            print("  请确保Celery worker正在运行:")
            print("  cd backend && celery -A app.celery_app worker --loglevel=info --pool=solo")
            return False
            
    except Exception as e:
        print(f"✗ Celery连接失败: {str(e)}")
        print("  请检查:")
        print("  1. Redis是否正在运行")
        print("  2. CELERY_BROKER_URL配置是否正确")
        return False
    
    return True


def check_registered_tasks():
    """检查已注册的任务"""
    print("\n" + "=" * 60)
    print("2. 检查已注册的任务")
    print("=" * 60)
    
    try:
        inspect = celery_app.control.inspect()
        registered = inspect.registered()
        
        if registered:
            for worker_name, tasks in registered.items():
                print(f"\nWorker: {worker_name}")
                calc_tasks = [t for t in tasks if 'calculation' in t.lower()]
                if calc_tasks:
                    print("  计算相关任务:")
                    for task in calc_tasks:
                        print(f"    - {task}")
                else:
                    print("  ✗ 未找到计算相关任务")
                    print("  所有已注册任务:")
                    for task in tasks:
                        print(f"    - {task}")
        else:
            print("✗ 无法获取已注册任务列表")
            return False
            
    except Exception as e:
        print(f"✗ 检查失败: {str(e)}")
        return False
    
    return True


def check_pending_tasks():
    """检查待处理的任务"""
    print("\n" + "=" * 60)
    print("3. 检查数据库中的任务状态")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 查询最近的10个任务
        tasks = db.query(CalculationTask).order_by(
            desc(CalculationTask.created_at)
        ).limit(10).all()
        
        if not tasks:
            print("  数据库中没有任务记录")
            return True
        
        print(f"\n最近的{len(tasks)}个任务:")
        print("-" * 60)
        
        status_count = {}
        for task in tasks:
            status = task.status
            status_count[status] = status_count.get(status, 0) + 1
            
            status_icon = {
                'pending': '⏳',
                'running': '▶️',
                'completed': '✓',
                'failed': '✗',
                'cancelled': '⊗'
            }.get(status, '?')
            
            print(f"{status_icon} {task.task_id[:8]}... | {status:10} | {task.created_at}")
            if task.error_message:
                print(f"   错误: {task.error_message[:100]}")
        
        print("\n状态统计:")
        for status, count in status_count.items():
            print(f"  {status}: {count}")
        
        # 检查是否有长时间pending的任务
        pending_tasks = [t for t in tasks if t.status == 'pending']
        if pending_tasks:
            print(f"\n⚠️  发现 {len(pending_tasks)} 个pending状态的任务")
            print("  这可能意味着:")
            print("  1. Celery worker未运行")
            print("  2. 任务提交失败")
            print("  3. Worker无法处理任务")
            
    except Exception as e:
        print(f"✗ 检查失败: {str(e)}")
        return False
    finally:
        db.close()
    
    return True


def check_active_tasks():
    """检查活跃的任务"""
    print("\n" + "=" * 60)
    print("4. 检查Celery队列中的任务")
    print("=" * 60)
    
    try:
        inspect = celery_app.control.inspect()
        
        # 检查活跃任务
        active = inspect.active()
        if active:
            print("\n活跃任务:")
            for worker_name, tasks in active.items():
                if tasks:
                    print(f"  Worker {worker_name}: {len(tasks)} 个任务")
                    for task in tasks:
                        print(f"    - {task.get('name')} ({task.get('id')[:8]}...)")
                else:
                    print(f"  Worker {worker_name}: 无活跃任务")
        else:
            print("  无活跃任务")
        
        # 检查预定任务
        scheduled = inspect.scheduled()
        if scheduled:
            print("\n预定任务:")
            for worker_name, tasks in scheduled.items():
                if tasks:
                    print(f"  Worker {worker_name}: {len(tasks)} 个任务")
                else:
                    print(f"  Worker {worker_name}: 无预定任务")
        else:
            print("  无预定任务")
        
        # 检查保留任务
        reserved = inspect.reserved()
        if reserved:
            print("\n保留任务:")
            for worker_name, tasks in reserved.items():
                if tasks:
                    print(f"  Worker {worker_name}: {len(tasks)} 个任务")
                else:
                    print(f"  Worker {worker_name}: 无保留任务")
        else:
            print("  无保留任务")
            
    except Exception as e:
        print(f"✗ 检查失败: {str(e)}")
        return False
    
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Celery任务执行诊断工具")
    print("=" * 60)
    
    results = []
    
    # 1. 检查连接
    results.append(("Celery连接", check_celery_connection()))
    
    # 2. 检查已注册任务
    if results[0][1]:  # 只有连接成功才继续
        results.append(("已注册任务", check_registered_tasks()))
        results.append(("数据库任务", check_pending_tasks()))
        results.append(("队列任务", check_active_tasks()))
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    if not all(r[1] for r in results):
        print("\n建议:")
        print("1. 确保Redis正在运行: redis-server")
        print("2. 启动Celery worker:")
        print("   cd backend")
        print("   celery -A app.celery_app worker --loglevel=debug --pool=solo")
        print("3. 检查后端日志输出")
        print("4. 检查Celery worker日志输出")
    else:
        print("\n✓ 所有检查通过!")


if __name__ == "__main__":
    main()
