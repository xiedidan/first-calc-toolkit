"""
迁移脚本：更新现有角色的role_type字段
运行方式：python -m scripts.migrate_roles
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Role
from app.models.role import RoleType


def migrate_roles():
    """更新现有角色的role_type字段"""
    db = SessionLocal()
    
    try:
        print("开始迁移角色数据...")
        
        # 更新admin角色
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if admin_role:
            if not admin_role.role_type:
                admin_role.role_type = RoleType.ADMIN
                print(f"  更新角色 '{admin_role.name}' -> role_type=admin")
        
        # 更新user角色
        user_role = db.query(Role).filter(Role.code == "user").first()
        if user_role:
            if not user_role.role_type:
                user_role.role_type = RoleType.HOSPITAL_USER
                print(f"  更新角色 '{user_role.name}' -> role_type=hospital_user")
        
        # 检查是否存在maintainer角色，不存在则创建
        maintainer_role = db.query(Role).filter(Role.code == "maintainer").first()
        if not maintainer_role:
            maintainer_role = Role(
                name="系统维护者",
                code="maintainer",
                role_type=RoleType.MAINTAINER,
                description="系统最高权限，可管理所有用户和AI接口"
            )
            db.add(maintainer_role)
            print("  创建角色 '系统维护者' (maintainer)")
        
        # 检查是否存在科室用户角色
        dept_role = db.query(Role).filter(Role.code == "dept_user").first()
        if not dept_role:
            dept_role = Role(
                name="科室用户",
                code="dept_user",
                role_type=RoleType.DEPARTMENT_USER,
                description="科室用户，只能查看本科室的业务价值报表"
            )
            db.add(dept_role)
            print("  创建角色 '科室用户' (dept_user)")
        
        # 更新其他没有role_type的角色为hospital_user
        other_roles = db.query(Role).filter(Role.role_type == None).all()
        for role in other_roles:
            role.role_type = RoleType.HOSPITAL_USER
            print(f"  更新角色 '{role.name}' -> role_type=hospital_user (默认)")
        
        db.commit()
        print("\n角色迁移完成！")
        
        # 显示当前角色列表
        print("\n当前角色列表：")
        all_roles = db.query(Role).all()
        for role in all_roles:
            print(f"  - {role.name} ({role.code}): {role.role_type.value if role.role_type else 'N/A'}")
        
    except Exception as e:
        print(f"错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_roles()
