"""
比较工作流 29 和 30 的步骤内容，找出差异
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def compare_workflows():
    with engine.connect() as conn:
        print("=" * 80)
        print("比较工作流 29 和 30 的步骤")
        print("=" * 80)
        
        # 获取两个工作流的步骤
        result = conn.execute(text("""
            SELECT 
                ws.workflow_id,
                cw.name as workflow_name,
                ws.id as step_id,
                ws.name as step_name,
                ws.sort_order,
                LENGTH(ws.code_content) as sql_length,
                LEFT(ws.code_content, 200) as sql_preview
            FROM calculation_steps ws
            JOIN calculation_workflows cw ON ws.workflow_id = cw.id
            WHERE ws.workflow_id IN (29, 30)
            ORDER BY ws.workflow_id, ws.sort_order
        """))
        
        workflows = {}
        for row in result:
            wf_id = row.workflow_id
            if wf_id not in workflows:
                workflows[wf_id] = {'name': row.workflow_name, 'steps': []}
            workflows[wf_id]['steps'].append({
                'step_id': row.step_id,
                'name': row.step_name,
                'sort_order': row.sort_order,
                'sql_length': row.sql_length,
                'sql_preview': row.sql_preview
            })
        
        for wf_id, wf_data in workflows.items():
            print(f"\n工作流 {wf_id}: {wf_data['name']}")
            print("-" * 60)
            for step in wf_data['steps']:
                print(f"  步骤 {step['sort_order']}: {step['name']} (ID: {step['step_id']}, SQL长度: {step['sql_length']})")
                # 显示SQL预览的前100个字符
                preview = step['sql_preview'].replace('\n', ' ')[:100] if step['sql_preview'] else 'NULL'
                print(f"    预览: {preview}...")
        
        # 比较相同 sort_order 的步骤
        print("\n" + "=" * 80)
        print("比较相同排序位置的步骤差异")
        print("=" * 80)
        
        if 29 in workflows and 30 in workflows:
            steps_29 = {s['sort_order']: s for s in workflows[29]['steps']}
            steps_30 = {s['sort_order']: s for s in workflows[30]['steps']}
            
            all_orders = sorted(set(steps_29.keys()) | set(steps_30.keys()))
            
            for order in all_orders:
                s29 = steps_29.get(order)
                s30 = steps_30.get(order)
                
                if s29 and s30:
                    if s29['sql_length'] != s30['sql_length']:
                        print(f"\n排序 {order}: SQL长度不同!")
                        print(f"  工作流29: {s29['name']} - {s29['sql_length']} 字符")
                        print(f"  工作流30: {s30['name']} - {s30['sql_length']} 字符")
                elif s29:
                    print(f"\n排序 {order}: 只在工作流29中存在 - {s29['name']}")
                elif s30:
                    print(f"\n排序 {order}: 只在工作流30中存在 - {s30['name']}")

if __name__ == '__main__':
    compare_workflows()
