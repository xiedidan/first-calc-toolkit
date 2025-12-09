"""
测试API密钥加密解密功能
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.encryption import encrypt_api_key, decrypt_api_key, mask_api_key


def test_encrypt_decrypt():
    """测试加密和解密"""
    print("测试1: 加密和解密")
    print("-" * 50)
    
    # 测试API密钥
    original_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
    print(f"原始密钥: {original_key}")
    
    # 加密
    encrypted = encrypt_api_key(original_key)
    print(f"加密后: {encrypted}")
    
    # 解密
    decrypted = decrypt_api_key(encrypted)
    print(f"解密后: {decrypted}")
    
    # 验证
    assert decrypted == original_key, "解密后的密钥与原始密钥不匹配"
    print("✓ 加密解密测试通过")
    print()


def test_mask():
    """测试掩码显示"""
    print("测试2: 掩码显示")
    print("-" * 50)
    
    # 测试不同长度的加密密钥
    test_cases = [
        ("sk-1234567890abcdefghijklmnopqrstuvwxyz", "长密钥"),
        ("short", "短密钥"),
        ("", "空密钥"),
    ]
    
    for key, desc in test_cases:
        if key:
            encrypted = encrypt_api_key(key)
            masked = mask_api_key(encrypted)
            print(f"{desc}: {masked}")
            assert masked.startswith("****"), f"{desc}掩码格式错误"
        else:
            masked = mask_api_key(key)
            print(f"{desc}: {masked}")
            assert masked == "****", f"{desc}掩码格式错误"
    
    print("✓ 掩码显示测试通过")
    print()


def test_round_trip():
    """测试往返一致性"""
    print("测试3: 往返一致性")
    print("-" * 50)
    
    test_keys = [
        "sk-test123",
        "deepseek-api-key-1234567890",
        "openai-key-abcdefghijklmnopqrstuvwxyz",
        "中文密钥测试",
        "special!@#$%^&*()chars",
    ]
    
    for key in test_keys:
        encrypted = encrypt_api_key(key)
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == key, f"往返测试失败: {key}"
        print(f"✓ {key[:20]}... 往返一致")
    
    print("✓ 所有往返测试通过")
    print()


def test_different_keys_different_ciphertext():
    """测试不同的密钥产生不同的密文"""
    print("测试4: 不同密钥产生不同密文")
    print("-" * 50)
    
    key1 = "sk-key1"
    key2 = "sk-key2"
    
    encrypted1 = encrypt_api_key(key1)
    encrypted2 = encrypt_api_key(key2)
    
    print(f"密钥1加密: {encrypted1[:30]}...")
    print(f"密钥2加密: {encrypted2[:30]}...")
    
    assert encrypted1 != encrypted2, "不同的密钥应该产生不同的密文"
    print("✓ 不同密钥产生不同密文测试通过")
    print()


def test_encrypted_not_equal_plaintext():
    """测试加密后的值与明文不同"""
    print("测试5: 加密后的值与明文不同")
    print("-" * 50)
    
    key = "sk-plaintext-key"
    encrypted = encrypt_api_key(key)
    
    print(f"明文: {key}")
    print(f"密文: {encrypted}")
    
    assert encrypted != key, "加密后的值应该与明文不同"
    print("✓ 加密后的值与明文不同测试通过")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("API密钥加密解密功能测试")
    print("=" * 50)
    print()
    
    try:
        test_encrypt_decrypt()
        test_mask()
        test_round_trip()
        test_different_keys_different_ciphertext()
        test_encrypted_not_equal_plaintext()
        
        print("=" * 50)
        print("所有测试通过! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
