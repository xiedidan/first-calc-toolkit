#!/usr/bin/env python3
"""
测试新的标准计算流程（包含步骤1：数据准备）
"""

import requests
import time
import sys

# API配置
BASE_URL = "http://localhost:8000/api/v1"
HOSPITAL_ID = 1
VERSION_ID = 1
WORKFLOW_ID = 24  # 新导入的流程ID（使用数据源3）
PERIOD = "2025-11"

# 认证配置
USERNAME = "admin"
PASSWORD = "admin123"

# 全局session
session = requests.Session()


def login():
    """登录获取token"""
    print("=" * 80)
    print("步骤0: 用户登录")
    print("=" * 80)
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = session.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        token = result.get('access_token')
        session.headers.update({
            "Authorization": f"Bearer {token}",
            "X-Hospital-ID": str(HOSPITAL_ID)  # 添加医疗机构ID到请求头
        })
        print(f"✅ 登录成功")
        print(f"   用户: {USERNAME}")
        print(f"   医疗机构ID: {HOSPITAL_ID}")
        return True
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False


def activate_hospital():
    """激活医疗机构"""
    print("\n" + "=" * 80)
    print("步骤0.5: 激活医疗机构")
    print("=" * 80)
    
    url = f"{BASE_URL}/hospitals/{HOSPITAL_ID}/activate"
    response = session.post(url)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 医疗机构激活成功")
        print(f"   医疗机构ID: {HOSPITAL_ID}")
        print(f"   医疗机构名称: {result.get('name', 'N/A')}")
        
        # 重新登录以刷新token中的医疗机构信息
        print(f"\n   重新登录以刷新会话...")
        return login()
    else:
        print(f"❌ 医疗机构激活失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return False

def create_task():
    """创建计算任务"""
    print("\n" + "=" * 80)
    print("步骤1: 创建计算任务")
    print("=" * 80)
    
    url = f"{BASE_URL}/calculation/tasks"
    payload = {
        "hospital_id": HOSPITAL_ID,  # 显式指定医疗机构ID
        "model_version_id": VERSION_ID,
        "workflow_id": WORKFLOW_ID,
        "period": PERIOD,
        "description": f"测试新流程-包含数据准备步骤-{PERIOD}"
    }
    
    print(f"请求URL: {url}")
    print(f"请求数据: {payload}")
    
    response = session.post(url, json=payload)
    
    if response.status_code == 200:
        task = response.json()
        # 使用task_id而不是id
        task_id = task.get('task_id') or task.get('id')
        print(f"✅ 任务创建成功!")
        print(f"   任务ID: {task_id}")
        print(f"   数据库ID: {task.get('id')}")
        print(f"   任务状态: {task['status']}")
        print(f"   工作流: {task.get('workflow_name', 'N/A')}")
        return task_id
    else:
        print(f"❌ 任务创建失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        sys.exit(1)


def get_task_status(task_id):
    """获取任务状态"""
    url = f"{BASE_URL}/calculation/tasks/{task_id}"
    response = session.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 获取任务状态失败: {response.status_code}")
        return None


def wait_for_completion(task_id, timeout=300):
    """等待任务完成"""
    print("\n" + "=" * 80)
    print("步骤2: 等待任务执行完成")
    print("=" * 80)
    
    start_time = time.time()
    last_status = None
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"\n❌ 超时: 任务执行超过 {timeout} 秒")
            return False
        
        task = get_task_status(task_id)
        if not task:
            time.sleep(2)
            continue
        
        status = task['status']
        
        # 只在状态变化时打印
        if status != last_status:
            print(f"\n[{elapsed:.1f}s] 任务状态: {status}")
            if task.get('current_step'):
                print(f"   当前步骤: {task['current_step']}")
            if task.get('progress'):
                print(f"   进度: {task['progress']}")
            last_status = status
        
        if status == 'completed':
            print(f"\n✅ 任务执行成功!")
            print(f"   总耗时: {elapsed:.1f} 秒")
            return True
        elif status == 'failed':
            print(f"\n❌ 任务执行失败!")
            if task.get('error_message'):
                print(f"   错误信息: {task['error_message']}")
            return False
        
        time.sleep(2)


def get_task_results(task_id):
    """获取任务结果统计"""
    print("\n" + "=" * 80)
    print("步骤3: 查看任务结果")
    print("=" * 80)
    
    # 获取任务详情
    task = get_task_status(task_id)
    if not task:
        return
    
    print(f"\n任务信息:")
    print(f"  任务ID: {task['id']}")
    print(f"  状态: {task['status']}")
    print(f"  周期: {task['period']}")
    print(f"  工作流: {task.get('workflow_name', 'N/A')}")
    print(f"  创建时间: {task.get('created_at', 'N/A')}")
    print(f"  完成时间: {task.get('completed_at', 'N/A')}")
    
    # 获取计算结果统计
    url = f"{BASE_URL}/calculation/tasks/{task_id}/results/summary"
    response = session.get(url)
    
    if response.status_code == 200:
        summary = response.json()
        print(f"\n计算结果统计:")
        print(f"  总记录数: {summary.get('total_records', 0)}")
        print(f"  科室数: {summary.get('department_count', 0)}")
        print(f"  节点数: {summary.get('node_count', 0)}")
        
        if summary.get('by_node_type'):
            print(f"\n按节点类型统计:")
            for node_type, count in summary['by_node_type'].items():
                print(f"    {node_type}: {count} 条")
        
        if summary.get('total_value'):
            print(f"\n总业务价值: {summary['total_value']:.2f}")
    else:
        print(f"\n⚠️  无法获取结果统计: {response.status_code}")
    
    # 获取步骤执行日志
    print(f"\n步骤执行日志:")
    url = f"{BASE_URL}/calculation/tasks/{task_id}/logs"
    response = session.get(url)
    
    if response.status_code == 200:
        logs = response.json()
        if isinstance(logs, list):
            for log in logs:
                status_icon = "✅" if log['status'] == 'completed' else "❌" if log['status'] == 'failed' else "⏳"
                print(f"  {status_icon} 步骤{log['step_order']}: {log['step_name']}")
                print(f"     状态: {log['status']}")
                if log.get('started_at'):
                    print(f"     开始: {log['started_at']}")
                if log.get('completed_at'):
                    print(f"     完成: {log['completed_at']}")
                if log.get('records_affected'):
                    print(f"     影响记录数: {log['records_affected']}")
                if log.get('error_message'):
                    print(f"     错误: {log['error_message']}")
        else:
            print(f"  ⚠️  日志格式异常: {logs}")
    else:
        print(f"  ⚠️  无法获取执行日志: {response.status_code}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("测试新的标准计算流程")
    print("=" * 80)
    print(f"医疗机构ID: {HOSPITAL_ID}")
    print(f"模型版本ID: {VERSION_ID}")
    print(f"工作流ID: {WORKFLOW_ID}")
    print(f"统计周期: {PERIOD}")
    print("=" * 80)
    
    try:
        # 登录
        if not login():
            sys.exit(1)
        
        # 激活医疗机构
        if not activate_hospital():
            sys.exit(1)
        
        # 创建任务
        task_id = create_task()
        
        # 等待完成
        success = wait_for_completion(task_id)
        
        # 查看结果
        get_task_results(task_id)
        
        if success:
            print("\n" + "=" * 80)
            print("✅ 测试完成!")
            print("=" * 80)
            print(f"\n可以在前端查看详细结果:")
            print(f"  http://localhost/calculation-tasks/{task_id}")
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ 测试失败!")
            print("=" * 80)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
