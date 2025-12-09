#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试医技业务价值计算步骤
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# API配置
BASE_URL = "http://localhost:8000"
HOSPITAL_ID = 1
VERSION_ID = 26
WORKFLOW_ID = 31

def login():
    """登录获取token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        sys.exit(1)

def create_task(token):
    """创建计算任务"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    
    data = {
        "version_id": VERSION_ID,
        "workflow_id": WORKFLOW_ID,
        "period": "2025-10",
        "description": "测试医技业务价值计算"
    }
    
    print(f"创建任务: {data}")
    response = requests.post(
        f"{BASE_URL}/api/v1/calculation-tasks",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        task = response.json()
        print(f"任务创建成功: {task['task_id']}")
        return task['task_id']
    else:
        print(f"任务创建失败: {response.status_code}")
        print(response.text)
        sys.exit(1)

def check_task_status(token, task_id):
    """检查任务状态"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    
    max_attempts = 60
    for i in range(max_attempts):
        response = requests.get(
            f"{BASE_URL}/api/v1/calculation-tasks/{task_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            task = response.json()
            status = task['status']
            print(f"[{i+1}/{max_attempts}] 任务状态: {status}")
            
            if status == 'completed':
                print("任务完成！")
                return task
            elif status == 'failed':
                print(f"任务失败: {task.get('error_message', '未知错误')}")
                return task
            
            time.sleep(2)
        else:
            print(f"查询任务失败: {response.status_code}")
            print(response.text)
            sys.exit(1)
    
    print("任务超时")
    return None

def check_results(token, task_id):
    """检查计算结果"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Hospital-ID": str(HOSPITAL_ID)
    }
    
    # 检查医技维度的结果
    from sqlalchemy import create_engine, text
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://root:root@47.108.227.254:50016/hospital_value')
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 统计各维度的记录数
        sql = text("""
            SELECT 
                SUBSTRING(node_code FROM 'dim-tech-([^-]+)') as category,
                COUNT(*) as count,
                SUM(workload) as total_workload,
                SUM(value) as total_value
            FROM calculation_results
            WHERE task_id = :task_id
              AND node_code LIKE 'dim-tech%'
            GROUP BY SUBSTRING(node_code FROM 'dim-tech-([^-]+)')
            ORDER BY category
        """)
        result = conn.execute(sql, {'task_id': task_id})
        
        print("\n医技维度统计:")
        print("-" * 80)
        print(f"{'类别':<10} {'记录数':<10} {'总工作量':<20} {'总价值':<20}")
        print("-" * 80)
        
        total_count = 0
        total_workload = 0
        total_value = 0
        
        for row in result:
            category_map = {
                'exam': '检查',
                'lab': '化验',
                'ana': '麻醉'
            }
            category_name = category_map.get(row[0], row[0])
            print(f"{category_name:<10} {row[1]:<10} {float(row[2]):<20,.2f} {float(row[3]):<20,.2f}")
            total_count += row[1]
            total_workload += float(row[2])
            total_value += float(row[3])
        
        print("-" * 80)
        print(f"{'合计':<10} {total_count:<10} {total_workload:<20,.2f} {total_value:<20,.2f}")
        
        # 检查各末级维度
        sql2 = text("""
            SELECT 
                node_code,
                node_name,
                COUNT(*) as dept_count,
                SUM(workload) as total_workload,
                AVG(weight) as avg_weight,
                SUM(value) as total_value
            FROM calculation_results
            WHERE task_id = :task_id
              AND node_code LIKE 'dim-tech%'
            GROUP BY node_code, node_name
            ORDER BY node_code
        """)
        result2 = conn.execute(sql2, {'task_id': task_id})
        
        print("\n各末级维度明细:")
        print("-" * 100)
        print(f"{'维度编码':<25} {'维度名称':<20} {'科室数':<8} {'总工作量':<15} {'平均权重':<10} {'总价值':<15}")
        print("-" * 100)
        
        for row in result2:
            print(f"{row[0]:<25} {row[1]:<20} {row[2]:<8} {float(row[3]):<15,.2f} {float(row[4]):<10.4f} {float(row[5]):<15,.2f}")

if __name__ == '__main__':
    print("开始测试医技业务价值计算...")
    print("=" * 80)
    
    # 登录
    print("\n1. 登录系统...")
    token = login()
    print("登录成功")
    
    # 创建任务
    print("\n2. 创建计算任务...")
    task_id = create_task(token)
    
    # 等待任务完成
    print("\n3. 等待任务完成...")
    task = check_task_status(token, task_id)
    
    if task and task['status'] == 'completed':
        # 检查结果
        print("\n4. 检查计算结果...")
        check_results(token, task_id)
        print("\n测试完成！")
    else:
        print("\n测试失败！")
        sys.exit(1)
