"""
检查最近任务为什么结果是0条
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def check_recent_task():
    with engine.connect() as conn:
        # 获取最近的任务详情
        result = conn.execute(text("""
            SELECT 
                ct.id as task_id,
                ct.task_id as task_uuid,
                ct.period,
                ct.status,
                ct.workflow_id,
                ct.model_version_id,
                ct.error_message,
                ct.created_at
            FROM calculation_tasks ct
            ORDER BY ct.created_at DESC
            LIMIT 5
        """))
        
        print("最近的任务详情:")
        for row in result:
            print(f"\n任务 {row.task_id} ({row.task_uuid}):")
            print(f"  期间: {row.period}")
            print(f"  状态: {row.status}")
            print(f"  工作流ID: {row.workflow_id}")
            print(f"  版本ID: {row.model_version_id}")
            print(f"  错误信息: {row.error_message}")
            print(f"  创建时间: {row.created_at}")
        
        # 检查步骤执行日志
        print("\n" + "=" * 80)
        print("检查最近任务的步骤执行日志")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                csl.task_id,
                csl.step_name,
                csl.status,
                csl.error_message,
                csl.started_at,
                csl.completed_at
            FROM calculation_step_logs csl
            WHERE csl.task_id IN (
                SELECT id::text FROM calculation_tasks ORDER BY created_at DESC LIMIT 3
            )
            ORDER BY csl.task_id, csl.started_at
        """))
        
        logs = list(result)
        if logs:
            current_task = None
            for log in logs:
                if log.task_id != current_task:
                    current_task = log.task_id
                    print(f"\n任务 {log.task_id}:")
                print(f"  {log.step_name}: {log.status}")
                if log.error_message:
                    print(f"    错误: {log.error_message[:200]}")
        else:
            print("没有找到步骤执行日志")
        
        # 检查有结果的旧任务
        print("\n" + "=" * 80)
        print("检查有结果的旧任务")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                cr.task_id,
                COUNT(*) as result_count,
                COUNT(DISTINCT cr.node_code) as unique_nodes,
                COUNT(DISTINCT cr.department_id) as unique_depts
            FROM calculation_results cr
            GROUP BY cr.task_id
            ORDER BY result_count DESC
            LIMIT 5
        """))
        
        for row in result:
            print(f"  任务 {row.task_id}: {row.result_count} 条结果, {row.unique_nodes} 个节点, {row.unique_depts} 个科室")

if __name__ == '__main__':
    check_recent_task()
