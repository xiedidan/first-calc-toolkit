"""
计算步骤管理API
"""
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.schemas.calculation_step import (
    CalculationStepCreate,
    CalculationStepUpdate,
    CalculationStepResponse,
    CalculationStepListResponse,
    CalculationStepMoveResponse,
    TestCodeRequest,
    TestCodeResponse,
)

router = APIRouter()


@router.get("", response_model=CalculationStepListResponse)
def get_calculation_steps(
    workflow_id: int = Query(..., description="计算流程ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取计算步骤列表"""
    # 验证流程是否存在
    workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 查询步骤
    items = db.query(CalculationStep).filter(
        CalculationStep.workflow_id == workflow_id
    ).order_by(CalculationStep.sort_order).all()
    
    # 加载关联数据
    for item in items:
        item.workflow_name = workflow.name
    
    return {"total": len(items), "items": items}


@router.post("", response_model=CalculationStepResponse, status_code=status.HTTP_201_CREATED)
def create_calculation_step(
    step_in: CalculationStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建计算步骤"""
    # 验证流程是否存在
    workflow = db.query(CalculationWorkflow).filter(CalculationWorkflow.id == step_in.workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算流程不存在"
        )
    
    # 验证代码类型
    if step_in.code_type not in ['python', 'sql']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="代码类型必须是python或sql"
        )
    
    # 如果没有指定sort_order，自动设置为最大值+1
    if step_in.sort_order is None or step_in.sort_order == 0:
        max_order = db.query(func.coalesce(func.max(CalculationStep.sort_order), 0)).filter(
            CalculationStep.workflow_id == step_in.workflow_id
        ).scalar()
        step_in.sort_order = max_order + 1
    
    # 创建步骤
    db_step = CalculationStep(**step_in.model_dump())
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    
    # 加载关联数据
    db_step.workflow_name = workflow.name
    
    return db_step


@router.get("/{step_id}", response_model=CalculationStepResponse)
def get_calculation_step(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取计算步骤详情"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    # 加载关联数据
    if step.workflow:
        step.workflow_name = step.workflow.name
    
    return step


@router.put("/{step_id}", response_model=CalculationStepResponse)
def update_calculation_step(
    step_id: int,
    step_in: CalculationStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新计算步骤"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    # 验证代码类型
    if step_in.code_type and step_in.code_type not in ['python', 'sql']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="代码类型必须是python或sql"
        )
    
    # 更新字段
    update_data = step_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)
    
    db.commit()
    db.refresh(step)
    
    # 加载关联数据
    if step.workflow:
        step.workflow_name = step.workflow.name
    
    return step


@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation_step(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除计算步骤"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    # 删除步骤
    db.delete(step)
    db.commit()


@router.post("/{step_id}/move-up", response_model=CalculationStepMoveResponse)
def move_step_up(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上移计算步骤"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    # 查找上一个步骤
    prev_step = db.query(CalculationStep).filter(
        CalculationStep.workflow_id == step.workflow_id,
        CalculationStep.sort_order < step.sort_order
    ).order_by(CalculationStep.sort_order.desc()).first()
    
    if not prev_step:
        return {"success": False, "message": "已经是第一个步骤"}
    
    # 交换sort_order
    step.sort_order, prev_step.sort_order = prev_step.sort_order, step.sort_order
    
    db.commit()
    
    return {"success": True, "message": "上移成功"}


@router.post("/{step_id}/move-down", response_model=CalculationStepMoveResponse)
def move_step_down(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下移计算步骤"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    # 查找下一个步骤
    next_step = db.query(CalculationStep).filter(
        CalculationStep.workflow_id == step.workflow_id,
        CalculationStep.sort_order > step.sort_order
    ).order_by(CalculationStep.sort_order).first()
    
    if not next_step:
        return {"success": False, "message": "已经是最后一个步骤"}
    
    # 交换sort_order
    step.sort_order, next_step.sort_order = next_step.sort_order, step.sort_order
    
    db.commit()
    
    return {"success": True, "message": "下移成功"}


@router.post("/{step_id}/test", response_model=TestCodeResponse)
def test_step_code(
    step_id: int,
    test_request: TestCodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """测试计算步骤代码"""
    step = db.query(CalculationStep).filter(CalculationStep.id == step_id).first()
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="计算步骤不存在"
        )
    
    start_time = time.time()
    
    try:
        # TODO: 实现代码测试逻辑
        # 这里需要根据代码类型（SQL/Python）执行相应的测试
        # 暂时返回模拟结果
        
        # 模拟执行时间
        time.sleep(0.1)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "duration_ms": duration_ms,
            "result": {
                "message": "代码测试功能待实现",
                "code_type": step.code_type,
                "code_preview": step.code_content[:100] + "..." if len(step.code_content) > 100 else step.code_content,
                "test_params": test_request.test_params
            }
        }
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "duration_ms": duration_ms,
            "error": str(e)
        }
