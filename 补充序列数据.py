import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

task_id = '124694a7-3f17-4ff3-831e-5e7efb6febe2'
version_id = 1

print(f"=== 为任务 {task_id} 补充序列数据 ===\n")

# 读取 Step3 SQL
with open('backend/standard_workflow_templates/step3_value_aggregation.sql', 'r', encoding='utf-8') as f:
    sql_template = f.read()

# 替换占位符
sql = sql_template.replace('{task_id}', task_id).replace('{version_id}', str(version_id))

try:
    # 执行 SQL
    print("执行 Step3 SQL...")
    result = db.execute(text(sql))
    
    # 获取插入的记录数
    count_result = result.fetchone()
    if count_result:
        inserted_count = count_result[0]
        print(f"✅ 成功插入 {inserted_count} 条序列数据")
    
    # 提交事务
    db.commit()
    print("✅ 事务已提交")
    
    # 验证结果
    print("\n=== 验证结果 ===")
    verify_result = db.execute(text(f"""
        SELECT node_type, COUNT(*) as count
        FROM calculation_results
        WHERE task_id = '{task_id}'
        GROUP BY node_type
    """))
    
    print("node_type | count")
    print("-" * 30)
    for row in verify_result.fetchall():
        print(f"{row[0]} | {row[1]}")
    
    # 查看序列数据示例
    print("\n=== 序列数据示例 ===")
    sample_result = db.execute(text(f"""
        SELECT node_id, department_id, node_name, value
        FROM calculation_results
        WHERE task_id = '{task_id}'
          AND node_type = 'sequence'
        ORDER BY department_id, node_id
        LIMIT 10
    """))
    
    print("node_id | dept_id | node_name | value")
    print("-" * 60)
    for row in sample_result.fetchall():
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    
    print("\n✅ 完成！现在可以查看报表了。")
    
except Exception as e:
    print(f"❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
