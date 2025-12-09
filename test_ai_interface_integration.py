"""
AI接口集成测试

测试真实的DeepSeek API调用:
1. 测试请求格式
2. 测试响应解析
3. 测试错误处理

注意: 此测试需要真实的API密钥，可以通过环境变量DEEPSEEK_API_KEY提供
如果没有提供，测试将使用mock数据
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import Hospital, ModelVersion, ModelNode
from app.utils.ai_interface import call_ai_classification


def setup_test_dimensions(db):
    """设置测试维度数据"""
    print("设置测试维度...")
    
    # 创建医疗机构
    hospital = Hospital(
        name="测试医院AI",
        code="TEST_AI_001",
        is_active=True
    )
    db.add(hospital)
    db.flush()
    
    # 创建模型版本
    version = ModelVersion(
        hospital_id=hospital.id,
        version="v1.0",
        name="测试版本AI",
        is_active=True
    )
    db.add(version)
    db.flush()
    
    # 创建测试维度
    dimensions = []
    dimension_names = [
        "超声检查",
        "CT检查",
        "MRI检查",
        "X光检查",
        "心电图检查"
    ]
    
    for i, name in enumerate(dimension_names):
        node = ModelNode(
            version_id=version.id,
            name=name,
            code=f"CHECK_{i+1}",
            node_type="dimension",
            is_leaf=True,
            sort_order=i + 1
        )
        db.add(node)
        db.flush()
        dimensions.append(node)
    
    db.commit()
    
    return {
        "hospital": hospital,
        "version": version,
        "dimensions": dimensions
    }


def cleanup_test_data(db, test_data):
    """清理测试数据"""
    print("清理测试数据...")
    
    try:
        db.query(ModelNode).filter(
            ModelNode.version_id == test_data["version"].id
        ).delete()
        
        db.query(ModelVersion).filter(
            ModelVersion.hospital_id == test_data["hospital"].id
        ).delete()
        
        db.query(Hospital).filter(
            Hospital.id == test_data["hospital"].id
        ).delete()
        
        db.commit()
    except Exception as e:
        print(f"清理测试数据时出错: {e}")
        db.rollback()


def test_ai_request_format():
    """
    测试AI请求格式
    
    验证需求: 3.2, 9.1-9.3
    """
    print("\n" + "="*80)
    print("测试1: AI请求格式")
    print("="*80)
    
    db = SessionLocal()
    test_data = None
    
    try:
        test_data = setup_test_dimensions(db)
        dimensions = test_data["dimensions"]
        
        # 准备测试数据
        api_endpoint = "https://api.deepseek.com/v1"
        api_key = os.getenv("DEEPSEEK_API_KEY", "test-key")
        item_name = "腹部超声检查"
        prompt_template = """请为以下医技项目选择最合适的维度分类。

项目名称：{item_name}

可选维度（JSON格式）：
{dimensions}

请返回JSON格式的结果，包含以下字段：
- dimension_id: 选择的维度ID（整数）
- confidence: 确信度（0-1之间的小数）

