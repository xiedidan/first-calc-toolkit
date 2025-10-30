"""
计算任务API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_version import ModelVersion
from app.models.calculation_workflow import CalculationWorkflow
from app.models.model_node import ModelNode
from app.schemas.calculation_task import (
    CalculationTaskCreate,
    CalculationTaskResponse,
    CalculationTaskListResponse,
    SummaryListResponse,
    CalculationSummaryResponse,
    DepartmentDetailResponse,
    SequenceDetail,
    DimensionDetail,
    ExportSummaryRequest,
    ExportDetailRequest,
    ExportTaskResponse
)
from app.tasks.calculation_tasks import execute_calculation_task

router = APIRouter()


@router.post("/tasks", response_model=CalculationTaskResponse)
def create_calculation_task(
    task_data: CalculationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建计算任务"""
    # 验证模型版本是否存在
    model_version = db.query(ModelVersion).filter(ModelVersion.id == task_data.model_version_id).first()
    if not model_version:
        raise HTTPException(status_code=404, detail="模型版本不存在")
    
    # 如果指定了workflow_id，验证是否存在
    if task_data.workflow_id:
        workflow = db.query(CalculationWorkflow).filter(
            CalculationWorkflow.id == task_data.workflow_id,
            CalculationWorkflow.version_id == task_data.model_version_id
        ).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="计算流程不存在或不属于该模型版本")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建任务记录（写入数据库即表示任务已创建）
    db_task = CalculationTask(
        task_id=task_id,
        model_version_id=task_data.model_version_id,
        workflow_id=task_data.workflow_id,
        period=task_data.period,
        status="pending",
        description=task_data.description,
        created_by=current_user.id,
        created_at=datetime.now()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 异步提交计算任务（不等待结果）
    try:
        execute_calculation_task.delay(
            task_id=task_id,
            model_version_id=task_data.model_version_id,
            workflow_id=task_data.workflow_id,
            department_ids=task_data.department_ids,
            period=task_data.period
        )
    except Exception as e:
        # 即使异步任务提交失败，任务也已创建，只是状态会保持为pending
        print(f"提交异步任务失败: {str(e)}")
    
    # 立即返回任务信息
    return db_task


@router.get("/tasks", response_model=CalculationTaskListResponse)
def get_calculation_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=10000),
    status: Optional[str] = None,
    model_version_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取计算任务列表"""
    query = db.query(CalculationTask)
    
    # 筛选条件
    if status:
        query = query.filter(CalculationTask.status == status)
    if model_version_id:
        query = query.filter(CalculationTask.model_version_id == model_version_id)
    
    # 总数
    total = query.count()
    
    # 分页
    tasks = query.order_by(CalculationTask.created_at.desc()).offset((page - 1) * size).limit(size).all()
    
    return {
        "total": total,
        "items": tasks
    }


@router.get("/tasks/{task_id}", response_model=CalculationTaskResponse)
def get_calculation_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取计算任务详情"""
    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/tasks/{task_id}/cancel")
def cancel_calculation_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消计算任务"""
    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="只能取消排队中或运行中的任务")
    
    # 更新任务状态
    task.status = "cancelled"
    task.completed_at = datetime.now()
    db.commit()
    
    # TODO: 实际取消Celery任务
    
    return {"success": True, "message": "任务已取消"}


@router.get("/results/summary", response_model=SummaryListResponse)
def get_results_summary(
    period: str = Query(..., description="评估月份(YYYY-MM)"),
    model_version_id: Optional[int] = Query(None, description="模型版本ID"),
    department_id: Optional[int] = Query(None, description="科室ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取科室汇总数据"""
    # 查找最新的完成任务
    query = db.query(CalculationTask).filter(
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    )
    
    if model_version_id:
        query = query.filter(CalculationTask.model_version_id == model_version_id)
    else:
        # 使用激活版本
        active_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
        if active_version:
            query = query.filter(CalculationTask.model_version_id == active_version.id)
    
    task = query.order_by(CalculationTask.completed_at.desc()).first()
    if not task:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    # 查询汇总数据
    summaries_query = db.query(
        CalculationSummary,
        Department.his_name
    ).join(
        Department, CalculationSummary.department_id == Department.id
    ).filter(
        CalculationSummary.task_id == task.task_id
    )
    
    if department_id:
        summaries_query = summaries_query.filter(CalculationSummary.department_id == department_id)
    
    summaries = summaries_query.all()
    
    # 计算全院汇总
    total_doctor_value = sum(s[0].doctor_value for s in summaries)
    total_nurse_value = sum(s[0].nurse_value for s in summaries)
    total_tech_value = sum(s[0].tech_value for s in summaries)
    total_value = total_doctor_value + total_nurse_value + total_tech_value
    
    summary_data = CalculationSummaryResponse(
        department_id=0,
        department_name="全院汇总",
        doctor_value=total_doctor_value,
        doctor_ratio=total_doctor_value / total_value * 100 if total_value > 0 else 0,
        nurse_value=total_nurse_value,
        nurse_ratio=total_nurse_value / total_value * 100 if total_value > 0 else 0,
        tech_value=total_tech_value,
        tech_ratio=total_tech_value / total_value * 100 if total_value > 0 else 0,
        total_value=total_value
    )
    
    # 各科室数据
    departments_data = [
        CalculationSummaryResponse(
            department_id=s[0].department_id,
            department_name=s[1],
            doctor_value=s[0].doctor_value,
            doctor_ratio=s[0].doctor_ratio,
            nurse_value=s[0].nurse_value,
            nurse_ratio=s[0].nurse_ratio,
            tech_value=s[0].tech_value,
            tech_ratio=s[0].tech_ratio,
            total_value=s[0].total_value
        )
        for s in summaries
    ]
    
    return {
        "task_id": task.task_id,
        "summary": summary_data,
        "departments": departments_data
    }


