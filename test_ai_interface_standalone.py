"""
独立测试AI接口集成功能（不依赖项目导入）
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import json
from unittest.mock import Mock, patch

# 直接导入模块
from app.utils.ai_interface import (
    _build_dimensions_json,
    _render_prompt_template,
    _parse_ai_response,
    call_ai_classification,
    test_ai_connection,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError
)


def test_build_dimensions_json():
    """测试维度列表JSON构建"""
    print("测试: 维度列表JSON构建...")
    dimensions = [
        {"id": 1, "name": "检验类", "path": "医技项目/检验类"},
        {"id": 2, "name": "检查类", "path": "医技项目/检查类"}
    ]
    
    result = _build_dimensions_json(dimensions)
    parsed = json.loads(result)
    
    assert len(parsed) == 2
    assert parsed[0]["id"] == 1
    assert parsed[0]["name"] == "检验类"
    assert parsed[0]["path"] == "医技项目/检验类"
    print("  ✓ 通过")


def test_render_prompt_template():
    """测试提示词模板渲染"""
    print("测试: 提示词模板渲染...")
    template = "请对以下医技项目进行分类：{item_name}\n可选维度：{dimensions}"
    item_name = "血常规检查"
    dimensions_json = '[{"id": 1, "name": "检验类"}]'
    
    result = _render_prompt_template(template, item_name, dimensions_json)
    
    assert "{item_name}" not in result
    assert "{dimensions}" not in result
    assert "血常规检查" in result
    assert '[{"id": 1, "name": "检验类"}]' in result
    print("  ✓ 通过")


def test_parse_ai_response_success():
    """测试AI响应解析（成功场景）"""
    print("测试: AI响应解析（成功）...")
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [
        {"id": 1, "name": "检验类"},
        {"id": 2, "name": "检查类"}
    ]
    
    result = _parse_ai_response(mock_response, dimensions)
    
    assert result["dimension_id"] == 1
    assert result["confidence"] == 0.95
    print("  ✓ 通过")


def test_parse_ai_response_missing_confidence():
    """测试AI响应解析（缺少confidence字段）"""
    print("测试: AI响应解析（缺少confidence）...")
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    result = _parse_ai_response(mock_response, dimensions)
    
    assert result["dimension_id"] == 1
    assert result["confidence"] == 0.0
    print("  ✓ 通过")


def test_parse_ai_response_invalid_json():
    """测试AI响应解析（非JSON格式）"""
    print("测试: AI响应解析（非JSON格式）...")
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = 'This is not JSON'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    try:
        _parse_ai_response(mock_response, dimensions)
        assert False, "应该抛出AIResponseError"
    except AIResponseError as e:
        assert "无法解析JSON" in str(e)
        print("  ✓ 通过")


def test_parse_ai_response_missing_dimension_id():
    """测试AI响应解析（缺少dimension_id字段）"""
    print("测试: AI响应解析（缺少dimension_id）...")
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    try:
        _parse_ai_response(mock_response, dimensions)
        assert False, "应该抛出AIResponseError"
    except AIResponseError as e:
        assert "缺少dimension_id字段" in str(e)
        print("  ✓ 通过")


@patch('app.utils.ai_interface.OpenAI')
def test_call_ai_classification_success(mock_openai_class):
    """测试AI分类调用（成功场景）"""
    print("测试: AI分类调用（成功）...")
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client.chat.completions.create.return_value = mock_response
    
    result = call_ai_classification(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}\n维度：{dimensions}",
        item_name="血常规检查",
        dimensions=[
            {"id": 1, "name": "检验类", "path": "医技项目/检验类"},
            {"id": 2, "name": "检查类", "path": "医技项目/检查类"}
        ]
    )
    
    assert result["dimension_id"] == 1
    assert result["confidence"] == 0.95
    
    # 验证OpenAI客户端被正确创建
    mock_openai_class.assert_called_once()
    call_kwargs = mock_openai_class.call_args[1]
    assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"
    assert call_kwargs["api_key"] == "test-key"
    
    # 验证chat.completions.create被调用
    mock_client.chat.completions.create.assert_called_once()
    create_kwargs = mock_client.chat.completions.create.call_args[1]
    assert create_kwargs["model"] == "deepseek-chat"
    assert len(create_kwargs["messages"]) == 2
    assert "血常规检查" in create_kwargs["messages"][1]["content"]
    
    print("  ✓ 通过")


@patch('app.utils.ai_interface.OpenAI')
@patch('app.utils.ai_interface.time.sleep')
def test_call_ai_classification_retry(mock_sleep, mock_openai_class):
    """测试AI分类调用（连接错误重试）"""
    print("测试: AI分类调用（连接错误重试）...")
    from openai import APIConnectionError
    
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # 创建一个模拟的APIConnectionError
    connection_error = APIConnectionError(request=Mock())
    
    # 第一次失败，第二次成功
    mock_client.chat.completions.create.side_effect = [
        connection_error,
        mock_response
    ]
    
    result = call_ai_classification(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}",
        item_name="血常规检查",
        dimensions=[{"id": 1, "name": "检验类", "path": "医技项目/检验类"}],
        max_retries=2
    )
    
    assert result["dimension_id"] == 1
    assert mock_client.chat.completions.create.call_count == 2
    assert mock_sleep.call_count == 1
    print("  ✓ 通过")


@patch('app.utils.ai_interface.call_ai_classification')
def test_test_ai_connection_success(mock_call_ai):
    """测试AI连接测试功能（成功）"""
    print("测试: AI连接测试（成功）...")
    mock_call_ai.return_value = {"dimension_id": 1, "confidence": 0.95}
    
    result = test_ai_connection(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}\n维度：{dimensions}"
    )
    
    assert result["success"] is True
    assert "成功" in result["message"]
    assert result["test_item"] == "血常规检查"
    assert result["response"]["dimension_id"] == 1
    print("  ✓ 通过")


@patch('app.utils.ai_interface.call_ai_classification')
def test_test_ai_connection_failure(mock_call_ai):
    """测试AI连接测试功能（失败）"""
    print("测试: AI连接测试（失败）...")
    mock_call_ai.side_effect = AIConnectionError("Connection failed")
    
    result = test_ai_connection(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}"
    )
    
    assert result["success"] is False
    assert "连接失败" in result["message"]
    assert result["error_type"] == "connection_error"
    print("  ✓ 通过")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试AI接口集成功能")
    print("=" * 60)
    print()
    
    try:
        test_build_dimensions_json()
        test_render_prompt_template()
        test_parse_ai_response_success()
        test_parse_ai_response_missing_confidence()
        test_parse_ai_response_invalid_json()
        test_parse_ai_response_missing_dimension_id()
        test_call_ai_classification_success()
        test_call_ai_classification_retry()
        test_test_ai_connection_success()
        test_test_ai_connection_failure()
        
        print()
        print("=" * 60)
        print("所有测试通过！✓")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"测试失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
