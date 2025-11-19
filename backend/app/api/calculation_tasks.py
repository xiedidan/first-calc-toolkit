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
    
    task = query.order_by(CalculationTask.completed_at.desc()).first()
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
    """获取科室汇总数据 - 使用明细表相同的逐级汇总算法"""
    from decimal import Decimal
    from collections import defaultdict
    
    # 查找最新的完成任务（使用辅助函数）
    task = _get_latest_completed_task(db, period, model_version_id)
    
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
    
    # 获取科室信息
    dept_ids = list(results_by_dept.keys())
    departments = db.query(Department).filter(Department.id.in_(dept_ids)).all()
    dept_map = {d.id: d for d in departments}
    
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
    
    # 计算每个科室的汇总数据
    departments_data = []
    total_doctor_value = Decimal('0')
    total_nurse_value = Decimal('0')
    total_tech_value = Decimal('0')
    
    for dept_id_val, results in sorted(results_by_dept.items()):
        dept = dept_map.get(dept_id_val)
        if not dept:
            continue
        
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
        
        # 计算科室总价值和占比
        total_val = doctor_value + nurse_value + tech_value
        
        if total_val > 0:
            doctor_ratio = float(doctor_value / total_val * 100)
            nurse_ratio = float(nurse_value / total_val * 100)
            tech_ratio = float(tech_value / total_val * 100)
        else:
            doctor_ratio = 0
            nurse_ratio = 0
            tech_ratio = 0
        
        departments_data.append(CalculationSummaryResponse(
            department_id=dept_id_val,
            department_name=dept.his_name,
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
                tree_node = {
                    "id": node.node_id,
                    "dimension_name": node.dimension_name,
                    "workload": current_workload,
                    "hospital_value": str(node.weight) if node.weight is not None else "-",
                    "business_guide": node.business_guide or "-",
                    "dept_value": str(node.weight) if node.weight is not None else "-",
                    "amount": current_amount,
                    "ratio": ratio
                }
            else:
                # 非末级维度：部分信息用"-"，包含children数组
                tree_node = {
                    "id": node.node_id,
                    "dimension_name": node.dimension_name,
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
        "department_id": dept_id,
        "department_name": department.his_name,
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
    
    # 查询所有科室的所有计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id
    ).order_by(CalculationResult.department_id, CalculationResult.node_id).all()
    
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
                    "dimension_name": node.dimension_name,
                    "workload": current_workload,
                    "hospital_value": str(node.weight) if node.weight is not None else "-",
                    "business_guide": node.business_guide or "-",
                    "dept_value": str(node.weight) if node.weight is not None else "-",
                    "amount": current_amount,
                    "ratio": ratio
                }
            else:
                # 非末级维度：部分信息用"-"，包含children数组
                tree_node = {
                    "id": node.node_id,
                    "dimension_name": node.dimension_name,
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
    period: str = Query(..., description="评估月份(YYYY-MM)"),
    model_version_id: Optional[int] = Query(None, description="模型版本ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出汇总表（同步）"""
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    
    # 获取汇总数据（复用现有逻辑）
    from decimal import Decimal
    from collections import defaultdict
    
    # 查找最新的完成任务（使用辅助函数）
    task = _get_latest_completed_task(db, period, model_version_id)
    
    # 查询所有计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id
    ).all()
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 获取科室信息
    dept_ids = list(results_by_dept.keys())
    departments = db.query(Department).filter(Department.id.in_(dept_ids)).all()
    dept_map = {d.id: d for d in departments}
    
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
    
    # 计算每个科室的汇总数据
    departments_data = []
    total_doctor_value = Decimal('0')
    total_nurse_value = Decimal('0')
    total_tech_value = Decimal('0')
    
    for dept_id_val, results in sorted(results_by_dept.items()):
        dept = dept_map.get(dept_id_val)
        if not dept:
            continue
        
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
        
        total_val = doctor_value + nurse_value + tech_value
        
        if total_val > 0:
            doctor_ratio = float(doctor_value / total_val * 100)
            nurse_ratio = float(nurse_value / total_val * 100)
            tech_ratio = float(tech_value / total_val * 100)
        else:
            doctor_ratio = 0
            nurse_ratio = 0
            tech_ratio = 0
        
        departments_data.append({
            'department_id': dept_id_val,
            'department_name': dept.his_name,
            'doctor_value': doctor_value,
            'doctor_ratio': doctor_ratio,
            'nurse_value': nurse_value,
            'nurse_ratio': nurse_ratio,
            'tech_value': tech_value,
            'tech_ratio': tech_ratio,
            'total_value': total_val
        })
        
        total_doctor_value += doctor_value
        total_nurse_value += nurse_value
        total_tech_value += tech_value
    
    # 计算全院汇总
    total_value = total_doctor_value + total_nurse_value + total_tech_value
    
    summary_data = {
        'department_id': 0,
        'department_name': '全院汇总',
        'doctor_value': total_doctor_value,
        'doctor_ratio': float(total_doctor_value / total_value * 100) if total_value > 0 else 0,
        'nurse_value': total_nurse_value,
        'nurse_ratio': float(total_nurse_value / total_value * 100) if total_value > 0 else 0,
        'tech_value': total_tech_value,
        'tech_ratio': float(total_tech_value / total_value * 100) if total_value > 0 else 0,
        'total_value': total_value
    }
    
    # 生成Excel
    excel_data = {
        'summary': summary_data,
        'departments': departments_data
    }
    
    excel_file = ExportService.export_summary_to_excel(excel_data, period)
    
    # 返回文件流
    from urllib.parse import quote
    filename = f"科室业务价值汇总_{period}.xlsx"
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出明细表（同步，ZIP打包）"""
    from fastapi.responses import StreamingResponse
    from app.services.export_service import ExportService
    from urllib.parse import quote
    from collections import defaultdict
    
    # 验证任务是否存在且属于当前医疗机构
    task = _get_task_with_hospital_check(db, task_id)
    
    # 查询所有科室的计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id
    ).order_by(CalculationResult.department_id, CalculationResult.node_id).all()
    
    if not all_results:
        raise HTTPException(status_code=404, detail="未找到计算结果")
    
    # 查询模型节点信息
    node_ids = list(set([r.node_id for r in all_results]))
    model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
    node_info_map = {node.id: node for node in model_nodes}
    
    # 按科室分组
    results_by_dept = defaultdict(list)
    for result in all_results:
        results_by_dept[result.department_id].append(result)
    
    # 获取科室信息
    dept_ids = list(results_by_dept.keys())
    departments = db.query(Department).filter(Department.id.in_(dept_ids)).all()
    dept_map = {d.id: d for d in departments}
    
    # 为每个科室生成明细数据
    departments_data = []
    
    for dept_id, results in sorted(results_by_dept.items()):
        dept = dept_map.get(dept_id)
        if not dept:
            continue
        
        # 构建树形结构（复用现有逻辑）
        def build_dimension_tree(parent_id, level):
            """递归构建维度树"""
            children = []
            for result in results:
                if result.parent_id == parent_id and result.node_type == "dimension":
                    node_info = node_info_map.get(result.node_id)
                    
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
                        'business_guide': node_info.business_guide if node_info else None,
                        'children': build_dimension_tree(result.node_id, level + 1)
                    }
                    children.append(dim)
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
                    tree_node = {
                        "id": node['node_id'],
                        "dimension_name": node['dimension_name'],
                        "workload": current_workload,
                        "hospital_value": str(node['weight']) if node.get('weight') is not None else "-",
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
        
        sequences = [r for r in results if r.node_type == "sequence"]
        
        for seq in sequences:
            dimensions = build_dimension_tree(seq.node_id, 1)
            rows = build_tree_rows(dimensions)
            
            if "医生" in seq.node_name:
                doctor_rows = rows
            elif "护理" in seq.node_name:
                nurse_rows = rows
            elif "医技" in seq.node_name:
                tech_rows = rows
        
        departments_data.append({
            'dept_name': dept.his_name,
            'doctor': doctor_rows,
            'nurse': nurse_rows,
            'tech': tech_rows
        })
    
    # 生成ZIP文件
    zip_file = ExportService.export_all_details_to_zip(task.period, departments_data)
    
    # 返回文件流
    filename = f"业务价值明细表_{task.period}.zip"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        zip_file,
        media_type="application/zip",
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
