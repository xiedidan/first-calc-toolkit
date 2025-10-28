"""
生成加密密钥并更新.env文件
"""
import os
from cryptography.fernet import Fernet


def generate_key():
    """生成新的加密密钥"""
    key = Fernet.generate_key().decode()
    return key


def update_env_file(key):
    """更新.env文件"""
    env_file = ".env"
    
    # 读取现有的.env文件
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # 检查是否已存在ENCRYPTION_KEY
    key_exists = False
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('ENCRYPTION_KEY='):
            # 如果已存在，询问是否覆盖
            print(f"发现已存在的ENCRYPTION_KEY: {line.strip()}")
            response = input("是否覆盖? (y/n): ")
            if response.lower() == 'y':
                new_lines.append(f'ENCRYPTION_KEY={key}\n')
                key_exists = True
                print("✅ 已更新ENCRYPTION_KEY")
            else:
                new_lines.append(line)
                key_exists = True
                print("⏭️ 保持原有ENCRYPTION_KEY")
        else:
            new_lines.append(line)
    
    # 如果不存在，添加新的
    if not key_exists:
        new_lines.append(f'\n# 数据源密码加密密钥\n')
        new_lines.append(f'ENCRYPTION_KEY={key}\n')
        print("✅ 已添加ENCRYPTION_KEY到.env文件")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


def main():
    """主函数"""
    print("=" * 60)
    print("数据源加密密钥生成工具")
    print("=" * 60)
    print()
    
    # 生成密钥
    key = generate_key()
    print(f"生成的加密密钥: {key}")
    print()
    
    # 询问是否更新.env文件
    response = input("是否将密钥添加到.env文件? (y/n): ")
    if response.lower() == 'y':
        update_env_file(key)
    else:
        print()
        print("请手动将以下内容添加到.env文件:")
        print(f"ENCRYPTION_KEY={key}")
    
    print()
    print("⚠️ 重要提示:")
    print("1. 请妥善保管此密钥，不要泄露")
    print("2. 密钥一旦设置不应更改，否则已加密的密码无法解密")
    print("3. 生产环境建议使用密钥管理服务（如AWS KMS、Azure Key Vault）")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
