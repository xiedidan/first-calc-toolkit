"""
分类任务管理服务
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.models.classification_task import ClassificationTask, TaskStatus
from app.models.classification_plan import ClassificationPlan
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.task_progress import TaskProgress
from app.models.api_usage_log import APIUsageLog
from app.models.charge_item import ChargeItem
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.schemas.classification_task import (
    ClassificationTaskCreate,
    ClassificationTaskResponse,
    ClassificationTaskListResponse,
    TaskProgressResponse,
    TaskLogResponse,
    TaskProgressRecordResponse,
    ContinueTaskResponse,
)
from app.tasks.classification_tasks import classify_items_task, continue_classification_task

logger = logging.getLogger(__name__)


class ClassificationTaskService:
    """分类任务管理服务"""
    
    @staticmethod
    def create_task(
        db: Session,
        hospital_id: int,
        user_id: int,
        task_data: ClassificationTaskCreate
    ) -> ClassificationTaskResponse:
        """
        创建分类任务
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            user_id: 创建用户ID
            task_data: 任务创建数据
            
        Returns:
            创建的任务响应
            
        Raises:
            ValueError: 如果模型版本不存在或没有找到医技项目
        """
        logger.info(
            f"[分类任务服务] 创建任务: hospital_id={hospital_id}, "
            f"task_name={task_data.task_name}, "
            f"model_version_id={task_data.model_version_id}"
        )
        
        # 1. 验证模型版本是否存在且属于当前医疗机构
        model_version = db.query(ModelVersion).filter(
            ModelVersion.id == task_data.model_version_id,
            ModelVersion.hospital_id == hospital_id
        ).first()
        
        if not model_version:
            raise ValueError(f"模型版本 {task_data.model_version_id} 不存在或不属于当前医疗机构")
        
        # 2. 快速验证是否存在符合条件的医技项目（使用EXISTS而非COUNT，更快）
        has_items = db.query(
            db.query(ChargeItem.id).filter(
                ChargeItem.hospital_id == hospital_id,
                ChargeItem.item_category.in_(task_data.charge_categories)
            ).exists()
        ).scalar()
        
        if not has_items:
            raise ValueError(f"没有找到符合条件的医技项目（收费类别: {', '.join(task_data.charge_categories)}）")
        
        logger.info(f"[分类任务服务] 验证通过，存在符合条件的医技项目")
        
        # 3. 创建分类任务
        task = ClassificationTask(
            hospital_id=hospital_id,
            task_name=task_data.task_name,
            model_version_id=task_data.model_version_id,
            charge_categories=task_data.charge_categories,
            status=TaskStatus.pending,
            total_items=0,  # 将在Celery任务中更新
            processed_items=0,
            failed_items=0,
            created_by=user_id
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"[分类任务服务] 创建任务成功: task_id={task.id}")
        
        # 4. 启动Celery异步任务（使用apply_async设置超时，避免阻塞）
        try:
            celery_task = classify_items_task.apply_async(
                args=[task.id, hospital_id],
                retry=False,  # 不重试，避免阻塞
                ignore_result=True  # 不等待结果
            )
            task.celery_task_id = celery_task.id
            task.status = TaskStatus.processing
            db.commit()
            
            logger.info(f"[分类任务服务] 启动Celery任务: celery_task_id={celery_task.id}")
        except Exception as e:
            logger.error(f"[分类任务服务] 启动Celery任务失败: {str(e)}", exc_info=True)
            task.status = TaskStatus.failed
            task.error_message = f"启动异步任务失败: {str(e)}"
            db.commit()
        
        # 5. 构建响应
        return ClassificationTaskService._build_task_response(task)
    
    @staticmethod
    def get_tasks(
        db: Session,
        hospital_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> ClassificationTaskListResponse:
        """
        获取分类任务列表
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            skip: 跳过记录数
            limit: 返回记录数
            status: 任务状态筛选（可选）
            
        Returns:
            任务列表响应
        """
        logger.info(
            f"[分类任务服务] 查询任务列表: hospital_id={hospital_id}, "
            f"skip={skip}, limit={limit}, status={status}"
        )
        
        # 构建查询
        query = db.query(ClassificationTask).filter(
            ClassificationTask.hospital_id == hospital_id
        )
        
        # 状态筛选
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter(ClassificationTask.status == status_enum)
            except ValueError:
                logger.warning(f"[分类任务服务] 无效的状态值: {status}")
        
        # 总数
        total = query.count()
        
        # 分页查询
        tasks = query.order_by(desc(ClassificationTask.created_at)).offset(skip).limit(limit).all()
        
        # 构建响应
        items = [ClassificationTaskService._build_task_response(task) for task in tasks]
        
        logger.info(f"[分类任务服务] 查询到 {len(items)} 个任务，总数 {total}")
        
        return ClassificationTaskListResponse(total=total, items=items)
    
    @staticmethod
    def get_task_detail(
        db: Session,
        hospital_id: int,
        task_id: int
    ) -> ClassificationTaskResponse:
        """
        获取分类任务详情
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            task_id: 任务ID
            
        Returns:
            任务详情响应
            
        Raises:
            ValueError: 如果任务不存在
        """
        logger.info(f"[分类任务服务] 查询任务详情: task_id={task_id}, hospital_id={hospital_id}")
        
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise ValueError(f"任务 {task_id} 不存在或不属于当前医疗机构")
        
        return ClassificationTaskService._build_task_response(task)
    
    @staticmethod
    def delete_task(
        db: Session,
        hospital_id: int,
        task_id: int
    ) -> Dict[str, Any]:
        """
        删除分类任务
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            task_id: 任务ID
            
        Returns:
            删除结果
            
        Raises:
            ValueError: 如果任务不存在或正在处理中
        """
        logger.info(f"[分类任务服务] 删除任务: task_id={task_id}, hospital_id={hospital_id}")
        
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise ValueError(f"任务 {task_id} 不存在或不属于当前医疗机构")
        
        # 检查任务状态
        if task.status == TaskStatus.processing:
            raise ValueError("任务正在处理中，无法删除。请先暂停任务。")
        
        # 删除任务（级联删除关联的预案和进度记录）
        db.delete(task)
        db.commit()
        
        logger.info(f"[分类任务服务] 任务删除成功: task_id={task_id}")
        
        return {
            "success": True,
            "message": "任务删除成功"
        }
    
    @staticmethod
    def continue_task(
        db: Session,
        hospital_id: int,
        task_id: int
    ) -> ContinueTaskResponse:
        """
        继续处理中断的任务
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            task_id: 任务ID
            
        Returns:
            继续处理响应
            
        Raises:
            ValueError: 如果任务不存在或状态不允许继续
        """
        logger.info(f"[分类任务服务] 继续处理任务: task_id={task_id}, hospital_id={hospital_id}")
        
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise ValueError(f"任务 {task_id} 不存在或不属于当前医疗机构")
        
        # 检查任务状态
        if task.status not in [TaskStatus.failed, TaskStatus.paused]:
            raise ValueError(f"任务状态为 {task.status.value}，无法继续处理。只有失败或暂停的任务可以继续。")
        
        # 启动Celery任务（使用apply_async设置超时，避免阻塞）
        try:
            celery_task = continue_classification_task.apply_async(
                args=[task.id, hospital_id],
                retry=False,  # 不重试，避免阻塞
                ignore_result=True  # 不等待结果
            )
            task.celery_task_id = celery_task.id
            task.status = TaskStatus.processing
            task.error_message = None
            db.commit()
            
            logger.info(f"[分类任务服务] 继续处理任务成功: celery_task_id={celery_task.id}")
            
            return ContinueTaskResponse(
                success=True,
                message="任务已重新启动",
                celery_task_id=celery_task.id
            )
        except Exception as e:
            logger.error(f"[分类任务服务] 继续处理任务失败: {str(e)}", exc_info=True)
            return ContinueTaskResponse(
                success=False,
                message=f"启动任务失败: {str(e)}",
                celery_task_id=None
            )
    
    @staticmethod
    def get_task_progress(
        db: Session,
        hospital_id: int,
        task_id: int
    ) -> TaskProgressResponse:
        """
        获取任务实时进度
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            task_id: 任务ID
            
        Returns:
            任务进度响应
            
        Raises:
            ValueError: 如果任务不存在
        """
        logger.debug(f"[分类任务服务] 查询任务进度: task_id={task_id}, hospital_id={hospital_id}")
        
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise ValueError(f"任务 {task_id} 不存在或不属于当前医疗机构")
        
        # 计算进度百分比
        progress_percentage = 0.0
        if task.total_items > 0:
            progress_percentage = (task.processed_items / task.total_items) * 100
        
        # 查询当前正在处理的项目
        current_item_name = None
        if task.status == TaskStatus.processing:
            current_item = db.query(PlanItem).join(ClassificationPlan).filter(
                ClassificationPlan.task_id == task_id,
                PlanItem.processing_status == ProcessingStatus.processing
            ).first()
            
            if current_item:
                current_item_name = current_item.charge_item_name
        
        # 估算剩余时间（基于已处理项目的平均时间）
        estimated_remaining_time = None
        if task.status == TaskStatus.processing and task.processed_items > 0:
            # 计算已用时间
            if task.started_at:
                elapsed_seconds = (datetime.utcnow() - task.started_at).total_seconds()
                # 计算平均每项时间
                avg_time_per_item = elapsed_seconds / task.processed_items
                # 估算剩余时间
                remaining_items = task.total_items - task.processed_items
                estimated_remaining_time = int(avg_time_per_item * remaining_items)
        
        return TaskProgressResponse(
            task_id=task.id,
            status=task.status.value,
            total_items=task.total_items,
            processed_items=task.processed_items,
            failed_items=task.failed_items,
            progress_percentage=progress_percentage,
            current_item=current_item_name,
            estimated_remaining_time=estimated_remaining_time
        )
    
    @staticmethod
    def get_task_logs(
        db: Session,
        hospital_id: int,
        task_id: int
    ) -> TaskLogResponse:
        """
        获取任务处理日志
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            task_id: 任务ID
            
        Returns:
            任务日志响应
            
        Raises:
            ValueError: 如果任务不存在
        """
        logger.info(f"[分类任务服务] 查询任务日志: task_id={task_id}, hospital_id={hospital_id}")
        
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == task_id,
            ClassificationTask.hospital_id == hospital_id
        ).first()
        
        if not task:
            raise ValueError(f"任务 {task_id} 不存在或不属于当前医疗机构")
        
        # 计算执行时长
        duration = None
        if task.started_at:
            end_time = task.completed_at or datetime.utcnow()
            duration = int((end_time - task.started_at).total_seconds())
        
        # 查询失败的项目记录
        failed_items = db.query(PlanItem).join(ClassificationPlan).filter(
            ClassificationPlan.task_id == task_id,
            PlanItem.processing_status == ProcessingStatus.failed
        ).all()
        
        # 构建失败记录列表
        failed_records = []
        for item in failed_items:
            # 查询对应的收费项目名称
            charge_item = db.query(ChargeItem).filter(
                ChargeItem.id == item.charge_item_id
            ).first()
            
            failed_records.append(TaskProgressRecordResponse(
                id=item.id,
                task_id=task_id,
                charge_item_id=item.charge_item_id,
                charge_item_name=charge_item.item_name if charge_item else item.charge_item_name,
                status=item.processing_status.value,
                error_message=item.error_message,
                processed_at=None,
                created_at=item.created_at
            ))
        
        logger.info(f"[分类任务服务] 查询到 {len(failed_records)} 条失败记录")
        
        return TaskLogResponse(
            task_id=task.id,
            task_name=task.task_name,
            status=task.status.value,
            total_items=task.total_items,
            processed_items=task.processed_items,
            failed_items=task.failed_items,
            started_at=task.started_at,
            completed_at=task.completed_at,
            duration=duration,
            failed_records=failed_records
        )
    
    @staticmethod
    def _build_task_response(task: ClassificationTask) -> ClassificationTaskResponse:
        """
        构建任务响应对象
        
        Args:
            task: 任务模型
            
        Returns:
            任务响应对象
        """
        # 计算进度百分比
        progress_percentage = None
        if task.total_items > 0:
            progress_percentage = (task.processed_items / task.total_items) * 100
        
        return ClassificationTaskResponse(
            id=task.id,
            hospital_id=task.hospital_id,
            task_name=task.task_name,
            model_version_id=task.model_version_id,
            charge_categories=task.charge_categories,
            status=task.status.value,
            total_items=task.total_items,
            processed_items=task.processed_items,
            failed_items=task.failed_items,
            celery_task_id=task.celery_task_id,
            error_message=task.error_message,
            started_at=task.started_at,
            completed_at=task.completed_at,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
            progress_percentage=progress_percentage
        )
