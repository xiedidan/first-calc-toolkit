"""
将护理维度的dimension_item_mappings进行迁移：
- dim-nur-ind -> dim-nur-base (基础护理)
- dim-nur-extra -> dim-nur-tr-c (丙级护理治疗)
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

# 源维度code -> 目标维度code
# 注意：dim-nur-ind 和 dim-nur-extra 在model_nodes表中不存在
# 但在dimension_item_mappings表中有数据，可能是历史遗留数据
mappings = {
    'dim-nur-ind': 'dim-nur-base',      # 基础护理
    'dim-nur-extra': 'dim-nur-tr-c',    # 丙级护理治疗
}

def main():
    with engine.connect() as conn:
        # 开始事务
        trans = conn.begin()
        
        try:
            total_updated = 0
            
            for source_code, target_code in mappings.items():
                # 验证目标维度存在（源维度可能不在model_nodes中，是历史遗留数据）
                target_check = conn.execute(
                    text("SELECT id, name FROM model_nodes WHERE code = :code"),
                    {"code": target_code}
                ).fetchone()
                
                if not target_check:
                    print(f"警告: 目标维度 {target_code} 不存在")
                    continue
                
                print(f"\n迁移: {source_code} -> {target_check[1]} ({target_code})")
                
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
