"""
测试AI接口集成功能

测试call_ai_classification函数的各种场景
"""
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.app.utils.ai_interface import (
    call_ai_classification,
    verify_ai_connection,
    _build_dimensions_json,
    _render_prompt_template,
    _parse_ai_response,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError
)


def test_build_dimensions_json():
    """测试维度列表JSON构建"""
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
    assert parsed[1]["id"] == 2
    print("✓ 维度列表JSON构建测试通过")


def test_build_dimensions_json_with_alternative_keys():
    """测试维度列表JSON构建（使用备选字段名）"""
    dimensions = [
        {"dimension_id": 1, "dimension_name": "检验类", "full_path": "医技项目/检验类"}
    ]
    
    result = _build_dimensions_json(dimensions)
    parsed = json.loads(result)
    
    assert parsed[0]["id"] == 1
    assert parsed[0]["name"] == "检验类"
    assert parsed[0]["path"] == "医技项目/检验类"
    print("✓ 维度列表JSON构建（备选字段）测试通过")


def test_render_prompt_template():
    """测试提示词模板渲染"""
    template = "请对以下医技项目进行分类：{item_name}\n可选维度：{dimensions}"
    item_name = "血常规检查"
    dimensions_json = '[{"id": 1, "name": "检验类"}]'
    
    result = _render_prompt_template(template, item_name, dimensions_json)
    
    assert "{item_name}" not in result
    assert "{dimensions}" not in result
    assert "血常规检查" in result
    assert '[{"id": 1, "name": "检验类"}]' in result
    print("✓ 提示词模板渲染测试通过")


def test_parse_ai_response_success():
    """测试AI响应解析（成功场景）"""
    # 模拟OpenAI响应对象
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
    print("✓ AI响应解析（成功）测试通过")


def test_parse_ai_response_missing_confidence():
    """测试AI响应解析（缺少confidence字段）"""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    result = _parse_ai_response(mock_response, dimensions)
    
    assert result["dimension_id"] == 1
    assert result["confidence"] == 0.0  # 默认值
    print("✓ AI响应解析（缺少confidence）测试通过")


def test_parse_ai_response_invalid_confidence():
    """测试AI响应解析（confidence超出范围）"""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 1.5}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    result = _parse_ai_response(mock_response, dimensions)
    
    assert result["dimension_id"] == 1
    assert result["confidence"] == 1.0  # 限制在有效范围内
    print("✓ AI响应解析（confidence超出范围）测试通过")


def test_parse_ai_response_invalid_json():
    """测试AI响应解析（非JSON格式）"""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = 'This is not JSON'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    with pytest.raises(AIResponseError) as exc_info:
        _parse_ai_response(mock_response, dimensions)
    
    assert "无法解析JSON" in str(exc_info.value)
    print("✓ AI响应解析（非JSON格式）测试通过")


def test_parse_ai_response_missing_dimension_id():
    """测试AI响应解析（缺少dimension_id字段）"""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    with pytest.raises(AIResponseError) as exc_info:
        _parse_ai_response(mock_response, dimensions)
    
    assert "缺少dimension_id字段" in str(exc_info.value)
    print("✓ AI响应解析（缺少dimension_id）测试通过")


def test_parse_ai_response_empty():
    """测试AI响应解析（空响应）"""
    mock_response = Mock()
    mock_response.choices = []
    
    dimensions = [{"id": 1, "name": "检验类"}]
    
    with pytest.raises(AIResponseError) as exc_info:
        _parse_ai_response(mock_response, dimensions)
    
    assert "响应为空" in str(exc_info.value)
    print("✓ AI响应解析（空响应）测试通过")


@patch('backend.app.utils.ai_interface.OpenAI')
def test_call_ai_classification_success(mock_openai_class):
    """测试AI分类调用（成功场景）"""
    # 模拟OpenAI客户端
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    # 模拟响应
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client.chat.completions.create.return_value = mock_response
    
    # 调用函数
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
    
    print("✓ AI分类调用（成功）测试通过")


