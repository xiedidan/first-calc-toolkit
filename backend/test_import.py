"""
测试导入system_settings模块
"""
import sys
import traceback

print("=" * 60)
print("测试导入system_settings模块")
print("=" * 60)

try:
    print("\n1. 导入app.api.system_settings...")
    from app.api import system_settings
    print("   ✓ 成功")
    print(f"   router对象: {system_settings.router}")
    print(f"   路由数量: {len(system_settings.router.routes)}")
    
    print("\n2. 检查路由...")
    for route in system_settings.router.routes:
        print(f"   - {route.methods} {route.path}")
    
    print("\n3. 导入app.services.system_setting_service...")
    from app.services.system_setting_service import SystemSettingService
    print("   ✓ 成功")
    
    print("\n4. 导入app.schemas.system_setting...")
    from app.schemas.system_setting import SystemSettingsResponse, SystemSettingsUpdate
    print("   ✓ 成功")
    
    print("\n5. 导入app.models.system_setting...")
    from app.models.system_setting import SystemSetting
    print("   ✓ 成功")
    
    print("\n" + "=" * 60)
    print("所有导入测试通过！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 导入失败: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    sys.exit(1)
