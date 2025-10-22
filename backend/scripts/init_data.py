"""
Initialize database with default data
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables before importing app modules
os.environ.setdefault('DATABASE_URL', 'postgresql://admin:admin123@localhost:5432/hospital_value')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-for-init')
os.environ.setdefault('CELERY_BROKER_URL', 'redis://localhost:6379/0')
os.environ.setdefault('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Role, Permission, user_roles, role_permissions
from app.utils.security import get_password_hash


def init_permissions(db: Session):
    """Initialize default permissions"""
    # Check if permissions already exist
    existing_count = db.query(Permission).count()
    if existing_count > 0:
        print(f"Permissions already exist ({existing_count} found), skipping...")
        return db.query(Permission).all()
    
    permissions_data = [
        # User management
        {"name": "Create User", "code": "user:create", "resource": "user", "action": "create"},
        {"name": "Read User", "code": "user:read", "resource": "user", "action": "read"},
        {"name": "Update User", "code": "user:update", "resource": "user", "action": "update"},
        {"name": "Delete User", "code": "user:delete", "resource": "user", "action": "delete"},
        
        # Role management
        {"name": "Create Role", "code": "role:create", "resource": "role", "action": "create"},
        {"name": "Read Role", "code": "role:read", "resource": "role", "action": "read"},
        {"name": "Update Role", "code": "role:update", "resource": "role", "action": "update"},
        {"name": "Delete Role", "code": "role:delete", "resource": "role", "action": "delete"},
        
        # Model management
        {"name": "Create Model", "code": "model:create", "resource": "model", "action": "create"},
        {"name": "Read Model", "code": "model:read", "resource": "model", "action": "read"},
        {"name": "Update Model", "code": "model:update", "resource": "model", "action": "update"},
        {"name": "Delete Model", "code": "model:delete", "resource": "model", "action": "delete"},
        
        # Department management
        {"name": "Create Department", "code": "department:create", "resource": "department", "action": "create"},
        {"name": "Read Department", "code": "department:read", "resource": "department", "action": "read"},
        {"name": "Update Department", "code": "department:update", "resource": "department", "action": "update"},
        {"name": "Delete Department", "code": "department:delete", "resource": "department", "action": "delete"},
        
        # Calculation management
        {"name": "Create Calculation", "code": "calculation:create", "resource": "calculation", "action": "create"},
        {"name": "Read Calculation", "code": "calculation:read", "resource": "calculation", "action": "read"},
        {"name": "Cancel Calculation", "code": "calculation:cancel", "resource": "calculation", "action": "cancel"},
        
        # Result management
        {"name": "Read Result", "code": "result:read", "resource": "result", "action": "read"},
        {"name": "Export Result", "code": "result:export", "resource": "result", "action": "export"},
    ]
    
    permissions = []
    for perm_data in permissions_data:
        perm = Permission(**perm_data)
        db.add(perm)
        permissions.append(perm)
    
    db.commit()
    print(f"✓ Created {len(permissions)} permissions")
    return permissions


def init_roles(db: Session, permissions: list):
    """Initialize default roles"""
    # Check if roles already exist
    existing_count = db.query(Role).count()
    if existing_count > 0:
        print(f"Roles already exist ({existing_count} found), skipping...")
        return db.query(Role).all()
    
    # Get all permissions
    all_perms = {p.code: p for p in permissions}
    
    roles_data = [
        {
            "name": "System Administrator",
            "code": "admin",
            "description": "Full system access",
            "permissions": list(all_perms.values())  # All permissions
        },
        {
            "name": "Model Designer",
            "code": "model_designer",
            "description": "Can design and manage evaluation models",
            "permissions": [
                all_perms["model:create"],
                all_perms["model:read"],
                all_perms["model:update"],
                all_perms["model:delete"],
                all_perms["department:read"],
                all_perms["calculation:read"],
                all_perms["result:read"],
            ]
        },
        {
            "name": "Data Analyst",
            "code": "data_analyst",
            "description": "Can trigger calculations and export results",
            "permissions": [
                all_perms["model:read"],
                all_perms["department:read"],
                all_perms["calculation:create"],
                all_perms["calculation:read"],
                all_perms["calculation:cancel"],
                all_perms["result:read"],
                all_perms["result:export"],
            ]
        },
        {
            "name": "Business Expert",
            "code": "business_expert",
            "description": "Can view and adjust models, trigger calculations",
            "permissions": [
                all_perms["model:read"],
                all_perms["model:update"],
                all_perms["department:read"],
                all_perms["calculation:create"],
                all_perms["calculation:read"],
                all_perms["result:read"],
                all_perms["result:export"],
            ]
        },
        {
            "name": "Department Manager",
            "code": "dept_manager",
            "description": "Can view results for their department",
            "permissions": [
                all_perms["result:read"],
            ]
        },
    ]
    
    roles = []
    for role_data in roles_data:
        perms = role_data.pop("permissions")
        role = Role(**role_data)
        role.permissions = perms
        db.add(role)
        roles.append(role)
    
    db.commit()
    print(f"✓ Created {len(roles)} roles")
    return roles


def init_admin_user(db: Session, admin_role: Role):
    """Initialize default admin user"""
    # Check if admin user already exists
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("Admin user already exists, skipping...")
        return existing_admin
    
    admin = User(
        username="admin",
        name="System Administrator",
        email="admin@hospital.com",
        hashed_password=get_password_hash("admin123"),
        status="active"
    )
    admin.roles = [admin_role]
    db.add(admin)
    db.commit()
    
    print("✓ Created admin user")
    print("  Username: admin")
    print("  Password: admin123")
    print("  Please change the password after first login!")
    
    return admin


def main():
    """Main function"""
    print("========================================")
    print("Initialize Database with Default Data")
    print("========================================")
    print()
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    print()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        existing_roles = db.query(Role).count()
        existing_perms = db.query(Permission).count()
        
        if existing_users > 0 and existing_roles > 0 and existing_perms > 0:
            print("Database already fully initialized!")
            print(f"Found {existing_users} users, {existing_roles} roles, {existing_perms} permissions")
            return
        
        # Initialize data
        print("Initializing permissions...")
        permissions = init_permissions(db)
        print()
        
        print("Initializing roles...")
        roles = init_roles(db, permissions)
        print()
        
        print("Initializing admin user...")
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        init_admin_user(db, admin_role)
        print()
        
        print("========================================")
        print("Initialization complete!")
        print("========================================")
        print()
        print("You can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
