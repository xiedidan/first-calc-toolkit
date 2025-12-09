"""直接更新Step 5的SQL"""
import psycopg2

# 数据库连接信息
DB_CONFIG = {
    'host': '47.108.227.254',
    'port': 50016,
    'user': 'root',
    'password': 'root',
    'database': 'hospital_value'
}

# 要更新的步骤ID
STEP_IDS = [67, 75, 80, 85]

# 读取新的SQL
with open('backend/standard_workflow_templates/step5_value_aggregation.sql', 'r', encoding='utf-8') as f:
    new_sql = f.read()

print("连接数据库...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

try:
    # 查询步骤信息
    cur.execute("""
        SELECT cs.id, w.name, cs.name
        FROM calculation_steps cs
        INNER JOIN calculation_workflows w ON cs.workflow_id = w.id
        WHERE cs.id = ANY(%s)
        ORDER BY cs.id
    """, (STEP_IDS,))
    
    steps = cur.fetchall()
    
    print(f"\n将更新 {len(steps)} 个步骤:")
    for step_id, workflow_name, step_name in steps:
        print(f"  - ID {step_id}: {workflow_name} / {step_name}")
    
    # 更新每个步骤
    for step_id, workflow_name, step_name in steps:
        cur.execute("""
            UPDATE calculation_steps
            SET code_content = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (new_sql, step_id))
        print(f"✓ 已更新步骤 {step_id}")
    
    conn.commit()
    print(f"\n成功更新 {len(steps)} 个步骤")
    
except Exception as e:
    conn.rollback()
    print(f"\n错误: {e}")
    raise
finally:
    cur.close()
    conn.close()

print("\n修复内容:")
print("1. dimension_results: 使用cr.weight（调整后）")
print("2. 非叶子节点: original_weight = NULL")
