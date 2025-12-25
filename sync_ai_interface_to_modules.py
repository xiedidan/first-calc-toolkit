"""
同步AI接口配置到提示词模块

问题：AI接口管理中已配置接口，但提示词模块未关联该接口
解决：自动将第一个启用的AI接口关联到所有未配置接口的提示词模块

注意：这是一次性修复脚本，新版本代码已在创建AI接口时自动关联
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')

# 添加backend到路径
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("错误：未找到 DATABASE_URL 环境变量")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def main():
    session = Session()
    try:
        # 1. 查看当前状态
        print("=== 当前配置状态 ===")
        
        # 查看所有AI接口
        interfaces = session.execute(text("""
            SELECT id, hospital_id, name, model_name, is_active 
            FROM ai_interfaces 
            ORDER BY hospital_id, id
        """)).fetchall()
        
        print("\nAI接口列表:")
        for i in interfaces:
            status = "启用" if i.is_active else "禁用"
            print(f"  ID: {i.id}, 医院ID: {i.hospital_id}, 名称: {i.name}, 状态: {status}")
        
        # 查看未配置接口的提示词模块
        unconfigured = session.execute(text("""
            SELECT m.id, m.hospital_id, m.module_code, m.module_name
            FROM ai_prompt_modules m
            WHERE m.ai_interface_id IS NULL
            ORDER BY m.hospital_id, m.module_code
        """)).fetchall()
        
        print(f"\n未配置接口的提示词模块 ({len(unconfigured)} 个):")
        for m in unconfigured:
            print(f"  医院ID: {m.hospital_id}, {m.module_name} ({m.module_code})")
        
        if not unconfigured:
            print("\n所有模块已配置接口，无需同步")
            return
        
        # 2. 按医院分组，找出需要同步的配置
        print("\n=== 同步计划 ===")
        
        hospital_ids = set(m.hospital_id for m in unconfigured)
        sync_plan = []
        
        for hospital_id in hospital_ids:
            # 获取该医院的第一个启用的AI接口
            active_interface = session.execute(text("""
                SELECT id, name FROM ai_interfaces 
                WHERE hospital_id = :hospital_id AND is_active = true
                ORDER BY id LIMIT 1
            """), {"hospital_id": hospital_id}).fetchone()
            
            if not active_interface:
                print(f"  医院ID {hospital_id}: 没有启用的AI接口，跳过")
                continue
            
            # 获取该医院未配置接口的模块
            modules = [m for m in unconfigured if m.hospital_id == hospital_id]
            
            print(f"  医院ID {hospital_id}: 将使用接口 '{active_interface.name}' (ID: {active_interface.id})")
            for m in modules:
                print(f"    - {m.module_name}")
            
            sync_plan.append({
                "hospital_id": hospital_id,
                "interface_id": active_interface.id,
                "interface_name": active_interface.name,
                "module_count": len(modules)
            })
        
        if not sync_plan:
            print("\n没有可同步的配置")
            return
        
        # 3. 执行同步
        confirm = input("\n是否执行同步？(y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
        
        total_updated = 0
        for plan in sync_plan:
            result = session.execute(text("""
                UPDATE ai_prompt_modules 
                SET ai_interface_id = :interface_id, updated_at = NOW()
                WHERE hospital_id = :hospital_id 
                  AND ai_interface_id IS NULL
            """), {"interface_id": plan["interface_id"], "hospital_id": plan["hospital_id"]})
            
            total_updated += result.rowcount
        
        session.commit()
        print(f"\n同步完成，更新了 {total_updated} 个模块配置")
        
        # 4. 验证结果
        print("\n=== 同步后状态 ===")
        modules = session.execute(text("""
            SELECT m.hospital_id, m.module_name, i.name as interface_name
            FROM ai_prompt_modules m
            LEFT JOIN ai_interfaces i ON m.ai_interface_id = i.id
            ORDER BY m.hospital_id, m.module_code
        """)).fetchall()
        
        for m in modules:
            interface_info = m.interface_name if m.interface_name else "未配置"
            print(f"  医院ID: {m.hospital_id}, {m.module_name}: {interface_info}")
        
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
