"""
AI分类任务Celery任务
"""
import time
import logging
from datetime import datetime
from typing import Tuple
from decimal import Decimal

from sqlalchemy.orm import Session
from celery.exceptions import SoftTimeLimitExceeded

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.classification_task import ClassificationTask, TaskStatus
from app.models.classification_plan import ClassificationPlan, PlanStatus
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.ai_interface import AIInterface
from app.models.ai_prompt_module import AIPromptModule, PromptModuleCode
from app.models.model_node import ModelNode
from app.models.model_version import ModelVersion
from app.models.charge_item import ChargeItem
from app.models.api_usage_log import APIUsageLog
from app.utils.encryption import decrypt_api_key
from app.utils.ai_interface import call_ai_classification_batch, AIClassificationError

logger = logging.getLogger(__name__)


def _get_classification_ai_config(db: Session, hospital_id: int) -> Tuple[str, str, str, str, str, float, int, int]:
    """
    获取分类任务的AI配置（使用ai_interfaces + ai_prompt_modules体系）
    
    Args:
        db: 数据库会话
        hospital_id: 医疗机构ID
        
    Returns:
        (api_endpoint, api_key, model_name, system_prompt, user_prompt, call_delay, daily_limit, batch_size) 元组
        
    Raises:
        ValueError: 如果没有找到有效的AI配置
    """
    # 查询分类模块配置
    module = db.query(AIPromptModule).filter(
        AIPromptModule.hospital_id == hospital_id,
        AIPromptModule.module_code == PromptModuleCode.CLASSIFICATION
    ).first()
    
    if not module:
        raise ValueError(
            "分类模块未配置，请先在「AI提示词模块」中配置分类模块（classification）"
        )
    
    if not module.user_prompt:
        raise ValueError(
            "分类模块的用户提示词未配置，请在「AI提示词模块」中配置分类模块的提示词"
        )
    
    if not module.ai_interface_id:
        raise ValueError(
            "分类模块未关联AI接口，请在「AI提示词模块」中为分类模块选择AI接口"
        )
    
    # 查询关联的AI接口
    ai_interface = db.query(AIInterface).filter(
        AIInterface.id == module.ai_interface_id,
        AIInterface.is_active == True
    ).first()
    
    if not ai_interface:
        raise ValueError(
            "分类模块关联的AI接口不存在或已禁用，请在「AI接口管理」中检查配置"
        )
    
    # 解密API密钥
    try:
        api_key = decrypt_api_key(ai_interface.api_key_encrypted)
    except Exception as e:
        raise ValueError(f"AI接口密钥解密失败: {str(e)}")
    
    logger.info(
        f"[AI分类任务] 加载AI配置: interface_id={ai_interface.id}, "
        f"module_code={PromptModuleCode.CLASSIFICATION}, model={ai_interface.model_name}"
    )
    
    return (
        ai_interface.api_endpoint,
        api_key,
        ai_interface.model_name,
        module.system_prompt,
        module.user_prompt,
        float(ai_interface.call_delay or 1.0),
        int(ai_interface.daily_limit or 10000),
        20  # 默认批次大小
    )


