"""
测试用户角色功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.hospital import Hospital
from app.utils.security import get_password_hash


def test_roles():
    """测试角色功能"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 50)
        print("测试用户角色功能")
        print("=" * 50)
        
        # 1. 检查角色是否存在
        print("\n1. 检查角色...")
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        user_role = db.query(Role).filter(Role.code == "user").first()
        
        if admin_role:
            print(f"  ✓ admin角色存在: {admin_role.name}")
        else:
            print("  ✗ admin角色不存在")
            
        if user_role:
            print(f"  ✓ user角色存在: {user_role.name}")
        else:
            print("  ✗ user角色不存在")
        
        # 2. 检查管理员用户
        print("\n2. 检查管理员用户...")
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print(f"  ✓ 管理员用户存在: {admin_user.name}")
            print(f"    - 角色: {[r.code for r in admin_user.roles]}")
            print(f"    - 医疗机构: {admin_user.hospital_id}")
        else:
            print("  ✗ 管理员用户不存在")
        
        # 3. 检查医疗机构
        print("\n3. 检查医疗机构...")
        hospitals = db.query(Hospital).limit(3).all()
        if hospitals:
            print(f"  ✓ 找到 {len(hospitals)} 个医疗机构:")
            for h in hospitals:
                print(f"    - {h.id}: {h.name}")
        else:
            print("  ⚠ 没有找到医疗机构")
        
        # 4. 检查普通用户
        print("\n4. 检查普通用户...")
        normal_users = db.query(User).join(User.roles).filter(Role.code == "user").limit(3).all()
        if normal_users:
            print(f"  ✓ 找到 {len(normal_users)} 个普通用户:")
            for u in normal_users:
                print(f"    - {u.username}: {u.name} (医疗机构: {u.hospital_id})")
        else:
            print("  ⚠ 没有找到普通用户")
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_roles()
