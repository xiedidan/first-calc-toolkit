"""
修复 dimension_item_mappings 表中的重复记录
"""
import os
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    print("=" * 80)
    print("1. 检查重复映射的数量")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT COUNT(*) as total_duplicates
        FROM (
            SELECT dimension_code, item_code, hospital_id
            FROM dimension_item_mappings
            GROUP BY dimension_code, item_code, hospital_id
            HAVING COUNT(*) > 1
        ) t
    """))
    row = result.fetchone()
    print(f"  发现 {row.total_duplicates} 组重复的映射")
    
    print("\n" + "=" * 80)
    print("2. 检查重复映射的详细信息")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT dimension_code, item_code, hospital_id, COUNT(*) as cnt
        FROM dimension_item_mappings
        GROUP BY dimension_code, item_code, hospital_id
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
        LIMIT 20
    """))
    for row in result:
        print(f"  {row.dimension_code}, {row.item_code}, hospital={row.hospital_id}: {row.cnt} 条")
    
    print("\n" + "=" * 80)
    print("3. 删除重复记录（保留一条）")
    print("=" * 80)
    
    # 使用 ctid 删除重复记录
    result = conn.execute(text("""
        DELETE FROM dimension_item_mappings
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM dimension_item_mappings
            GROUP BY dimension_code, item_code, hospital_id
        )
    """))
    print(f"  删除了 {result.rowcount} 条重复记录")
    
    print("\n" + "=" * 80)
    print("4. 验证删除结果")
    print("=" * 80)
    result = conn.execute(text("""
        SELECT COUNT(*) as total_duplicates
        FROM (
            SELECT dimension_code, item_code, hospital_id
            FROM dimension_item_mappings
            GROUP BY dimension_code, item_code, hospital_id
            HAVING COUNT(*) > 1
        ) t
    """))
    row = result.fetchone()
    print(f"  剩余重复映射: {row.total_duplicates} 组")
    
    print("\n" + "=" * 80)
    print("5. 添加唯一约束防止未来重复")
    print("=" * 80)
    try:
        conn.execute(text("""
            ALTER TABLE dimension_item_mappings 
            ADD CONSTRAINT uq_dimension_item_mapping 
            UNIQUE (dimension_code, item_code, hospital_id)
        """))
        print("  已添加唯一约束")
    except Exception as e:
        if "already exists" in str(e):
            print("  唯一约束已存在")
        else:
            print(f"  添加约束失败: {e}")
