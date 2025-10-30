"""
显示序列名称 - 简单版本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接使用psycopg2，避免依赖问题
import psycopg2

# 数据库连接
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="hospital_performance",
    user="postgres",
    password="123456"
)

cur = conn.cursor()

print("=" * 80)
print("模型中的序列节点")
print("=" * 80)

# 查询序列节点
cur.execute("""
    SELECT id, name, code
    FROM model_nodes
    WHERE version_id = (SELECT id FROM model_versions WHERE is_active = true)
        AND node_type = 'sequence'
    ORDER BY sort_order
""")

sequences = cur.fetchall()
print(f"\n找到 {len(sequences)} 个序列:\n")

for seq_id, name, code in sequences:
    print(f"ID: {seq_id:3d} | 名称: {name:40s} | 编码: {code}")

print("\n" + "=" * 80)
print("最新任务的序列结果（科室ID=3）")
print("=" * 80)

# 查询最新任务的序列结果
cur.execute("""
    SELECT cr.node_id, cr.node_name, cr.value
    FROM calculation_results cr
    WHERE cr.task_id = (
        SELECT task_id 
        FROM calculation_tasks 
        WHERE status = 'completed' 
        ORDER BY completed_at DESC 
        LIMIT 1
    )
        AND cr.department_id = 3
        AND cr.node_type = 'sequence'
    ORDER BY cr.node_id
""")

results = cur.fetchall()
print(f"\n找到 {len(results)} 条序列结果:\n")

for node_id, name, value in results:
    # 判断序列类型
    seq_type = "未识别"
    if "医生" in name or "医疗" in name or "医师" in name:
        seq_type = "医生序列"
    elif "护理" in name or "护士" in name:
        seq_type = "护理序列"
    elif "医技" in name or "技师" in name:
        seq_type = "医技序列"
    
    print(f"ID: {node_id:3d} | 名称: {name:40s} | 价值: {value:12,.2f} | 类型: {seq_type}")

print("\n" + "=" * 80)

cur.close()
conn.close()
