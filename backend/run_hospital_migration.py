"""
执行医疗机构管理数据迁移
"""
import subprocess
import sys
import os

def run_migration():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始执行医疗机构管理数据迁移")
    print("=" * 60)
    
    # 1. 检查当前迁移状态
    print("\n1. 检查当前迁移状态...")
    result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 检查迁移状态失败: {result.stderr}")
        return 1
    
    # 2. 执行迁移
    print("\n2. 执行数据库迁移...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ 迁移执行失败: {result.stderr}")
        return 1
    
    print("✓ 数据库迁移执行成功")
    
    # 3. 验证迁移结果
    print("\n3. 验证迁移结果...")
    result = subprocess.run(
        [sys.executable, "verify_hospital_migration.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("❌ 迁移验证失败")
        return 1
    
    print("\n" + "=" * 60)
    print("✓ 医疗机构管理数据迁移完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    # 确保在 backend 目录下执行
    if not os.path.exists("alembic.ini"):
        print("❌ 请在 backend 目录下执行此脚本")
        sys.exit(1)
    
    sys.exit(run_migration())