@celery_app.task(bind=True, max_retries=0, time_limit=7200, soft_time_limit=7000)
def classify_items_task(
    self,
    task_id: int,
    hospital_id: int
):
    """
    异步执行医技项目AI分类任务
    
    Args:
        task_id: 分类任务ID
        hospital_id: 医疗机构ID
        
    Task配置:
        max_retries: 0 - 不自动重试
        time_limit: 7200秒 - 硬超时限制（2小时）
        soft_time_limit: 7000秒 - 软超时限制（约116分钟）
    """
    db = SessionLocal()
    task = None
    
    try:
        logger.info(f"[AI分类任务] 开始执行任务 {task_id}, 医疗机构 {hospital_id}")
        
        # 1. 加载任务
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            logger.error(f"[AI分类任务] 任务不存在: task_id={task_id}, hospital_id={hospital_id}")
            return {"success": False, "error": "任务不存在"}
        
        # 更新任务状态为处理中
        task.status = TaskStatus.processing
        task.started_at = datetime.utcnow()
        db.commit()
        logger.info(f"[AI分类任务] 任务 {task_id} 状态更新为 processing")
        
        # 2. 加载AI配置
        try:
            (api_endpoint, api_key, model_name, system_prompt, prompt_template,
             call_delay, daily_limit, batch_size) = _get_classification_ai_config(db, hospital_id)
            logger.info(f"[AI分类任务] 加载AI配置: endpoint={api_endpoint}, model={model_name}")
        except ValueError as e:
            raise ValueError(str(e))
        
        # 3. 创建或获取分类预案
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.task_id == task_id
        ).first()
        
        if not plan:
            # 创建新预案
            plan = ClassificationPlan(
                hospital_id=hospital_id,
                task_id=task_id,
                status=PlanStatus.draft
            )
            db.add(plan)
            db.commit()
            logger.info(f"[AI分类任务] 创建分类预案 {plan.id}")
        
        # 4. 查询待处理项目（pending或failed）
        pending_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.processing_status.in_([ProcessingStatus.pending, ProcessingStatus.failed])
        ).all()
        
        if not pending_items:
            # 如果没有待处理项目，可能是首次执行，需要创建项目
            logger.info(f"[AI分类任务] 没有待处理项目，开始创建项目列表")
            pending_items = _create_plan_items(db, task, plan)
            
            if not pending_items:
                raise ValueError("没有找到符合条件的医技项目")
        
        logger.info(f"[AI分类任务] 找到 {len(pending_items)} 个待处理项目")
        
        # 5. 加载目标模型版本的末级维度
        dimensions = db.query(ModelNode).filter(
            ModelNode.version_id == task.model_version_id,
            ModelNode.is_leaf == True
        ).all()
        
        if not dimensions:
            raise ValueError(f"模型版本 {task.model_version_id} 没有末级维度")
        
        logger.info(f"[AI分类任务] 加载 {len(dimensions)} 个末级维度")
        
        # 构建维度列表（用于AI接口）
        dimension_list = []
        for dim in dimensions:
            # 构建路径：从父节点递归获取完整路径
            path_parts = [dim.name]
            current = dim
            while current.parent_id:
                parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
                if parent:
                    path_parts.insert(0, parent.name)
                    current = parent
                else:
                    break
            
            dimension_list.append({
                "id": dim.id,
                "name": dim.name,
                "path": " / ".join(path_parts)
            })
        
        # 6. 批量调用AI接口处理项目
        total_items = len(pending_items)
        processed_count = 0
        failed_count = 0
        
        # 使用从配置获取的限流参数（已在_get_classification_ai_config中获取）
        logger.info(
            f"[AI分类任务] 批量处理配置: 批次大小={batch_size}, "
            f"调用延迟={call_delay}秒, 每日限额={daily_limit}, 模型={model_name}"
        )
        
        # 将待处理项目分批
        for batch_start in range(0, total_items, batch_size):
            batch_end = min(batch_start + batch_size, total_items)
            batch_items = pending_items[batch_start:batch_end]
            
            try:
                # 检查每日限额
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_calls = db.query(APIUsageLog).filter(
                    APIUsageLog.hospital_id == hospital_id,
                    APIUsageLog.created_at >= today_start
                ).count()
                
                if today_calls >= daily_limit:
                    error_msg = f"已达到每日API调用限额 ({daily_limit} 次)，任务已暂停"
                    logger.warning(f"[AI分类任务] {error_msg}")
                    
                    task.status = TaskStatus.paused
                    task.error_message = error_msg
                    db.commit()
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "total": total_items,
                        "processed": processed_count,
                        "failed": failed_count,
                        "paused_at": batch_start
                    }
                
                logger.info(f"[AI分类任务] 处理批次 {batch_start//batch_size + 1}: 项目 {batch_start+1}-{batch_end}/{total_items}")
                
                # 更新批次内项目状态为处理中
                for item in batch_items:
                    item.processing_status = ProcessingStatus.processing
                db.commit()
                
                # 构建批量请求数据
                items_for_ai = [
                    {"id": item.id, "name": item.charge_item_name}
                    for item in batch_items
                ]
                
                # 批量调用AI接口
                call_start_time = datetime.utcnow()
                results = call_ai_classification_batch(
                    api_endpoint=api_endpoint,
                    api_key=api_key,
                    prompt_template=prompt_template,
                    items=items_for_ai,
                    dimensions=dimension_list,
                    max_retries=3,
                    timeout=60.0,
                    model_name=model_name,
                    system_prompt=system_prompt
                )
                call_duration = (datetime.utcnow() - call_start_time).total_seconds()
                
                # 构建结果映射：优先使用 item_name，其次使用 item_id
                result_by_id = {r['item_id']: r for r in results if r.get('item_id')}
                result_by_name = {r['item_name']: r for r in results if r.get('item_name')}
                
                # 处理每个项目的结果
                batch_processed = 0
                batch_failed = 0
                for item in batch_items:
                    # 优先通过 item_name 匹配，其次通过 item_id
                    result = result_by_name.get(item.charge_item_name) or result_by_id.get(item.id)
                    if result:
                        item.ai_suggested_dimension_id = result['dimension_id']
                        item.ai_confidence = Decimal(str(result['confidence']))
                        item.processing_status = ProcessingStatus.completed
                        item.error_message = None
                        batch_processed += 1
                        logger.debug(
                            f"[AI分类任务] 项目分类成功: {item.charge_item_name}, "
                            f"维度ID={result['dimension_id']}, 确信度={result['confidence']}"
                        )
                    else:
                        item.processing_status = ProcessingStatus.failed
                        item.error_message = "AI未返回该项目的分类结果"
                        batch_failed += 1
                        logger.warning(f"[AI分类任务] 项目无结果: {item.charge_item_name}")
                
                db.commit()
                processed_count += batch_processed
                failed_count += batch_failed
                
                logger.info(
                    f"[AI分类任务] 批次处理完成: 成功={batch_processed}, 失败={batch_failed}, "
                    f"耗时={call_duration:.2f}秒"
                )
                
                # 记录API使用日志（每批一条）
                try:
                    log = APIUsageLog(
                        hospital_id=hospital_id,
                        task_id=task_id,
                        charge_item_id=batch_items[0].charge_item_id,  # 使用批次第一个项目ID
                        request_data={
                            "batch_size": len(batch_items),
                            "item_names": [item.charge_item_name for item in batch_items],
                            "dimensions_count": len(dimension_list)
                        },
                        response_data={"results_count": len(results), "results": results},
                        status_code=200,
                        call_duration=call_duration
                    )
                    db.add(log)
                    db.commit()
                except Exception as log_error:
                    logger.warning(f"[AI分类任务] 记录API使用日志失败: {str(log_error)}")
                    db.rollback()
                
                # 更新任务进度
                task.processed_items = processed_count
                task.failed_items = failed_count
                db.commit()
                
                # 更新Celery任务状态
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': processed_count,
                        'total': total_items,
                        'failed': failed_count,
                        'batch': batch_start // batch_size + 1
                    }
                )
                
                # 批次间延迟
                if batch_end < total_items:
                    logger.debug(f"[AI分类任务] 批次间延迟 {call_delay} 秒")
                    time.sleep(call_delay)
                
            except AIClassificationError as e:
                # AI接口调用失败，整批标记为失败
                error_msg = str(e)
                logger.error(f"[AI分类任务] 批次处理失败: {error_msg}")
                
                for item in batch_items:
                    item.processing_status = ProcessingStatus.failed
                    item.error_message = error_msg
                    failed_count += 1
                db.commit()
                
                # 记录失败日志
                try:
                    log = APIUsageLog(
                        hospital_id=hospital_id,
                        task_id=task_id,
                        charge_item_id=batch_items[0].charge_item_id,
                        request_data={"batch_size": len(batch_items)},
                        response_data=None,
                        status_code=500,
                        error_message=error_msg
                    )
                    db.add(log)
                    db.commit()
                except Exception as log_error:
                    logger.warning(f"[AI分类任务] 记录失败日志失败: {str(log_error)}")
                    db.rollback()
                
                task.failed_items = failed_count
                db.commit()
                
                # 继续处理下一批
                continue
                
            except Exception as e:
                # 其他未预期的错误
                error_msg = f"未知错误: {str(e)}"
                logger.error(f"[AI分类任务] 批次处理异常: {error_msg}", exc_info=True)
                
                for item in batch_items:
                    item.processing_status = ProcessingStatus.failed
                    item.error_message = error_msg
                    failed_count += 1
                db.commit()
                
                task.failed_items = failed_count
                db.commit()
                
                # 继续处理下一批
                continue
        
        # 7. 完成后更新任务状态
        task.status = TaskStatus.completed
        task.completed_at = datetime.utcnow()
        task.processed_items = processed_count
        task.failed_items = failed_count
        db.commit()
        
        logger.info(
            f"[AI分类任务] 任务 {task_id} 执行完成: "
            f"总数={total_items}, 成功={processed_count}, 失败={failed_count}"
        )
        
        return {
            "success": True,
            "message": "分类任务完成",
            "total": total_items,
            "processed": processed_count,
            "failed": failed_count
        }
        
    except SoftTimeLimitExceeded:
        # 任务超时
        error_msg = "任务执行超时（超过116分钟）"
        logger.error(f"[AI分类任务] 任务 {task_id} 超时")
        
        try:
            db.rollback()
            if not task:
                task = db.query(ClassificationTask).filter(
                    ClassificationTask.id == task_id
                ).first()
            
            if task and task.status != TaskStatus.failed:
                task.status = TaskStatus.paused
                task.error_message = error_msg
                db.commit()
                logger.info(f"[AI分类任务] 任务 {task_id} 状态更新为 paused（超时）")
        except Exception as commit_error:
            logger.error(f"[AI分类任务] 更新任务超时状态失败: {str(commit_error)}")
        
        return {"success": False, "error": error_msg}
        
    except Exception as e:
        # 捕获所有其他异常
        error_msg = str(e)
        logger.error(f"[AI分类任务] 任务 {task_id} 执行异常: {error_msg}", exc_info=True)
        
        try:
            db.rollback()
            if not task:
                task = db.query(ClassificationTask).filter(
                    ClassificationTask.id == task_id
                ).first()
            
            if task and task.status != TaskStatus.failed:
                task.status = TaskStatus.failed
                task.error_message = error_msg
                task.completed_at = datetime.utcnow()
                db.commit()
                logger.info(f"[AI分类任务] 任务 {task_id} 状态更新为 failed")
        except Exception as commit_error:
            logger.error(f"[AI分类任务] 更新任务失败状态失败: {str(commit_error)}")
        
        return {"success": False, "error": error_msg}
        
    finally:
        try:
            db.close()
        except Exception:
            pass