@router.get("/results/detail", response_model=DepartmentDetailResponse)
def get_results_detail(
    dept_id: int = Query(..., description="科室ID"),
    task_id: str = Query(..., description="任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取科室详细业务价值数据 - 按模型结构展示"""
    # 验证任务是否存在
    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 验证科室是否存在
    department = db.query(Department).filter(Department.id == dept_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    # 查询该科室的所有计算结果
    results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id
    ).order_by(CalculationResult.node_id).all()
    
    # 查询模型节点信息以获取业务导向等额外信息
    node_ids = [r.node_id for r in results]
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 构建节点映射
    result_map = {r.node_id: r for r in results}
    
    # 构建树形结构（包含所有节点，不仅仅是叶子节点）
    def build_dimension_tree(parent_id, level):
        """递归构建维度树"""
        children = []
        for result in results:
            if result.parent_id == parent_id and result.node_type == "dimension":
                node_info = node_info_map.get(result.node_id)
                dim = DimensionDetail(
                    node_id=result.node_id,
                    parent_id=result.parent_id,
                    dimension_name=result.node_name,
                    dimension_code=result.node_code,
                    level=level,
                    value=result.value or 0,
                    ratio=result.ratio or 0,
                    workload=result.workload,
                    weight=result.weight,
                    business_guide=node_info.business_guide if node_info else None,
                    children=build_dimension_tree(result.node_id, level + 1)
                )
                children.append(dim)
        return children
    
    # 组织序列数据
    sequences = []
    for result in results:
        if result.node_type == "sequence":
            sequence = SequenceDetail(
                sequence_type=result.node_name,
                sequence_name=result.node_name,
                total_value=result.value or 0,
                dimensions=build_dimension_tree(result.node_id, 1)
            )
            sequences.append(sequence)
    
    # 生成表格数据 - 包含所有节点（末级和非末级）
    def flatten_tree_to_rows(sequence_name, dimensions):
        """将树形结构扁平化为表格行格式 - 包含所有节点"""
        rows = []
        
        def calculate_sum_from_children(node):
            """计算节点的工作量和金额（从子节点汇总）"""
            if not node.children or len(node.children) == 0:
                # 叶子节点，直接返回自己的值
                return node.workload or 0, node.value or 0
            
            # 非叶子节点，汇总子节点
            total_workload = 0
            total_amount = 0
            for child in node.children:
                child_workload, child_amount = calculate_sum_from_children(child)
                total_workload += child_workload
                total_amount += child_amount
            
            return total_workload, total_amount
        
        def collect_all_nodes(node, level_names, siblings_total=None):
            """递归收集所有节点（末级和非末级）
            
            level_names: 当前路径上各级维度的名称 [level1, level2, level3, ...]
            siblings_total: 同级节点的金额总和（用于计算占比）
            """
            # 判断是否为末级维度
            is_leaf = not node.children or len(node.children) == 0
            
            # 更新level_names，添加当前节点
            new_level_names = level_names + [node.dimension_name]
            
            # 构建维度名称列（最多支持4级）
            level1_name = new_level_names[0] if len(new_level_names) >= 1 else None
            level2_name = new_level_names[1] if len(new_level_names) >= 2 else None
            level3_name = new_level_names[2] if len(new_level_names) >= 3 else None
            level4_name = new_level_names[3] if len(new_level_names) >= 4 else None
            
            # 计算当前节点的金额
            if is_leaf:
                current_amount = node.value or 0
            else:
                _, current_amount = calculate_sum_from_children(node)
            
            # 计算占比
            if siblings_total and siblings_total > 0:
                ratio = (current_amount / siblings_total * 100)
                from decimal import Decimal
                ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
            else:
                ratio = node.ratio or 0
            
            # 创建行数据
            if is_leaf:
                # 末级维度：显示工作量、全院业务价值、业务导向、科室业务价值、金额、占比
                row = {
                    "level1": level1_name,
                    "level2": level2_name,
                    "level3": level3_name,
                    "level4": level4_name,
                    "workload": node.workload,  # 工作量（总收入）
                    "hospital_value": str(node.weight) if node.weight is not None else "-",  # 全院业务价值（权重/单价）
                    "business_guide": node.business_guide or "-",  # 业务导向
                    "dept_value": str(node.weight) if node.weight is not None else "-",  # 科室业务价值（权重/单价）
                    "amount": node.value,  # 金额
                    "ratio": ratio,  # 占比（重新计算）
                }
            else:
                # 非末级维度：工作量和金额由子维度之和计算
                sum_workload, sum_amount = calculate_sum_from_children(node)
                row = {
                    "level1": level1_name,
                    "level2": level2_name,
                    "level3": level3_name,
                    "level4": level4_name,
                    "workload": sum_workload,  # 工作量（子维度之和）
                    "hospital_value": "-",  # 非末级用"-"
                    "business_guide": "-",  # 非末级用"-"
                    "dept_value": "-",  # 非末级用"-"
                    "amount": sum_amount,  # 金额（子维度之和）
                    "ratio": ratio,  # 占比（重新计算）
                }
            
            rows.append(row)
            
            # 递归处理子节点
            if node.children:
                # 计算子节点的金额总和（用于计算子节点的占比）
                children_total = sum(
                    (calculate_sum_from_children(child)[1] if child.children else (child.value or 0))
                    for child in node.children
                )
                
                for child in node.children:
                    collect_all_nodes(child, new_level_names, children_total)
        
        # 计算一级维度的金额总和
        first_level_total = sum(
            (calculate_sum_from_children(dim)[1] if dim.children else (dim.value or 0))
            for dim in dimensions
        )
        
        # 处理每个一级维度
        for dim in dimensions:
            collect_all_nodes(dim, [], first_level_total)
        
        return rows
    
    # 为每个序列生成表格数据
    doctor_rows = []
    nurse_rows = []
    tech_rows = []
    
    for seq in sequences:
        if "医生" in seq.sequence_name:
            doctor_rows = flatten_tree_to_rows(seq.sequence_name, seq.dimensions)
        elif "护理" in seq.sequence_name:
            nurse_rows = flatten_tree_to_rows(seq.sequence_name, seq.dimensions)
        elif "医技" in seq.sequence_name:
            tech_rows = flatten_tree_to_rows(seq.sequence_name, seq.dimensions)
    
    return {
        "department_id": dept_id,
        "department_name": department.his_name,
        "period": task.period,
        "sequences": sequences,
        "doctor": doctor_rows,
        "nurse": nurse_rows,
        "tech": tech_rows
    }


@router.get("/tasks/{task_id}/logs")
def get_task_logs(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取任务执行日志"""
    from app.models.calculation_step_log import CalculationStepLog
    
    # 验证任务是否存在
    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 查询步骤日志
    logs = db.query(CalculationStepLog).filter(
        CalculationStepLog.task_id == task_id
    ).order_by(
        CalculationStepLog.start_time.desc()
    ).all()
    
    return {
        "task_id": task_id,
        "logs": [
            {
                "id": log.id,
                "step_id": log.step_id,
                "department_id": log.department_id,
                "status": log.status,
                "start_time": log.start_time,
                "end_time": log.end_time,
                "duration_ms": log.duration_ms,
                "result_data": log.result_data,
                "execution_info": log.execution_info
            }
            for log in logs
        ]
    }


@router.post("/results/export/summary", response_model=ExportTaskResponse)
def export_summary(
    request: ExportSummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出汇总表"""
    # TODO: 实现异步导出任务
    export_task_id = str(uuid.uuid4())
    
    return {
        "task_id": export_task_id,
        "download_url": None
    }


@router.post("/results/export/detail", response_model=ExportTaskResponse)
def export_detail(
    request: ExportDetailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出明细表"""
    # TODO: 实现异步导出任务
    export_task_id = str(uuid.uuid4())
    
    return {
        "task_id": export_task_id,
        "download_url": None
    }


@router.get("/results/export/{task_id}/download")
def download_export(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载报表文件"""
    # TODO: 实现文件下载
    raise HTTPException(status_code=501, detail="功能开发中")
