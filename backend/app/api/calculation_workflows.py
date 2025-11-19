"""
计算流程管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.model_version import ModelVersion
from app.schemas.calculation_workflow import (
    CalculationWorkflowCreate,
    CalculationWorkflowUpdate,
    CalculationWorkflowResponse,
    CalculationWorkflowListResponse,
    CalculationWorkflowCopyRequest,
    CalculationWorkflowCopyResponse,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    validate_hospital_access,
)

router = APIRouter()


@router.get("", response_model=CalculationWorkflowListResponse)
def get_calculation_workflows(
    version_id: Optional[int] = Query(None, description="模型版本ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=10000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取计算流程列表"""
    # Join ModelVersion以应用医疗机构过滤
    query = db.query(CalculationWorkflow).join(
        ModelVersion, CalculationWorkflow.version_id == ModelVersion.id
    ).options(joinedload(CalculationWorkflow.version))
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    # 版本筛选
    if version_id:
        query = query.filter(CalculationWorkflow.version_id == version_id)
    
    # 关键词搜索
    if keyword:
        query = query.filter(CalculationWorkflow.name.ilike(f"%{keyword}%"))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.order_by(CalculationWorkflow.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    # 加载关联数据
    for item in items:
        # 获取版本名称
        if item.version:
            item.version_name = item.version.name
        else:
            item.version_name = None
        # 获取步骤数量
        item.step_count = db.query(func.count(CalculationStep.id)).filter(
            CalculationStep.workflow_id == item.id
        ).scalar()
    
    return {"total": total, "items": items}


@router.post("", response_model=CalculationWorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_calculation_workflow(
    workflow_in: CalculationWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建计算流程"""
    # 验证版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == workflow_in.version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 验证版本所属医疗机构
    validate_hospital_access(db, version)
    
    # 检查同一版本下流程名称是否重复
    existing = db.query(CalculationWorkflow).filter(
        CalculationWorkflow.version_id == workflow_in.version_id,
        CalculationWorkflow.name == workflow_in.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该版本下已存在同名流程"
        )
    
    # 创建流程
    db_workflow = CalculationWorkflow(**workflow_in.model_dump())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    
    # 加载关联数据
    db_workflow.version_name = version.name
    db_workflow.step_count = 0
    
    return db_workflow


@router.get("/{workflow_id}", response_model=CalculationWorkflowResponse)
def get_calculation_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取计算流程详情"""
    workflow = db.query(CalculationWorkflow).options(joinedload(CalculationWorkflow.version)).filter(CalculationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 验证流程所属的版本是否属于当前医疗机构
    validate_hospital_access(db, workflow.version)
    
    # 加载关联数据
    if workflow.version:
        workflow.version_name = workflow.version.name
    else:
        workflow.version_name = None
    workflow.step_count = db.query(func.count(CalculationStep.id)).filter(
        CalculationStep.workflow_id == workflow.id
    ).scalar()
    
    return workflow


@router.put("/{workflow_id}", response_model=CalculationWorkflowResponse)
def update_calculation_workflow(
    workflow_id: int,
    workflow_in: CalculationWorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新计算流程"""
    workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 验证流程所属的版本是否属于当前医疗机构
    validate_hospital_access(db, workflow.version)
    
    # 如果更新名称，检查是否重复
    if workflow_in.name and workflow_in.name != workflow.name:
        existing = db.query(CalculationWorkflow).filter(
            CalculationWorkflow.version_id == workflow.version_id,
            CalculationWorkflow.name == workflow_in.name,
            CalculationWorkflow.id != workflow_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该版本下已存在同名流程"
            )
    
    # 更新字段
    update_data = workflow_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    # 加载关联数据
    if workflow.version:
        workflow.version_name = workflow.version.name
    workflow.step_count = db.query(func.count(CalculationStep.id)).filter(
        CalculationStep.workflow_id == workflow.id
    ).scalar()
    
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除计算流程（级联删除所有步骤）"""
    workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 验证流程所属的版本是否属于当前医疗机构
    validate_hospital_access(db, workflow.version)
    
    # 删除流程（会级联删除所有步骤）
    db.delete(workflow)
    db.commit()


@router.post("/{workflow_id}/copy", response_model=CalculationWorkflowCopyResponse)
def copy_calculation_workflow(
    workflow_id: int,
    copy_request: CalculationWorkflowCopyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """复制计算流程（包括所有步骤）"""
    # 获取原流程
    source_workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
    if not source_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 验证流程所属的版本是否属于当前医疗机构
    validate_hospital_access(db, source_workflow.version)
    
    # 检查新名称是否重复
    existing = db.query(CalculationWorkflow).filter(
        CalculationWorkflow.version_id == source_workflow.version_id,
        CalculationWorkflow.name == copy_request.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该版本下已存在同名流程"
        )
    
    # 创建新流程
    new_workflow = CalculationWorkflow(
        version_id=source_workflow.version_id,
        name=copy_request.name,
        description=copy_request.description or source_workflow.description,
        is_active=source_workflow.is_active
    )
    db.add(new_workflow)
    db.flush()  # 获取新流程的ID
    
    # 复制所有步骤
    source_steps = db.query(CalculationStep).filter(
        CalculationStep.workflow_id == workflow_id
    ).order_by(CalculationStep.sort_order).all()
    
    step_count = 0
    for source_step in source_steps:
        new_step = CalculationStep(
            workflow_id=new_workflow.id,
            name=source_step.name,
            description=source_step.description,
            code_type=source_step.code_type,
            code_content=source_step.code_content,
            sort_order=source_step.sort_order,
            is_enabled=source_step.is_enabled
        )
        db.add(new_step)
        step_count += 1
    
    db.commit()
    
    return {
        "id": new_workflow.id,
        "name": new_workflow.name,
        "step_count": step_count
    }
