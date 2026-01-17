"""
计算任务API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sqlalchemy as sa
from typing import Optional
from decimal import Decimal
import uuid
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.utils.timezone import utc_now
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
    ExportTaskResponse,
    OrientationAdjustmentDetailResponse,
    OrientationAdjustmentListResponse,
    OrientationSummaryResponse,
    BatchInfo,
    BatchListResponse
)
from app.tasks.calculation_tasks import execute_calculation_task
from app.utils.hospital_filter import (
    apply_hospital_filter,
    validate_hospital_access,
)

router = APIRouter()


def _get_task_with_hospital_check(db: Session, task_id: str) -> CalculationTask:
    """
    获取任务并验证所属医疗机构
    
    Args:
        db: 数据库会话
        task_id: 任务ID
        
    Returns:
        任务对象
        
    Raises:
        HTTPException: 如果任务不存在或不属于当前医疗机构
    """
    query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    ).filter(CalculationTask.task_id == task_id)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


def _get_latest_completed_task(
    db: Session,
    period: str,
    model_version_id: Optional[int] = None
) -> CalculationTask:
    """
    获取最新的完成任务
    
    Args:
        db: 数据库会话
        period: 评估月份
        model_version_id: 模型版本ID（可选）
        
    Returns:
        任务对象
        
    Raises:
        HTTPException: 如果未找到计算结果
    """
    query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    ).filter(
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    )
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    if model_version_id:
        query = query.filter(CalculationTask.model_version_id == model_version_id)
    else:
        # 使用激活版本（当前医疗机构的）
        active_query = db.query(ModelVersion).filter(ModelVersion.is_active == True)
        active_query = apply_hospital_filter(active_query, ModelVersion, required=True)
        active_version = active_query.first()
        if active_version:
            query = query.filter(CalculationTask.model_version_id == active_version.id)
    
    # 使用自增ID排序，比时间戳更稳定
    task = query.order_by(CalculationTask.id.desc()).first()
    if not task:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    return task


@router.post("/tasks", response_model=CalculationTaskResponse)
def create_calculation_task(
    task_data: CalculationTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建计算任务"""
    # 验证模型版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == task_data.model_version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    model_version = query.first()
    if not model_version:
        raise HTTPException(status_code=404, detail="模型版本不存在")
    
    # 验证模型版本所属医疗机构
    validate_hospital_access(db, model_version)
    
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
    
    # 使用传入的batch_id，如果没有则生成新的
    batch_id = task_data.batch_id or str(uuid.uuid4())
    
    # 创建任务记录（写入数据库即表示任务已创建）
    db_task = CalculationTask(
        task_id=task_id,
        batch_id=batch_id,
        model_version_id=task_data.model_version_id,
        workflow_id=task_data.workflow_id,
        period=task_data.period,
        status="pending",
        description=task_data.description,
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 异步提交计算任务（不等待结果）
    try:
        print(f"[INFO] 提交Celery任务: task_id={task_id}")
        result = execute_calculation_task.delay(
            task_id=task_id,
            model_version_id=task_data.model_version_id,
            workflow_id=task_data.workflow_id,
            department_ids=task_data.department_ids,
            period=task_data.period
        )
        print(f"[INFO] Celery任务已提交: celery_task_id={result.id}")
    except Exception as e:
        # 即使异步任务提交失败，任务也已创建，只是状态会保持为pending
        print(f"[ERROR] 提交异步任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 立即返回任务信息
    return db_task


@router.get("/tasks", response_model=CalculationTaskListResponse)
def get_calculation_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=10000),
    status: Optional[str] = None,
    model_version_id: Optional[int] = None,
    period: Optional[str] = Query(None, description="评估月份(YYYY-MM)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取计算任务列表
    
    当指定 model_version_id 时，返回该模型版本下所有计算流程的任务
    """
    # Join ModelVersion以应用医疗机构过滤
    query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    )
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    # 筛选条件
    if status:
        query = query.filter(CalculationTask.status == status)
    if model_version_id:
        # 查询该模型版本下所有计算流程的ID
        workflow_ids = db.query(CalculationWorkflow.id).filter(
            CalculationWorkflow.version_id == model_version_id
        ).all()
        workflow_ids = [wf_id[0] for wf_id in workflow_ids]
        
        # 筛选：任务的 workflow_id 在该版本的流程列表中，或者 workflow_id 为空但 model_version_id 匹配
        if workflow_ids:
            query = query.filter(
                sa.or_(
                    CalculationTask.workflow_id.in_(workflow_ids),
                    sa.and_(
                        CalculationTask.workflow_id.is_(None),
                        CalculationTask.model_version_id == model_version_id
                    )
                )
            )
        else:
            # 如果该版本没有计算流程，只查询直接关联该版本的任务
            query = query.filter(CalculationTask.model_version_id == model_version_id)
    if period:
        query = query.filter(CalculationTask.period == period)
    
    # 总数
    total = query.count()
    
    # 分页（使用自增ID排序，比时间戳更稳定）
    tasks = query.order_by(CalculationTask.id.desc()).offset((page - 1) * size).limit(size).all()
    
    # 加载关联的workflow_name
    for task in tasks:
        if task.workflow:
            task.workflow_name = task.workflow.name
        else:
            task.workflow_name = None
    
    return {
        "total": total,
        "items": tasks
    }


@router.get("/tasks/batch/{batch_id}", response_model=CalculationTaskListResponse)
def get_tasks_by_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据批次ID获取同批次的所有任务
    
    用于报表页面查找同批次的环比、同比任务
    """
    # Join ModelVersion以应用医疗机构过滤
    query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    ).filter(CalculationTask.batch_id == batch_id)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    # 总数
    total = query.count()
    
    # 按创建时间排序
    tasks = query.order_by(CalculationTask.id.desc()).all()
    
    # 加载关联的workflow_name
    for task in tasks:
        if task.workflow:
            task.workflow_name = task.workflow.name
        else:
            task.workflow_name = None
    
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
    task = _get_task_with_hospital_check(db, task_id)
    return task


@router.post("/tasks/{task_id}/cancel")
def cancel_calculation_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消计算任务"""
    task = _get_task_with_hospital_check(db, task_id)
    
    if task.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="只能取消排队中或运行中的任务")
    
    # 更新任务状态
    task.status = "cancelled"
    task.completed_at = datetime.utcnow()
    db.commit()
    
    # TODO: 实际取消Celery任务
    
    return {"success": True, "message": "任务已取消"}


@router.get("/results/summary", response_model=SummaryListResponse)
def get_results_summary(
    period: Optional[str] = Query(None, description="评估月份(YYYY-MM)"),
    model_version_id: Optional[int] = Query(None, description="模型版本ID"),
    department_id: Optional[int] = Query(None, description="科室ID"),
    task_id: Optional[str] = Query(None, description="任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取科室汇总数据 - 使用明细表相同的逐级汇总算法，显示所有参与核算的科室"""
    from decimal import Decimal
    from collections import defaultdict
    from app.utils.hospital_filter import get_current_hospital_id_or_raise
    
    # 参数验证：task_id和period不能同时为空
    if not task_id and not period:
        raise HTTPException(status_code=400, detail="必须指定task_id或period参数")
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取任务：task_id优先于period+model_version_id
    if task_id:
        # 使用指定的任务ID
        task = _get_task_with_hospital_check(db, task_id)
    else:
        # 查找最新的完成任务（使用辅助函数）
        task = _get_latest_completed_task(db, period, model_version_id)
    
    # 获取所有参与核算的科室（is_active=True）
    all_active_depts_query = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).order_by(Department.sort_order, Department.id)
    
    if department_id:
        all_active_depts_query = all_active_depts_query.filter(Department.id == department_id)
    
    all_active_depts = all_active_depts_query.all()
    dept_map = {d.id: d for d in all_active_depts}
    
    # 查询所有计算结果（维度和序列）
    all_results_query = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id
    )
    
    if department_id:
        all_results_query = all_results_query.filter(CalculationResult.department_id == department_id)
    
    all_results = all_results_query.all()
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 使用明细表相同的算法计算每个科室的汇总
    def calculate_sum_from_children(node_id, results):
        """递归计算节点的价值（从子节点汇总） - 与明细表算法完全相同"""
        # 找到当前节点
        current_node = next((r for r in results if r.node_id == node_id), None)
        if not current_node:
            return Decimal('0')
        
        # 找到所有子节点（维度）
        children = [r for r in results if r.parent_id == node_id and r.node_type == "dimension"]
        
        if not children or len(children) == 0:
            # 叶子节点，直接返回自己的值
            return current_node.value or Decimal('0')
        
        # 非叶子节点，汇总子节点
        total_value = Decimal('0')
        for child in children:
            child_value = calculate_sum_from_children(child.node_id, results)
            total_value += child_value
        
        return total_value
    
    # 按核算单元分组汇总（多个科室可能属于同一个核算单元）
    accounting_units = {}  # key: (accounting_unit_code, accounting_unit_name), value: {dept_ids, values}
    
    for dept in all_active_depts:
        dept_id_val = dept.id
        results = results_by_dept.get(dept_id_val, [])
        
        # 找出所有序列
        sequences = [r for r in results if r.node_type == "sequence"]
        
        # 计算每个序列的价值（使用明细表算法）
        doctor_value = Decimal('0')
        nurse_value = Decimal('0')
        tech_value = Decimal('0')
        
        for seq in sequences:
            # 使用明细表相同的逐级汇总算法计算序列价值
            seq_value = calculate_sum_from_children(seq.node_id, results)
            
            # 根据序列名称分类
            node_name_lower = seq.node_name.lower()
            if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_value += seq_value
            elif "护理" in seq.node_name or "护士" in seq.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_value += seq_value
            elif "医技" in seq.node_name or "技师" in seq.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_value += seq_value
        
        # 确定核算单元标识（使用accounting_unit_code和accounting_unit_name，如果没有则使用科室自己的信息）
        unit_code = dept.accounting_unit_code or dept.his_code
        unit_name = dept.accounting_unit_name or dept.his_name
        unit_key = (unit_code, unit_name)
        
        # 累加到核算单元
        if unit_key not in accounting_units:
            accounting_units[unit_key] = {
                'dept_ids': [],
                'doctor_value': Decimal('0'),
                'nurse_value': Decimal('0'),
                'tech_value': Decimal('0'),
                'sort_order': dept.sort_order  # 用于排序
            }
        
        accounting_units[unit_key]['dept_ids'].append(dept_id_val)
        accounting_units[unit_key]['doctor_value'] += doctor_value
        accounting_units[unit_key]['nurse_value'] += nurse_value
        accounting_units[unit_key]['tech_value'] += tech_value
    
    # 生成汇总数据（按核算单元）
    departments_data = []
    total_doctor_value = Decimal('0')
    total_nurse_value = Decimal('0')
    total_tech_value = Decimal('0')
    
    # 按sort_order排序
    sorted_units = sorted(accounting_units.items(), key=lambda x: x[1]['sort_order'])
    
    for (unit_code, unit_name), unit_data in sorted_units:
        doctor_value = unit_data['doctor_value']
        nurse_value = unit_data['nurse_value']
        tech_value = unit_data['tech_value']
        total_val = doctor_value + nurse_value + tech_value
        
        if total_val > 0:
            doctor_ratio = float(doctor_value / total_val * 100)
            nurse_ratio = float(nurse_value / total_val * 100)
            tech_ratio = float(tech_value / total_val * 100)
        else:
            doctor_ratio = 0
            nurse_ratio = 0
            tech_ratio = 0
        
        # 使用第一个科室的ID作为代表（用于查看明细）
        representative_dept_id = unit_data['dept_ids'][0]
        
        departments_data.append(CalculationSummaryResponse(
            department_id=representative_dept_id,
            department_code=unit_code,
            department_name=unit_name,
            doctor_value=doctor_value,
            doctor_ratio=doctor_ratio,
            nurse_value=nurse_value,
            nurse_ratio=nurse_ratio,
            tech_value=tech_value,
            tech_ratio=tech_ratio,
            total_value=total_val
        ))
        
        total_doctor_value += doctor_value
        total_nurse_value += nurse_value
        total_tech_value += tech_value
    
    # 计算全院汇总
    total_value = total_doctor_value + total_nurse_value + total_tech_value
    
    summary_data = CalculationSummaryResponse(
        department_id=0,
        department_code=None,
        department_name="全院汇总",
        doctor_value=total_doctor_value,
        doctor_ratio=float(total_doctor_value / total_value * 100) if total_value > 0 else 0,
        nurse_value=total_nurse_value,
        nurse_ratio=float(total_nurse_value / total_value * 100) if total_value > 0 else 0,
        tech_value=total_tech_value,
        tech_ratio=float(total_tech_value / total_value * 100) if total_value > 0 else 0,
        total_value=total_value
    )
    
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
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    
    # 验证科室是否存在
    department = db.query(Department).filter(Department.id == dept_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    # 查询该科室的所有计算结果（按模型节点排序）
    results = db.query(CalculationResult).join(
        ModelNode, CalculationResult.node_id == ModelNode.id
    ).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id
    ).order_by(ModelNode.sort_order).all()
    
    # 查询模型节点信息以获取业务导向等额外信息
    node_ids = [r.node_id for r in results]
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 查询导向规则名称映射
    from app.models.orientation_rule import OrientationRule
    orientation_rule_ids = set()
    for node in model_nodes:
        if node.orientation_rule_ids:
            orientation_rule_ids.update(node.orientation_rule_ids)
    
    orientation_rules = {}
    if orientation_rule_ids:
        rules = db.query(OrientationRule).filter(OrientationRule.id.in_(orientation_rule_ids)).all()
        orientation_rules = {rule.id: rule.name for rule in rules}
    
    # 构建节点映射
    result_map = {r.node_id: r for r in results}
    
    # 构建树形结构（包含所有节点，不仅仅是叶子节点）
    def build_dimension_tree(parent_id, level):
        """递归构建维度树"""
        children = []
        for result in results:
            if result.parent_id == parent_id and result.node_type == "dimension":
                node_info = node_info_map.get(result.node_id)
                
                # 获取导向规则名称
                orientation_names = []
                if node_info and node_info.orientation_rule_ids:
                    orientation_names = [
                        orientation_rules.get(rule_id, f"规则{rule_id}")
                        for rule_id in node_info.orientation_rule_ids
                    ]
                business_guide = "、".join(orientation_names) if orientation_names else (node_info.business_guide if node_info else None)
                
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
                    hospital_value=result.original_weight or result.weight,
                    dept_value=result.weight,
                    business_guide=business_guide,
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
    
    # 生成表格数据 - 转换为树形结构
    def build_tree_rows(sequence_name, dimensions):
        """将维度树转换为表格树形数据"""
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
        
        def build_tree_node(node, siblings_total=None):
            """构建树形节点数据
            
            siblings_total: 同级节点的金额总和（用于计算占比）
            """
            # 判断是否为末级维度
            is_leaf = not node.children or len(node.children) == 0
            
            # 计算当前节点的金额
            if is_leaf:
                current_amount = node.value or 0
                current_workload = node.workload or 0
            else:
                current_workload, current_amount = calculate_sum_from_children(node)
            
            # 计算占比
            if siblings_total and siblings_total > 0:
                ratio = (current_amount / siblings_total * 100)
                from decimal import Decimal
                ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
            else:
                ratio = node.ratio or 0
            
            # 创建节点数据
            if is_leaf:
                # 末级维度：显示完整信息（不包含children属性）
                node_info = node_info_map.get(node.node_id)
                tree_node = {
                    "id": node.node_id,
                    "node_id": node.node_id,
                    "dimension_name": node.dimension_name,
                    "dimension_code": node.dimension_code,
                    "node_code": node.dimension_code,  # 别名，兼容前端
                    "workload": current_workload,
                    "hospital_value": str(node.hospital_value) if node.hospital_value is not None else "-",
                    "business_guide": node.business_guide if node.business_guide else "-",
                    "dept_value": str(node.dept_value) if node.dept_value is not None else "-",
                    "amount": current_amount,
                    "ratio": ratio,
                    "calc_type": node_info.calc_type if node_info else None
                }
            else:
                # 非末级维度：部分信息用"-"，包含children数组
                node_info = node_info_map.get(node.node_id)
                tree_node = {
                    "id": node.node_id,
                    "node_id": node.node_id,
                    "dimension_name": node.dimension_name,
                    "dimension_code": node.dimension_code,
                    "node_code": node.dimension_code,  # 别名，兼容前端
                    "workload": current_workload,
                    "hospital_value": "-",
                    "business_guide": "-",
                    "dept_value": "-",
                    "amount": current_amount,
                    "ratio": ratio,
                    "calc_type": node_info.calc_type if node_info else None,
                    "children": []
                }
            
            # 递归处理子节点
            if node.children:
                # 计算子节点的金额总和
                children_total = sum(
                    (calculate_sum_from_children(child)[1] if child.children else (child.value or 0))
                    for child in node.children
                )
                
                for child in node.children:
                    child_node = build_tree_node(child, children_total)
                    tree_node["children"].append(child_node)
            
            return tree_node
        
        # 计算一级维度的金额总和
        first_level_total = sum(
            (calculate_sum_from_children(dim)[1] if dim.children else (dim.value or 0))
            for dim in dimensions
        )
        
        # 处理每个一级维度
        for dim in dimensions:
            tree_node = build_tree_node(dim, first_level_total)
            rows.append(tree_node)
        
        return rows
    
    # 为每个序列生成树形表格数据
    doctor_rows = []
    nurse_rows = []
    tech_rows = []
    
    for seq in sequences:
        if "医生" in seq.sequence_name:
            doctor_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
        elif "护理" in seq.sequence_name:
            nurse_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
        elif "医技" in seq.sequence_name:
            tech_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
    
    return {
        "department_id": dept_id,
        "department_name": department.accounting_unit_name or department.his_name,
        "period": task.period,
        "sequences": sequences,
        "doctor": doctor_rows,
        "nurse": nurse_rows,
        "tech": tech_rows
    }