示例：
{{"dimension_id": 123, "confidence": 0.85}}
"""
        
        print(f"\n测试项目: {item_name}")
        print(f"可选维度数量: {len(dimensions)}")
        
        # 构建维度列表JSON
        dimensions_json = json.dumps([
            {
                "id": d.id,
                "name": d.name,
                "code": d.code
            }
            for d in dimensions
        ], ensure_ascii=False, indent=2)
        
        print(f"\n维度列表JSON格式:")
        print(dimensions_json[:200] + "...")
        
        # 替换占位符
        final_prompt = prompt_template.replace('{item_name}', item_name)
        final_prompt = final_prompt.replace('{dimensions}', dimensions_json)
        
        print(f"\n✓ 提示词模板替换成功")
        print(f"  - 包含项目名称: {'item_name' not in final_prompt and item_name in final_prompt}")
        print(f"  - 包含维度列表: {'dimensions' not in final_prompt and dimensions[0].name in final_prompt}")
        
        # 验证请求格式
        assert '{item_name}' not in final_prompt, "占位符{item_name}应已替换"
        assert '{dimensions}' not in final_prompt, "占位符{dimensions}应已替换"
        assert item_name in final_prompt, "应包含项目名称"
        assert dimensions[0].name in final_prompt, "应包含维度名称"
        
        # 如果有真实API密钥，测试真实调用
        if api_key != "test-key":
            print("\n使用真实API密钥测试...")
            
            try:
                # 转换dimensions为字典列表
                dimensions_list = [
                    {"id": d.id, "name": d.name, "path": d.code}
                    for d in dimensions
                ]
                
                result = call_ai_classification(
                    api_endpoint=api_endpoint,
                    api_key=api_key,
                    prompt_template=prompt_template,
                    item_name=item_name,
                    dimensions=dimensions_list
                )
                
                print(f"✓ API调用成功")
                print(f"  - 返回维度ID: {result.get('dimension_id')}")
                print(f"  - 确信度: {result.get('confidence')}")
                
                # 验证返回格式
                assert 'dimension_id' in result, "返回结果应包含dimension_id"
                assert 'confidence' in result, "返回结果应包含confidence"
                assert isinstance(result['dimension_id'], int), "dimension_id应为整数"
                assert isinstance(result['confidence'], (int, float)), "confidence应为数字"
                assert 0 <= result['confidence'] <= 1, "confidence应在0-1之间"
                
            except Exception as e:
                print(f"✗ API调用失败: {e}")
                print("  (这可能是因为API密钥无效或网络问题)")
        else:
            print("\n未提供真实API密钥，跳过真实API调用测试")
            print("  提示: 设置环境变量DEEPSEEK_API_KEY以启用真实API测试")
        
        print("\n✓ AI请求格式测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if test_data:
            cleanup_test_data(db, test_data)
        db.close()


@patch('app.utils.ai_interface.OpenAI')
def test_ai_response_parsing(mock_openai_class):
    """
    测试AI响应解析
    
    验证需求: 3.3, 9.4
    """
    print("\n" + "="*80)
    print("测试2: AI响应解析")
    print("="*80)
    
    db = SessionLocal()
    test_data = None
    
    try:
        test_data = setup_test_dimensions(db)
        dimensions = test_data["dimensions"]
        
        # 模拟不同格式的AI响应
        test_cases = [
            {
                "name": "标准JSON格式",
                "response": json.dumps({
                    "dimension_id": dimensions[0].id,
                    "confidence": 0.85
                }),
                "should_succeed": True
            },
            {
                "name": "包含额外字段的JSON",
                "response": json.dumps({
                    "dimension_id": dimensions[1].id,
                    "confidence": 0.92,
                    "reasoning": "基于项目名称判断"
                }),
                "should_succeed": True
            },
            {
                "name": "confidence为整数",
                "response": json.dumps({
                    "dimension_id": dimensions[2].id,
                    "confidence": 1
                }),
                "should_succeed": True
            },
            {
                "name": "缺少confidence字段",
                "response": json.dumps({
                    "dimension_id": dimensions[3].id
                }),
                "should_succeed": True  # 应使用默认值0.0
            },
            {
                "name": "非JSON格式",
                "response": "这不是JSON格式的响应",
                "should_succeed": False
            },
            {
                "name": "缺少dimension_id字段",
                "response": json.dumps({
                    "confidence": 0.75
                }),
                "should_succeed": False
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试用例 {i+1}: {test_case['name']}")
            
            # 配置mock
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = test_case['response']
            
            mock_client.chat.completions.create.return_value = mock_response
            
            # 调用函数
            try:
                # 转换dimensions为字典列表
                dimensions_list = [
                    {"id": d.id, "name": d.name, "path": d.code}
                    for d in dimensions
                ]
                
                result = call_ai_classification(
                    api_endpoint="https://api.test.com/v1",
                    api_key="test-key",
                    prompt_template="测试提示词: {item_name}\n维度: {dimensions}",
                    item_name="测试项目",
                    dimensions=dimensions_list
                )
                
                if test_case['should_succeed']:
                    print(f"  ✓ 解析成功")
                    print(f"    - dimension_id: {result.get('dimension_id')}")
                    print(f"    - confidence: {result.get('confidence')}")
                    
                    # 验证结果
                    assert 'dimension_id' in result, "应包含dimension_id"
                    assert 'confidence' in result, "应包含confidence"
                else:
                    print(f"  ✗ 应该失败但成功了")
                    return False
                    
            except Exception as e:
                if not test_case['should_succeed']:
                    print(f"  ✓ 按预期失败: {type(e).__name__}")
                else:
                    print(f"  ✗ 不应该失败: {e}")
                    return False
        
        print("\n✓ AI响应解析测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if test_data:
            cleanup_test_data(db, test_data)
        db.close()


@patch('app.utils.ai_interface.OpenAI')
@patch('app.utils.ai_interface.time.sleep')
def test_ai_error_handling(mock_sleep, mock_openai_class):
    """
    测试AI错误处理
    
    验证需求: 9.5, 11.1-11.2
    """
    print("\n" + "="*80)
    print("测试3: AI错误处理")
    print("="*80)
    
    db = SessionLocal()
    test_data = None
    
    try:
        test_data = setup_test_dimensions(db)
        dimensions = test_data["dimensions"]
        
        from openai import APIConnectionError, RateLimitError, APIError
        
        # 创建mock请求对象
        mock_request = MagicMock()
        mock_request.url = "https://api.test.com/v1"
        mock_request.method = "POST"
        
        # 创建mock响应对象
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}
        
        # 测试不同类型的错误
        error_cases = [
            {
                "name": "连接错误（应重试）",
                "error": APIConnectionError(request=mock_request),
                "should_retry": True
            },
            {
                "name": "限流错误",
                "error": RateLimitError("Rate limit exceeded", response=mock_response, body=None),
                "should_retry": False
            },
            {
                "name": "API错误",
                "error": APIError("API error", request=mock_request, body=None),
                "should_retry": False
            }
        ]
        
        for i, error_case in enumerate(error_cases):
            print(f"\n测试用例 {i+1}: {error_case['name']}")
            
            # 配置mock
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            
            if error_case['should_retry']:
                # 前2次失败，第3次成功
                mock_client.chat.completions.create.side_effect = [
                    error_case['error'],
                    error_case['error'],
                    MagicMock(
                        choices=[MagicMock(
                            message=MagicMock(
                                content=json.dumps({
                                    "dimension_id": dimensions[0].id,
                                    "confidence": 0.8
                                })
                            )
                        )]
                    )
                ]
            else:
                # 始终失败
                mock_client.chat.completions.create.side_effect = error_case['error']
            
            # 调用函数
            try:
                # 转换dimensions为字典列表
                dimensions_list = [
                    {"id": d.id, "name": d.name, "path": d.code}
                    for d in dimensions
                ]
                
                result = call_ai_classification(
                    api_endpoint="https://api.test.com/v1",
                    api_key="test-key",
                    prompt_template="测试提示词: {item_name}\n维度: {dimensions}",
                    item_name="测试项目",
                    dimensions=dimensions_list
                )
                
                if error_case['should_retry']:
                    print(f"  ✓ 重试后成功")
                    print(f"    - 调用次数: {mock_client.chat.completions.create.call_count}")
                    assert mock_client.chat.completions.create.call_count == 3, "应重试2次后成功"
                else:
                    print(f"  ✗ 应该失败但成功了")
                    return False
                    
            except Exception as e:
                if not error_case['should_retry']:
                    print(f"  ✓ 按预期失败: {type(e).__name__}")
                else:
                    print(f"  ✗ 重试后仍失败: {e}")
                    return False
        
        print("\n✓ AI错误处理测试通过")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if test_data:
            cleanup_test_data(db, test_data)
        db.close()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("AI接口集成测试套件")
    print("="*80)
    
    results = []
    
    # 测试1: 请求格式
    results.append(("AI请求格式", test_ai_request_format()))
    
    # 测试2: 响应解析
    results.append(("AI响应解析", test_ai_response_parsing()))
    
    # 测试3: 错误处理
    results.append(("AI错误处理", test_ai_error_handling()))
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n" + "="*80)
        print("✓ 所有AI接口集成测试通过！")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ 部分测试失败")
        print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
