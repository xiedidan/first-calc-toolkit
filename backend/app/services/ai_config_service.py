"""
AI配置服务
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.ai_config import AIConfig
from app.models.api_usage_log import APIUsageLog
from app.schemas.ai_config import (
    AIConfigCreate,
    AIConfigUpdate,
    AIConfigResponse,
    AIConfigTest,
    APIUsageStatsResponse,
)
from app.utils.encryption import encrypt_api_key, decrypt_api_key, mask_api_key
from app.utils.ai_interface import call_ai_classification


class AIConfigService:
    """AI配置服务"""
    
    # 默认系统提示词
    DEFAULT_SYSTEM_PROMPT = """你是一个医院收费项目分类专家。请根据提供的医技项目列表和可选维度列表，为每个项目判断最适合归属的维度，并给出确信度（0-1之间的小数）。必须返回JSON格式：{"results": [{"item_id": <项目ID>, "dimension_id": <维度ID>, "confidence": <确信度>}, ...]}"""

    # 默认用户提示词模板（批量处理）
    DEFAULT_PROMPT_TEMPLATE = """请为以下医技项目分类：

待分类项目列表：
{items}

可选维度列表：
{dimensions}

请返回JSON格式的分类结果。"""

    @staticmethod
    def get_config(db: Session, hospital_id: int) -> Optional[AIConfigResponse]:
        """
        获取AI配置（返回掩码密钥）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            
        Returns:
            AI配置响应对象，如果不存在则自动创建默认配置
        """
        config = db.query(AIConfig).filter(
            AIConfig.hospital_id == hospital_id
        ).first()
        
        if not config:
            # 自动创建默认配置
            config = AIConfig(
                hospital_id=hospital_id,
                api_endpoint="https://api.deepseek.com/v1",
                model_name="deepseek-chat",
                api_key_encrypted=encrypt_api_key("请输入您的API密钥"),  # 占位符
                system_prompt=AIConfigService.DEFAULT_SYSTEM_PROMPT,
                prompt_template=AIConfigService.DEFAULT_PROMPT_TEMPLATE,
                call_delay=1.0,
                daily_limit=10000,
                batch_size=20,
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        
        # 返回掩码密钥
        return AIConfigResponse(
            id=config.id,
            hospital_id=config.hospital_id,
            api_endpoint=config.api_endpoint,
            model_name=config.model_name or "deepseek-chat",
            api_key_masked=mask_api_key(config.api_key_encrypted),
            system_prompt=config.system_prompt,
            prompt_template=config.prompt_template,
            call_delay=config.call_delay,
            daily_limit=config.daily_limit,
            batch_size=config.batch_size,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
    
    @staticmethod
    def create_or_update_config(
        db: Session,
        hospital_id: int,
        config_data: AIConfigCreate
    ) -> AIConfigResponse:
        """
        创建或更新AI配置（加密密钥）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            config_data: AI配置数据
            
        Returns:
            AI配置响应对象
        """
        # 查找现有配置
        config = db.query(AIConfig).filter(
            AIConfig.hospital_id == hospital_id
        ).first()
        
        if config:
            # 更新现有配置
            config.api_endpoint = config_data.api_endpoint
            config.model_name = config_data.model_name
            # 只有当提供了新密钥时才更新（空字符串表示不更新）
            if config_data.api_key:
                config.api_key_encrypted = encrypt_api_key(config_data.api_key)
            config.system_prompt = config_data.system_prompt
            config.prompt_template = config_data.prompt_template
            config.call_delay = config_data.call_delay
            config.daily_limit = config_data.daily_limit
            config.batch_size = config_data.batch_size
            config.updated_at = datetime.utcnow()
        else:
            # 创建新配置时必须提供密钥
            if not config_data.api_key:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="创建配置时必须提供API密钥"
                )
            encrypted_key = encrypt_api_key(config_data.api_key)
            config = AIConfig(
                hospital_id=hospital_id,
                api_endpoint=config_data.api_endpoint,
                model_name=config_data.model_name,
                api_key_encrypted=encrypted_key,
                system_prompt=config_data.system_prompt,
                prompt_template=config_data.prompt_template,
                call_delay=config_data.call_delay,
                daily_limit=config_data.daily_limit,
                batch_size=config_data.batch_size,
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        # 返回掩码密钥
        return AIConfigResponse(
            id=config.id,
            hospital_id=config.hospital_id,
            api_endpoint=config.api_endpoint,
            model_name=config.model_name or "deepseek-chat",
            api_key_masked=mask_api_key(config.api_key_encrypted),
            system_prompt=config.system_prompt,
            prompt_template=config.prompt_template,
            call_delay=config.call_delay,
            daily_limit=config.daily_limit,
            batch_size=config.batch_size,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
    
    @staticmethod
    def test_config(
        db: Session,
        hospital_id: int,
        test_data: AIConfigTest
    ) -> Dict[str, Any]:
        """
        测试AI配置
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            test_data: 测试数据
            
        Returns:
            测试结果
        """
        # 获取配置
        config = db.query(AIConfig).filter(
            AIConfig.hospital_id == hospital_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI配置不存在，请先配置"
            )
        
        # 解密API密钥
        api_key = decrypt_api_key(config.api_key_encrypted)
        
        # 构建测试维度列表
        test_dimensions = [
            {"id": 1, "name": "检查费", "path": "医技/检查费"},
            {"id": 2, "name": "放射费", "path": "医技/放射费"},
            {"id": 3, "name": "化验费", "path": "医技/化验费"},
        ]
        
        try:
            # 调用AI接口
            start_time = datetime.utcnow()
            result = call_ai_classification(
                api_endpoint=config.api_endpoint,
                api_key=api_key,
                prompt_template=config.prompt_template,
                item_name=test_data.test_item_name,
                dimensions=test_dimensions,
                model_name=config.model_name or "deepseek-chat"
            )
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "message": "测试成功",
                "result": result,
                "duration": duration,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"测试失败: {str(e)}",
                "error": str(e),
            }
    
    @staticmethod
    def get_usage_stats(
        db: Session,
        hospital_id: int,
        days: int = 30,
        cost_per_call: float = 0.001
    ) -> APIUsageStatsResponse:
        """
        获取API使用统计
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            days: 统计天数
            cost_per_call: 每次调用成本（元），默认0.001元
            
        Returns:
            使用统计响应对象
        """
        # 计算起始日期
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 查询总调用次数
        total_calls = db.query(func.count(APIUsageLog.id)).filter(
            APIUsageLog.hospital_id == hospital_id,
            APIUsageLog.created_at >= start_date
        ).scalar() or 0
        
        # 查询成功调用次数
        successful_calls = db.query(func.count(APIUsageLog.id)).filter(
            APIUsageLog.hospital_id == hospital_id,
            APIUsageLog.created_at >= start_date,
            APIUsageLog.status_code == 200
        ).scalar() or 0
        
        # 查询失败调用次数
        failed_calls = total_calls - successful_calls
        
        # 查询今日调用次数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_calls = db.query(func.count(APIUsageLog.id)).filter(
            APIUsageLog.hospital_id == hospital_id,
            APIUsageLog.created_at >= today_start
        ).scalar() or 0
        
        # 查询平均响应时间
        avg_duration = db.query(func.avg(APIUsageLog.call_duration)).filter(
            APIUsageLog.hospital_id == hospital_id,
            APIUsageLog.created_at >= start_date,
            APIUsageLog.status_code == 200
        ).scalar() or 0.0
        
        # 获取配置的每日限额
        config = db.query(AIConfig).filter(
            AIConfig.hospital_id == hospital_id
        ).first()
        daily_limit = config.daily_limit if config else 10000
        
        # 计算预估成本（可配置单价）
        estimated_cost = total_calls * cost_per_call
        
        return APIUsageStatsResponse(
            total_calls=total_calls,
            successful_calls=successful_calls,
            failed_calls=failed_calls,
            today_calls=today_calls,
            daily_limit=daily_limit,
            avg_duration=float(avg_duration),
            estimated_cost=estimated_cost,
            period_days=days,
        )
