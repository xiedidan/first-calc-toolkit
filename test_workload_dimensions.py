#!/usr/bin/env python3
"""
测试工作量维度统计步骤
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

def test_workload_statistics_data():
    """测试workload_statistics表中的数据"""
    print("\n📊 检查workload_statistics表数据...")
    
    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'workload_statistics'
            );
        """))
        exists = result.scalar()
        
        if not exists:
            print("❌ workload_statistics表不存在")
            return False
        
        # 查询数据
        result = conn.execute(text("""
            SELECT 
                stat_type,
                COUNT(*) as count,
                SUM(stat_value) as total_value
            FROM workload_statistics
            WHERE stat_month = '2025-10'
            GROUP BY stat_type
            ORDER BY stat_type;
        """))
        
        rows = result.fetchall()
        if not rows:
            print("⚠️  workload_statistics表中没有2025-10的数据")
            return False
        
        print("\n统计类型分布:")
        for row in rows:
            print(f"  {row[0]}: {row[1]}条记录, 总值={row[2]}")
        
        return True

def test_model_nodes():
    """测试模型节点中是否有对应的维度"""
    print("\n🔍 检查模型节点中的相关维度...")
    
    with engine.connect() as conn:
        # 查询相关维度
        result = conn.execute(text("""
            SELECT 
                id,
                code,
                name,
                node_type
            FROM model_nodes
            WHERE node_type = 'dimension'
              AND (
                code LIKE '%nursing_bed_days%' 
                OR code LIKE '%admission_discharge_transfer%'
                OR code LIKE '%surgery_management%'
                OR code LIKE '%operating_room_nursing%'
                OR code LIKE '%护理床日%'
                OR code LIKE '%出入转院%'
                OR code LIKE '%手术管理%'
                OR code LIKE '%手术室护理%'
              )
            ORDER BY code;
        """))
        
        rows = result.fetchall()
        if not rows:
            print("⚠️  模型节点中没有找到相关维度")
            print("提示: 需要在模型中创建以下维度:")
            print("  - 护理床日 (code包含 nursing_bed_days)")
            print("  - 出入转院 (code包含 admission_discharge_transfer)")
            print("  - 手术管理 (code包含 surgery_management)")
            print("  - 手术室护理 (code包含 operating_room_nursing)")
            return False
        
        print("\n找到的相关维度:")
        for row in rows:
            print(f"  ID={row[0]}, code={row[1]}, name={row[2]}")
        
        return True

def test_sql_syntax():
    """测试SQL语法是否正确"""
    print("\n✅ 测试SQL语法...")
    
    # 读取SQL文件
    sql_file = 'backend/standard_workflow_templates/step3c_workload_dimensions.sql'
    if not os.path.exists(sql_file):
        print(f"❌ SQL文件不存在: {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 替换占位符
    sql_content = sql_content.replace('{task_id}', 'test-task-001')
    sql_content = sql_content.replace('{current_year_month}', '2025-10')
    sql_content = sql_content.replace('{hospital_id}', '1')
    sql_content = sql_content.replace('{version_id}', '1')
    
    # 分割SQL语句
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"找到 {len(statements)} 条SQL语句")
    
    with engine.connect() as conn:
        try:
            # 测试每条语句
            for i, stmt in enumerate(statements, 1):
                if 'INSERT INTO' in stmt:
                    print(f"  测试INSERT语句 {i}...")
                    # 使用EXPLAIN测试语法
                    conn.execute(text(f"EXPLAIN {stmt}"))
                elif 'SELECT' in stmt:
                    print(f"  测试SELECT语句 {i}...")
                    conn.execute(text(stmt))
            
            print("✅ SQL语法检查通过")
            return True
            
        except Exception as e:
            print(f"❌ SQL语法错误: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("工作量维度统计步骤测试")
    print("=" * 60)
    
    # 测试数据
    if not test_workload_statistics_data():
        print("\n⚠️  建议先运行测试数据生成脚本:")
        print("  cd backend/standard_workflow_templates")
        print("  python generate_test_data.py --period 2025-10")
    
    # 测试模型节点
    test_model_nodes()
    
    # 测试SQL语法
    test_sql_syntax()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