@router.get("/results/hospital-detail", response_model=DepartmentDetailResponse)
def get_hospital_detail(
    task_id: str = Query(..., description="任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取全院汇总的详细业务价值数据 - 各维度汇总所有科室的数据"""
    from decimal import Decimal
    from collections import defaultdict
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    
    # 查询所有科室的所有计算结果（按模型节点排序）
    all_results = db.query(CalculationResult).join(
        ModelNode, CalculationResult.node_id == ModelNode.id
    ).filter(
        CalculationResult.task_id == task_id
    ).order_by(
        CalculationResult.department_id,
        ModelNode.sort_order
    ).all()
    
    if not all_results:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    # 查询模型节点信息
    node_ids = list(set([r.node_id for r in all_results]))
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 按节点ID汇总所有科室的数据
    node_aggregated = defaultdict(lambda: {
        'node_id': 0,
        'node_name': '',
        'node_code': '',
        'node_type': '',
        'parent_id': None,
        'workload': Decimal('0'),
        'value': Decimal('0'),
        'weight': None,  # 权重不汇总，取第一个
        'business_guide': None
    })
    
    for result in all_results:
        node_id = result.node_id
        agg = node_aggregated[node_id]
        
        # 基本信息（取第一次遇到的）
        if agg['node_id'] == 0:
            agg['node_id'] = result.node_id
            agg['node_name'] = result.node_name
            agg['node_code'] = result.node_code
            agg['node_type'] = result.node_type
            agg['parent_id'] = result.parent_id
            agg['weight'] = result.weight
            node_info = node_info_map.get(result.node_id)
            if node_info:
                agg['business_guide'] = node_info.business_guide
        
        # 汇总工作量和价值
        if result.workload:
            agg['workload'] += result.workload
        if result.value:
            agg['value'] += result.value
    
    # 构建汇总后的结果列表（模拟单个科室的结果结构）
    aggregated_results = []
    for node_id, agg in node_aggregated.items():
        # 创建一个模拟的CalculationResult对象
        class AggregatedResult:
            def __init__(self, data):
                self.node_id = data['node_id']
                self.node_name = data['node_name']
                self.node_code = data['node_code']
                self.node_type = data['node_type']
                self.parent_id = data['parent_id']
                self.workload = data['workload']
                self.value = data['value']
                self.weight = data['weight']
                self.ratio = Decimal('0')  # 稍后计算
        
        aggregated_results.append(AggregatedResult(agg))
    
    # 使用与单科室明细相同的逻辑构建树形结构
    results = aggregated_results  # 重命名以复用下面的代码
    
    # 构建节点映射
    result_map = {r.node_id: r for r in results}
    
    # 构建树形结构
    def build_dimension_tree(parent_id, level):
        """递归构建维度树"""
        children = []
        for result in results:
            if result.parent_id == parent_id and result.node_type == "dimension":
                node_info = node_info_map.get(result.node_id)
                agg_data = node_aggregated[result.node_id]
                
                dim = DimensionDetail(
                    node_id=result.node_id,
                    parent_id=result.parent_id,
                    dimension_name=result.node_name,
                    dimension_code=result.node_code,
                    level=level,
                    value=result.value or 0,
                    ratio=0,  # 稍后计算
                    workload=result.workload,
                    weight=result.weight,
                    hospital_value=result.weight,  # 全院汇总时，两个值相同
                    dept_value=result.weight,
                    business_guide=agg_data['business_guide'],
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
    
    # 生成表格数据 - 转换为树形结构（复用单科室的逻辑）
    def build_tree_rows(sequence_name, dimensions):
        """将维度树转换为表格树形数据"""
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
        
        def build_tree_node(node, siblings_total=None):
            """构建树形节点数据"""
            # 判断是否为末级维度
            is_leaf = not node.children or len(node.children) == 0
            
            # 计算当前节点的金额
            if is_leaf:
                current_amount = node.value or 0
                current_workload = node.workload or 0
            else:
                current_workload, current_amount = calculate_sum_from_children(node)
            
            # 计算占比
            if siblings_total and siblings_total > 0:
                ratio = (current_amount / siblings_total * 100)
                ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
            else:
                ratio = node.ratio or 0
            
            # 创建节点数据
            if is_leaf:
                # 末级维度：显示完整信息
                tree_node = {
                    "id": node.node_id,
                    "node_id": node.node_id,
                    "dimension_name": node.dimension_name,
                    "dimension_code": node.dimension_code,
                    "node_code": node.dimension_code,  # 别名，兼容前端
                    "workload": current_workload,
                    "hospital_value": str(node.hospital_value) if node.hospital_value is not None else "-",
                    "business_guide": node.business_guide or "-",
                    "dept_value": str(node.dept_value) if node.dept_value is not None else "-",
                    "amount": current_amount,
                    "ratio": ratio
                }
            else:
                # 非末级维度：部分信息用"-"，包含children数组
                tree_node = {
                    "id": node.node_id,
                    "node_id": node.node_id,
                    "dimension_name": node.dimension_name,
                    "dimension_code": node.dimension_code,
                    "node_code": node.dimension_code,  # 别名，兼容前端
                    "workload": current_workload,
                    "hospital_value": "-",
                    "business_guide": "-",
                    "dept_value": "-",
                    "amount": current_amount,
                    "ratio": ratio,
                    "children": []
                }
            
            # 递归处理子节点
            if node.children:
                # 计算子节点的金额总和
                children_total = sum(
                    (calculate_sum_from_children(child)[1] if child.children else (child.value or 0))
                    for child in node.children
                )
                
                for child in node.children:
                    child_node = build_tree_node(child, children_total)
                    tree_node["children"].append(child_node)
            
            return tree_node
        
        # 计算一级维度的金额总和
        first_level_total = sum(
            (calculate_sum_from_children(dim)[1] if dim.children else (dim.value or 0))
            for dim in dimensions
        )
        
        # 处理每个一级维度
        for dim in dimensions:
            tree_node = build_tree_node(dim, first_level_total)
            rows.append(tree_node)
        
        return rows
    
    # 为每个序列生成树形表格数据
    doctor_rows = []
    nurse_rows = []
    tech_rows = []
    
    for seq in sequences:
        if "医生" in seq.sequence_name:
            doctor_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
        elif "护理" in seq.sequence_name:
            nurse_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
        elif "医技" in seq.sequence_name:
            tech_rows = build_tree_rows(seq.sequence_name, seq.dimensions)
    
    return {
        "department_id": 0,
        "department_name": "全院汇总",
        "period": task.period,
        "sequences": sequences,
        "doctor": doctor_rows,
        "nurse": nurse_rows,
        "tech": tech_rows
    }


@router.get("/results/orientation-summary", response_model=OrientationSummaryResponse)
def get_orientation_summary(
    task_id: str = Query(..., description="任务ID"),
    dept_id: Optional[int] = Query(None, description="科室ID，不传则查询全院"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取导向汇总数据 - 直接展示业务导向过程表内容"""
    from app.models.orientation_adjustment_detail import OrientationAdjustmentDetail
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    
    # 查询导向调整明细
    query = db.query(OrientationAdjustmentDetail).filter(
        OrientationAdjustmentDetail.task_id == task_id
    )
    
    if dept_id:
        query = query.filter(OrientationAdjustmentDetail.department_id == dept_id)
    
    # 查询所有明细，按科室和维度名称排序
    details = query.order_by(
        OrientationAdjustmentDetail.department_name,
        OrientationAdjustmentDetail.node_name
    ).all()
    
    # 如果没有数据，返回空结构
    if not details:
        return {
            "task_id": task_id,
            "department_id": dept_id or 0,
            "department_name": "全院" if not dept_id else "",
            "period": task.period,
            "doctor": [],
            "nurse": [],
            "tech": []
        }
    
    # 查询节点信息以获取准确的序列归属和完整路径
    node_ids = list(set([d.node_id for d in details]))
    
    # 使用递归CTE查询每个节点所属的序列和完整路径
    from sqlalchemy import text
    path_query = text("""
        WITH RECURSIVE node_path AS (
            -- 基础查询：起始节点
            SELECT 
                id as original_id,
                id,
                name,
                node_type,
                parent_id,
                CAST(name AS TEXT) as path,
                1 as level
            FROM model_nodes
            WHERE id = ANY(:node_ids)
            
            UNION ALL
            
            -- 递归查询：向上查找父节点
            SELECT 
                np.original_id,
                p.id,
                p.name,
                p.node_type,
                p.parent_id,
                CAST(p.name || '-' || np.path AS TEXT),
                np.level + 1
            FROM model_nodes p
            INNER JOIN node_path np ON p.id = np.parent_id
        )
        SELECT 
            original_id,
            path,
            node_type
        FROM node_path
        WHERE parent_id IS NULL OR node_type = 'sequence'
        ORDER BY original_id, level DESC
    """)
    
    result = db.execute(path_query, {"node_ids": node_ids})
    node_data = {}
    for row in result:
        if row[0] not in node_data:  # 只取第一条（最长路径）
            node_data[row[0]] = {
                'path': row[1],
                'sequence': row[1].split('-')[0] if row[1] else ''
            }
    
    # 按序列分组
    doctor_details = []
    nurse_details = []
    tech_details = []
    
    for detail in details:
        # 获取节点的完整路径和序列
        node_info = node_data.get(detail.node_id, {'path': detail.node_name, 'sequence': ''})
        
        # 创建响应对象并设置完整路径
        detail_dict = {
            'id': detail.id,
            'department_name': detail.department_name,
            'node_code': detail.node_code,
            'node_name': node_info['path'],  # 使用完整路径
            'orientation_rule_name': detail.orientation_rule_name,
            'orientation_type': detail.orientation_type,
            'actual_value': detail.actual_value,
            'benchmark_value': detail.benchmark_value,
            'orientation_ratio': detail.orientation_ratio,
            'ladder_lower_limit': detail.ladder_lower_limit,
            'ladder_upper_limit': detail.ladder_upper_limit,
            'adjustment_intensity': detail.adjustment_intensity,
            'original_weight': detail.original_weight,
            'adjusted_weight': detail.adjusted_weight,
            'is_adjusted': detail.is_adjusted,
            'adjustment_reason': detail.adjustment_reason
        }
        
        detail_response = OrientationAdjustmentDetailResponse(**detail_dict)
        
        # 根据节点所属序列判断
        sequence_name = node_info['sequence']
        
        if "医生" in sequence_name or "医疗" in sequence_name or "医师" in sequence_name:
            doctor_details.append(detail_response)
        elif "护理" in sequence_name or "护士" in sequence_name:
            nurse_details.append(detail_response)
        elif "医技" in sequence_name or "技师" in sequence_name:
            tech_details.append(detail_response)
        else:
            # 如果没有找到序列，打印日志
            print(f"[WARNING] 无法判断节点 {detail.node_name} (ID: {detail.node_id}) 的序列归属")
            # 默认归入医生序列
            doctor_details.append(detail_response)
    
    return {
        "task_id": task_id,
        "department_id": dept_id or 0,
        "department_name": details[0].department_name if dept_id else "全院",
        "period": task.period,
        "doctor": doctor_details,
        "nurse": nurse_details,
        "tech": tech_details
    }


def _get_sequence_name(db: Session, node: ModelNode) -> str:
    """通过节点向上查找序列名称"""
    current = node
    while current.parent_id:
        parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
        if not parent:
            break
        if parent.node_type == "sequence":
            return parent.name
        current = parent
    return "未知序列"


@router.get("/tasks/{task_id}/logs")
def get_task_logs(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取任务执行日志"""
    from app.models.calculation_step_log import CalculationStepLog
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    
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


@router.get("/results/export/summary")
def export_summary(
    task_id: Optional[str] = Query(None, description="计算任务ID（优先使用）"),
    period: Optional[str] = Query(None, description="评估月份(YYYY-MM)"),
    model_version_id: Optional[int] = Query(None, description="模型版本ID"),
    mom_task_id: Optional[str] = Query(None, description="环比任务ID"),
    yoy_task_id: Optional[str] = Query(None, description="同比任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出汇总表（同步）- 按核算单元分组，与页面显示一致，包含参考值、环比、同比数据"""
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    from app.utils.hospital_filter import get_current_hospital_id_or_raise
    from app.models.reference_value import ReferenceValue
    from decimal import Decimal
    from collections import defaultdict
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 优先使用task_id，否则按period和model_version_id查找
    if task_id:
        task = db.query(CalculationTask).filter(
            CalculationTask.task_id == task_id,
            CalculationTask.status == "completed"
        ).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"未找到任务: {task_id}")
        period = task.period
    else:
        if not period:
            raise HTTPException(status_code=400, detail="请提供task_id或period参数")
        # 查找最新的完成任务（使用辅助函数）
        task = _get_latest_completed_task(db, period, model_version_id)
    
    # 获取所有参与核算的科室（is_active=True）
    all_active_depts = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).order_by(Department.sort_order, Department.id).all()
    
    # 查询所有计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id
    ).all()
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 计算汇总数据
    def calculate_sum_from_children(node_id, results):
        """递归计算节点的价值"""
        current_node = next((r for r in results if r.node_id == node_id), None)
        if not current_node:
            return Decimal('0')
        
        children = [r for r in results if r.parent_id == node_id and r.node_type == "dimension"]
        
        if not children or len(children) == 0:
            return current_node.value or Decimal('0')
        
        total_value = Decimal('0')
        for child in children:
            child_value = calculate_sum_from_children(child.node_id, results)
            total_value += child_value
        
        return total_value
    
    # 辅助函数：获取任务的汇总数据（按科室代码索引）
    def get_task_summary_by_dept_code(task_id_param):
        """获取指定任务的汇总数据，返回按科室代码索引的字典"""
        if not task_id_param:
            return {}
        
        compare_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id_param
        ).all()
        
        if not compare_results:
            return {}
        
        # 按科室分组
        compare_by_dept = defaultdict(list)
        for result in compare_results:
            compare_by_dept[result.department_id].append(result)
        
        # 按核算单元汇总
        compare_units = {}
        for dept in all_active_depts:
            dept_id_val = dept.id
            results = compare_by_dept.get(dept_id_val, [])
            
            sequences = [r for r in results if r.node_type == "sequence"]
            total_val = Decimal('0')
            
            for seq in sequences:
                seq_value = calculate_sum_from_children(seq.node_id, results)
                total_val += seq_value
            
            unit_code = dept.accounting_unit_code or dept.his_code
            if unit_code not in compare_units:
                compare_units[unit_code] = Decimal('0')
            compare_units[unit_code] += total_val
        
        return compare_units
    
    # 获取参考值数据（按科室代码索引）
    reference_values = {}
    ref_records = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == period
    ).all()
    for ref in ref_records:
        reference_values[ref.department_code] = ref.reference_value
    
    # 获取环比数据
    mom_summary = get_task_summary_by_dept_code(mom_task_id)
    
    # 获取同比数据
    yoy_summary = get_task_summary_by_dept_code(yoy_task_id)
    
    # 按核算单元分组汇总（与页面显示逻辑一致）
    accounting_units = {}  # key: (accounting_unit_code, accounting_unit_name), value: {dept_ids, values}
    
    for dept in all_active_depts:
        dept_id_val = dept.id
        results = results_by_dept.get(dept_id_val, [])
        
        sequences = [r for r in results if r.node_type == "sequence"]
        
        doctor_value = Decimal('0')
        nurse_value = Decimal('0')
        tech_value = Decimal('0')
        
        for seq in sequences:
            seq_value = calculate_sum_from_children(seq.node_id, results)
            
            node_name_lower = seq.node_name.lower()
            if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
               "doctor" in node_name_lower or "physician" in node_name_lower:
                doctor_value += seq_value
            elif "护理" in seq.node_name or "护士" in seq.node_name or \
                 "nurse" in node_name_lower or "nursing" in node_name_lower:
                nurse_value += seq_value
            elif "医技" in seq.node_name or "技师" in seq.node_name or \
                 "tech" in node_name_lower or "technician" in node_name_lower:
                tech_value += seq_value
        
        # 确定核算单元标识（使用accounting_unit_code和accounting_unit_name，如果没有则使用科室自己的信息）
        unit_code = dept.accounting_unit_code or dept.his_code
        unit_name = dept.accounting_unit_name or dept.his_name
        unit_key = (unit_code, unit_name)
        
        # 累加到核算单元
        if unit_key not in accounting_units:
            accounting_units[unit_key] = {
                'dept_ids': [],
                'doctor_value': Decimal('0'),
                'nurse_value': Decimal('0'),
                'tech_value': Decimal('0'),
                'sort_order': dept.sort_order
            }
        
        accounting_units[unit_key]['dept_ids'].append(dept_id_val)
        accounting_units[unit_key]['doctor_value'] += doctor_value
        accounting_units[unit_key]['nurse_value'] += nurse_value
        accounting_units[unit_key]['tech_value'] += tech_value
    
    # 生成汇总数据（按核算单元）
    departments_data = []
    total_doctor_value = Decimal('0')
    total_nurse_value = Decimal('0')
    total_tech_value = Decimal('0')
    total_reference_value = Decimal('0')
    total_mom_value = Decimal('0')
    total_yoy_value = Decimal('0')
    has_reference = False
    has_mom = False
    has_yoy = False
    
    # 按sort_order排序
    sorted_units = sorted(accounting_units.items(), key=lambda x: x[1]['sort_order'])
    
    for (unit_code, unit_name), unit_data in sorted_units:
        doctor_value = unit_data['doctor_value']
        nurse_value = unit_data['nurse_value']
        tech_value = unit_data['tech_value']
        total_val = doctor_value + nurse_value + tech_value
        
        if total_val > 0:
            doctor_ratio = float(doctor_value / total_val * 100)
            nurse_ratio = float(nurse_value / total_val * 100)
            tech_ratio = float(tech_value / total_val * 100)
        else:
            doctor_ratio = 0
            nurse_ratio = 0
            tech_ratio = 0
        
        # 获取参考值
        ref_value = reference_values.get(unit_code)
        if ref_value is not None:
            has_reference = True
            total_reference_value += Decimal(str(ref_value))
        
        # 计算核算/实发比例
        actual_ref_ratio = None
        if ref_value is not None and ref_value != 0:
            actual_ref_ratio = float(total_val / Decimal(str(ref_value)))
        
        # 获取环比价值
        mom_value = mom_summary.get(unit_code)
        if mom_value is not None:
            has_mom = True
            total_mom_value += mom_value
        
        # 计算当期/环期比例
        mom_ratio = None
        if mom_value is not None and mom_value != 0:
            mom_ratio = float(total_val / mom_value)
        
        # 获取同比价值
        yoy_value = yoy_summary.get(unit_code)
        if yoy_value is not None:
            has_yoy = True
            total_yoy_value += yoy_value
        
        # 计算当期/同期比例
        yoy_ratio = None
        if yoy_value is not None and yoy_value != 0:
            yoy_ratio = float(total_val / yoy_value)
        
        departments_data.append({
            'department_id': unit_data['dept_ids'][0],
            'department_code': unit_code,
            'department_name': unit_name,
            'doctor_value': doctor_value,
            'doctor_ratio': doctor_ratio,
            'nurse_value': nurse_value,
            'nurse_ratio': nurse_ratio,
            'tech_value': tech_value,
            'tech_ratio': tech_ratio,
            'total_value': total_val,
            'reference_value': ref_value,
            'actual_reference_ratio': actual_ref_ratio,
            'mom_value': float(mom_value) if mom_value is not None else None,
            'mom_ratio': mom_ratio,
            'yoy_value': float(yoy_value) if yoy_value is not None else None,
            'yoy_ratio': yoy_ratio
        })
        
        total_doctor_value += doctor_value
        total_nurse_value += nurse_value
        total_tech_value += tech_value
    
    # 计算全院汇总
    total_value = total_doctor_value + total_nurse_value + total_tech_value
    
    # 全院汇总的比例计算
    summary_actual_ref_ratio = None
    if has_reference and total_reference_value != 0:
        summary_actual_ref_ratio = float(total_value / total_reference_value)
    
    summary_mom_ratio = None
    if has_mom and total_mom_value != 0:
        summary_mom_ratio = float(total_value / total_mom_value)
    
    summary_yoy_ratio = None
    if has_yoy and total_yoy_value != 0:
        summary_yoy_ratio = float(total_value / total_yoy_value)
    
    summary_data = {
        'department_id': 0,
        'department_code': None,
        'department_name': '全院汇总',
        'doctor_value': total_doctor_value,
        'doctor_ratio': float(total_doctor_value / total_value * 100) if total_value > 0 else 0,
        'nurse_value': total_nurse_value,
        'nurse_ratio': float(total_nurse_value / total_value * 100) if total_value > 0 else 0,
        'tech_value': total_tech_value,
        'tech_ratio': float(total_tech_value / total_value * 100) if total_value > 0 else 0,
        'total_value': total_value,
        'reference_value': float(total_reference_value) if has_reference else None,
        'actual_reference_ratio': summary_actual_ref_ratio,
        'mom_value': float(total_mom_value) if has_mom else None,
        'mom_ratio': summary_mom_ratio,
        'yoy_value': float(total_yoy_value) if has_yoy else None,
        'yoy_ratio': summary_yoy_ratio
    }
    
    # 获取医院名称
    from app.models.hospital import Hospital
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    hospital_name = hospital.name if hospital else "未知医院"
    
    # 获取版本号
    version = task.model_version.version if task.model_version else None
    
    # 生成Excel
    excel_data = {
        'summary': summary_data,
        'departments': departments_data
    }
    
    excel_file = ExportService.export_summary_to_excel(excel_data, period, hospital_name, version)
    
    # 返回文件流
    from urllib.parse import quote
    version_suffix = f"_v{version}" if version else ""
    filename = f"{hospital_name}_科室业务价值汇总_{period}{version_suffix}.xlsx"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/results/export/detail")
def export_detail(
    task_id: str = Query(..., description="计算任务ID"),
    mom_task_id: Optional[str] = Query(None, description="环比任务ID"),
    yoy_task_id: Optional[str] = Query(None, description="同比任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出明细表（同步，ZIP打包）- 按核算单元分组，与页面显示一致，包含参考值、环比、同比数据"""
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    from urllib.parse import quote
    from collections import defaultdict
    from app.utils.hospital_filter import get_current_hospital_id_or_raise
    from app.models.orientation_rule import OrientationRule
    from app.models.reference_value import ReferenceValue
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询所有科室的计算结果（按模型节点排序）
    all_results = db.query(CalculationResult).join(
        ModelNode, CalculationResult.node_id == ModelNode.id
    ).filter(
        CalculationResult.task_id == task_id
    ).order_by(
        CalculationResult.department_id,
        ModelNode.sort_order
    ).all()
    
    if not all_results:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    # 查询模型节点信息
    node_ids = list(set([r.node_id for r in all_results]))
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 查询导向规则名称映射（与页面显示一致）
    orientation_rule_ids = set()
    for node in model_nodes:
        if node.orientation_rule_ids:
            orientation_rule_ids.update(node.orientation_rule_ids)
    
    orientation_rules = {}
    if orientation_rule_ids:
        rules = db.query(OrientationRule).filter(OrientationRule.id.in_(orientation_rule_ids)).all()
        orientation_rules = {rule.id: rule.name for rule in rules}
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 获取所有参与核算的科室（is_active=True）
    all_active_depts = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).order_by(Department.sort_order, Department.id).all()
    
    # 按核算单元分组（与页面显示逻辑一致）
    accounting_units = {}  # key: (unit_code, unit_name), value: {dept_ids, sort_order}
    
    for dept in all_active_depts:
        unit_code = dept.accounting_unit_code or dept.his_code
        unit_name = dept.accounting_unit_name or dept.his_name
        unit_key = (unit_code, unit_name)
        
        if unit_key not in accounting_units:
            accounting_units[unit_key] = {
                'dept_ids': [],
                'sort_order': dept.sort_order
            }
        accounting_units[unit_key]['dept_ids'].append(dept.id)
    
    # 为每个核算单元生成明细数据
    departments_data = []
    
    # 按sort_order排序
    sorted_units = sorted(accounting_units.items(), key=lambda x: x[1]['sort_order'])
    
    for (unit_code, unit_name), unit_data in sorted_units:
        # 合并该核算单元下所有科室的计算结果
        combined_results = []
        for dept_id in unit_data['dept_ids']:
            combined_results.extend(results_by_dept.get(dept_id, []))
        
        if not combined_results:
            continue
        
        # 构建树形结构（复用现有逻辑）
        def build_dimension_tree(parent_id, level, results):
            """递归构建维度树"""
            children = []
            for result in results:
                if result.parent_id == parent_id and result.node_type == "dimension":
                    node_info = node_info_map.get(result.node_id)
                    
                    # 获取导向规则名称（与页面显示一致）
                    orientation_names = []
                    if node_info and node_info.orientation_rule_ids:
                        orientation_names = [
                            orientation_rules.get(rule_id, f"规则{rule_id}")
                            for rule_id in node_info.orientation_rule_ids
                        ]
                    business_guide = "、".join(orientation_names) if orientation_names else (node_info.business_guide if node_info else None)
                    
                    dim = {
                        'node_id': result.node_id,
                        'parent_id': result.parent_id,
                        'dimension_name': result.node_name,
                        'dimension_code': result.node_code,
                        'level': level,
                        'value': result.value or 0,
                        'ratio': result.ratio or 0,
                        'workload': result.workload,
                        'weight': result.weight,
                        'original_weight': result.original_weight,
                        'business_guide': business_guide,
                        'sort_order': node_info.sort_order if node_info else 999,
                        'children': build_dimension_tree(result.node_id, level + 1, results)
                    }
                    children.append(dim)
            # 按sort_order排序（同一父节点下的兄弟节点排序）
            children.sort(key=lambda x: x['sort_order'])
            return children
        
        # 生成表格数据
        def build_tree_rows(dimensions):
            """将维度树转换为表格树形数据"""
            rows = []
            
            def calculate_sum_from_children(node):
                """计算节点的工作量和金额"""
                if not node.get('children') or len(node['children']) == 0:
                    return node.get('workload') or 0, node.get('value') or 0
                
                total_workload = 0
                total_amount = 0
                for child in node['children']:
                    child_workload, child_amount = calculate_sum_from_children(child)
                    total_workload += child_workload
                    total_amount += child_amount
                
                return total_workload, total_amount
            
            def build_tree_node(node, siblings_total=None):
                """构建树形节点数据"""
                is_leaf = not node.get('children') or len(node['children']) == 0
                
                if is_leaf:
                    current_amount = node.get('value') or 0
                    current_workload = node.get('workload') or 0
                else:
                    current_workload, current_amount = calculate_sum_from_children(node)
                
                if siblings_total and siblings_total > 0:
                    ratio = (current_amount / siblings_total * 100)
                    from decimal import Decimal
                    ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
                else:
                    ratio = node.get('ratio') or 0
                
                if is_leaf:
                    # 叶子节点：显示完整信息（与页面显示一致）
                    hospital_value = node.get('original_weight') or node.get('weight')
                    tree_node = {
                        "id": node['node_id'],
                        "dimension_name": node['dimension_name'],
                        "workload": current_workload,
                        "hospital_value": str(hospital_value) if hospital_value is not None else "-",
                        "business_guide": node.get('business_guide') or "-",
                        "dept_value": str(node['weight']) if node.get('weight') is not None else "-",
                        "amount": current_amount,
                        "ratio": ratio
                    }
                else:
                    tree_node = {
                        "id": node['node_id'],
                        "dimension_name": node['dimension_name'],
                        "workload": current_workload,
                        "hospital_value": "-",
                        "business_guide": "-",
                        "dept_value": "-",
                        "amount": current_amount,
                        "ratio": ratio,
                        "children": []
                    }
                
                if node.get('children'):
                    children_total = sum(
                        (calculate_sum_from_children(child)[1] if child.get('children') else (child.get('value') or 0))
                        for child in node['children']
                    )
                    
                    for child in node['children']:
                        child_node = build_tree_node(child, children_total)
                        tree_node["children"].append(child_node)
                
                return tree_node
            
            first_level_total = sum(
                (calculate_sum_from_children(dim)[1] if dim.get('children') else (dim.get('value') or 0))
                for dim in dimensions
            )
            
            for dim in dimensions:
                tree_node = build_tree_node(dim, first_level_total)
                rows.append(tree_node)
            
            return rows
        
        # 为每个序列生成数据
        doctor_rows = []
        nurse_rows = []
        tech_rows = []
        
        sequences = [r for r in combined_results if r.node_type == "sequence"]
        
        for seq in sequences:
            dimensions = build_dimension_tree(seq.node_id, 1, combined_results)
            rows = build_tree_rows(dimensions)
            
            if "医生" in seq.node_name:
                doctor_rows = rows
            elif "护理" in seq.node_name:
                nurse_rows = rows
            elif "医技" in seq.node_name:
                tech_rows = rows
        
        departments_data.append({
            'dept_name': unit_name,
            'doctor': doctor_rows,
            'nurse': nurse_rows,
            'tech': tech_rows
        })
    
    # 获取医院名称
    from app.models.hospital import Hospital
    from decimal import Decimal
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    hospital_name = hospital.name if hospital else "未知医院"
    
    # 生成全院汇总数据（按维度节点累加所有科室的数据）
    node_aggregated = defaultdict(lambda: {
        'node_id': 0,
        'node_name': '',
        'node_code': '',
        'node_type': '',
        'parent_id': None,
        'workload': Decimal('0'),
        'value': Decimal('0'),
        'weight': None,
        'business_guide': None
    })
    
    for result in all_results:
        node_id = result.node_id
        agg = node_aggregated[node_id]
        
        if agg['node_id'] == 0:
            agg['node_id'] = result.node_id
            agg['node_name'] = result.node_name
            agg['node_code'] = result.node_code
            agg['node_type'] = result.node_type
            agg['parent_id'] = result.parent_id
            agg['weight'] = result.weight
            node_info = node_info_map.get(result.node_id)
            if node_info:
                orientation_names = []
                if node_info.orientation_rule_ids:
                    orientation_names = [
                        orientation_rules.get(rule_id, f"规则{rule_id}")
                        for rule_id in node_info.orientation_rule_ids
                    ]
                agg['business_guide'] = "、".join(orientation_names) if orientation_names else node_info.business_guide
        
        if result.workload:
            agg['workload'] += result.workload
        if result.value:
            agg['value'] += result.value
    
    # 构建全院汇总的树形结构
    def build_hospital_dimension_tree(parent_id, level):
        children = []
        for node_id, agg in node_aggregated.items():
            if agg['parent_id'] == parent_id and agg['node_type'] == "dimension":
                node_info = node_info_map.get(agg['node_id'])
                dim = {
                    'node_id': agg['node_id'],
                    'parent_id': agg['parent_id'],
                    'dimension_name': agg['node_name'],
                    'dimension_code': agg['node_code'],
                    'level': level,
                    'value': agg['value'] or 0,
                    'ratio': 0,
                    'workload': agg['workload'],
                    'weight': agg['weight'],
                    'business_guide': agg['business_guide'],
                    'sort_order': node_info.sort_order if node_info else 999,
                    'children': build_hospital_dimension_tree(agg['node_id'], level + 1)
                }
                children.append(dim)
        children.sort(key=lambda x: x['sort_order'])
        return children
    
    def build_hospital_tree_rows(dimensions):
        rows = []
        
        def calculate_sum_from_children(node):
            if not node.get('children') or len(node['children']) == 0:
                return node.get('workload') or 0, node.get('value') or 0
            total_workload = 0
            total_amount = 0
            for child in node['children']:
                child_workload, child_amount = calculate_sum_from_children(child)
                total_workload += child_workload
                total_amount += child_amount
            return total_workload, total_amount
        
        def build_tree_node(node, siblings_total=None):
            is_leaf = not node.get('children') or len(node['children']) == 0
            
            if is_leaf:
                current_amount = node.get('value') or 0
                current_workload = node.get('workload') or 0
            else:
                current_workload, current_amount = calculate_sum_from_children(node)
            
            if siblings_total and siblings_total > 0:
                ratio = (float(current_amount) / float(siblings_total) * 100)
                ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
            else:
                ratio = node.get('ratio') or 0
            
            tree_node = {
                "id": node['node_id'],
                "dimension_name": node['dimension_name'],
                "workload": current_workload,
                "hospital_value": str(node['weight']) if node.get('weight') is not None else "-",
                "business_guide": node.get('business_guide') or "-",
                "amount": current_amount,
                "ratio": ratio
            }
            
            if node.get('children'):
                tree_node["children"] = []
                children_total = sum(
                    (calculate_sum_from_children(child)[1] if child.get('children') else (child.get('value') or 0))
                    for child in node['children']
                )
                for child in node['children']:
                    child_node = build_tree_node(child, children_total)
                    tree_node["children"].append(child_node)
            
            return tree_node
        
        first_level_total = sum(
            (calculate_sum_from_children(dim)[1] if dim.get('children') else (dim.get('value') or 0))
            for dim in dimensions
        )
        
        for dim in dimensions:
            tree_node = build_tree_node(dim, first_level_total)
            rows.append(tree_node)
        
        return rows
    
    # 生成全院汇总的各序列数据
    hospital_detail_data = {'doctor': [], 'nurse': [], 'tech': []}
    for node_id, agg in node_aggregated.items():
        if agg['node_type'] == "sequence":
            dimensions = build_hospital_dimension_tree(agg['node_id'], 1)
            rows = build_hospital_tree_rows(dimensions)
            
            if "医生" in agg['node_name']:
                hospital_detail_data['doctor'] = rows
            elif "护理" in agg['node_name']:
                hospital_detail_data['nurse'] = rows
            elif "医技" in agg['node_name']:
                hospital_detail_data['tech'] = rows
    
    # 生成汇总表数据（复用汇总API的逻辑）
    def calculate_sum_from_children_for_summary(node_id, results):
        """递归计算节点的价值（从子节点汇总）"""
        current_node = next((r for r in results if r.node_id == node_id), None)
        if not current_node:
            return Decimal('0')
        children = [r for r in results if r.parent_id == node_id and r.node_type == "dimension"]
        if not children:
            return current_node.value or Decimal('0')
        total_value = Decimal('0')
        for child in children:
            child_value = calculate_sum_from_children_for_summary(child.node_id, results)
            total_value += child_value
        return total_value
    
    # 辅助函数：获取任务的汇总数据（按科室代码索引）
    def get_task_summary_by_dept_code(task_id_param):
        """获取指定任务的汇总数据，返回按科室代码索引的字典"""
        if not task_id_param:
            return {}
        
        compare_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id_param
        ).all()
        
        if not compare_results:
            return {}
        
        # 按科室分组
        compare_by_dept = defaultdict(list)
        for result in compare_results:
            compare_by_dept[result.department_id].append(result)
        
        # 按核算单元汇总
        compare_units = {}
        for dept in all_active_depts:
            dept_id_val = dept.id
            results = compare_by_dept.get(dept_id_val, [])
            
            sequences = [r for r in results if r.node_type == "sequence"]
            total_val = Decimal('0')
            
            for seq in sequences:
                seq_value = calculate_sum_from_children_for_summary(seq.node_id, results)
                total_val += seq_value
            
            unit_code = dept.accounting_unit_code or dept.his_code
            if unit_code not in compare_units:
                compare_units[unit_code] = Decimal('0')
            compare_units[unit_code] += total_val
        
        return compare_units
    
    # 获取参考值数据（按科室代码索引）
    reference_values = {}
    ref_records = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == task.period
    ).all()
    for ref in ref_records:
        reference_values[ref.department_code] = ref.reference_value
    
    # 获取环比数据
    mom_summary = get_task_summary_by_dept_code(mom_task_id)
    
    # 获取同比数据
    yoy_summary = get_task_summary_by_dept_code(yoy_task_id)
    
    # 按核算单元计算汇总
    summary_by_unit = {}
    for (unit_code, unit_name), unit_data in sorted_units:
        combined_results = []
        for dept_id in unit_data['dept_ids']:
            combined_results.extend(results_by_dept.get(dept_id, []))
        
        sequences = [r for r in combined_results if r.node_type == "sequence"]
        doctor_value = Decimal('0')
        nurse_value = Decimal('0')
        tech_value = Decimal('0')
        
        for seq in sequences:
            seq_value = calculate_sum_from_children_for_summary(seq.node_id, combined_results)
            if "医生" in seq.node_name:
                doctor_value += seq_value
            elif "护理" in seq.node_name:
                nurse_value += seq_value
            elif "医技" in seq.node_name:
                tech_value += seq_value
        
        total_val = doctor_value + nurse_value + tech_value
        
        # 获取参考值
        ref_value = reference_values.get(unit_code)
        
        # 计算核算/实发比例
        actual_ref_ratio = None
        if ref_value is not None and ref_value != 0:
            actual_ref_ratio = float(total_val / Decimal(str(ref_value)))
        
        # 获取环比价值
        mom_value = mom_summary.get(unit_code)
        
        # 计算当期/环期比例
        mom_ratio = None
        if mom_value is not None and mom_value != 0:
            mom_ratio = float(total_val / mom_value)
        
        # 获取同比价值
        yoy_value = yoy_summary.get(unit_code)
        
        # 计算当期/同期比例
        yoy_ratio = None
        if yoy_value is not None and yoy_value != 0:
            yoy_ratio = float(total_val / yoy_value)
        
        summary_by_unit[(unit_code, unit_name)] = {
            'doctor_value': doctor_value,
            'nurse_value': nurse_value,
            'tech_value': tech_value,
            'total_value': total_val,
            'doctor_ratio': float(doctor_value / total_val * 100) if total_val > 0 else 0,
            'nurse_ratio': float(nurse_value / total_val * 100) if total_val > 0 else 0,
            'tech_ratio': float(tech_value / total_val * 100) if total_val > 0 else 0,
            'reference_value': ref_value,
            'actual_reference_ratio': actual_ref_ratio,
            'mom_value': float(mom_value) if mom_value is not None else None,
            'mom_ratio': mom_ratio,
            'yoy_value': float(yoy_value) if yoy_value is not None else None,
            'yoy_ratio': yoy_ratio
        }
    
    # 构建汇总表数据结构
    total_doctor = sum(v['doctor_value'] for v in summary_by_unit.values())
    total_nurse = sum(v['nurse_value'] for v in summary_by_unit.values())
    total_tech = sum(v['tech_value'] for v in summary_by_unit.values())
    total_all = total_doctor + total_nurse + total_tech
    
    # 计算全院汇总的参考值、环比、同比
    total_reference_value = Decimal('0')
    total_mom_value = Decimal('0')
    total_yoy_value = Decimal('0')
    has_reference = False
    has_mom = False
    has_yoy = False
    
    for v in summary_by_unit.values():
        if v['reference_value'] is not None:
            has_reference = True
            total_reference_value += Decimal(str(v['reference_value']))
        if v['mom_value'] is not None:
            has_mom = True
            total_mom_value += Decimal(str(v['mom_value']))
        if v['yoy_value'] is not None:
            has_yoy = True
            total_yoy_value += Decimal(str(v['yoy_value']))
    
    # 全院汇总的比例计算
    summary_actual_ref_ratio = None
    if has_reference and total_reference_value != 0:
        summary_actual_ref_ratio = float(total_all / total_reference_value)
    
    summary_mom_ratio = None
    if has_mom and total_mom_value != 0:
        summary_mom_ratio = float(total_all / total_mom_value)
    
    summary_yoy_ratio = None
    if has_yoy and total_yoy_value != 0:
        summary_yoy_ratio = float(total_all / total_yoy_value)
    
    summary_data = {
        'summary': {
            'department_id': 0,
            'department_code': None,
            'department_name': '全院汇总',
            'doctor_value': total_doctor,
            'doctor_ratio': float(total_doctor / total_all * 100) if total_all > 0 else 0,
            'nurse_value': total_nurse,
            'nurse_ratio': float(total_nurse / total_all * 100) if total_all > 0 else 0,
            'tech_value': total_tech,
            'tech_ratio': float(total_tech / total_all * 100) if total_all > 0 else 0,
            'total_value': total_all,
            'reference_value': float(total_reference_value) if has_reference else None,
            'actual_reference_ratio': summary_actual_ref_ratio,
            'mom_value': float(total_mom_value) if has_mom else None,
            'mom_ratio': summary_mom_ratio,
            'yoy_value': float(total_yoy_value) if has_yoy else None,
            'yoy_ratio': summary_yoy_ratio
        },
        'departments': [
            {
                'department_id': unit_data['dept_ids'][0] if accounting_units[(unit_code, unit_name)]['dept_ids'] else 0,
                'department_code': unit_code,
                'department_name': unit_name,
                'doctor_value': summary_by_unit[(unit_code, unit_name)]['doctor_value'],
                'doctor_ratio': summary_by_unit[(unit_code, unit_name)]['doctor_ratio'],
                'nurse_value': summary_by_unit[(unit_code, unit_name)]['nurse_value'],
                'nurse_ratio': summary_by_unit[(unit_code, unit_name)]['nurse_ratio'],
                'tech_value': summary_by_unit[(unit_code, unit_name)]['tech_value'],
                'tech_ratio': summary_by_unit[(unit_code, unit_name)]['tech_ratio'],
                'total_value': summary_by_unit[(unit_code, unit_name)]['total_value'],
                'reference_value': summary_by_unit[(unit_code, unit_name)]['reference_value'],
                'actual_reference_ratio': summary_by_unit[(unit_code, unit_name)]['actual_reference_ratio'],
                'mom_value': summary_by_unit[(unit_code, unit_name)]['mom_value'],
                'mom_ratio': summary_by_unit[(unit_code, unit_name)]['mom_ratio'],
                'yoy_value': summary_by_unit[(unit_code, unit_name)]['yoy_value'],
                'yoy_ratio': summary_by_unit[(unit_code, unit_name)]['yoy_ratio']
            }
            for (unit_code, unit_name), _ in sorted_units
            if (unit_code, unit_name) in summary_by_unit
        ]
    }
    
    # 获取版本号
    version = task.model_version.version if task.model_version else None
    
    # 生成ZIP文件（包含汇总表、全院明细和各科室明细）
    zip_file = ExportService.export_all_reports_to_zip(
        task.period, summary_data, departments_data, hospital_name, hospital_detail_data, version
    )
    
    # 返回文件流（版本号本身可能已包含v前缀，不重复添加）
    version_suffix = f"_{version}" if version else ""
    filename = f"{hospital_name}_业务价值报表_{task.period}{version_suffix}.zip"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        zip_file,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/results/export/hospital-detail")
def export_hospital_detail(
    task_id: str = Query(..., description="计算任务ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出全院明细表（单个Excel文件，包含所有科室数据）"""
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    from urllib.parse import quote
    from collections import defaultdict
    from app.utils.hospital_filter import get_current_hospital_id_or_raise
    from app.models.orientation_rule import OrientationRule
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询所有科室的计算结果（按模型节点排序）
    all_results = db.query(CalculationResult).join(
        ModelNode, CalculationResult.node_id == ModelNode.id
    ).filter(
        CalculationResult.task_id == task_id
    ).order_by(
        CalculationResult.department_id,
        ModelNode.sort_order
    ).all()
    
    if not all_results:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    # 查询模型节点信息
    node_ids = list(set([r.node_id for r in all_results]))
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 查询导向规则名称映射
    orientation_rule_ids = set()
    for node in model_nodes:
        if node.orientation_rule_ids:
            orientation_rule_ids.update(node.orientation_rule_ids)
    
    orientation_rules = {}
    if orientation_rule_ids:
        rules = db.query(OrientationRule).filter(OrientationRule.id.in_(orientation_rule_ids)).all()
        orientation_rules = {rule.id: rule.name for rule in rules}
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 获取所有参与核算的科室
    all_active_depts = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).order_by(Department.sort_order, Department.id).all()
    
    # 按核算单元分组
    accounting_units = {}
    for dept in all_active_depts:
        unit_code = dept.accounting_unit_code or dept.his_code
        unit_name = dept.accounting_unit_name or dept.his_name
        unit_key = (unit_code, unit_name)
        
        if unit_key not in accounting_units:
            accounting_units[unit_key] = {
                'dept_ids': [],
                'sort_order': dept.sort_order
            }
        accounting_units[unit_key]['dept_ids'].append(dept.id)
    
    # 为每个核算单元生成明细数据（复用export_detail的逻辑）
    departments_data = []
    sorted_units = sorted(accounting_units.items(), key=lambda x: x[1]['sort_order'])
    
    for (unit_code, unit_name), unit_data in sorted_units:
        combined_results = []
        for dept_id in unit_data['dept_ids']:
            combined_results.extend(results_by_dept.get(dept_id, []))
        
        if not combined_results:
            continue
        
        # 构建树形结构
        def build_dimension_tree(parent_id, level, results):
            children = []
            for result in results:
                if result.parent_id == parent_id and result.node_type == "dimension":
                    node_info = node_info_map.get(result.node_id)
                    
                    orientation_names = []
                    if node_info and node_info.orientation_rule_ids:
                        orientation_names = [
                            orientation_rules.get(rule_id, f"规则{rule_id}")
                            for rule_id in node_info.orientation_rule_ids
                        ]
                    business_guide = "、".join(orientation_names) if orientation_names else (node_info.business_guide if node_info else None)
                    
                    dim = {
                        'node_id': result.node_id,
                        'parent_id': result.parent_id,
                        'dimension_name': result.node_name,
                        'dimension_code': result.node_code,
                        'level': level,
                        'value': result.value or 0,
                        'ratio': result.ratio or 0,
                        'workload': result.workload,
                        'weight': result.weight,
                        'original_weight': result.original_weight,
                        'business_guide': business_guide,
                        'sort_order': node_info.sort_order if node_info else 999,
                        'children': build_dimension_tree(result.node_id, level + 1, results)
                    }
                    children.append(dim)
            children.sort(key=lambda x: x['sort_order'])
            return children
        
        def build_tree_rows(dimensions):
            rows = []
            
            def calculate_sum_from_children(node):
                if not node.get('children') or len(node['children']) == 0:
                    return node.get('workload') or 0, node.get('value') or 0
                
                total_workload = 0
                total_amount = 0
                for child in node['children']:
                    child_workload, child_amount = calculate_sum_from_children(child)
                    total_workload += child_workload
                    total_amount += child_amount
                
                return total_workload, total_amount
            
            def build_tree_node(node, siblings_total=None):
                is_leaf = not node.get('children') or len(node['children']) == 0
                
                if is_leaf:
                    current_amount = node.get('value') or 0
                    current_workload = node.get('workload') or 0
                else:
                    current_workload, current_amount = calculate_sum_from_children(node)
                
                if siblings_total and siblings_total > 0:
                    ratio = (current_amount / siblings_total * 100)
                    from decimal import Decimal
                    ratio = Decimal(str(ratio)).quantize(Decimal("0.01"))
                else:
                    ratio = node.get('ratio') or 0
                
                if is_leaf:
                    hospital_value = node.get('original_weight') or node.get('weight')
                    tree_node = {
                        "id": node['node_id'],
                        "dimension_name": node['dimension_name'],
                        "workload": current_workload,
                        "hospital_value": str(hospital_value) if hospital_value is not None else "-",
                        "business_guide": node.get('business_guide') or "-",
                        "dept_value": str(node['weight']) if node.get('weight') is not None else "-",
                        "amount": current_amount,
                        "ratio": ratio
                    }
                else:
                    tree_node = {
                        "id": node['node_id'],
                        "dimension_name": node['dimension_name'],
                        "workload": current_workload,
                        "hospital_value": "-",
                        "business_guide": "-",
                        "dept_value": "-",
                        "amount": current_amount,
                        "ratio": ratio,
                        "children": []
                    }
                
                if node.get('children'):
                    children_total = sum(
                        (calculate_sum_from_children(child)[1] if child.get('children') else (child.get('value') or 0))
                        for child in node['children']
                    )
                    
                    for child in node['children']:
                        child_node = build_tree_node(child, children_total)
                        tree_node["children"].append(child_node)
                
                return tree_node
            
            first_level_total = sum(
                (calculate_sum_from_children(dim)[1] if dim.get('children') else (dim.get('value') or 0))
                for dim in dimensions
            )
            
            for dim in dimensions:
                tree_node = build_tree_node(dim, first_level_total)
                rows.append(tree_node)
            
            return rows
        
        doctor_rows = []
        nurse_rows = []
        tech_rows = []
        
        sequences = [r for r in combined_results if r.node_type == "sequence"]
        
        for seq in sequences:
            dimensions = build_dimension_tree(seq.node_id, 1, combined_results)
            rows = build_tree_rows(dimensions)
            
            if "医生" in seq.node_name:
                doctor_rows = rows
            elif "护理" in seq.node_name:
                nurse_rows = rows
            elif "医技" in seq.node_name:
                tech_rows = rows
        
        departments_data.append({
            'dept_name': unit_name,
            'doctor': doctor_rows,
            'nurse': nurse_rows,
            'tech': tech_rows
        })
    
    # 获取医院名称
    from app.models.hospital import Hospital
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    hospital_name = hospital.name if hospital else "未知医院"
    
    # 获取版本号
    version = task.model_version.version if task.model_version else None
    
    # 生成Excel文件
    excel_file = ExportService.export_hospital_detail_to_excel(task.period, departments_data, hospital_name, version)
    
    # 返回文件流
    version_suffix = f"_v{version}" if version else ""
    filename = f"{hospital_name}_全院业务价值明细表_{task.period}{version_suffix}.xlsx"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/results/export/{task_id}/download")
def download_export(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载报表文件"""
    # TODO: 实现文件下载
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/batches", response_model=BatchListResponse)
def get_batch_list(
    model_version_id: Optional[int] = Query(None, description="模型版本ID"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取批次列表
    
    返回所有已完成任务的批次信息，每个批次包含多个任务（当期、环比、同比）
    """
    from sqlalchemy import func, distinct
    
    # 基础查询：只查询有batch_id且已完成的任务
    base_query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    ).filter(
        CalculationTask.batch_id.isnot(None),
        CalculationTask.status == "completed"
    )
    
    # 应用医疗机构过滤
    base_query = apply_hospital_filter(base_query, ModelVersion, required=True)
    
    if model_version_id:
        base_query = base_query.filter(CalculationTask.model_version_id == model_version_id)
    
    # 获取所有符合条件的任务
    all_tasks = base_query.order_by(CalculationTask.created_at.desc()).all()
    
    # 按batch_id分组
    batches_dict = {}
    for task in all_tasks:
        if task.batch_id not in batches_dict:
            batches_dict[task.batch_id] = {
                'batch_id': task.batch_id,
                'tasks': [],
                'periods': set(),
                'created_at': task.created_at,
                'model_version_id': task.model_version_id,
                'model_version_name': task.model_version.name if task.model_version else None
            }
        batches_dict[task.batch_id]['tasks'].append(task)
        batches_dict[task.batch_id]['periods'].add(task.period)
        # 使用最早的创建时间
        if task.created_at < batches_dict[task.batch_id]['created_at']:
            batches_dict[task.batch_id]['created_at'] = task.created_at
    
    # 转换为列表并排序（按创建时间倒序）
    batches_list = sorted(batches_dict.values(), key=lambda x: x['created_at'], reverse=True)
    
    # 分页
    total = len(batches_list)
    start = (page - 1) * size
    end = start + size
    paginated_batches = batches_list[start:end]
    
    # 构建响应
    items = []
    for batch in paginated_batches:
        items.append(BatchInfo(
            batch_id=batch['batch_id'],
            task_count=len(batch['tasks']),
            periods=sorted(list(batch['periods'])),
            created_at=batch['created_at'],
            model_version_id=batch['model_version_id'],
            model_version_name=batch['model_version_name']
        ))
    
    return BatchListResponse(total=total, items=items)


@router.get("/results/export/batch/{batch_id}")
def export_batch_reports(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出批次报表
    
    将批次中每个任务的报表打包到一个ZIP文件中，每个任务一个子目录。
    对于同比/环比，如果缺少对应月份的数据，则汇总表中不计算同比/环比。
    """
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    from urllib.parse import quote
    from collections import defaultdict
    from decimal import Decimal
    from app.utils.hospital_filter import get_current_hospital_id_or_raise
    from app.models.hospital import Hospital
    from app.models.orientation_rule import OrientationRule
    from app.models.reference_value import ReferenceValue
    from io import BytesIO
    import zipfile
    
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取批次中的所有已完成任务
    tasks_query = db.query(CalculationTask).join(
        ModelVersion, CalculationTask.model_version_id == ModelVersion.id
    ).filter(
        CalculationTask.batch_id == batch_id,
        CalculationTask.status == "completed"
    )
    tasks_query = apply_hospital_filter(tasks_query, ModelVersion, required=True)
    tasks = tasks_query.order_by(CalculationTask.period).all()
    
    if not tasks:
        raise HTTPException(status_code=404, detail="批次不存在或没有已完成的任务")
    
    # 获取医院名称
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    hospital_name = hospital.name if hospital else "未知医院"
    
    # 获取版本号
    version = tasks[0].model_version.version if tasks[0].model_version else None
    
    # 按月份组织任务，找出当期、环比、同比
    tasks_by_period = {task.period: task for task in tasks}
    periods = sorted(tasks_by_period.keys())
    
    # 确定当期任务（最新月份）
    current_period = periods[-1] if periods else None
    if not current_period:
        raise HTTPException(status_code=404, detail="批次中没有有效任务")
    
    current_task = tasks_by_period[current_period]
    
    # 计算环比和同比月份
    def get_mom_period(period: str) -> str:
        """获取环比月份（上月）"""
        year, month = map(int, period.split('-'))
        if month == 1:
            return f"{year - 1}-12"
        return f"{year}-{str(month - 1).zfill(2)}"
    
    def get_yoy_period(period: str) -> str:
        """获取同比月份（去年同月）"""
        year, month = map(int, period.split('-'))
        return f"{year - 1}-{str(month).zfill(2)}"
    
    mom_period = get_mom_period(current_period)
    yoy_period = get_yoy_period(current_period)
    
    mom_task = tasks_by_period.get(mom_period)
    yoy_task = tasks_by_period.get(yoy_period)
    
    # 创建主ZIP文件
    main_zip_buffer = BytesIO()
    
    with zipfile.ZipFile(main_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as main_zip:
        # 为每个任务生成报表
        for task in tasks:
            task_period = task.period
            
            # 确定该任务的环比和同比任务
            task_mom_period = get_mom_period(task_period)
            task_yoy_period = get_yoy_period(task_period)
            task_mom_task = tasks_by_period.get(task_mom_period)
            task_yoy_task = tasks_by_period.get(task_yoy_period)
            
            # 生成该任务的报表数据
            task_reports = _generate_task_reports(
                db, task, hospital_id, hospital_name, version,
                task_mom_task, task_yoy_task
            )
            
            # 将报表添加到ZIP中，使用月份作为子目录
            folder_name = f"{task_period}"
            
            for filename, file_content in task_reports.items():
                main_zip.writestr(f"{folder_name}/{filename}", file_content)
    
    main_zip_buffer.seek(0)
    
    # 返回文件流
    version_suffix = f"_{version}" if version else ""
    filename = f"{hospital_name}_批次报表_{batch_id[-8:]}{version_suffix}.zip"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        main_zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


def _generate_task_reports(
    db: Session,
    task: CalculationTask,
    hospital_id: int,
    hospital_name: str,
    version: str,
    mom_task: Optional[CalculationTask],
    yoy_task: Optional[CalculationTask]
) -> dict:
    """生成单个任务的所有报表
    
    返回字典：{文件名: 文件内容(bytes)}
    """
    from app.services.export_service import ExportService
    from collections import defaultdict
    from decimal import Decimal
    from app.models.reference_value import ReferenceValue
    from app.models.orientation_rule import OrientationRule
    
    reports = {}
    version_suffix = ExportService._format_version(version)
    
    # 获取所有参与核算的科室
    all_active_depts = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).order_by(Department.sort_order, Department.id).all()
    
    dept_map = {d.id: d for d in all_active_depts}
    
    # 查询当期计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id
    ).all()
    
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 查询模型节点信息
    node_ids = list(set([r.node_id for r in all_results]))
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all() if node_ids else []
    node_info_map = {node.id: node for node in model_nodes}
    
    # 查询导向规则名称映射
    orientation_rule_ids = set()
    for node in model_nodes:
        if node.orientation_rule_ids:
            orientation_rule_ids.update(node.orientation_rule_ids)
    
    orientation_rules = {}
    if orientation_rule_ids:
        rules = db.query(OrientationRule).filter(OrientationRule.id.in_(orientation_rule_ids)).all()
        orientation_rules = {rule.id: rule.name for rule in rules}
    
    # 查询参考价值
    ref_values = db.query(ReferenceValue).filter(
        ReferenceValue.hospital_id == hospital_id,
        ReferenceValue.period == task.period
    ).all()
    ref_value_map = {rv.department_code: rv.reference_value for rv in ref_values}
    
    # 查询环比数据
    mom_summary = {}
    if mom_task:
        mom_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == mom_task.task_id
        ).all()
        mom_by_dept = defaultdict(list)
        for r in mom_results:
            mom_by_dept[r.department_id].append(r)
        
        for dept in all_active_depts:
            unit_code = dept.accounting_unit_code or dept.his_code
            dept_results = mom_by_dept.get(dept.id, [])
            total_value = _calculate_dept_total_value(dept_results)
            if unit_code not in mom_summary:
                mom_summary[unit_code] = Decimal('0')
            mom_summary[unit_code] += total_value
    
    # 查询同比数据
    yoy_summary = {}
    if yoy_task:
        yoy_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == yoy_task.task_id
        ).all()
        yoy_by_dept = defaultdict(list)
        for r in yoy_results:
            yoy_by_dept[r.department_id].append(r)
        
        for dept in all_active_depts:
            unit_code = dept.accounting_unit_code or dept.his_code
            dept_results = yoy_by_dept.get(dept.id, [])
            total_value = _calculate_dept_total_value(dept_results)
            if unit_code not in yoy_summary:
                yoy_summary[unit_code] = Decimal('0')
            yoy_summary[unit_code] += total_value
    
    # 按核算单元分组
    accounting_units = {}
    for dept in all_active_depts:
        unit_code = dept.accounting_unit_code or dept.his_code
        unit_name = dept.accounting_unit_name or dept.his_name
        unit_key = (unit_code, unit_name)
        
        if unit_key not in accounting_units:
            accounting_units[unit_key] = {
                'dept_ids': [],
                'sort_order': dept.sort_order
            }
        accounting_units[unit_key]['dept_ids'].append(dept.id)
    
    sorted_units = sorted(accounting_units.items(), key=lambda x: x[1]['sort_order'])
    
    # 计算汇总数据
    summary_by_unit = {}
    for (unit_code, unit_name), unit_data in sorted_units:
        combined_results = []
        for dept_id in unit_data['dept_ids']:
            combined_results.extend(results_by_dept.get(dept_id, []))
        
        doctor_value, nurse_value, tech_value = _calculate_sequence_values(combined_results)
        total_val = doctor_value + nurse_value + tech_value
        
        # 参考价值
        ref_value = ref_value_map.get(unit_code)
        actual_ref_ratio = None
        if ref_value is not None and ref_value != 0:
            actual_ref_ratio = float(total_val / ref_value)
        
        # 环比
        mom_value = mom_summary.get(unit_code)
        mom_ratio = None
        if mom_value is not None and mom_value != 0:
            mom_ratio = float(total_val / mom_value)
        
        # 同比
        yoy_value = yoy_summary.get(unit_code)
        yoy_ratio = None
        if yoy_value is not None and yoy_value != 0:
            yoy_ratio = float(total_val / yoy_value)
        
        summary_by_unit[(unit_code, unit_name)] = {
            'doctor_value': doctor_value,
            'nurse_value': nurse_value,
            'tech_value': tech_value,
            'total_value': total_val,
            'doctor_ratio': float(doctor_value / total_val * 100) if total_val > 0 else 0,
            'nurse_ratio': float(nurse_value / total_val * 100) if total_val > 0 else 0,
            'tech_ratio': float(tech_value / total_val * 100) if total_val > 0 else 0,
            'reference_value': float(ref_value) if ref_value is not None else None,
            'actual_reference_ratio': actual_ref_ratio,
            'mom_value': float(mom_value) if mom_value is not None else None,
            'mom_ratio': mom_ratio,
            'yoy_value': float(yoy_value) if yoy_value is not None else None,
            'yoy_ratio': yoy_ratio
        }
    
    # 构建汇总表数据
    total_doctor = sum(v['doctor_value'] for v in summary_by_unit.values())
    total_nurse = sum(v['nurse_value'] for v in summary_by_unit.values())
    total_tech = sum(v['tech_value'] for v in summary_by_unit.values())
    total_all = total_doctor + total_nurse + total_tech
    
    # 计算全院汇总的参考值、环比、同比
    total_reference_value = Decimal('0')
    total_mom_value = Decimal('0')
    total_yoy_value = Decimal('0')
    has_reference = False
    has_mom = bool(mom_task)
    has_yoy = bool(yoy_task)
    
    for v in summary_by_unit.values():
        if v['reference_value'] is not None:
            has_reference = True
            total_reference_value += Decimal(str(v['reference_value']))
        if v['mom_value'] is not None:
            total_mom_value += Decimal(str(v['mom_value']))
        if v['yoy_value'] is not None:
            total_yoy_value += Decimal(str(v['yoy_value']))
    
    summary_actual_ref_ratio = None
    if has_reference and total_reference_value != 0:
        summary_actual_ref_ratio = float(total_all / total_reference_value)
    
    summary_mom_ratio = None
    if has_mom and total_mom_value != 0:
        summary_mom_ratio = float(total_all / total_mom_value)
    
    summary_yoy_ratio = None
    if has_yoy and total_yoy_value != 0:
        summary_yoy_ratio = float(total_all / total_yoy_value)
    
    summary_data = {
        'summary': {
            'department_id': 0,
            'department_code': None,
            'department_name': '全院汇总',
            'doctor_value': total_doctor,
            'doctor_ratio': float(total_doctor / total_all * 100) if total_all > 0 else 0,
            'nurse_value': total_nurse,
            'nurse_ratio': float(total_nurse / total_all * 100) if total_all > 0 else 0,
            'tech_value': total_tech,
            'tech_ratio': float(total_tech / total_all * 100) if total_all > 0 else 0,
            'total_value': total_all,
            'reference_value': float(total_reference_value) if has_reference else None,
            'actual_reference_ratio': summary_actual_ref_ratio,
            'mom_value': float(total_mom_value) if has_mom else None,
            'mom_ratio': summary_mom_ratio,
            'yoy_value': float(total_yoy_value) if has_yoy else None,
            'yoy_ratio': summary_yoy_ratio
        },
        'departments': [
            {
                'department_id': accounting_units[(unit_code, unit_name)]['dept_ids'][0] if accounting_units[(unit_code, unit_name)]['dept_ids'] else 0,
                'department_code': unit_code,
                'department_name': unit_name,
                **summary_by_unit[(unit_code, unit_name)]
            }
            for (unit_code, unit_name), _ in sorted_units
            if (unit_code, unit_name) in summary_by_unit
        ]
    }
    
    # 生成汇总表Excel
    summary_excel = ExportService.export_summary_to_excel(summary_data, task.period, hospital_name, version)
    summary_filename = f"{hospital_name}_科室业务价值汇总_{task.period}{version_suffix}.xlsx"
    reports[summary_filename] = summary_excel.getvalue()
    
    # 生成全院明细表
    hospital_detail_data = _build_hospital_detail_data(all_results, node_info_map, orientation_rules)
    if hospital_detail_data:
        hospital_excel = ExportService.export_hospital_detail_to_excel(task.period, hospital_detail_data, hospital_name, version)
        hospital_filename = f"{hospital_name}_全院业务价值明细_{task.period}{version_suffix}.xlsx"
        reports[hospital_filename] = hospital_excel.getvalue()
    
    # 生成各科室明细表
    for (unit_code, unit_name), unit_data in sorted_units:
        combined_results = []
        for dept_id in unit_data['dept_ids']:
            combined_results.extend(results_by_dept.get(dept_id, []))
        
        if not combined_results:
            continue
        
        detail_data = _build_dept_detail_data(combined_results, node_info_map, orientation_rules)
        
        detail_excel = ExportService.export_detail_to_excel(unit_name, task.period, detail_data, hospital_name, version)
        detail_filename = f"{hospital_name}_{unit_name}_业务价值明细_{task.period}{version_suffix}.xlsx"
        reports[detail_filename] = detail_excel.getvalue()
    
    return reports


def _calculate_dept_total_value(results: list) -> Decimal:
    """计算科室总价值"""
    from decimal import Decimal
    
    def calculate_sum_from_children(node_id, results):
        current_node = next((r for r in results if r.node_id == node_id), None)
        if not current_node:
            return Decimal('0')
        
        children = [r for r in results if r.parent_id == node_id and r.node_type == "dimension"]
        
        if not children:
            return current_node.value or Decimal('0')
        
        total_value = Decimal('0')
        for child in children:
            child_value = calculate_sum_from_children(child.node_id, results)
            total_value += child_value
        
        return total_value
    
    sequences = [r for r in results if r.node_type == "sequence"]
    total = Decimal('0')
    for seq in sequences:
        total += calculate_sum_from_children(seq.node_id, results)
    
    return total


def _calculate_sequence_values(results: list) -> tuple:
    """计算各序列价值，返回(doctor, nurse, tech)"""
    from decimal import Decimal
    
    def calculate_sum_from_children(node_id, results):
        current_node = next((r for r in results if r.node_id == node_id), None)
        if not current_node:
            return Decimal('0')
        
        children = [r for r in results if r.parent_id == node_id and r.node_type == "dimension"]
        
        if not children:
            return current_node.value or Decimal('0')
        
        total_value = Decimal('0')
        for child in children:
            child_value = calculate_sum_from_children(child.node_id, results)
            total_value += child_value
        
        return total_value
    
    sequences = [r for r in results if r.node_type == "sequence"]
    doctor_value = Decimal('0')
    nurse_value = Decimal('0')
    tech_value = Decimal('0')
    
    for seq in sequences:
        seq_value = calculate_sum_from_children(seq.node_id, results)
        node_name_lower = seq.node_name.lower()
        
        if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
           "doctor" in node_name_lower or "physician" in node_name_lower:
            doctor_value += seq_value
        elif "护理" in seq.node_name or "护士" in seq.node_name or \
             "nurse" in node_name_lower or "nursing" in node_name_lower:
            nurse_value += seq_value
        elif "医技" in seq.node_name or "技师" in seq.node_name or \
             "tech" in node_name_lower or "technician" in node_name_lower:
            tech_value += seq_value
    
    return doctor_value, nurse_value, tech_value


def _build_hospital_detail_data(results: list, node_info_map: dict, orientation_rules: dict) -> dict:
    """构建全院明细数据"""
    from collections import defaultdict
    from decimal import Decimal
    
    # 按节点ID汇总所有科室的数据
    node_aggregated = defaultdict(lambda: {
        'node_id': 0,
        'node_name': '',
        'node_code': '',
        'node_type': '',
        'parent_id': None,
        'workload': Decimal('0'),
        'value': Decimal('0'),
        'weight': None,
        'business_guide': None,
        'sort_order': 999
    })
    
    for result in results:
        node_id = result.node_id
        agg = node_aggregated[node_id]
        
        if agg['node_id'] == 0:
            agg['node_id'] = result.node_id
            agg['node_name'] = result.node_name
            agg['node_code'] = result.node_code
            agg['node_type'] = result.node_type
            agg['parent_id'] = result.parent_id
            agg['weight'] = result.weight
            node_info = node_info_map.get(result.node_id)
            if node_info:
                agg['business_guide'] = node_info.business_guide
                agg['sort_order'] = node_info.sort_order
        
        if result.workload:
            agg['workload'] += result.workload
        if result.value:
            agg['value'] += result.value
    
    # 构建树形结构
    def build_dimension_tree(parent_id, level):
        children = []
        for node_id, agg in node_aggregated.items():
            if agg['parent_id'] == parent_id and agg['node_type'] == "dimension":
                node_info = node_info_map.get(agg['node_id'])
                
                orientation_names = []
                if node_info and node_info.orientation_rule_ids:
                    orientation_names = [
                        orientation_rules.get(rule_id, f"规则{rule_id}")
                        for rule_id in node_info.orientation_rule_ids
                    ]
                business_guide = "、".join(orientation_names) if orientation_names else agg.get('business_guide')
                
                dim = {
                    'node_id': agg['node_id'],
                    'dimension_name': agg['node_name'],
                    'workload': agg['workload'],
                    'hospital_value': str(agg['weight']) if agg['weight'] is not None else "-",
                    'business_guide': business_guide or "-",
                    'amount': agg['value'],
                    'ratio': 0,
                    'sort_order': agg['sort_order'],
                    'children': build_dimension_tree(agg['node_id'], level + 1)
                }
                children.append(dim)
        
        children.sort(key=lambda x: x['sort_order'])
        return children
    
    # 按序列组织数据
    hospital_detail_data = {}
    for node_id, agg in node_aggregated.items():
        if agg['node_type'] == "sequence":
            dimensions = build_dimension_tree(agg['node_id'], 1)
            
            if "医生" in agg['node_name']:
                hospital_detail_data['doctor'] = dimensions
            elif "护理" in agg['node_name']:
                hospital_detail_data['nurse'] = dimensions
            elif "医技" in agg['node_name']:
                hospital_detail_data['tech'] = dimensions
    
    return hospital_detail_data


def _build_dept_detail_data(results: list, node_info_map: dict, orientation_rules: dict) -> dict:
    """构建科室明细数据"""
    
    def build_dimension_tree(parent_id, level):
        children = []
        for result in results:
            if result.parent_id == parent_id and result.node_type == "dimension":
                node_info = node_info_map.get(result.node_id)
                
                orientation_names = []
                if node_info and node_info.orientation_rule_ids:
                    orientation_names = [
                        orientation_rules.get(rule_id, f"规则{rule_id}")
                        for rule_id in node_info.orientation_rule_ids
                    ]
                business_guide = "、".join(orientation_names) if orientation_names else (node_info.business_guide if node_info else None)
                
                dim = {
                    'node_id': result.node_id,
                    'dimension_name': result.node_name,
                    'workload': result.workload,
                    'hospital_value': str(result.original_weight or result.weight) if (result.original_weight or result.weight) is not None else "-",
                    'business_guide': business_guide or "-",
                    'dept_value': str(result.weight) if result.weight is not None else "-",
                    'amount': result.value or 0,
                    'ratio': result.ratio or 0,
                    'sort_order': node_info.sort_order if node_info else 999,
                    'children': build_dimension_tree(result.node_id, level + 1)
                }
                children.append(dim)
        
        children.sort(key=lambda x: x['sort_order'])
        return children
    
    detail_data = {}
    sequences = [r for r in results if r.node_type == "sequence"]
    
    for seq in sequences:
        dimensions = build_dimension_tree(seq.node_id, 1)
        
        if "医生" in seq.node_name:
            detail_data['doctor'] = dimensions
        elif "护理" in seq.node_name:
            detail_data['nurse'] = dimensions
        elif "医技" in seq.node_name:
            detail_data['tech'] = dimensions
    
    return detail_data
