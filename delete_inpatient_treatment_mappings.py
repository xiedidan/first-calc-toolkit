"""
删除医生-住院-治疗下的甲、乙、丙维度的所有dimension_item_mappings
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

engine = create_engine(DATABASE_URL)

# 要删除的维度code（医生-住院-治疗下的甲、乙、丙）
dimension_codes_to_delete = [
    'dim-doc-in-tr-1',  # 甲级治疗
    'dim-doc-in-tr-2',  # 乙级治疗
    'dim-doc-in-tr-3',  # 丙级治疗
]

def main():
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            total_deleted = 0
            
            for code in dimension_codes_to_delete:
                # 验证维度存在
                node_check = conn.execute(
                    text("SELECT id, name FROM model_nodes WHERE code = :code AND version_id = 1"),
                    {"code": code}
                ).fetchone()
                
                if not node_check:
                    print(f"警告: 维度 {code} 不存在")
                    continue
                
                print(f"\n删除维度: {node_check[1]} ({code})")
                
                # 查询需要删除的记录数
                count_result = conn.execute(
                    text("""
                        SELECT COUNT(*) 
                        FROM dimension_item_mappings 
                        WHERE dimension_code = :code
                    """),
                    {"code": code}
                ).fetchone()
                
                count = count_result[0]
                print(f"  找到 {count} 条记录")
                
                if count == 0:
                    continue
                
                # 删除记录
                result = conn.execute(
                    text("""
                        DELETE FROM dimension_item_mappings 
                        WHERE dimension_code = :code
                    """),
                    {"code": code}
                )
                
                deleted = result.rowcount
                total_deleted += deleted
                print(f"  成功删除 {deleted} 条记录")
            
            # 提交事务
            trans.commit()
            print(f"\n✓ 删除完成！共删除 {total_deleted} 条记录")
            
        except Exception as e:
            # 回滚事务
            trans.rollback()
            print(f"\n✗ 删除失败: {e}")
            raise

if __name__ == "__main__":
    main()
