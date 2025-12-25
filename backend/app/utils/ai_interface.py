"""
AI接口集成模块

提供与AI服务（DeepSeek/OpenAI Compatible API）的集成功能
使用 requests 直接调用 API，避免 OpenAI SDK 被某些中转服务商屏蔽
"""
import json
import logging
import time
import requests
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AIClassificationError(Exception):
    """AI分类错误基类"""
    pass


class AIConnectionError(AIClassificationError):
    """AI连接错误"""
    pass


class AIResponseError(AIClassificationError):
    """AI响应错误"""
    pass


class AIRateLimitError(AIClassificationError):
    """AI限流错误"""
    pass


def call_ai_classification(
    api_endpoint: str,
    api_key: str,
    prompt_template: str,
    item_name: str,
    dimensions: List[Dict[str, Any]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 30.0,
    model_name: str = "deepseek-chat",
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    调用AI接口进行单个医技项目分类（兼容旧接口）
    
    Args:
        api_endpoint: API访问端点
        api_key: API密钥
        prompt_template: 提示词模板
        item_name: 医技项目名称
        dimensions: 可选维度列表
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        timeout: 请求超时时间（秒）
        model_name: AI模型名称
        system_prompt: 系统提示词
    
    Returns:
        包含dimension_id和confidence的字典
    """
    # 调用批量接口处理单个项目
    results = call_ai_classification_batch(
        api_endpoint=api_endpoint,
        api_key=api_key,
        prompt_template=prompt_template,
        items=[{"id": 0, "name": item_name}],
        dimensions=dimensions,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
        model_name=model_name,
        system_prompt=system_prompt
    )
    
    if results and len(results) > 0:
        return results[0]
    else:
        raise AIResponseError("AI未返回分类结果")


def call_ai_classification_batch(
    api_endpoint: str,
    api_key: str,
    prompt_template: str,
    items: List[Dict[str, Any]],
    dimensions: List[Dict[str, Any]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 60.0,
    model_name: str = "deepseek-chat",
    system_prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    批量调用AI接口进行医技项目分类（节省Token）
    
    Args:
        api_endpoint: API访问端点（如 https://api.deepseek.com/v1）
        api_key: API密钥
        prompt_template: 用户提示词模板（包含{items}和{dimensions}占位符）
        items: 待分类项目列表，每个项目包含id和name字段
        dimensions: 可选维度列表，每个维度包含id、name、path字段
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        timeout: 请求超时时间（秒）
        model_name: AI模型名称
        system_prompt: 系统提示词（可选）
    
    Returns:
        分类结果列表，每个结果包含item_id、dimension_id和confidence
        
    Raises:
        AIConnectionError: 连接失败
        AIResponseError: 响应解析失败
        AIRateLimitError: 达到限流
    """
    # 构建维度列表JSON
    dimensions_json = _build_dimensions_json(dimensions)
    
    # 构建项目列表JSON
    items_json = _build_items_json(items)
    
    # 替换提示词模板中的占位符
    final_prompt = _render_prompt_template_batch(prompt_template, items_json, dimensions_json)
    
    # 使用自定义系统提示词或默认值
    default_system = '你是一个医技项目分类专家。请根据提供的医技项目列表和可选维度列表，为每个项目判断最适合归属的维度，并给出确信度（0-1之间的小数）。必须返回JSON格式：{"results": [{"item_id": <项目ID>, "dimension_id": <维度ID>, "confidence": <确信度>}, ...]}'
    actual_system_prompt = system_prompt if system_prompt else default_system
    
    # 调用通用 API 函数
    response_data = _call_openai_compatible_api(
        api_endpoint=api_endpoint,
        api_key=api_key,
        model_name=model_name,
        messages=[
            {"role": "system", "content": actual_system_prompt},
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.3,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout
    )
    
    # 解析响应
    results = _parse_ai_response_batch_from_dict(response_data, items, dimensions)
    
    logger.info(f"AI批量分类成功: 处理 {len(results)} 个项目")
    return results


def _call_openai_compatible_api(
    api_endpoint: str,
    api_key: str,
    model_name: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 60.0
) -> Dict[str, Any]:
    """
    使用 requests 直接调用 OpenAI 兼容 API
    
    避免 OpenAI SDK 被某些中转服务商屏蔽的问题
    
    Args:
        api_endpoint: API 基础端点（如 https://api.deepseek.com/v1）
        api_key: API 密钥
        model_name: 模型名称
        messages: 消息列表
        temperature: 温度参数
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        timeout: 请求超时时间（秒）
    
    Returns:
        API 响应的 JSON 数据
        
    Raises:
        AIConnectionError: 连接失败
        AIResponseError: 响应错误
        AIRateLimitError: 达到限流
    """
    # 构建完整的 API URL
    # api_endpoint 应只包含基础路径（如 https://api.deepseek.com/v1）
    # 代码会自动追加 /chat/completions
    url = f"{api_endpoint.rstrip('/')}/chat/completions"
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 请求体
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature
    }
    
    # 调试日志：打印请求详情
    logger.info("=" * 60)
    logger.info("AI 请求调试信息")
    logger.info("=" * 60)
    logger.info(f"API 端点: {url}")
    logger.info(f"模型: {model_name}")
    logger.info(f"温度: {temperature}")
    logger.info(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '****'}")
    logger.info("-" * 60)
    
    # 打印每条消息
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        logger.info(f"消息 {i + 1} [{role}]:")
        # 如果内容太长，截断显示
        if len(content) > 2000:
            logger.info(f"{content[:2000]}...\n[内容已截断，总长度: {len(content)} 字符]")
        else:
            logger.info(content)
        logger.info("-" * 60)
    
    logger.info("=" * 60)
    
    # 重试机制
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"调用AI接口 (尝试 {attempt + 1}/{max_retries}): {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            # 检查状态码
            if response.status_code == 429:
                logger.warning(f"AI接口限流 (尝试 {attempt + 1}/{max_retries})")
                last_error = AIRateLimitError("达到API限流")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                continue
            
            if response.status_code == 403:
                error_text = response.text
                logger.error(f"AI接口返回403 (尝试 {attempt + 1}/{max_retries}): {error_text}")
                last_error = AIResponseError(f"API访问被拒绝: {error_text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"AI接口返回错误 (尝试 {attempt + 1}/{max_retries}): {response.status_code} - {error_text}")
                last_error = AIResponseError(f"API返回错误 {response.status_code}: {error_text}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
            
            # 解析响应
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"AI响应不是有效的JSON: {response.text[:500]}")
                last_error = AIResponseError(f"响应格式错误: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                continue
            
            # 调试日志：打印响应详情
            logger.info("=" * 60)
            logger.info("AI 响应调试信息")
            logger.info("=" * 60)
            logger.info(f"状态码: {response.status_code}")
            
            # 打印 usage 信息
            usage = response_data.get("usage", {})
            if usage:
                logger.info(f"Token 使用: prompt={usage.get('prompt_tokens', 0)}, "
                           f"completion={usage.get('completion_tokens', 0)}, "
                           f"total={usage.get('total_tokens', 0)}")
            
            # 打印响应内容
            choices = response_data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                logger.info(f"响应内容长度: {len(content)} 字符")
                # 如果内容太长，截断显示
                if len(content) > 2000:
                    logger.info(f"响应内容（截断）:\n{content[:2000]}...\n[内容已截断]")
                else:
                    logger.info(f"响应内容:\n{content}")
            
            logger.info("=" * 60)
            
            return response_data
            
        except requests.exceptions.Timeout:
            logger.warning(f"AI接口超时 (尝试 {attempt + 1}/{max_retries})")
            last_error = AIConnectionError("请求超时")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"AI接口连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            last_error = AIConnectionError(f"无法连接到AI服务: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                
        except Exception as e:
            logger.error(f"AI接口调用异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}", exc_info=True)
            last_error = AIClassificationError(f"AI调用失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    raise last_error


def _build_items_json(items: List[Dict[str, Any]]) -> str:
    """构建项目列表JSON字符串"""
    item_list = []
    for item in items:
        item_list.append({
            "id": item.get("id"),
            "name": item.get("name")
        })
    return json.dumps(item_list, ensure_ascii=False, indent=2)


def _render_prompt_template_batch(
    template: str,
    items_json: str,
    dimensions_json: str
) -> str:
    """渲染批量提示词模板"""
    rendered = template.replace("{items}", items_json)
    rendered = rendered.replace("{dimensions}", dimensions_json)
    # 兼容旧模板的单项目占位符
    rendered = rendered.replace("{item_name}", items_json)
    return rendered


def _parse_ai_response_batch_from_dict(
    response_data: Dict[str, Any],
    items: List[Dict[str, Any]],
    dimensions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    从字典格式的 API 响应中解析批量分类结果
    
    Args:
        response_data: API 响应的 JSON 数据（字典格式）
        items: 原始项目列表
        dimensions: 维度列表
    
    Returns:
        分类结果列表，每个结果包含item_id、dimension_id和confidence
    """
    try:
        choices = response_data.get("choices", [])
        if not choices:
            raise AIResponseError("AI响应为空")
        
        message = choices[0].get("message", {})
        content = message.get("content", "")
        
        if not content:
            raise AIResponseError("AI响应内容为空")
        
        # DeepSeek R1 模型可能返回带有 <think> 标签的内容，需要提取 JSON 部分
        # 尝试找到 JSON 内容
        json_content = content
        
        # 如果内容包含 <think> 标签，尝试提取 JSON
        if "<think>" in content:
            # 尝试在 </think> 之后找 JSON
            import re
            # 查找 JSON 对象或数组
            json_match = re.search(r'(\{[^{}]*"results"[^{}]*\[.*?\]\s*\}|\[.*?\])', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                # 如果没找到，尝试去掉 think 标签后解析
                json_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        try:
            result = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"AI响应不是有效的JSON: {content[:500]}")
            raise AIResponseError(f"AI响应格式错误: {str(e)}")
        
        # 支持两种格式：{results: [...]} 或直接 [...]
        if isinstance(result, dict):
            results = result.get("results", [])
        elif isinstance(result, list):
            results = result
        else:
            # 单项目响应兼容
            results = [result]
        
        # 构建 item_name -> item_id 映射
        name_to_id = {item.get("name"): item.get("id") for item in items}
        
        # 验证和规范化结果
        normalized_results = []
        
        for r in results:
            # 优先使用 item_name 匹配，其次使用 item_id
            item_name = r.get("item_name")
            item_id = r.get("item_id")
            
            # 通过 item_name 查找对应的 item_id
            if item_name and item_name in name_to_id:
                item_id = name_to_id[item_name]
            elif item_id is None:
                item_id = 0
            
            dimension_id = r.get("dimension_id")
            confidence = float(r.get("confidence", 0.0))
            
            if dimension_id is None:
                logger.warning(f"AI响应缺少dimension_id: {r}")
                continue
            
            confidence = max(0.0, min(1.0, confidence))
            
            normalized_results.append({
                "item_id": item_id,
                "item_name": item_name,
                "dimension_id": dimension_id,
                "confidence": confidence
            })
        
        return normalized_results
        
    except AIResponseError:
        raise
    except Exception as e:
        logger.error(f"解析AI批量响应异常: {str(e)}", exc_info=True)
        raise AIResponseError(f"解析AI响应失败: {str(e)}")


def _build_dimensions_json(dimensions: List[Dict[str, Any]]) -> str:
    """
    构建维度列表JSON字符串
    
    Args:
        dimensions: 维度列表，每个维度应包含id、name、path等字段
        
    Returns:
        格式化的JSON字符串
    """
    dimension_list = []
    for dim in dimensions:
        dimension_list.append({
            "id": dim.get("id") or dim.get("dimension_id"),
            "name": dim.get("name") or dim.get("dimension_name"),
            "path": dim.get("path") or dim.get("full_path", "")
        })
    
    return json.dumps(dimension_list, ensure_ascii=False, indent=2)


def _render_prompt_template(
    template: str,
    item_name: str,
    dimensions_json: str
) -> str:
    """
    渲染提示词模板，替换占位符
    
    Args:
        template: 提示词模板
        item_name: 项目名称
        dimensions_json: 维度列表JSON字符串
        
    Returns:
        渲染后的提示词
    """
    # 替换占位符
    rendered = template.replace("{item_name}", item_name)
    rendered = rendered.replace("{dimensions}", dimensions_json)
    
    return rendered


def _parse_ai_response(
    response: Any,
    dimensions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    解析AI响应，提取dimension_id和confidence
    
    Args:
        response: OpenAI API响应对象
        dimensions: 维度列表（用于验证返回的维度ID是否有效）
        
    Returns:
        包含dimension_id和confidence的字典
        
    Raises:
        AIResponseError: 响应格式错误或解析失败
    """
    try:
        # 获取响应内容
        if not response.choices or len(response.choices) == 0:
            raise AIResponseError("AI响应为空")
        
        content = response.choices[0].message.content
        if not content:
            raise AIResponseError("AI响应内容为空")
        
        # 解析JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"AI响应不是有效的JSON: {content}")
            raise AIResponseError(f"AI响应格式错误，无法解析JSON: {str(e)}")
        
        # 提取必需字段
        if "dimension_id" not in result:
            raise AIResponseError(f"AI响应缺少dimension_id字段: {content}")
        
        dimension_id = result["dimension_id"]
        confidence = float(result.get("confidence", 0.0))
        
        # 验证confidence范围
        if not (0.0 <= confidence <= 1.0):
            logger.warning(f"AI返回的确信度超出范围[0,1]: {confidence}，将限制在有效范围内")
            confidence = max(0.0, min(1.0, confidence))
        
        # 验证dimension_id是否在可选维度列表中
        valid_dimension_ids = [
            dim.get("id") or dim.get("dimension_id") 
            for dim in dimensions
        ]
        
        if dimension_id not in valid_dimension_ids:
            logger.warning(
                f"AI返回的维度ID {dimension_id} 不在可选维度列表中: {valid_dimension_ids}"
            )
            # 不抛出异常，允许AI返回不在列表中的维度（可能是更合适的分类）
        
        return {
            "dimension_id": dimension_id,
            "confidence": confidence
        }
        
    except AIResponseError:
        raise
    except Exception as e:
        logger.error(f"解析AI响应时发生异常: {str(e)}", exc_info=True)
        raise AIResponseError(f"解析AI响应失败: {str(e)}")


def _clean_ai_text_response(content: str) -> str:
    """
    清理AI文本响应中的包装标记
    
    处理以下情况：
    1. <think>...</think> 标签（DeepSeek R1 模型）
    2. ```markdown ... ``` 代码块包裹
    3. ``` ... ``` 代码块包裹（无语言标识）
    
    Args:
        content: 原始AI响应内容
        
    Returns:
        清理后的内容
    """
    import re
    
    if not content:
        return content
    
    # 1. 移除 <think>...</think> 标签
    if "<think>" in content and "</think>" in content:
        content = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL).strip()
    
    # 2. 移除 Markdown 代码块包裹
    # 匹配 ```markdown 或 ```md 或 ``` 开头，``` 结尾的情况
    # 使用非贪婪匹配，处理整个内容被包裹的情况
    markdown_block_pattern = r'^```(?:markdown|md)?\s*\n?(.*?)\n?```\s*$'
    match = re.match(markdown_block_pattern, content.strip(), re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        logger.info("已移除AI响应中的Markdown代码块包裹")
    
    return content


def call_ai_text_generation(
    api_endpoint: str,
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 60.0,
    model_name: str = "deepseek-chat"
) -> str:
    """
    调用AI接口生成文本内容（用于报告生成等场景）
    
    Args:
        api_endpoint: API访问端点
        api_key: API密钥
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        timeout: 请求超时时间（秒）
        model_name: AI模型名称
    
    Returns:
        生成的文本内容
        
    Raises:
        AIConnectionError: 连接失败
        AIResponseError: 响应解析失败
        AIRateLimitError: 达到限流
    """
    # 调用通用 API 函数
    response_data = _call_openai_compatible_api(
        api_endpoint=api_endpoint,
        api_key=api_key,
        model_name=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,  # 文本生成使用稍高的温度以增加创造性
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout
    )
    
    # 解析响应
    choices = response_data.get("choices", [])
    if not choices:
        raise AIResponseError("AI响应为空")
    
    message = choices[0].get("message", {})
    content = message.get("content", "")
    
    if not content:
        raise AIResponseError("AI响应内容为空")
    
    # 清理AI响应中的包装标记（<think>标签、Markdown代码块等）
    content = _clean_ai_text_response(content)
    
    logger.info(f"AI文本生成成功: 内容长度={len(content)}")
    return content


def verify_ai_connection(
    api_endpoint: str,
    api_key: str,
    prompt_template: str,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    测试AI接口连接
    
    Args:
        api_endpoint: API访问端点
        api_key: API密钥
        prompt_template: 提示词模板
        timeout: 请求超时时间（秒）
        
    Returns:
        测试结果字典，包含success、message、response等字段
    """
    try:
        # 使用示例数据测试
        test_item_name = "血常规检查"
        test_dimensions = [
            {"id": 1, "name": "检验类", "path": "医技项目/检验类"},
            {"id": 2, "name": "检查类", "path": "医技项目/检查类"}
        ]
        
        result = call_ai_classification(
            api_endpoint=api_endpoint,
            api_key=api_key,
            prompt_template=prompt_template,
            item_name=test_item_name,
            dimensions=test_dimensions,
            max_retries=1,
            timeout=timeout
        )
        
        return {
            "success": True,
            "message": "AI接口连接成功",
            "test_item": test_item_name,
            "response": result
        }
        
    except AIConnectionError as e:
        return {
            "success": False,
            "message": f"连接失败: {str(e)}",
            "error_type": "connection_error"
        }
        
    except AIRateLimitError as e:
        return {
            "success": False,
            "message": f"限流错误: {str(e)}",
            "error_type": "rate_limit_error"
        }
        
    except AIResponseError as e:
        return {
            "success": False,
            "message": f"响应错误: {str(e)}",
            "error_type": "response_error"
        }
        
    except Exception as e:
        logger.error(f"测试AI接口时发生异常: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"未知错误: {str(e)}",
            "error_type": "unknown_error"
        }
