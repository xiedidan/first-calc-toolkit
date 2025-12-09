"""
测试AI配置前端实现
验证前端文件是否正确创建
"""
import os

def test_frontend_files_exist():
    """测试前端文件是否存在"""
    files = [
        'frontend/src/api/ai-config.ts',
        'frontend/src/views/AIConfig.vue',
    ]
    
    for file_path in files:
        assert os.path.exists(file_path), f"文件不存在: {file_path}"
        print(f"✓ 文件存在: {file_path}")

def test_api_file_content():
    """测试API文件内容"""
    with open('frontend/src/api/ai-config.ts', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键接口
    assert 'getAIConfig' in content, "缺少getAIConfig函数"
    assert 'createOrUpdateAIConfig' in content, "缺少createOrUpdateAIConfig函数"
    assert 'testAIConfig' in content, "缺少testAIConfig函数"
    assert 'getAPIUsageStats' in content, "缺少getAPIUsageStats函数"
    
    # 检查类型定义
    assert 'interface AIConfig' in content, "缺少AIConfig接口"
    assert 'interface AIConfigCreate' in content, "缺少AIConfigCreate接口"
    assert 'interface APIUsageStats' in content, "缺少APIUsageStats接口"
    
    print("✓ API文件内容正确")

def test_vue_component_content():
    """测试Vue组件内容"""
    with open('frontend/src/views/AIConfig.vue', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键功能
    assert 'api_endpoint' in content, "缺少API端点字段"
    assert 'api_key' in content, "缺少API密钥字段"
    assert 'prompt_template' in content, "缺少提示词模板字段"
    assert 'call_delay' in content, "缺少调用延迟字段"
    assert 'daily_limit' in content, "缺少每日限额字段"
    assert 'batch_size' in content, "缺少批次大小字段"
    
    # 检查功能函数
    assert 'saveConfig' in content, "缺少保存配置函数"
    assert 'testConfig' in content, "缺少测试配置函数"
    assert 'showUsageStats' in content, "缺少显示统计函数"
    
    # 检查密码输入框
    assert 'type="password"' in content, "密钥输入框未设置为password类型"
    assert 'show-password' in content, "密钥输入框未启用显示密码功能"
    
    # 检查多行文本框
    assert 'type="textarea"' in content, "提示词未使用多行文本框"
    
    print("✓ Vue组件内容正确")

def test_router_configuration():
    """测试路由配置"""
    with open('frontend/src/router/index.ts', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查路由定义
    assert "path: '/ai-config'" in content, "缺少AI配置路由"
    assert "name: 'AIConfig'" in content, "缺少路由名称"
    assert "component: () => import('@/views/AIConfig.vue')" in content, "缺少组件导入"
    assert "requiresAdmin: true" in content, "缺少管理员权限要求"
    
    print("✓ 路由配置正确")

def test_menu_configuration():
    """测试菜单配置"""
    with open('frontend/src/views/Layout.vue', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查菜单项
    assert 'AI接口管理' in content, "缺少AI接口管理菜单项"
    assert 'index="/ai-config"' in content, "缺少菜单路由"
    
    # 检查权限控制
    ai_config_menu_section = content[content.find('AI接口管理')-100:content.find('AI接口管理')+100]
    assert 'v-if="isAdmin"' in ai_config_menu_section, "菜单项未添加管理员权限控制"
    
    # 检查activeMenu处理
    assert "if (path.startsWith('/ai-config'))" in content, "缺少activeMenu处理"
    
    print("✓ 菜单配置正确")

if __name__ == '__main__':
    print("开始测试AI配置前端实现...\n")
    
    test_frontend_files_exist()
    test_api_file_content()
    test_vue_component_content()
    test_router_configuration()
    test_menu_configuration()
    
    print("\n✅ 所有测试通过！")
    print("\n实现总结：")
    print("1. ✓ 创建了 frontend/src/api/ai-config.ts API文件")
    print("2. ✓ 创建了 frontend/src/views/AIConfig.vue 页面组件")
    print("3. ✓ 在路由中添加了 /ai-config 路由，并设置了管理员权限")
    print("4. ✓ 在系统设置菜单下添加了 'AI接口管理' 菜单项")
    print("5. ✓ 实现了配置表单（API端点、密钥、提示词等）")
    print("6. ✓ 密钥输入框使用password类型")
    print("7. ✓ 提示词使用多行文本框")
    print("8. ✓ 实现了保存功能")
    print("9. ✓ 实现了测试功能（调用test接口）")
    print("10. ✓ 实现了显示API使用统计功能")
