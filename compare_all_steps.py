"""
比较工作流29和30的所有步骤SQL
"""
import os
import sys
sys.path.insert(0, 'backend')
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

def compare_all():
    with engine.connect() as conn:
        # 获取工作流29和30的所有步骤
        result = conn.execute(text("""
            SELECT 
                ws.workflow_id,
                ws.id as step_id,
                ws.name as step_name,
                ws.sort_order,
                ws.code_content
            FROM calculation_steps ws
            WHERE ws.workflow_id IN (29, 30)
            ORDER BY ws.workflow_id, ws.sort_order
        """))
        
        workflows = {}
        for row in result:
            wf_id = row.workflow_id
            if wf_id not in workflows:
                workflows[wf_id] = {}
            workflows[wf_id][row.sort_order] = {
                'step_id': row.step_id,
                'name': row.step_name,
                'sql': row.code_content
            }
        
        print("=" * 80)
        print("比较工作流29和30的所有步骤")
        print("=" * 80)
        
        if 29 in workflows and 30 in workflows:
            all_orders = sorted(set(workflows[29].keys()) | set(workflows[30].keys()))
            
            for order in all_orders:
                s29 = workflows[29].get(order)
                s30 = workflows[30].get(order)
                
                if s29 and s30:
                    if s29['sql'] == s30['sql']:
                        print(f"\n排序 {order}: {s29['name']} - ✓ SQL一致 ({len(s29['sql'])} 字符)")
                    else:
                        print(f"\n排序 {order}: {s29['name']} - ✗ SQL不一致!")
                        print(f"  工作流29: {len(s29['sql'])} 字符")
                        print(f"  工作流30: {len(s30['sql'])} 字符")
                        
                        # 显示差异
                        sql29 = s29['sql']
                        sql30 = s30['sql']
                        min_len = min(len(sql29), len(sql30))
                        diff_pos = None
                        for i in range(min_len):
                            if sql29[i] != sql30[i]:
                                diff_pos = i
                                break
                        
                        if diff_pos:
                            print(f"  第一个差异位置: {diff_pos}")
                            print(f"  工作流29: ...{sql29[max(0,diff_pos-30):diff_pos+30]}...")
                            print(f"  工作流30: ...{sql30[max(0,diff_pos-30):diff_pos+30]}...")
                elif s29:
                    print(f"\n排序 {order}: 只在工作流29中存在 - {s29['name']}")
                elif s30:
                    print(f"\n排序 {order}: 只在工作流30中存在 - {s30['name']}")

if __name__ == '__main__':
    compare_all()
