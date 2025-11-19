"""
检查FastAPI应用的所有路由
"""
from app.main import app

print("=" * 60)
print("FastAPI应用路由检查")
print("=" * 60)

print(f"\n应用名称: {app.title}")
print(f"应用版本: {app.version}")
print(f"\n总路由数: {len(app.routes)}")

print("\n所有路由:")
print("-" * 60)

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods)
        print(f"{methods:10} {route.path}")
        if hasattr(route, 'tags') and route.tags:
            print(f"           Tags: {route.tags}")

print("\n" + "=" * 60)

# 检查是否有系统设置相关的路由
system_settings_routes = [r for r in app.routes if hasattr(r, 'path') and 'system' in r.path.lower()]
if system_settings_routes:
    print(f"\n✓ 找到 {len(system_settings_routes)} 个系统设置相关路由")
else:
    print("\n✗ 未找到系统设置相关路由")

print("=" * 60)
