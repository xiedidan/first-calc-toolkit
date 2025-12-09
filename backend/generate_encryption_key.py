"""
生成加密密钥工具

用于生成Fernet加密密钥，用于API密钥和密码的加密存储。
"""
from cryptography.fernet import Fernet


def generate_key():
    """生成新的加密密钥"""
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    print("=" * 60)
    print("Fernet加密密钥生成工具")
    print("=" * 60)
    print()
    print("生成的加密密钥:")
    print(generate_key())
    print()
    print("使用说明:")
    print("1. 将生成的密钥复制到 .env 文件中的 ENCRYPTION_KEY 变量")
    print("2. 确保在生产环境中使用不同的密钥")
    print("3. 密钥一旦设置，不要随意更改，否则已加密的数据将无法解密")
    print()
    print("示例:")
    print("ENCRYPTION_KEY=<生成的密钥>")
    print("=" * 60)
