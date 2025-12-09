"""
分类预案管理服务
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, and_, or_

from app.models.classification_plan import ClassificationPlan, PlanStatus
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.classification_task import ClassificationTask
from app.models.model_node import ModelNode
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.charge_item import ChargeItem
from app.schemas.classification_plan import (
    ClassificationPlanResponse,
    ClassificationPlanListResponse,
    PlanItemResponse,
    PlanItemListResponse,
    PlanItemQueryParams,
    PlanItemUpdate,
    UpdatePlanRequest,
    SubmitPreviewResponse,
    SubmitPreviewItem,
    SubmitPreviewOverwriteItem,
    SubmitPlanRequest,
    SubmitPlanResponse,
)

logger = logging.getLogger(__name__)


class ClassificationPlanService:
    """分类预案管理服务"""
    
    @staticmethod
    def get_plans(
        db: Session,
        hospital_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> ClassificationPlanListResponse:
        """
        获取分类预案列表
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            skip: 跳过记录数
            limit: 返回记录数
            status: 预案状态筛选（可选）
            
        Returns:
            预案列表响应
        """
        logger.info(
            f"[分类预案服务] 查询预案列表: hospital_id={hospital_id}, "
            f"skip={skip}, limit={limit}, status={status}"
        )
        
        # 构建查询
        query = db.query(ClassificationPlan).filter(
            ClassificationPlan.hospital_id == hospital_id
        )
        
        # 状态筛选
        if status:
            try:
                status_enum = PlanStatus(status)
                query = query.filter(ClassificationPlan.status == status_enum)
            except ValueError:
                logger.warning(f"[分类预案服务] 无效的状态值: {status}")
        
        # 总数
        total = query.count()
        
        # 分页查询
        plans = query.order_by(desc(ClassificationPlan.created_at)).offset(skip).limit(limit).all()
        
        # 构建响应
        items = [ClassificationPlanService._build_plan_response(db, plan) for plan in plans]
        
        logger.info(f"[分类预案服务] 查询到 {len(items)} 个预案，总数 {total}")
        
        return ClassificationPlanListResponse(total=total, items=items)
    
    @staticmethod
    def get_plan_detail(
        db: Session,
        hospital_id: int,
        plan_id: int
    ) -> ClassificationPlanResponse:
        """
        获取分类预案详情（包含所有项目）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            
        Returns:
            预案详情响应
            
        Raises:
            ValueError: 如果预案不存在
        """
        logger.info(f"[分类预案服务] 查询预案详情: plan_id={plan_id}, hospital_id={hospital_id}")
        
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        return ClassificationPlanService._build_plan_response(db, plan)
    
    @staticmethod
    def update_plan(
        db: Session,
        hospital_id: int,
        plan_id: int,
        update_data: UpdatePlanRequest
    ) -> ClassificationPlanResponse:
        """
        更新预案（名称、状态）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            update_data: 更新数据
            
        Returns:
            更新后的预案响应
            
        Raises:
            ValueError: 如果预案不存在或已提交
        """
        logger.info(f"[分类预案服务] 更新预案: plan_id={plan_id}, hospital_id={hospital_id}")
        
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        # 更新预案名称（允许已提交的预案修改名称）
        if update_data.plan_name is not None:
            plan.plan_name = update_data.plan_name
        
        plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(plan)
        
        logger.info(f"[分类预案服务] 预案更新成功: plan_id={plan_id}")
        
        return ClassificationPlanService._build_plan_response(db, plan)
    
    @staticmethod
    def delete_plan(
        db: Session,
        hospital_id: int,
        plan_id: int
    ) -> Dict[str, Any]:
        """
        删除预案
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            
        Returns:
            删除结果
            
        Raises:
            ValueError: 如果预案不存在或已提交
        """
        logger.info(f"[分类预案服务] 删除预案: plan_id={plan_id}, hospital_id={hospital_id}")
        
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        if plan.status == PlanStatus.submitted:
            raise ValueError("预案已提交，无法删除")
        
        # 删除预案（级联删除关联的项目）
        db.delete(plan)
        db.commit()
        
        logger.info(f"[分类预案服务] 预案删除成功: plan_id={plan_id}")
        
        return {
            "success": True,
            "message": "预案删除成功"
        }
    
    @staticmethod
    def get_plan_items(
        db: Session,
        hospital_id: int,
        plan_id: int,
        query_params: PlanItemQueryParams
    ) -> PlanItemListResponse:
        """
        获取预案项目列表（支持排序和筛选）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            query_params: 查询参数
            
        Returns:
            预案项目列表响应
            
        Raises:
            ValueError: 如果预案不存在
        """
        logger.info(
            f"[分类预案服务] 查询预案项目: plan_id={plan_id}, hospital_id={hospital_id}, "
            f"sort_by={query_params.sort_by}, min_confidence={query_params.min_confidence}, "
            f"max_confidence={query_params.max_confidence}"
        )
        
        # 验证预案存在
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        # 构建查询
        query = db.query(PlanItem).filter(
            PlanItem.plan_id == plan_id,
            PlanItem.hospital_id == hospital_id
        )
        
        # 确信度范围筛选
        if query_params.min_confidence is not None:
            query = query.filter(PlanItem.ai_confidence >= query_params.min_confidence)
        
        if query_params.max_confidence is not None:
            query = query.filter(PlanItem.ai_confidence <= query_params.max_confidence)
        
        # 是否已调整筛选
        if query_params.is_adjusted is not None:
            query = query.filter(PlanItem.is_adjusted == query_params.is_adjusted)
        
        # 处理状态筛选
        if query_params.processing_status:
            try:
                status_enum = ProcessingStatus(query_params.processing_status)
                query = query.filter(PlanItem.processing_status == status_enum)
            except ValueError:
                logger.warning(f"[分类预案服务] 无效的处理状态: {query_params.processing_status}")
        
        # 排序
        if query_params.sort_by == "confidence_asc":
            query = query.order_by(asc(PlanItem.ai_confidence))
        elif query_params.sort_by == "confidence_desc":
            query = query.order_by(desc(PlanItem.ai_confidence))
        else:
            # 默认按创建时间排序
            query = query.order_by(PlanItem.created_at)
        
        # 总数
        total = query.count()
        
        # 分页查询
        skip = (query_params.page - 1) * query_params.size
        items = query.offset(skip).limit(query_params.size).all()
        
        # 构建响应
        item_responses = [
            ClassificationPlanService._build_plan_item_response(db, item) 
            for item in items
        ]
        
        logger.info(f"[分类预案服务] 查询到 {len(item_responses)} 个项目，总数 {total}")
        
        return PlanItemListResponse(total=total, items=item_responses)
    
    @staticmethod
    def update_plan_item(
        db: Session,
        hospital_id: int,
        plan_id: int,
        item_id: int,
        update_data: PlanItemUpdate
    ) -> PlanItemResponse:
        """
        调整预案项目维度
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            item_id: 项目ID
            update_data: 更新数据
            
        Returns:
            更新后的项目响应
            
        Raises:
            ValueError: 如果预案或项目不存在，或预案已提交
        """
        logger.info(
            f"[分类预案服务] 调整项目维度: plan_id={plan_id}, item_id={item_id}, "
            f"new_dimension_id={update_data.dimension_id}"
        )
        
        # 验证预案存在且未提交
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        if plan.status == PlanStatus.submitted:
            raise ValueError("预案已提交，无法修改")
        
        # 查询项目
        item = db.query(PlanItem).filter(
            PlanItem.id == item_id,
            PlanItem.plan_id == plan_id,
            PlanItem.hospital_id == hospital_id
        ).first()
        
        if not item:
            raise ValueError(f"项目 {item_id} 不存在或不属于该预案")
        
        # 如果设置了维度ID，验证维度存在且为末级维度
        if update_data.dimension_id is not None:
            from app.models.model_version import ModelVersion
            
            dimension = db.query(ModelNode).join(
                ModelVersion, ModelNode.version_id == ModelVersion.id
            ).filter(
                ModelNode.id == update_data.dimension_id,
                ModelVersion.hospital_id == hospital_id
            ).first()
            
            if not dimension:
                raise ValueError(f"维度 {update_data.dimension_id} 不存在或不属于当前医疗机构")
            
            if not dimension.is_leaf:
                raise ValueError(f"维度 {update_data.dimension_id} 不是末级维度，无法分配项目")
        
        # 更新项目（dimension_id为None表示清空用户设置，提交时将跳过该项目）
        item.user_set_dimension_id = update_data.dimension_id
        item.is_adjusted = True  # 标记为已调整（即使是清空）
        item.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(item)
        
        logger.info(f"[分类预案服务] 项目维度调整成功: item_id={item_id}")
        
        return ClassificationPlanService._build_plan_item_response(db, item)
    
    @staticmethod
    def generate_submit_preview(
        db: Session,
        hospital_id: int,
        plan_id: int
    ) -> SubmitPreviewResponse:
        """
        生成提交预览（分析新增/覆盖）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            
        Returns:
            提交预览响应
            
        Raises:
            ValueError: 如果预案不存在
        """
        logger.info(f"[分类预案服务] 生成提交预览: plan_id={plan_id}, hospital_id={hospital_id}")
        
        # 查询预案
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        # 查询所有预案项目
        items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan_id,
            PlanItem.hospital_id == hospital_id
        ).all()
        
        new_items = []
        overwrite_items = []
        warnings = []
        
        for item in items:
            # 确定最终维度（用户设置 ?? AI建议）
            final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
            
            if not final_dimension_id:
                warnings.append(f"项目 {item.charge_item_name} 没有维度分配，将被跳过")
                continue
            
            # 获取维度信息
            dimension = db.query(ModelNode).filter(
                ModelNode.id == final_dimension_id
            ).first()
            
            if not dimension:
                warnings.append(f"项目 {item.charge_item_name} 的维度 {final_dimension_id} 不存在")
                continue
            
            # 检查是否已存在映射
            existing = db.query(DimensionItemMapping).filter(
                DimensionItemMapping.hospital_id == hospital_id,
                DimensionItemMapping.charge_item_id == item.charge_item_id
            ).first()
            
            # 构建维度路径
            dimension_path = ClassificationPlanService._get_dimension_path(db, dimension)
            
            if existing:
                # 覆盖：查询原维度信息（通过ModelVersion验证hospital_id）
                from app.models.model_version import ModelVersion
                
                old_dimension = db.query(ModelNode).join(
                    ModelVersion, ModelNode.version_id == ModelVersion.id
                ).filter(
                    ModelNode.code == existing.dimension_code,
                    ModelVersion.hospital_id == hospital_id
                ).first()
                
                old_dimension_name = old_dimension.name if old_dimension else existing.dimension_code
                old_dimension_path = ClassificationPlanService._get_dimension_path(db, old_dimension) if old_dimension else ""
                
                overwrite_items.append(SubmitPreviewOverwriteItem(
                    item_id=item.id,
                    item_name=item.charge_item_name,
                    dimension_id=final_dimension_id,
                    dimension_name=dimension.name,
                    dimension_path=dimension_path,
                    old_dimension_id=old_dimension.id if old_dimension else 0,
                    old_dimension_name=old_dimension_name,
                    old_dimension_path=old_dimension_path
                ))
            else:
                # 新增
                new_items.append(SubmitPreviewItem(
                    item_id=item.id,
                    item_name=item.charge_item_name,
                    dimension_id=final_dimension_id,
                    dimension_name=dimension.name,
                    dimension_path=dimension_path
                ))
        
        logger.info(
            f"[分类预案服务] 预览生成完成: 新增 {len(new_items)} 项，覆盖 {len(overwrite_items)} 项"
        )
        
        return SubmitPreviewResponse(
            plan_id=plan.id,
            plan_name=plan.plan_name,
            total_items=len(items),
            new_count=len(new_items),
            overwrite_count=len(overwrite_items),
            new_items=new_items,
            overwrite_items=overwrite_items,
            warnings=warnings
        )
    
    @staticmethod
    def submit_plan(
        db: Session,
        hospital_id: int,
        plan_id: int,
        submit_data: SubmitPlanRequest
    ) -> SubmitPlanResponse:
        """
        提交预案（批量提交到维度目录）
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            plan_id: 预案ID
            submit_data: 提交请求数据
            
        Returns:
            提交响应
            
        Raises:
            ValueError: 如果预案不存在或已提交
        """
        logger.info(f"[分类预案服务] 提交预案: plan_id={plan_id}, hospital_id={hospital_id}")
        
        # 查询预案
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == plan_id,
            ClassificationPlan.hospital_id == hospital_id
        ).first()
        
        if not plan:
            raise ValueError(f"预案 {plan_id} 不存在或不属于当前医疗机构")
        
        if plan.status == PlanStatus.submitted:
            raise ValueError("预案已提交，不可重复提交")
        
        # 查询所有预案项目
        items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan_id,
            PlanItem.hospital_id == hospital_id
        ).all()
        
        new_count = 0
        overwrite_count = 0
        
        try:
            for item in items:
                # 确定最终维度（用户设置 ?? AI建议）
                final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
                
                if not final_dimension_id:
                    logger.warning(f"[分类预案服务] 项目 {item.charge_item_name} 没有维度分配，跳过")
                    continue
                
                # 获取维度信息
                dimension = db.query(ModelNode).filter(
                    ModelNode.id == final_dimension_id
                ).first()
                
                if not dimension:
                    logger.warning(f"[分类预案服务] 维度 {final_dimension_id} 不存在，跳过")
                    continue
                
                # 检查是否已存在映射
                existing = db.query(DimensionItemMapping).filter(
                    DimensionItemMapping.hospital_id == hospital_id,
                    DimensionItemMapping.charge_item_id == item.charge_item_id
                ).first()
                
                if existing:
                    # 更新维度归属
                    existing.dimension_code = dimension.code
                    existing.created_at = datetime.utcnow()  # 更新时间戳
                    overwrite_count += 1
                    logger.debug(
                        f"[分类预案服务] 更新映射: charge_item_id={item.charge_item_id}, "
                        f"dimension_code={dimension.code}"
                    )
                else:
                    # 创建新映射
                    # 获取收费项目编码
                    charge_item = db.query(ChargeItem).filter(
                        ChargeItem.id == item.charge_item_id
                    ).first()
                    
                    if not charge_item:
                        logger.warning(f"[分类预案服务] 收费项目 {item.charge_item_id} 不存在，跳过")
                        continue
                    
                    new_mapping = DimensionItemMapping(
                        hospital_id=hospital_id,
                        dimension_code=dimension.code,
                        item_code=charge_item.item_code,
                        charge_item_id=item.charge_item_id
                    )
                    db.add(new_mapping)
                    new_count += 1
                    logger.debug(
                        f"[分类预案服务] 创建映射: charge_item_id={item.charge_item_id}, "
                        f"dimension_code={dimension.code}"
                    )
            
            # 更新预案状态
            plan.status = PlanStatus.submitted
            plan.submitted_at = datetime.utcnow()
            
            # 提交事务
            db.commit()
            
            logger.info(
                f"[分类预案服务] 预案提交成功: plan_id={plan_id}, "
                f"新增 {new_count} 项，覆盖 {overwrite_count} 项"
            )
            
            return SubmitPlanResponse(
                success=True,
                message="预案提交成功",
                new_count=new_count,
                overwrite_count=overwrite_count,
                submitted_at=plan.submitted_at
            )
            
        except Exception as e:
            # 回滚事务
            db.rollback()
            logger.error(f"[分类预案服务] 预案提交失败: {str(e)}", exc_info=True)
            
            return SubmitPlanResponse(
                success=False,
                message=f"预案提交失败: {str(e)}",
                new_count=0,
                overwrite_count=0,
                submitted_at=None
            )
    
    @staticmethod
    def _build_plan_response(db: Session, plan: ClassificationPlan) -> ClassificationPlanResponse:
        """
        构建预案响应对象
        
        Args:
            db: 数据库会话
            plan: 预案模型
            
        Returns:
            预案响应对象
        """
        # 查询关联的任务信息
        task = db.query(ClassificationTask).filter(
            ClassificationTask.id == plan.task_id
        ).first()
        
        # 统计信息
        total_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id
        ).count()
        
        adjusted_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.is_adjusted == True
        ).count()
        
        low_confidence_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.ai_confidence < 0.5
        ).count()
        
        return ClassificationPlanResponse(
            id=plan.id,
            hospital_id=plan.hospital_id,
            task_id=plan.task_id,
            plan_name=plan.plan_name,
            status=plan.status.value,
            submitted_at=plan.submitted_at,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            task_name=task.task_name if task else None,
            model_version_id=task.model_version_id if task else None,
            charge_categories=task.charge_categories if task else None,
            total_items=total_items,
            adjusted_items=adjusted_items,
            low_confidence_items=low_confidence_items
        )
    
    @staticmethod
    def _build_plan_item_response(db: Session, item: PlanItem) -> PlanItemResponse:
        """
        构建预案项目响应对象
        
        Args:
            db: 数据库会话
            item: 预案项目模型
            
        Returns:
            预案项目响应对象
        """
        # AI建议维度信息
        ai_suggested_dimension_name = None
        ai_suggested_dimension_path = None
        if item.ai_suggested_dimension_id:
            ai_dimension = db.query(ModelNode).filter(
                ModelNode.id == item.ai_suggested_dimension_id
            ).first()
            if ai_dimension:
                ai_suggested_dimension_name = ai_dimension.name
                ai_suggested_dimension_path = ClassificationPlanService._get_dimension_path(db, ai_dimension)
        
        # 用户设置维度信息
        user_set_dimension_name = None
        user_set_dimension_path = None
        if item.user_set_dimension_id:
            user_dimension = db.query(ModelNode).filter(
                ModelNode.id == item.user_set_dimension_id
            ).first()
            if user_dimension:
                user_set_dimension_name = user_dimension.name
                user_set_dimension_path = ClassificationPlanService._get_dimension_path(db, user_dimension)
        
        # 最终维度（用户设置 ?? AI建议）
        final_dimension_id = item.user_set_dimension_id or item.ai_suggested_dimension_id
        final_dimension_name = user_set_dimension_name or ai_suggested_dimension_name
        final_dimension_path = user_set_dimension_path or ai_suggested_dimension_path
        
        # 查询收费项目的编码和类别
        charge_item_code = None
        charge_item_category = None
        charge_item = db.query(ChargeItem).filter(
            ChargeItem.id == item.charge_item_id
        ).first()
        if charge_item:
            charge_item_code = charge_item.item_code
            charge_item_category = charge_item.item_category
        
        return PlanItemResponse(
            id=item.id,
            plan_id=item.plan_id,
            charge_item_id=item.charge_item_id,
            charge_item_name=item.charge_item_name,
            charge_item_code=charge_item_code,
            charge_item_category=charge_item_category,
            ai_suggested_dimension_id=item.ai_suggested_dimension_id,
            ai_suggested_dimension_name=ai_suggested_dimension_name,
            ai_suggested_dimension_path=ai_suggested_dimension_path,
            ai_confidence=item.ai_confidence,
            user_set_dimension_id=item.user_set_dimension_id,
            user_set_dimension_name=user_set_dimension_name,
            user_set_dimension_path=user_set_dimension_path,
            is_adjusted=item.is_adjusted,
            final_dimension_id=final_dimension_id,
            final_dimension_name=final_dimension_name,
            final_dimension_path=final_dimension_path,
            processing_status=item.processing_status.value,
            error_message=item.error_message,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
    
    @staticmethod
    def _get_dimension_path(db: Session, dimension: Optional[ModelNode]) -> str:
        """
        获取维度的完整路径
        
        Args:
            db: 数据库会话
            dimension: 维度节点
            
        Returns:
            维度路径字符串（如："序列A / 一级维度 / 二级维度"）
        """
        if not dimension:
            return ""
        
        path_parts = [dimension.name]
        current = dimension
        
        # 向上遍历父节点
        while current.parent_id:
            parent = db.query(ModelNode).filter(
                ModelNode.id == current.parent_id
            ).first()
            
            if not parent:
                break
            
            path_parts.insert(0, parent.name)
            current = parent
        
        return " / ".join(path_parts)
