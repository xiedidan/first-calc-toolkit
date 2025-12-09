"""
加密工具类
用于数据源密码的加密和解密
"""
import os
from cryptography.fernet import Fernet
from typing import Optional


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self):
        """初始化加密管理器"""
        # 优先从环境变量获取加密密钥
        key = os.getenv('ENCRYPTION_KEY')
        
        # 如果环境变量没有，尝试从配置中获取
        if not key:
            try:
                from app.config import settings
                key = settings.ENCRYPTION_KEY
            except:
                pass
        
        if not key:
            # 如果没有设置密钥，生成一个新的（仅用于开发环境）
            key = Fernet.generate_key().decode()
            print(f"警告: 未设置ENCRYPTION_KEY环境变量，使用临时密钥: {key}")
            print("请在生产环境中设置ENCRYPTION_KEY环境变量")
        
        if isinstance(key, str):
            key = key.encode()
        
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文
        
        Args:
            plaintext: 明文字符串
            
        Returns:
            加密后的字符串（Base64编码）
        """
        if not plaintext:
            return ""
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文
        
        Args:
            ciphertext: 密文字符串（Base64编码）
            
        Returns:
            解密后的明文字符串
        """
        if not ciphertext:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")


# 全局加密管理器实例
encryption_manager = EncryptionManager()


def encrypt_password(password: str) -> str:
    """加密密码"""
    return encryption_manager.encrypt(password)


def decrypt_password(encrypted_password: str) -> str:
    """解密密码"""
    return encryption_manager.decrypt(encrypted_password)


def encrypt_api_key(api_key: str) -> str:
    """
    加密API密钥
    
    Args:
        api_key: 明文API密钥
        
    Returns:
        加密后的API密钥（Base64编码）
    """
    return encryption_manager.encrypt(api_key)


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    解密API密钥
    
    Args:
        encrypted_api_key: 加密的API密钥（Base64编码）
        
    Returns:
        解密后的明文API密钥
    """
    return encryption_manager.decrypt(encrypted_api_key)


def mask_api_key(encrypted_api_key: str) -> str:
    """
    掩码显示API密钥
    
    Args:
        encrypted_api_key: 加密的API密钥
        
    Returns:
        掩码后的显示字符串（如 "****abcd"）
    """
    if not encrypted_api_key:
        return "****"
    
    # 显示最后4个字符，其余用星号代替
    if len(encrypted_api_key) > 4:
        return "****" + encrypted_api_key[-4:]
    else:
        return "****"
