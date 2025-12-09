#!/usr/bin/env python3
"""
添加工作量维度统计步骤到现有流程
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 获取数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL未配置")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def add_step_to_workflow(workflow_id: int, data_source_id: int):
    """添加步骤3c到指定流程"""
    
    # 读取SQL文件
    sql_file = 'backend/standard_workflow_templates/step3c_workload_dimensions.sql'
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 转义单引号
    sql_content = sql_content.replace("'", "''")
    
    with engine.connect() as conn:
        # 检查步骤是否已存在
        result = conn.execute(text("""
            SELECT id FROM calculation_steps 
            WHERE workflow_id = :workflow_id 
              AND name = '工作量维度统计'
        """), {'workflow_id': workflow_id})
        
        existing = result.fetchone()
        if existing:
            print(f"⚠️  步骤已存在 (ID={existing[0]})，跳过")
            return existing[0]
        
        # 插入新步骤
        result = conn.execute(text(f"""
            INSERT INTO calculation_steps (
                workflow_id, 
                name, 
                description, 
                code_type, 
                code_content, 
                data_source_id,
                sort_order, 
                is_enabled, 
                created_at, 
                updated_at
            ) 
            VALUES (
                :workflow_id,
                '工作量维度统计',
                '从工作量统计表中提取护理床日、出入转院、手术管理、手术室护理等维度的工作量',
                'sql',
                '{sql_content}',
                :data_source_id,
                3.60,
                TRUE,
                NOW(),
                NOW()
            )
            RETURNING id;
        """), {
            'workflow_id': workflow_id,
            'data_source_id': data_source_id
        })
        
        step_id = result.scalar()
        conn.commit()
        
        print(f"✅ 成功添加步骤 (ID={step_id})")
        return step_id

def main():
    """主函数"""
    print("=" * 60)
    print("添加工作量维度统计步骤")
    print("=" * 60)
    
    # 默认参数
    workflow_id = 27  # 最新流程
    data_source_id = 3  # 数据源ID
    
    # 从命令行参数获取
    if len(sys.argv) > 1:
        workflow_id = int(sys.argv[1])
    if len(sys.argv) > 2:
        data_source_id = int(sys.argv[2])
    
    print(f"\n目标流程ID: {workflow_id}")
    print(f"数据源ID: {data_source_id}")
    
    # 查询流程信息
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT w.name, w.version_id, mv.name as version_name
            FROM calculation_workflows w
            JOIN model_versions mv ON w.version_id = mv.id
            WHERE w.id = :workflow_id
        """), {'workflow_id': workflow_id})
        
        workflow = result.fetchone()
        if not workflow:
            print(f"❌ 流程不存在: ID={workflow_id}")
            sys.exit(1)
        
        print(f"流程名称: {workflow[0]}")
        print(f"模型版本: {workflow[2]} (ID={workflow[1]})")
    
    # 添加步骤
    print("\n添加步骤...")
    step_id = add_step_to_workflow(workflow_id, data_source_id)
    
    # 显示所有步骤
    print("\n当前流程的所有步骤:")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, name, sort_order, is_enabled
            FROM calculation_steps
            WHERE workflow_id = :workflow_id
            ORDER BY sort_order
        """), {'workflow_id': workflow_id})
        
        for row in result:
            status = "✓" if row[3] else "✗"
            print(f"  [{status}] {row[0]:3d}. {row[1]:30s} (排序: {row[2]})")
    
    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
