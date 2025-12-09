"""
将医生-门诊-治疗下的甲、乙、丙维度的dimension_item_mappings
迁移到模型版本12的治疗护理甲、乙、丙维度
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

# 源维度code（模型版本1）
source_mappings = {
    'dim-doc-out-tr-1': 'dim-nur-tr-a',  # 甲级治疗 -> 甲级护理治疗
    'dim-doc-out-tr-2': 'dim-nur-tr-b',  # 乙级治疗 -> 乙级护理治疗
    'dim-doc-out-tr-3': 'dim-nur-tr-c',  # 丙级治疗 -> 丙级护理治疗
}

def main():
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            total_updated = 0
            
            for source_code, target_code in source_mappings.items():
                # 验证源维度存在
                source_check = conn.execute(
                    text("SELECT id, name FROM model_nodes WHERE code = :code AND version_id = 1"),
                    {"code": source_code}
                ).fetchone()
                
                if not source_check:
                    print(f"警告: 源维度 {source_code} 不存在")
                    continue
                
                # 验证目标维度存在
                target_check = conn.execute(
                    text("SELECT id, name FROM model_nodes WHERE code = :code AND version_id = 12"),
                    {"code": target_code}
                ).fetchone()
                
                if not target_check:
                    print(f"警告: 目标维度 {target_code} 不存在")
                    continue
                
                print(f"\n迁移: {source_check[1]} ({source_code}) -> {target_check[1]} ({target_code})")
                
                # 查询需要迁移的记录数
                count_result = conn.execute(
                    text("""
                        SELECT COUNT(*) 
                        FROM dimension_item_mappings 
                        WHERE dimension_code = :source_code
                    """),
                    {"source_code": source_code}
                ).fetchone()
                
                count = count_result[0]
                print(f"  找到 {count} 条记录")
                
                if count == 0:
                    continue
                
                # 更新dimension_code
                result = conn.execute(
                    text("""
                        UPDATE dimension_item_mappings 
                        SET dimension_code = :target_code
                        WHERE dimension_code = :source_code
                    """),
                    {
                        "source_code": source_code,
                        "target_code": target_code
                    }
                )
                
                updated = result.rowcount
                total_updated += updated
                print(f"  成功更新 {updated} 条记录")
            
            # 提交事务
            trans.commit()
            print(f"\n✓ 迁移完成！共更新 {total_updated} 条记录")
            
        except Exception as e:
            # 回滚事务
            trans.rollback()
            print(f"\n✗ 迁移失败: {e}")
            raise

if __name__ == "__main__":
    main()