def _create_plan_items(
    db: Session,
    task: ClassificationTask,
    plan: ClassificationPlan
) -> list:
    """
    创建预案项目列表
    
    Args:
        db: 数据库会话
        task: 分类任务
        plan: 分类预案
        
    Returns:
        创建的预案项目列表
    """
    logger.info(f"[AI分类任务] 开始创建预案项目，收费类别: {task.charge_categories}")
    
    # 查询符合条件的医技项目
    charge_items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == task.hospital_id,
        ChargeItem.item_category.in_(task.charge_categories)
    ).all()
    
    if not charge_items:
        logger.warning(f"[AI分类任务] 没有找到符合条件的收费项目")
        return []
    
    logger.info(f"[AI分类任务] 找到 {len(charge_items)} 个收费项目")
    
    # 创建预案项目（分批提交避免批量插入类型转换问题）
    plan_items = []
    batch_size = 50
    for i, charge_item in enumerate(charge_items):
        plan_item = PlanItem(
            hospital_id=task.hospital_id,
            plan_id=plan.id,
            charge_item_id=charge_item.id,
            charge_item_name=charge_item.item_name,
            processing_status=ProcessingStatus.pending
        )
        db.add(plan_item)
        plan_items.append(plan_item)
        
        # 每 batch_size 条提交一次
        if (i + 1) % batch_size == 0:
            db.flush()
    
    # 更新任务总项目数
    task.total_items = len(plan_items)
    
    db.commit()
    logger.info(f"[AI分类任务] 创建 {len(plan_items)} 个预案项目")
    
    return plan_items


@celery_app.task(bind=True, max_retries=0, time_limit=7200, soft_time_limit=7000)
def continue_classification_task(
    self,
    task_id: int,
    hospital_id: int
):
    """
    继续执行中断的分类任务（断点续传）
    
    Args:
        task_id: 分类任务ID
        hospital_id: 医疗机构ID
        
    Task配置:
        max_retries: 0 - 不自动重试
        time_limit: 7200秒 - 硬超时限制（2小时）
        soft_time_limit: 7000秒 - 软超时限制（约116分钟）
    """
    logger.info(f"[AI分类任务] 继续执行任务 {task_id}, 医疗机构 {hospital_id}")
    
    # 复用classify_items_task的逻辑
    # classify_items_task会自动跳过已完成的项目，只处理pending和failed的项目
    return classify_items_task(self, task_id, hospital_id)
