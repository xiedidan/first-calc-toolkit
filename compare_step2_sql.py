"""
比较数据库中的步骤2 SQL与模板文件
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def compare_sql():
    # 读取模板文件
    with open('backend/standard_workflow_templates/step2_dimension_catalog.sql', 'r', encoding='utf-8') as f:
        template_sql = f.read()
    
    print(f"模板文件长度: {len(template_sql)} 字符")
    
    with engine.connect() as conn:
        # 获取工作流30的步骤2
        result = conn.execute(text("""
            SELECT 
                ws.id as step_id,
                ws.name as step_name,
                ws.code_content
            FROM calculation_steps ws
            WHERE ws.workflow_id = 30
            AND ws.sort_order = 2.00
        """))
        
        row = result.fetchone()
        if row:
            db_sql = row.code_content
            print(f"数据库SQL长度: {len(db_sql)} 字符")
            
            if template_sql == db_sql:
                print("\n✓ SQL内容完全一致")
            else:
                print("\n✗ SQL内容不一致!")
                
                # 找出差异位置
                min_len = min(len(template_sql), len(db_sql))
                diff_pos = None
                for i in range(min_len):
                    if template_sql[i] != db_sql[i]:
                        diff_pos = i
                        break
                
                if diff_pos:
                    print(f"\n第一个差异位置: {diff_pos}")
                    print(f"模板: ...{template_sql[max(0,diff_pos-50):diff_pos+50]}...")
                    print(f"数据库: ...{db_sql[max(0,diff_pos-50):diff_pos+50]}...")
                elif len(template_sql) != len(db_sql):
                    print(f"\n长度不同: 模板={len(template_sql)}, 数据库={len(db_sql)}")
                    if len(template_sql) > len(db_sql):
                        print(f"模板多出的内容: {template_sql[len(db_sql):][:200]}...")
                    else:
                        print(f"数据库多出的内容: {db_sql[len(template_sql):][:200]}...")

if __name__ == '__main__':
    compare_sql()
