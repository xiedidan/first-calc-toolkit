"""
将旧的 ai_configs 和 ai_prompt_configs 表数据迁移到新的 ai_interfaces 和 ai_prompt_modules 表
用于已部署环境的数据迁移

使用方法:
    python migrate_ai_configs_to_interfaces.py
"""
import os
import sys

# 添加backend目录到路径
sys.path.insert(0, 'backend')

from sqlalchemy import text
from app.database import SessionLocal


# 旧分类到新模块代码的映射
CATEGORY_TO_MODULE_CODE = {
    "classification": "classification",
    "report_issues": "report_issues",
    "report_plans": "report_plans",
}


def migrate_ai_configs():
    """执行AI配置迁移（ai_configs -> ai_interfaces）"""
    db = SessionLocal()
    
    try:
        # 1. 检查 ai_configs 表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_configs'
            )
        """))
        if not result.scalar():
            print("ai_configs 表不存在，跳过AI接口迁移")
            return db
        
        # 2. 检查 ai_interfaces 表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_interfaces'
            )
        """))
        if not result.scalar():
            print("ai_interfaces 表不存在，请先执行数据库迁移")
            return db
        
        # 3. 查看 ai_configs 中的数据
        result = db.execute(text("SELECT COUNT(*) FROM ai_configs"))
        old_count = result.scalar()
        print(f"ai_configs 表中有 {old_count} 条记录")
        
        if old_count == 0:
            print("ai_configs 表为空，无需迁移AI接口配置")
            return db
        
        # 4. 查看 ai_interfaces 中已有的数据
        result = db.execute(text("SELECT COUNT(*) FROM ai_interfaces"))
        new_count = result.scalar()
        print(f"ai_interfaces 表中已有 {new_count} 条记录")
        
        # 5. 执行迁移 - 按 api_endpoint + model_name 组合判断是否已存在
        # 这样可以保留不同的配置（如代理地址、不同模型等）
        result = db.execute(text("""
            INSERT INTO ai_interfaces (
                hospital_id, 
                name, 
                api_endpoint, 
                model_name, 
                api_key_encrypted, 
                call_delay, 
                daily_limit, 
                is_active, 
                created_at, 
                updated_at
            )
            SELECT 
                c.hospital_id,
                COALESCE(c.model_name, 'deepseek-chat') || '（迁移）' as name,
                c.api_endpoint,
                COALESCE(c.model_name, 'deepseek-chat') as model_name,
                c.api_key_encrypted,
                c.call_delay,
                c.daily_limit,
                true as is_active,
                c.created_at,
                c.updated_at
            FROM ai_configs c
            WHERE NOT EXISTS (
                SELECT 1 FROM ai_interfaces i 
                WHERE i.hospital_id = c.hospital_id 
                AND i.api_endpoint = c.api_endpoint 
                AND i.model_name = COALESCE(c.model_name, 'deepseek-chat')
            )
            RETURNING id
        """))
        
        migrated_ids = result.fetchall()
        migrated_count = len(migrated_ids)
        print(f"成功迁移 {migrated_count} 条AI接口配置记录")
        
        db.commit()
        return db
        
    except Exception as e:
        db.rollback()
        print(f"AI接口迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return db


def migrate_prompt_configs(db):
    """执行提示词配置迁移（ai_prompt_configs -> ai_prompt_modules）"""
    
    try:
        # 1. 检查 ai_prompt_configs 表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_prompt_configs'
            )
        """))
        if not result.scalar():
            print("\nai_prompt_configs 表不存在，跳过提示词迁移")
            return
        
        # 2. 检查 ai_prompt_modules 表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ai_prompt_modules'
            )
        """))
        if not result.scalar():
            print("\nai_prompt_modules 表不存在，请先执行数据库迁移")
            return
        
        # 3. 查看 ai_prompt_configs 中的数据
        result = db.execute(text("SELECT COUNT(*) FROM ai_prompt_configs"))
        old_count = result.scalar()
        print(f"\nai_prompt_configs 表中有 {old_count} 条记录")
        
        if old_count == 0:
            print("ai_prompt_configs 表为空，无需迁移提示词配置")
            return
        
        # 4. 获取所有旧的提示词配置
        result = db.execute(text("""
            SELECT id, hospital_id, category, system_prompt, user_prompt, created_at, updated_at
            FROM ai_prompt_configs
        """))
        old_configs = result.fetchall()
        
        print(f"找到 {len(old_configs)} 条提示词配置需要迁移")
        
        # 5. 逐条迁移
        migrated_count = 0
        skipped_count = 0
        
        for config in old_configs:
            config_id, hospital_id, category, system_prompt, user_prompt, created_at, updated_at = config
            
            # 映射分类到模块代码
            module_code = CATEGORY_TO_MODULE_CODE.get(category)
            if not module_code:
                print(f"  跳过未知分类: {category}")
                skipped_count += 1
                continue
            
            # 检查目标模块是否已存在
            result = db.execute(text("""
                SELECT id, system_prompt, user_prompt 
                FROM ai_prompt_modules 
                WHERE hospital_id = :hospital_id AND module_code = :module_code
            """), {"hospital_id": hospital_id, "module_code": module_code})
            
            existing = result.fetchone()
            
            if existing:
                existing_id, existing_system, existing_user = existing
                
                # 检查是否需要更新（旧配置有自定义内容）
                if system_prompt or user_prompt:
                    # 更新现有模块的提示词
                    db.execute(text("""
                        UPDATE ai_prompt_modules 
                        SET system_prompt = COALESCE(:system_prompt, system_prompt),
                            user_prompt = COALESCE(:user_prompt, user_prompt),
                            updated_at = :updated_at
                        WHERE id = :id
                    """), {
                        "id": existing_id,
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "updated_at": updated_at,
                    })
                    print(f"  更新模块 {module_code} (医院ID: {hospital_id})")
                    migrated_count += 1
                else:
                    print(f"  跳过空配置: {category} (医院ID: {hospital_id})")
                    skipped_count += 1
            else:
                # 模块不存在，需要先初始化
                print(f"  模块 {module_code} 不存在 (医院ID: {hospital_id})，将在初始化时创建")
                skipped_count += 1
        
        db.commit()
        print(f"\n提示词迁移完成: 更新 {migrated_count} 条，跳过 {skipped_count} 条")
        
    except Exception as e:
        db.rollback()
        print(f"提示词迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()


def initialize_modules_and_link_interfaces(db):
    """初始化提示词模块并关联AI接口"""
    
    try:
        print("\n初始化提示词模块...")
        from app.services.ai_prompt_module_service import AIPromptModuleService
        
        result = db.execute(text('SELECT id FROM hospitals'))
        hospital_ids = [row[0] for row in result.fetchall()]
        
        for hospital_id in hospital_ids:
            AIPromptModuleService.ensure_modules_initialized(db, hospital_id)
            print(f"  已初始化医院 {hospital_id} 的提示词模块")
        
        # 为提示词模块关联AI接口
        result = db.execute(text("""
            UPDATE ai_prompt_modules m
            SET ai_interface_id = (
                SELECT id FROM ai_interfaces i 
                WHERE i.hospital_id = m.hospital_id 
                ORDER BY i.created_at ASC 
                LIMIT 1
            )
            WHERE m.ai_interface_id IS NULL
            AND EXISTS (
                SELECT 1 FROM ai_interfaces i 
                WHERE i.hospital_id = m.hospital_id
            )
        """))
        
        updated_modules = result.rowcount
        print(f"已为 {updated_modules} 个提示词模块关联AI接口")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"初始化模块失败: {str(e)}")
        import traceback
        traceback.print_exc()


