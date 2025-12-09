"""
更新业务导向调整步骤，使用新的带明细记录的 SQL
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# 读取新的 SQL 文件
sql_file_path = 'backend/standard_workflow_templates/step3a_orientation_adjustment_with_details.sql'
with open(sql_file_path, 'r', encoding='utf-8') as f:
    new_sql_content = f.read()

print(f"读取 SQL 文件: {sql_file_path}")
print(f"SQL 长度: {len(new_sql_content)} 字符")

# 更新数据库中的步骤
update_query = text("""
    UPDATE calculation_steps
    SET 
        code_content = :new_sql,
        description = '业务导向调整（含明细记录）',
        updated_at = NOW()
    WHERE name LIKE '%业务导向调整%'
       OR name LIKE '%orientation%adjustment%'
       OR code_content LIKE '%step3a_orientation_adjustment%'
    RETURNING id, workflow_id, name, sort_order;
""")

try:
    with engine.connect() as conn:
        # 执行更新
        result = conn.execute(update_query, {'new_sql': new_sql_content})
        conn.commit()
        
        # 获取更新的记录
        updated_rows = result.fetchall()
        
        if updated_rows:
            print(f"\n✓ 成功更新 {len(updated_rows)} 个步骤:")
            for row in updated_rows:
                print(f"  - ID: {row[0]}, Workflow: {row[1]}, Name: {row[2]}, Order: {row[3]}")
        else:
            print("\n⚠ 未找到需要更新的步骤")
            print("\n正在查找所有包含 'step3' 的步骤...")
            
            # 查找相关步骤
            search_query = text("""
                SELECT id, workflow_id, name, sort_order, 
                       LEFT(code_content, 100) as code_preview
                FROM calculation_steps
                WHERE name LIKE '%step3%'
                   OR name LIKE '%导向%'
                ORDER BY workflow_id, sort_order;
            """)
            
            search_result = conn.execute(search_query)
            steps = search_result.fetchall()
            
            if steps:
                print(f"\n找到 {len(steps)} 个相关步骤:")
                for step in steps:
                    print(f"  - ID: {step[0]}, Workflow: {step[1]}, Name: {step[2]}, Order: {step[3]}")
                    print(f"    代码预览: {step[4]}...")
            else:
                print("  未找到任何相关步骤")
                
except Exception as e:
    print(f"\n✗ 更新失败: {e}")
    import traceback
    traceback.print_exc()

print("\n完成!")
