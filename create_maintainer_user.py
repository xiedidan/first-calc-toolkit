"""创建 maintainer 用户"""
import sys
sys.path.append('backend')

from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Role
from app.utils.security import get_password_hash

def create_maintainer():
    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = db.query(User).filter(User.username == "maintainer").first()
        if existing:
            print("maintainer 用户已存在")
            return
        
        # 获取 maintainer 角色
        role = db.query(Role).filter(Role.code == "maintainer").first()
        if not role:
            print("maintainer 角色不存在")
            return
        
        # 创建用户
        user = User(
            username="maintainer",
            name="系统维护者",
            email="maintainer@hospital.com",
            hashed_password=get_password_hash("maintainer123"),
            status="active"
        )
        user.roles = [role]
        
        db.add(user)
        db.commit()
        
        print("maintainer 用户创建成功！")
        print("  用户名: maintainer")
        print("  密码: maintainer123")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_maintainer()