def show_migration_status(db):
    """显示迁移后的状态"""
    
    try:
        # 显示 ai_interfaces 状态
        result = db.execute(text("""
            SELECT 
                i.id,
                i.hospital_id,
                h.name as hospital_name,
                i.name as interface_name,
                i.api_endpoint,
                i.model_name,
                i.is_active
            FROM ai_interfaces i
            LEFT JOIN hospitals h ON i.hospital_id = h.id
            ORDER BY i.hospital_id
        """))
        
        rows = result.fetchall()
        print("\n当前 ai_interfaces 表内容:")
        print("-" * 100)
        for row in rows:
            endpoint = row[4][:50] + "..." if row[4] and len(row[4]) > 50 else row[4]
            print(f"ID: {row[0]}, 医院ID: {row[1]}, 医院: {row[2]}, "
                  f"接口名: {row[3]}, 端点: {endpoint}, "
                  f"模型: {row[5]}, 启用: {row[6]}")
        
        # 显示 ai_prompt_modules 状态
        result = db.execute(text("""
            SELECT 
                m.id,
                m.hospital_id,
                h.name as hospital_name,
                m.module_code,
                m.module_name,
                m.ai_interface_id,
                i.name as interface_name,
                LENGTH(m.system_prompt) as system_len,
                LENGTH(m.user_prompt) as user_len
            FROM ai_prompt_modules m
            LEFT JOIN hospitals h ON m.hospital_id = h.id
            LEFT JOIN ai_interfaces i ON m.ai_interface_id = i.id
            ORDER BY m.hospital_id, m.module_code
        """))
        
        rows = result.fetchall()
        print("\n当前 ai_prompt_modules 表内容:")
        print("-" * 120)
        for row in rows:
            print(f"ID: {row[0]}, 医院ID: {row[1]}, 医院: {row[2]}, "
                  f"模块: {row[3]}, 名称: {row[4]}, "
                  f"AI接口ID: {row[5]}, 接口名: {row[6]}, "
                  f"系统提示词长度: {row[7]}, 用户提示词长度: {row[8]}")
        
    except Exception as e:
        print(f"显示状态失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("=" * 60)
    print("AI配置迁移工具")
    print("=" * 60)
    
    # 1. 迁移 ai_configs -> ai_interfaces
    print("\n[步骤1] 迁移AI接口配置...")
    db = migrate_ai_configs()
    
    # 2. 初始化提示词模块并关联AI接口
    print("\n[步骤2] 初始化提示词模块...")
    initialize_modules_and_link_interfaces(db)
    
    # 3. 迁移 ai_prompt_configs -> ai_prompt_modules
    print("\n[步骤3] 迁移提示词配置...")
    migrate_prompt_configs(db)
    
    # 4. 显示迁移后的状态
    print("\n[步骤4] 显示迁移结果...")
    show_migration_status(db)
    
    db.close()
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
