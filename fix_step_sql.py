"""
修复被错误覆盖的步骤SQL
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取正确的SQL模板
with open('backend/standard_workflow_templates/step3c_workload_dimensions.sql', 'r', encoding='utf-8') as f:
    workload_sql = f.read()

print(f"工作量维度统计 SQL 长度: {len(workload_sql)}")

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    # 1. 恢复"工作量维度统计"步骤
    print("\n1. 恢复'工作量维度统计'步骤...")
    result = conn.execute(text("""
        UPDATE calculation_steps 
        SET code_content = :sql
        WHERE name = '工作量维度统计'
    """), {"sql": workload_sql})
    print(f"   更新了 {result.rowcount} 个步骤")
    
    # 2. 检查"成本维度计算"和"成本维度计算-材料费和折旧费"的原始SQL
    # 这些步骤可能有各自的SQL，需要从其他流程中恢复
    print("\n2. 检查成本维度计算步骤...")
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cw.name as workflow_name, LENGTH(cs.code_content) as sql_len
        FROM calculation_steps cs
        JOIN calculation_workflows cw ON cs.workflow_id = cw.id
        WHERE cs.name LIKE '%成本维度%'
        ORDER BY cw.name, cs.sort_order
    """))
    for row in result:
        print(f"   ID={row.id}, 名称={row.name}, 流程={row.workflow_name}, SQL长度={row.sql_len}")
    
    # 3. 查找成本维度计算的原始SQL（从其他流程中）
    print("\n3. 查找成本维度计算的原始SQL...")
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cw.name as workflow_name, 
               SUBSTRING(cs.code_content, 1, 200) as sql_preview
        FROM calculation_steps cs
        JOIN calculation_workflows cw ON cs.workflow_id = cw.id
        WHERE cs.name LIKE '%成本%'
          AND cs.code_content NOT LIKE '%维度目录统计%'
        ORDER BY cw.name, cs.sort_order
        LIMIT 5
    """))
    rows = list(result)
    if rows:
        print("   找到未被覆盖的成本相关步骤:")
        for row in rows:
            print(f"   ID={row.id}, 名称={row.name}, 流程={row.workflow_name}")
            print(f"   预览: {row.sql_preview[:100]}...")
    else:
        print("   没有找到未被覆盖的成本相关步骤")
    
    # 4. 检查流程30的所有步骤
    print("\n4. 流程30的所有步骤:")
    result = conn.execute(text("""
        SELECT cs.id, cs.name, cs.sort_order, 
               SUBSTRING(cs.code_content, 1, 100) as sql_preview
        FROM calculation_steps cs
        WHERE cs.workflow_id = 30
        ORDER BY cs.sort_order
    """))
    for row in result:
        print(f"   {row.sort_order}: {row.name} (ID={row.id})")
        print(f"      {row.sql_preview}...")
