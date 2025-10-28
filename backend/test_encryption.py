"""
测试加密功能
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.encryption import encrypt_password, decrypt_password

def test_encryption():
    """测试加密解密"""
    print("=== 测试密码加密功能 ===\n")
    
    # 测试密码
    test_passwords = [
        "simple_password",
        "complex_P@ssw0rd!",
        "中文密码123",
        "very_long_password_with_special_chars_!@#$%^&*()",
    ]
    
    for password in test_passwords:
        print(f"原始密码: {password}")
        
        # 加密
        encrypted = encrypt_password(password)
        print(f"加密后: {encrypted}")
        
        # 解密
        decrypted = decrypt_password(encrypted)
        print(f"解密后: {decrypted}")
        
        # 验证
        if password == decrypted:
            print("✅ 加密解密成功\n")
        else:
            print("❌ 加密解密失败\n")
            sys.exit(1)
    
    print("所有测试通过！")

if __name__ == "__main__":
    test_encryption()
