"""
初始化管理员用户脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.utils.security import get_password_hash


def init_admin():
    """初始化管理员用户"""
    db: Session = SessionLocal()
    
    try:
        # 检查是否已存在admin角色
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            print("错误：admin角色不存在，请先运行数据库迁移")
            return
        
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            name="系统管理员",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            status="active",
            hospital_id=None  # 管理员不属于任何医疗机构
        )
        admin_user.roles = [admin_role]
        
        db.add(admin_user)
        db.commit()
        
        print("✓ 管理员用户创建成功")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  请登录后立即修改密码！")
        
    except Exception as e:
        print(f"✗ 创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