@patch('backend.app.utils.ai_interface.OpenAI')
@patch('backend.app.utils.ai_interface.time.sleep')  # Mock sleep to speed up test
def test_call_ai_classification_retry_on_connection_error(mock_sleep, mock_openai_class):
    """测试AI分类调用（连接错误重试）"""
    from openai import APIConnectionError
    from httpx import Request
    
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    # 第一次调用失败，第二次成功
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = '{"dimension_id": 1, "confidence": 0.95}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Create a proper APIConnectionError with request parameter
    mock_request = Request("POST", "https://api.deepseek.com/v1")
    connection_error = APIConnectionError(request=mock_request)
    
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
    assert mock_sleep.call_count == 1  # 重试前sleep一次
    print("✓ AI分类调用（连接错误重试）测试通过")


@patch('backend.app.utils.ai_interface.OpenAI')
@patch('backend.app.utils.ai_interface.time.sleep')
def test_call_ai_classification_max_retries_exceeded(mock_sleep, mock_openai_class):
    """测试AI分类调用（超过最大重试次数）"""
    from openai import APIConnectionError
    from httpx import Request
    
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    # 所有调用都失败
    mock_request = Request("POST", "https://api.deepseek.com/v1")
    connection_error = APIConnectionError(request=mock_request)
    mock_client.chat.completions.create.side_effect = connection_error
    
    with pytest.raises(AIConnectionError) as exc_info:
        call_ai_classification(
            api_endpoint="https://api.deepseek.com/v1",
            api_key="test-key",
            prompt_template="分类项目：{item_name}",
            item_name="血常规检查",
            dimensions=[{"id": 1, "name": "检验类", "path": "医技项目/检验类"}],
            max_retries=3
        )
    
    assert "无法连接到AI服务" in str(exc_info.value)
    assert mock_client.chat.completions.create.call_count == 3
    print("✓ AI分类调用（超过最大重试次数）测试通过")


@patch('backend.app.utils.ai_interface.OpenAI')
def test_call_ai_classification_rate_limit_error(mock_openai_class):
    """测试AI分类调用（限流错误）"""
    from openai import RateLimitError
    
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    
    mock_client.chat.completions.create.side_effect = RateLimitError(
        "Rate limit exceeded",
        response=Mock(status_code=429),
        body=None
    )
    
    with pytest.raises(AIRateLimitError) as exc_info:
        call_ai_classification(
            api_endpoint="https://api.deepseek.com/v1",
            api_key="test-key",
            prompt_template="分类项目：{item_name}",
            item_name="血常规检查",
            dimensions=[{"id": 1, "name": "检验类", "path": "医技项目/检验类"}],
            max_retries=1
        )
    
    assert "达到API限流" in str(exc_info.value)
    print("✓ AI分类调用（限流错误）测试通过")


@patch('backend.app.utils.ai_interface.call_ai_classification')
def test_test_ai_connection_success(mock_call_ai):
    """测试AI连接测试功能（成功）"""
    mock_call_ai.return_value = {"dimension_id": 1, "confidence": 0.95}
    
    result = verify_ai_connection(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}\n维度：{dimensions}"
    )
    
    assert result["success"] is True
    assert "成功" in result["message"]
    assert result["test_item"] == "血常规检查"
    assert result["response"]["dimension_id"] == 1
    print("✓ AI连接测试（成功）测试通过")


@patch('backend.app.utils.ai_interface.call_ai_classification')
def test_test_ai_connection_failure(mock_call_ai):
    """测试AI连接测试功能（失败）"""
    mock_call_ai.side_effect = AIConnectionError("Connection failed")
    
    result = verify_ai_connection(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="test-key",
        prompt_template="分类项目：{item_name}"
    )
    
    assert result["success"] is False
    assert "连接失败" in result["message"]
    assert result["error_type"] == "connection_error"
    print("✓ AI连接测试（失败）测试通过")


if __name__ == "__main__":
    print("开始测试AI接口集成功能...\n")
    
    # 运行所有测试
    test_build_dimensions_json()
    test_build_dimensions_json_with_alternative_keys()
    test_render_prompt_template()
    test_parse_ai_response_success()
    test_parse_ai_response_missing_confidence()
    test_parse_ai_response_invalid_confidence()
    test_parse_ai_response_invalid_json()
    test_parse_ai_response_missing_dimension_id()
    test_parse_ai_response_empty()
    test_call_ai_classification_success()
    test_call_ai_classification_retry_on_connection_error()
    test_call_ai_classification_max_retries_exceeded()
    test_call_ai_classification_rate_limit_error()
    test_test_ai_connection_success()
    test_test_ai_connection_failure()
    
    print("\n所有测试通过！✓")
