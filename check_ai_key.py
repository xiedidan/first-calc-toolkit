"""检查 AI 配置中的 API Key"""
import sys
sys.path.insert(0, 'backend')

from app.utils.encryption import decrypt_api_key

encrypted = 'gAAAAABpN7--WJZ3u_pe0vaU2k_Sy3LN_kgNjVygtMyFcE_YIXEwxbsjAJs18tD9OSgvLkAUBOTb51alCBdkFA1nWn0nvta7GdVwDp1tHpK_8SU1o5mDZ7NVaX19q13ZAU6NH93JFH1Qm6-6Haz8HloD0yscHUUR5Q=='
decrypted = decrypt_api_key(encrypted)
print(f'解密后的 API Key: {decrypted}')
print(f'Key 长度: {len(decrypted)}')
