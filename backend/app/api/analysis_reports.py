"""
科室运营分析报告API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import IntegrityError

from app.api import deps
from app.models.analysis_report import AnalysisReport
from app.models.department import Department
from app.models.user import User
from app.models.role import RoleType
from app.schemas.analysis_report import (
    AnalysisReport as AnalysisReportSchema,
    AnalysisReportCreate,
    AnalysisReportUpdate,
    AnalysisReportList,
    ValueDistributionItem,
    ValueDistributionResponse,
    BusinessContentItem,
    BusinessContentResponse,
    DimensionBusinessContent,
    DimensionDrillDownItem,
    DimensionDrillDownResponse,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)

router = APIRouter()


def get_business_type_from_dimension_code(dimension_code: str) -> Optional[str]:
    """
    根据维度编码判断业务类型（门诊/住院）
    
    维度编码规则：
    - dim-doc-in-* : 住院非手术（诊断、评估等）
    - dim-doc-out-* : 门诊非手术
    - dim-doc-sur-in-* : 住院手术
    - dim-doc-sur-out-* : 门诊手术
    - dim-tech-* : 医技（不区分门诊住院）
    - dim-nur-* : 护理（不区分门诊住院）
    
    返回: "门诊", "住院", 或 None（不区分）
    """
    if not dimension_code:
        return None
    
    # 医生序列 - 需要区分门诊/住院
    if dimension_code.startswith('dim-doc-'):
        # 手术维度: dim-doc-sur-in-* 或 dim-doc-sur-out-*
        if dimension_code.startswith('dim-doc-sur-in-'):
            return "住院"
        elif dimension_code.startswith('dim-doc-sur-out-'):
            return "门诊"
        # 非手术维度: dim-doc-in-* 或 dim-doc-out-*
        elif dimension_code.startswith('dim-doc-in-'):
            return "住院"
        elif dimension_code.startswith('dim-doc-out-'):
            return "门诊"
    
    # 医技和护理序列 - 不区分门诊住院
    return None


def is_department_user(user: User) -> bool:
    """判断用户是否为科室用户"""
    if not user.roles:
        return False
    for role in user.roles:
        if role.role_type == RoleType.DEPARTMENT_USER:
            return True
    return False


def is_admin_or_higher(user: User) -> bool:
    """判断用户是否为管理员或更高权限"""
    if not user.roles:
        return False
    for role in user.roles:
        if role.role_type in [RoleType.ADMIN, RoleType.MAINTAINER, RoleType.HOSPITAL_USER]:
            return True
    return False


def get_user_department_id(user: User) -> Optional[int]:
    """获取用户所属科室ID"""
    return user.department_id


def check_report_access(user: User, report: AnalysisReport) -> None:
    """检查用户是否有权限访问报告"""
    # 管理员或更高权限可以访问所有报告
    if is_admin_or_higher(user):
        return
    
    # 科室用户只能访问自己科室的报告
    if is_department_user(user):
        user_dept_id = get_user_department_id(user)
        if user_dept_id is None or report.department_id != user_dept_id:
            raise HTTPException(
                status_code=403,
                detail="无权访问该科室的分析报告"
            )
        return
    
    # 其他情况拒绝访问
    raise HTTPException(
        status_code=403,
        detail="无权访问该分析报告"
    )


def apply_department_filter(query, user: User):
    """根据用户角色应用科室过滤"""
    # 科室用户只能看自己科室的报告
    if is_department_user(user):
        user_dept_id = get_user_department_id(user)
        if user_dept_id is not None:
            query = query.filter(AnalysisReport.department_id == user_dept_id)
        else:
            # 科室用户没有绑定科室，返回空结果
            query = query.filter(AnalysisReport.id == -1)
    
    return query


def get_task_by_id_or_latest(
    db: Session,
    hospital_id: int,
    period: str,
    task_id: Optional[str] = None
):
    """
    根据 task_id 获取任务，或获取最新完成的任务
    
    Args:
        db: 数据库会话
        hospital_id: 医疗机构ID
        period: 年月
        task_id: 可选的任务ID
        
    Returns:
        CalculationTask 或 None
    """
    from app.models.calculation_task import CalculationTask
    from app.models.model_version import ModelVersion
    
    if task_id:
        # 通过 task_id 直接查询
        task = db.query(CalculationTask).filter(
            CalculationTask.task_id == task_id,
            CalculationTask.status == "completed"
        ).first()
        return task
    
    # 查找激活版本的最新完成任务
    active_version = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    ).first()
    
    if not active_version:
        return None
    
    task = db.query(CalculationTask).filter(
        CalculationTask.model_version_id == active_version.id,
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    ).order_by(desc(CalculationTask.completed_at)).first()
    
    return task


@router.get("/available-tasks")
def get_available_tasks(
    period: Optional[str] = Query(None, description="年月筛选 (YYYY-MM)"),
    status: Optional[str] = Query("completed", description="任务状态筛选"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取可用的计算任务列表（用于报告创建时选择）
    
    - 返回当前医疗机构的已完成计算任务
    - 按完成时间倒序排列
    """
    from app.models.calculation_task import CalculationTask
    from app.models.calculation_workflow import CalculationWorkflow
    from app.models.model_version import ModelVersion
    
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询该医疗机构的所有版本
    version_ids = db.query(ModelVersion.id).filter(
        ModelVersion.hospital_id == hospital_id
    ).all()
    version_ids = [v[0] for v in version_ids]
    
    if not version_ids:
        return []
    
    # 查询任务
    query = db.query(CalculationTask).filter(
        CalculationTask.model_version_id.in_(version_ids)
    )
    
    if status:
        query = query.filter(CalculationTask.status == status)
    
    if period:
        query = query.filter(CalculationTask.period == period)
    
    # 按完成时间倒序
    query = query.order_by(desc(CalculationTask.completed_at))
    
    tasks = query.limit(100).all()
    
    # 预加载工作流名称
    result = []
    for task in tasks:
        workflow_name = None
        if task.workflow_id:
            workflow = db.query(CalculationWorkflow).filter(
                CalculationWorkflow.id == task.workflow_id
            ).first()
            if workflow:
                workflow_name = workflow.name
        
        result.append({
            "task_id": task.task_id,
            "period": task.period,
            "workflow_id": task.workflow_id,
            "workflow_name": workflow_name or "默认流程",
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        })
    
    return result


@router.get("", response_model=AnalysisReportList)
def get_analysis_reports(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    period: Optional[str] = Query(None, description="年月筛选 (YYYY-MM)"),
    department_code: Optional[str] = Query(None, description="科室代码搜索"),
    department_name: Optional[str] = Query(None, description="科室名称搜索"),
    task_id: Optional[str] = Query(None, description="计算任务ID筛选"),
    sort_by: Optional[str] = Query("period", description="排序字段: period, department_code, department_name"),
    sort_order: Optional[str] = Query("desc", description="排序方向: asc, desc"),
):
    """
    获取分析报告列表
    
    - 科室用户只能查看自己科室的报告
    - 管理员可以查看所有报告
    - 支持按年月、科室代码、科室名称、计算任务筛选和排序
    """
    query = db.query(AnalysisReport).join(
        Department, AnalysisReport.department_id == Department.id
    )
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    
    # 应用科室用户过滤
    query = apply_department_filter(query, current_user)
    
    # 年月筛选
    if period:
        query = query.filter(AnalysisReport.period == period)
    
    # 计算任务筛选
    if task_id:
        query = query.filter(AnalysisReport.task_id == task_id)
    
    # 科室代码搜索
    if department_code:
        query = query.filter(Department.his_code.contains(department_code))
    
    # 科室名称搜索
    if department_name:
        query = query.filter(Department.his_name.contains(department_name))
    
    # 排序
    if sort_by == "period":
        sort_column = AnalysisReport.period
    elif sort_by == "department_code":
        sort_column = Department.his_code
    elif sort_by == "department_name":
        sort_column = Department.his_name
    else:
        sort_column = AnalysisReport.period
    
    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 转换为响应格式，添加科室信息和工作流名称
    from app.models.calculation_task import CalculationTask
    from app.models.calculation_workflow import CalculationWorkflow
    
    result_items = []
    for report in items:
        dept = report.department
        
        # 获取工作流名称
        workflow_name = None
        if report.task_id:
            task = db.query(CalculationTask).filter(
                CalculationTask.task_id == report.task_id
            ).first()
            if task and task.workflow_id:
                workflow = db.query(CalculationWorkflow).filter(
                    CalculationWorkflow.id == task.workflow_id
                ).first()
                if workflow:
                    workflow_name = workflow.name
        
        report_dict = {
            "id": report.id,
            "hospital_id": report.hospital_id,
            "department_id": report.department_id,
            "department_code": dept.accounting_unit_code if dept else "",
            "department_name": (dept.accounting_unit_name or dept.his_name) if dept else "",
            "period": report.period,
            "task_id": report.task_id,
            "workflow_name": workflow_name,
            "current_issues": report.current_issues,
            "future_plans": report.future_plans,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
            "created_by": report.created_by,
        }
        result_items.append(AnalysisReportSchema(**report_dict))
    
    return AnalysisReportList(total=total, items=result_items)


@router.get("/dimension-drilldown", response_model=DimensionDrillDownResponse)
def get_dimension_drilldown_by_task(
    task_id: str = Query(..., description="任务ID"),
    department_id: int = Query(..., description="科室ID（0表示全院汇总）"),
    node_id: int = Query(..., description="节点ID"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取维度下钻明细（通过任务ID）
    
    - 用于计算结果页面的下钻功能
    - 查询该维度对应的收费项目明细
    - 仅支持医生序列中按维度目录计算的末级维度（除病例价值维度外）
    - department_id=0 表示全院汇总，将查询所有科室的数据
    """
    from decimal import Decimal
    from sqlalchemy import text
    from app.models.calculation_task import CalculationTask, CalculationResult
    from app.models.dimension_item_mapping import DimensionItemMapping
    from app.models.charge_item import ChargeItem
    from app.models.department import Department
    
    # 获取任务信息
    task = db.query(CalculationTask).filter(
        CalculationTask.task_id == task_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    hospital_id = get_current_hospital_id_or_raise()
    period = task.period
    
    # 判断是否为全院汇总
    is_hospital_summary = (department_id == 0)
    
    # 查询该维度节点信息
    # 对于全院汇总(department_id=0)，从任意一个科室获取维度信息（维度结构相同）
    if is_hospital_summary:
        dimension_result = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.node_id == node_id,
            CalculationResult.node_type == "dimension"
        ).first()
    else:
        dimension_result = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == department_id,
            CalculationResult.node_id == node_id,
            CalculationResult.node_type == "dimension"
        ).first()
    
    if not dimension_result:
        raise HTTPException(status_code=404, detail="未找到该维度的计算结果")
    
    dimension_name = dimension_result.node_name
    dimension_code = dimension_result.node_code
    
    if not dimension_code:
        raise HTTPException(status_code=400, detail="该维度缺少编码信息，无法下钻")
    
    # 检查是否为指标维度（成本等），指标维度不支持下钻
    if '-cost' in dimension_code:
        raise HTTPException(status_code=400, detail="指标维度（成本等）不支持下钻")
    
    # 检查是否为支持下钻的维度（医生、医技、护理序列中用charge_details计算的维度）
    is_doctor_dim = dimension_code.startswith('dim-doc-') and dimension_code != 'dim-doc-case'
    is_tech_dim = dimension_code.startswith('dim-tech-')
    # 护理序列中用charge_details计算的维度（排除用workload_statistics计算的床日、出入转院等维度）
    nurse_workload_prefixes = ['dim-nur-bed', 'dim-nur-trans', 'dim-nur-op', 'dim-nur-or', 'dim-nur-mon']
    nurse_charge_prefixes = ['dim-nur-base', 'dim-nur-collab', 'dim-nur-tr-', 'dim-nur-other']
    is_nurse_workload_dim = any(dimension_code.startswith(p) for p in nurse_workload_prefixes)
    is_nurse_charge_dim = (
        dimension_code.startswith('dim-nur-') and 
        not is_nurse_workload_dim and
        any(dimension_code.startswith(p) for p in nurse_charge_prefixes)
    )
    
    if not is_doctor_dim and not is_tech_dim and not is_nurse_charge_dim:
        raise HTTPException(
            status_code=400, 
            detail="仅支持医生、医技、护理序列中按维度目录计算的末级维度下钻（不包括病例价值维度和工作量统计维度）"
        )
    
    # 检查是否为叶子节点（对于全院汇总，从任意科室检查）
    if is_hospital_summary:
        has_children = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.parent_id == node_id
        ).first()
    else:
        has_children = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == department_id,
            CalculationResult.parent_id == node_id
        ).first()
    
    if has_children:
        raise HTTPException(status_code=400, detail="该维度不是末级维度，无法下钻")
    
    # 查询该维度对应的收费项目映射
    mappings = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        DimensionItemMapping.dimension_code == dimension_code
    ).all()
    
    if not mappings:
        return DimensionDrillDownResponse(
            dimension_name=dimension_name,
            items=[],
            total_amount=Decimal('0'),
            total_quantity=Decimal('0'),
            message="未找到该维度与收费项目的映射关系"
        )
    
    # 获取映射的收费项目编码
    item_codes = list(set(m.item_code for m in mappings))
    
    # 查询收费项目信息
    charge_items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == hospital_id,
        ChargeItem.item_code.in_(item_codes)
    ).all()
    
    item_info_map = {ci.item_code: ci for ci in charge_items}
    
    # 获取科室信息（department_id=0 表示全院汇总）
    if is_hospital_summary:
        dept_code = None
        dept_name = "全院汇总"
    else:
        department = db.query(Department).filter(
            Department.id == department_id
        ).first()
        
        if not department:
            raise HTTPException(status_code=404, detail="科室不存在")
        
        dept_code = department.his_code
        dept_name = department.accounting_unit_name or department.his_name
    
    # 根据维度编码判断业务类型
    business_type = get_business_type_from_dimension_code(dimension_code)
    
    # 从 charge_details 表查询该科室该月份该维度的收费明细
    try:
        # 根据是否为全院汇总和是否需要区分业务类型构建不同的SQL
        if is_hospital_summary:
            # 全院汇总：不按科室筛选
            if business_type:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    AND business_type = :business_type
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                """)
                result = db.execute(sql, {
                    "period": period,
                    "item_codes": item_codes,
                    "business_type": business_type
                })
            else:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                """)
                result = db.execute(sql, {
                    "period": period,
                    "item_codes": item_codes
                })
        elif business_type:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                AND business_type = :business_type
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes,
                "business_type": business_type
            })
        else:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes
            })
        
        charge_details_data = result.fetchall()
        
        # 构建响应
        items = []
        total_amount = Decimal('0')
        total_quantity = Decimal('0')
        
        for row in charge_details_data:
            item_code = row[0]
            charge_item = item_info_map.get(item_code)
            item_name = row[1] or (charge_item.item_name if charge_item else item_code)
            item_category = charge_item.item_category if charge_item else None
            unit_price = charge_item.unit_price if charge_item else None
            amount = Decimal(str(row[2])) if row[2] else Decimal('0')
            quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
            
            items.append(DimensionDrillDownItem(
                period=period,
                department_code=dept_code or "全院",
                department_name=dept_name,
                item_code=item_code,
                item_name=item_name,
                item_category=item_category,
                unit_price=unit_price,
                amount=amount,
                quantity=quantity
            ))
            
            total_amount += amount
            total_quantity += quantity
        
        if items:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=items,
                total_amount=total_amount,
                total_quantity=total_quantity,
                message=None
            )
        else:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=[],
                total_amount=Decimal('0'),
                total_quantity=Decimal('0'),
                message="未找到该月份该维度的收费明细数据"
            )
            
    except Exception as e:
        print(f"查询 charge_details 失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询收费明细失败: {str(e)}"
        )


@router.get("/preview/value-distribution", response_model=ValueDistributionResponse)
def preview_value_distribution(
    department_id: int = Query(..., description="科室ID"),
    period: str = Query(..., description="年月 (YYYY-MM)"),
    task_id: Optional[str] = Query(None, description="计算任务ID（可选，不传则使用最新任务）"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    预览科室主业价值分布（用于新建报告时）
    
    - 通过科室ID和年月直接查询，不需要报告ID
    - 可指定 task_id 使用特定任务的数据
    - 从 calculation_results 表提取 Top 5 维度
    """
    from decimal import Decimal
    from app.models.calculation_task import CalculationResult
    
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证科室存在且属于当前医疗机构
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.hospital_id == hospital_id
    ).first()
    if not department:
        raise HTTPException(status_code=400, detail="科室不存在或不属于当前医疗机构")
    
    # 获取任务
    task = get_task_by_id_or_latest(db, hospital_id, period, task_id)
    
    if not task:
        return ValueDistributionResponse(
            items=[],
            total_value=Decimal('0'),
            message="未找到该月份的计算结果"
        )
    
    # 查询该科室的维度计算结果
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.node_type == "dimension"
    ).all()
    
    if not all_results:
        return ValueDistributionResponse(
            items=[],
            total_value=Decimal('0'),
            message="未找到该科室的计算结果"
        )
    
    # 找出叶子节点
    parent_node_ids = set(r.parent_id for r in all_results if r.parent_id)
    leaf_results = [r for r in all_results if r.node_id not in parent_node_ids]
    
    # 按业务价值降序排序，取 Top 5
    leaf_results_sorted = sorted(leaf_results, key=lambda x: x.value or Decimal('0'), reverse=True)[:5]
    
    # 计算总价值
    total_value = sum(r.value or Decimal('0') for r in leaf_results)
    
    # 构建 node_id -> result 的映射
    all_nodes = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id
    ).all()
    node_map = {r.node_id: r for r in all_nodes}
    
    def build_full_path(result):
        path_parts = []
        current = result
        while current:
            path_parts.insert(0, current.node_name)
            if current.parent_id and current.parent_id in node_map:
                current = node_map[current.parent_id]
            else:
                break
        return '-'.join(path_parts)
    
    # 构建响应
    items = []
    for rank, result in enumerate(leaf_results_sorted, 1):
        value = result.value or Decimal('0')
        workload = result.workload or Decimal('0')
        full_path = build_full_path(result)
        
        items.append(ValueDistributionItem(
            rank=rank,
            node_id=result.node_id,
            dimension_name=full_path,
            value=value,
            workload=workload
        ))
    
    return ValueDistributionResponse(
        items=items,
        total_value=total_value,
        message=None
    )


@router.get("/preview/dimension-drilldown", response_model=DimensionDrillDownResponse)
def preview_dimension_drilldown(
    department_id: int = Query(..., description="科室ID"),
    period: str = Query(..., description="年月 (YYYY-MM)"),
    node_id: int = Query(..., description="节点ID"),
    task_id: Optional[str] = Query(None, description="计算任务ID（可选，不传则使用最新任务）"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    预览维度下钻明细（用于新建报告时）
    
    - 通过科室ID、年月和节点ID直接查询，不需要报告ID
    - 可指定 task_id 使用特定任务的数据
    - 查询该维度对应的收费项目明细
    """
    from decimal import Decimal
    from sqlalchemy import text
    from app.models.calculation_task import CalculationResult
    from app.models.dimension_item_mapping import DimensionItemMapping
    from app.models.charge_item import ChargeItem
    
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证科室存在且属于当前医疗机构
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.hospital_id == hospital_id
    ).first()
    if not department:
        raise HTTPException(status_code=400, detail="科室不存在或不属于当前医疗机构")
    
    dept_code = department.his_code
    dept_name = department.accounting_unit_name or department.his_name
    
    # 获取任务
    task = get_task_by_id_or_latest(db, hospital_id, period, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="未找到计算任务")
    
    # 查询该维度节点信息
    dimension_result = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.node_id == node_id,
        CalculationResult.node_type == "dimension"
    ).first()
    
    if not dimension_result:
        raise HTTPException(status_code=404, detail="未找到该维度的计算结果")
    
    dimension_name = dimension_result.node_name
    dimension_code = dimension_result.node_code
    
    if not dimension_code:
        raise HTTPException(status_code=400, detail="该维度缺少编码信息，无法下钻")
    
    # 检查是否为指标维度（成本等），指标维度不支持下钻
    if '-cost' in dimension_code:
        raise HTTPException(status_code=400, detail="指标维度（成本等）不支持下钻")
    
    # 检查是否为支持下钻的维度
    is_doctor_dim = dimension_code.startswith('dim-doc-') and dimension_code != 'dim-doc-case'
    is_tech_dim = dimension_code.startswith('dim-tech-')
    nurse_workload_prefixes = ['dim-nur-bed', 'dim-nur-trans', 'dim-nur-op', 'dim-nur-or', 'dim-nur-mon']
    nurse_charge_prefixes = ['dim-nur-base', 'dim-nur-collab', 'dim-nur-tr-', 'dim-nur-other']
    is_nurse_workload_dim = any(dimension_code.startswith(p) for p in nurse_workload_prefixes)
    is_nurse_charge_dim = (
        dimension_code.startswith('dim-nur-') and 
        not is_nurse_workload_dim and
        any(dimension_code.startswith(p) for p in nurse_charge_prefixes)
    )
    
    if not is_doctor_dim and not is_tech_dim and not is_nurse_charge_dim:
        raise HTTPException(
            status_code=400, 
            detail="仅支持医生、医技、护理序列中按维度目录计算的末级维度下钻"
        )
    
    # 检查是否为叶子节点
    has_children = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.parent_id == node_id
    ).first()
    
    if has_children:
        raise HTTPException(status_code=400, detail="该维度不是末级维度，无法下钻")
    
    # 查询该维度对应的收费项目映射
    mappings = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        DimensionItemMapping.dimension_code == dimension_code
    ).all()
    
    if not mappings:
        return DimensionDrillDownResponse(
            dimension_name=dimension_name,
            items=[],
            total_amount=Decimal('0'),
            total_quantity=Decimal('0'),
            message="未找到该维度与收费项目的映射关系"
        )
    
    # 获取映射的收费项目编码
    item_codes = list(set(m.item_code for m in mappings))
    
    # 查询收费项目信息
    charge_items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == hospital_id,
        ChargeItem.item_code.in_(item_codes)
    ).all()
    
    item_info_map = {ci.item_code: ci for ci in charge_items}
    
    # 根据维度编码判断业务类型
    business_type = get_business_type_from_dimension_code(dimension_code)
    
    # 从 charge_details 表查询该科室该月份该维度的收费明细
    try:
        # 根据是否需要区分业务类型构建不同的SQL
        if business_type:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                AND business_type = :business_type
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes,
                "business_type": business_type
            })
        else:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes
            })
        
        charge_details_data = result.fetchall()
        
        # 构建响应
        items = []
        total_amount = Decimal('0')
        total_quantity = Decimal('0')
        
        for row in charge_details_data:
            item_code = row[0]
            charge_item = item_info_map.get(item_code)
            item_name = row[1] or (charge_item.item_name if charge_item else item_code)
            item_category = charge_item.item_category if charge_item else None
            unit_price = charge_item.unit_price if charge_item else None
            amount = Decimal(str(row[2])) if row[2] else Decimal('0')
            quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
            
            items.append(DimensionDrillDownItem(
                period=period,
                department_code=dept_code,
                department_name=dept_name,
                item_code=item_code,
                item_name=item_name,
                item_category=item_category,
                unit_price=unit_price,
                amount=amount,
                quantity=quantity
            ))
            
            total_amount += amount
            total_quantity += quantity
        
        if items:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=items,
                total_amount=total_amount,
                total_quantity=total_quantity,
                message=None
            )
        else:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=[],
                total_amount=Decimal('0'),
                total_quantity=Decimal('0'),
                message="未找到该科室该月份该维度的收费明细数据"
            )
            
    except Exception as e:
        print(f"查询 charge_details 失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询收费明细失败: {str(e)}"
        )


@router.get("/preview/business-content", response_model=BusinessContentResponse)
def preview_business_content(
    department_id: int = Query(..., description="科室ID"),
    period: str = Query(..., description="年月 (YYYY-MM)"),
    task_id: Optional[str] = Query(None, description="计算任务ID（可选，不传则使用最新任务）"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    预览科室业务内涵展示（用于新建报告时）
    
    - 通过科室ID和年月直接查询，不需要报告ID
    - 可指定 task_id 使用特定任务的数据
    - 对于 Top 5 维度，取收入 Top 5 的项目
    """
    from decimal import Decimal
    from sqlalchemy import text
    from app.models.calculation_task import CalculationResult
    from app.models.dimension_item_mapping import DimensionItemMapping
    from app.models.charge_item import ChargeItem
    
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证科室存在且属于当前医疗机构
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.hospital_id == hospital_id
    ).first()
    if not department:
        raise HTTPException(status_code=400, detail="科室不存在或不属于当前医疗机构")
    
    dept_code = department.his_code
    
    # 获取任务
    task = get_task_by_id_or_latest(db, hospital_id, period, task_id)
    
    if not task:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该月份的计算结果"
        )
    
    # 查询该科室的所有计算结果
    all_nodes = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id
    ).all()
    
    if not all_nodes:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该科室的计算结果"
        )
    
    node_map = {r.node_id: r for r in all_nodes}
    
    def build_full_path(result):
        path_parts = []
        current = result
        while current:
            path_parts.insert(0, current.node_name)
            if current.parent_id and current.parent_id in node_map:
                current = node_map[current.parent_id]
            else:
                break
        return '-'.join(path_parts)
    
    # 筛选维度节点
    dimension_results = [r for r in all_nodes if r.node_type == "dimension"]
    
    # 找出叶子节点
    parent_node_ids = set(r.parent_id for r in dimension_results if r.parent_id)
    leaf_results = [r for r in dimension_results if r.node_id not in parent_node_ids]
    
    # 按业务价值降序排序，取 Top 5 维度
    top_dimensions = sorted(leaf_results, key=lambda x: x.value or Decimal('0'), reverse=True)[:5]
    
    if not top_dimensions:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到维度数据"
        )
    
    # 构建按维度分组的响应
    dimensions_list = []
    
    for dimension in top_dimensions:
        if not dimension.node_code:
            continue
        
        full_path = build_full_path(dimension)
        
        # 查询该维度对应的收费项目映射
        dim_mappings = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.hospital_id == hospital_id,
            DimensionItemMapping.dimension_code == dimension.node_code
        ).all()
        
        if not dim_mappings:
            continue
        
        dim_item_codes = [m.item_code for m in dim_mappings]
        
        # 查询收费项目信息
        charge_items = db.query(ChargeItem).filter(
            ChargeItem.hospital_id == hospital_id,
            ChargeItem.item_code.in_(dim_item_codes)
        ).all()
        
        item_info_map = {ci.item_code: ci for ci in charge_items}
        
        # 根据维度编码判断业务类型
        dim_business_type = get_business_type_from_dimension_code(dimension.node_code)
        
        # 从 charge_details 查询该维度收入 Top 5 的项目
        dim_items = []
        try:
            if dim_business_type:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE prescribing_dept_code = :dept_code
                    AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    AND business_type = :business_type
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                    LIMIT 5
                """)
                result = db.execute(sql, {
                    "dept_code": dept_code,
                    "period": period,
                    "item_codes": dim_item_codes,
                    "business_type": dim_business_type
                })
            else:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE prescribing_dept_code = :dept_code
                    AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                    LIMIT 5
                """)
                result = db.execute(sql, {
                    "dept_code": dept_code,
                    "period": period,
                    "item_codes": dim_item_codes
                })
            
            charge_details_data = result.fetchall()
            
            for row in charge_details_data:
                item_code = row[0]
                charge_item = item_info_map.get(item_code)
                item_name = row[1] or (charge_item.item_name if charge_item else item_code)
                item_category = charge_item.item_category if charge_item else None
                unit_price = charge_item.unit_price if charge_item else None
                amount = Decimal(str(row[2])) if row[2] else Decimal('0')
                quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
                
                dim_items.append(BusinessContentItem(
                    item_code=item_code,
                    item_name=item_name,
                    item_category=item_category,
                    unit_price=unit_price,
                    amount=amount,
                    quantity=quantity
                ))
                
        except Exception as e:
            print(f"查询维度 {dimension.node_code} 的 charge_details 失败: {str(e)}")
            continue
        
        if dim_items:
            dimensions_list.append(DimensionBusinessContent(
                dimension_name=full_path,
                items=dim_items
            ))
    
    if dimensions_list:
        return BusinessContentResponse(
            dimensions=dimensions_list,
            message=None
        )
    else:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该科室该月份的收费明细数据"
        )


@router.get("/{report_id}", response_model=AnalysisReportSchema)
def get_analysis_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取分析报告详情
    
    - 科室用户只能查看自己科室的报告
    - 管理员可以查看所有报告
    """
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 检查访问权限
    check_report_access(current_user, report)
    
    # 获取工作流名称
    workflow_name = None
    if report.task_id:
        from app.models.calculation_task import CalculationTask
        from app.models.calculation_workflow import CalculationWorkflow
        task = db.query(CalculationTask).filter(
            CalculationTask.task_id == report.task_id
        ).first()
        if task and task.workflow_id:
            workflow = db.query(CalculationWorkflow).filter(
                CalculationWorkflow.id == task.workflow_id
            ).first()
            if workflow:
                workflow_name = workflow.name
    
    # 转换为响应格式
    dept = report.department
    return AnalysisReportSchema(
        id=report.id,
        hospital_id=report.hospital_id,
        department_id=report.department_id,
        department_code=dept.accounting_unit_code if dept else "",
        department_name=(dept.accounting_unit_name or dept.his_name) if dept else "",
        period=report.period,
        task_id=report.task_id,
        workflow_name=workflow_name,
        current_issues=report.current_issues,
        future_plans=report.future_plans,
        created_at=report.created_at,
        updated_at=report.updated_at,
        created_by=report.created_by,
    )



@router.post("", response_model=AnalysisReportSchema)
def create_analysis_report(
    report_in: AnalysisReportCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    创建分析报告
    
    - 同一医疗机构、同一科室、同一年月只能有一条报告
    """
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证科室存在且属于当前医疗机构
    department = db.query(Department).filter(
        Department.id == report_in.department_id,
        Department.hospital_id == hospital_id
    ).first()
    if not department:
        raise HTTPException(status_code=400, detail="科室不存在或不属于当前医疗机构")
    
    # 创建报告数据
    report_data = report_in.model_dump()
    report_data = set_hospital_id_for_create(report_data, hospital_id)
    report_data["created_by"] = current_user.id
    
    # 创建报告
    report = AnalysisReport(**report_data)
    
    try:
        db.add(report)
        db.commit()
        db.refresh(report)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="该科室在该月份的分析报告已存在"
        )
    
    # 获取工作流名称
    workflow_name = None
    if report.task_id:
        from app.models.calculation_task import CalculationTask
        from app.models.calculation_workflow import CalculationWorkflow
        task = db.query(CalculationTask).filter(
            CalculationTask.task_id == report.task_id
        ).first()
        if task and task.workflow_id:
            workflow = db.query(CalculationWorkflow).filter(
                CalculationWorkflow.id == task.workflow_id
            ).first()
            if workflow:
                workflow_name = workflow.name
    
    # 转换为响应格式
    return AnalysisReportSchema(
        id=report.id,
        hospital_id=report.hospital_id,
        department_id=report.department_id,
        department_code=department.accounting_unit_code,
        department_name=department.accounting_unit_name or department.his_name,
        period=report.period,
        task_id=report.task_id,
        workflow_name=workflow_name,
        current_issues=report.current_issues,
        future_plans=report.future_plans,
        created_at=report.created_at,
        updated_at=report.updated_at,
        created_by=report.created_by,
    )


@router.put("/{report_id}", response_model=AnalysisReportSchema)
def update_analysis_report(
    report_id: int,
    report_in: AnalysisReportUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    更新分析报告
    
    - 只能更新当前存在问题和未来发展计划
    - 管理员可以更新所有报告
    """
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, report)
    
    # 更新字段
    update_data = report_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    # 转换为响应格式
    dept = report.department
    
    # 获取关联的计算任务信息
    workflow_name = None
    if report.task_id:
        from app.models.calculation_task import CalculationTask
        task = db.query(CalculationTask).filter(
            CalculationTask.task_id == report.task_id
        ).first()
        if task and task.workflow:
            workflow_name = task.workflow.name
    
    return AnalysisReportSchema(
        id=report.id,
        hospital_id=report.hospital_id,
        department_id=report.department_id,
        department_code=dept.accounting_unit_code if dept else "",
        department_name=(dept.accounting_unit_name or dept.his_name) if dept else "",
        period=report.period,
        task_id=report.task_id,
        workflow_name=workflow_name,
        current_issues=report.current_issues,
        future_plans=report.future_plans,
        created_at=report.created_at,
        updated_at=report.updated_at,
        created_by=report.created_by,
    )


@router.delete("/{report_id}")
def delete_analysis_report(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    删除分析报告
    
    - 管理员可以删除报告
    """
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, report)
    
    db.delete(report)
    db.commit()
    
    return {"message": "分析报告删除成功"}


@router.get("/{report_id}/value-distribution", response_model=ValueDistributionResponse)
def get_value_distribution(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取科室主业价值分布
    
    - 从 calculation_results 表提取 Top 10 维度
    - 计算占比
    - 需求: 4.3, 7.1, 7.4
    """
    from decimal import Decimal
    from app.models.calculation_task import CalculationTask, CalculationResult
    from app.models.model_version import ModelVersion
    
    # 获取报告
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 检查访问权限
    check_report_access(current_user, report)
    
    hospital_id = report.hospital_id
    department_id = report.department_id
    period = report.period
    
    # 查找该医疗机构激活版本的最新完成任务
    active_version_query = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    )
    active_version = active_version_query.first()
    
    if not active_version:
        return ValueDistributionResponse(
            items=[],
            total_value=Decimal('0'),
            message="未找到激活的模型版本"
        )
    
    # 查找最新完成的计算任务
    task_query = db.query(CalculationTask).filter(
        CalculationTask.model_version_id == active_version.id,
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    ).order_by(desc(CalculationTask.completed_at))
    
    task = task_query.first()
    
    if not task:
        return ValueDistributionResponse(
            items=[],
            total_value=Decimal('0'),
            message="未找到该月份的计算结果"
        )
    
    # 查询该科室的维度计算结果（只取叶子维度节点）
    # 叶子节点是没有子节点的维度节点
    results_query = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.node_type == "dimension"
    )
    
    all_results = results_query.all()
    
    if not all_results:
        return ValueDistributionResponse(
            items=[],
            total_value=Decimal('0'),
            message="未找到该科室的计算结果"
        )
    
    # 找出叶子节点（没有子节点的维度）
    # 获取所有作为父节点的 node_id
    parent_node_ids = set(r.parent_id for r in all_results if r.parent_id)
    # 叶子节点是那些 node_id 不在 parent_node_ids 中的节点
    leaf_results = [r for r in all_results if r.node_id not in parent_node_ids]
    
    # 按业务价值降序排序，取 Top 5
    leaf_results_sorted = sorted(leaf_results, key=lambda x: x.value or Decimal('0'), reverse=True)[:5]
    
    # 计算总价值（所有叶子节点的总和）
    total_value = sum(r.value or Decimal('0') for r in leaf_results)
    
    # 构建 node_id -> result 的映射，用于查找父节点
    # 需要查询所有节点（包括序列节点）来构建完整路径
    all_nodes_query = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id
    )
    all_nodes = all_nodes_query.all()
    node_map = {r.node_id: r for r in all_nodes}
    
    def build_full_path(result):
        """构建完整的维度路径：序列-一级维度-二级维度..."""
        path_parts = []
        current = result
        while current:
            path_parts.insert(0, current.node_name)
            if current.parent_id and current.parent_id in node_map:
                current = node_map[current.parent_id]
            else:
                break
        return '-'.join(path_parts)
    
    # 构建响应
    items = []
    for rank, result in enumerate(leaf_results_sorted, 1):
        value = result.value or Decimal('0')
        workload = result.workload or Decimal('0')
        
        # 构建完整维度路径
        full_path = build_full_path(result)
        
        items.append(ValueDistributionItem(
            rank=rank,
            node_id=result.node_id,
            dimension_name=full_path,
            value=value,
            workload=workload
        ))
    
    return ValueDistributionResponse(
        items=items,
        total_value=total_value,
        message=None
    )


@router.get("/{report_id}/business-content", response_model=BusinessContentResponse)
def get_business_content(
    report_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取科室业务内涵展示（按维度分组）
    
    - 对于科室主业价值分布中的每个维度（Top 5），取收入 Top 5 的项目
    - 按维度分组返回，每个维度一个表格
    """
    from decimal import Decimal
    from sqlalchemy import text
    from app.models.calculation_task import CalculationTask, CalculationResult
    from app.models.model_version import ModelVersion
    from app.models.dimension_item_mapping import DimensionItemMapping
    from app.models.charge_item import ChargeItem
    
    # 获取报告
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 检查访问权限
    check_report_access(current_user, report)
    
    hospital_id = report.hospital_id
    department_id = report.department_id
    period = report.period
    
    # 查找该医疗机构激活版本的最新完成任务
    active_version_query = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    )
    active_version = active_version_query.first()
    
    if not active_version:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到激活的模型版本"
        )
    
    # 查找最新完成的计算任务
    task_query = db.query(CalculationTask).filter(
        CalculationTask.model_version_id == active_version.id,
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    ).order_by(desc(CalculationTask.completed_at))
    
    task = task_query.first()
    
    if not task:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该月份的计算结果"
        )
    
    # 查询该科室的所有计算结果（包括序列节点，用于构建完整路径）
    all_nodes_query = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id
    )
    all_nodes = all_nodes_query.all()
    
    if not all_nodes:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该科室的计算结果"
        )
    
    # 构建 node_id -> result 的映射，用于查找父节点
    node_map = {r.node_id: r for r in all_nodes}
    
    def build_full_path(result):
        """构建完整的维度路径：序列-一级维度-二级维度..."""
        path_parts = []
        current = result
        while current:
            path_parts.insert(0, current.node_name)
            if current.parent_id and current.parent_id in node_map:
                current = node_map[current.parent_id]
            else:
                break
        return '-'.join(path_parts)
    
    # 筛选维度节点
    dimension_results = [r for r in all_nodes if r.node_type == "dimension"]
    
    # 找出叶子节点（没有子节点的维度）
    parent_node_ids = set(r.parent_id for r in dimension_results if r.parent_id)
    leaf_results = [r for r in dimension_results if r.node_id not in parent_node_ids]
    
    # 按业务价值降序排序，取 Top 5 维度
    top_dimensions = sorted(leaf_results, key=lambda x: x.value or Decimal('0'), reverse=True)[:5]
    
    if not top_dimensions:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到维度数据"
        )
    
    # 获取科室信息
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        return BusinessContentResponse(
            dimensions=[],
            message="科室不存在"
        )
    
    dept_code = department.his_code
    
    # 构建按维度分组的响应
    dimensions_list = []
    
    # 对每个 Top 5 维度，查询收入 Top 5 的项目
    for dimension in top_dimensions:
        if not dimension.node_code:
            continue
        
        # 构建完整维度路径
        full_path = build_full_path(dimension)
        
        # 查询该维度对应的收费项目映射
        dim_mappings = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.hospital_id == hospital_id,
            DimensionItemMapping.dimension_code == dimension.node_code
        ).all()
        
        if not dim_mappings:
            continue
        
        # 获取映射的收费项目编码
        dim_item_codes = [m.item_code for m in dim_mappings]
        
        # 查询收费项目信息
        charge_items = db.query(ChargeItem).filter(
            ChargeItem.hospital_id == hospital_id,
            ChargeItem.item_code.in_(dim_item_codes)
        ).all()
        
        item_info_map = {ci.item_code: ci for ci in charge_items}
        
        # 根据维度编码判断业务类型
        dim_business_type = get_business_type_from_dimension_code(dimension.node_code)
        
        # 从 charge_details 查询该维度收入 Top 5 的项目
        dim_items = []
        try:
            if dim_business_type:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE prescribing_dept_code = :dept_code
                    AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    AND business_type = :business_type
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                    LIMIT 5
                """)
                result = db.execute(sql, {
                    "dept_code": dept_code,
                    "period": period,
                    "item_codes": dim_item_codes,
                    "business_type": dim_business_type
                })
            else:
                sql = text("""
                    SELECT 
                        item_code,
                        item_name,
                        SUM(amount) as total_amount,
                        SUM(quantity) as total_quantity
                    FROM charge_details
                    WHERE prescribing_dept_code = :dept_code
                    AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                    AND item_code = ANY(:item_codes)
                    GROUP BY item_code, item_name
                    ORDER BY total_amount DESC
                    LIMIT 5
                """)
                result = db.execute(sql, {
                    "dept_code": dept_code,
                    "period": period,
                    "item_codes": dim_item_codes
                })
            
            charge_details_data = result.fetchall()
            
            for row in charge_details_data:
                item_code = row[0]
                charge_item = item_info_map.get(item_code)
                item_name = row[1] or (charge_item.item_name if charge_item else item_code)
                item_category = charge_item.item_category if charge_item else None
                unit_price = charge_item.unit_price if charge_item else None
                amount = Decimal(str(row[2])) if row[2] else Decimal('0')
                quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
                
                dim_items.append(BusinessContentItem(
                    item_code=item_code,
                    item_name=item_name,
                    item_category=item_category,
                    unit_price=unit_price,
                    amount=amount,
                    quantity=quantity
                ))
                
        except Exception as e:
            print(f"查询维度 {dimension.node_code} 的 charge_details 失败: {str(e)}")
            continue
        
        # 只有有数据的维度才添加到结果中
        if dim_items:
            dimensions_list.append(DimensionBusinessContent(
                dimension_name=full_path,
                items=dim_items
            ))
    
    if dimensions_list:
        return BusinessContentResponse(
            dimensions=dimensions_list,
            message=None
        )
    else:
        return BusinessContentResponse(
            dimensions=[],
            message="未找到该科室该月份的收费明细数据"
        )


@router.get("/{report_id}/dimension-drilldown/{node_id}", response_model=DimensionDrillDownResponse)
def get_dimension_drilldown(
    report_id: int,
    node_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取维度下钻明细
    
    - 查询该维度对应的收费项目明细
    - 仅支持医生序列中按维度目录计算的末级维度（除病例价值维度外）
    - 需求: 维度下钻功能
    """
    from decimal import Decimal
    from sqlalchemy import text
    from app.models.calculation_task import CalculationTask, CalculationResult
    from app.models.model_version import ModelVersion
    from app.models.dimension_item_mapping import DimensionItemMapping
    from app.models.charge_item import ChargeItem
    from app.models.department import Department
    
    # 获取报告
    query = db.query(AnalysisReport).filter(AnalysisReport.id == report_id)
    query = apply_hospital_filter(query, AnalysisReport, required=True)
    report = query.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="分析报告不存在或不属于当前医疗机构")
    
    # 检查访问权限
    check_report_access(current_user, report)
    
    hospital_id = report.hospital_id
    department_id = report.department_id
    period = report.period
    
    # 查找该医疗机构激活版本的最新完成任务
    active_version_query = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    )
    active_version = active_version_query.first()
    
    if not active_version:
        raise HTTPException(status_code=404, detail="未找到激活的模型版本")
    
    # 查找最新完成的计算任务
    task_query = db.query(CalculationTask).filter(
        CalculationTask.model_version_id == active_version.id,
        CalculationTask.period == period,
        CalculationTask.status == "completed"
    ).order_by(desc(CalculationTask.completed_at))
    
    task = task_query.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="未找到该月份的计算结果")
    
    # 查询该维度节点信息
    dimension_result = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.node_id == node_id,
        CalculationResult.node_type == "dimension"
    ).first()
    
    if not dimension_result:
        raise HTTPException(status_code=404, detail="未找到该维度的计算结果")
    
    dimension_name = dimension_result.node_name
    dimension_code = dimension_result.node_code
    
    if not dimension_code:
        raise HTTPException(status_code=400, detail="该维度缺少编码信息，无法下钻")
    
    # 检查是否为指标维度（成本等），指标维度不支持下钻
    if '-cost' in dimension_code:
        raise HTTPException(status_code=400, detail="指标维度（成本等）不支持下钻")
    
    # 检查是否为支持下钻的维度（医生、医技、护理序列中用charge_details计算的维度）
    is_doctor_dim = dimension_code.startswith('dim-doc-') and dimension_code != 'dim-doc-case'
    is_tech_dim = dimension_code.startswith('dim-tech-')
    # 护理序列中用charge_details计算的维度（排除用workload_statistics计算的床日、出入转院等维度）
    nurse_workload_prefixes = ['dim-nur-bed', 'dim-nur-trans', 'dim-nur-op', 'dim-nur-or', 'dim-nur-mon']
    nurse_charge_prefixes = ['dim-nur-base', 'dim-nur-collab', 'dim-nur-tr-', 'dim-nur-other']
    is_nurse_workload_dim = any(dimension_code.startswith(p) for p in nurse_workload_prefixes)
    is_nurse_charge_dim = (
        dimension_code.startswith('dim-nur-') and 
        not is_nurse_workload_dim and
        any(dimension_code.startswith(p) for p in nurse_charge_prefixes)
    )
    
    if not is_doctor_dim and not is_tech_dim and not is_nurse_charge_dim:
        raise HTTPException(
            status_code=400, 
            detail="仅支持医生、医技、护理序列中按维度目录计算的末级维度下钻（不包括病例价值维度和工作量统计维度）"
        )
    
    # 检查是否为叶子节点
    has_children = db.query(CalculationResult).filter(
        CalculationResult.task_id == task.task_id,
        CalculationResult.department_id == department_id,
        CalculationResult.parent_id == node_id
    ).first()
    
    if has_children:
        raise HTTPException(status_code=400, detail="该维度不是末级维度，无法下钻")
    
    # 查询该维度对应的收费项目映射
    mappings = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        DimensionItemMapping.dimension_code == dimension_code
    ).all()
    
    if not mappings:
        return DimensionDrillDownResponse(
            dimension_name=dimension_name,
            items=[],
            total_amount=Decimal('0'),
            total_quantity=Decimal('0'),
            message="未找到该维度与收费项目的映射关系"
        )
    
    # 获取映射的收费项目编码
    item_codes = list(set(m.item_code for m in mappings))
    
    # 查询收费项目信息
    charge_items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == hospital_id,
        ChargeItem.item_code.in_(item_codes)
    ).all()
    
    item_info_map = {ci.item_code: ci for ci in charge_items}
    
    # 获取科室信息
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()
    
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    dept_code = department.his_code
    dept_name = department.accounting_unit_name or department.his_name
    
    # 根据维度编码判断业务类型
    business_type = get_business_type_from_dimension_code(dimension_code)
    
    # 从 charge_details 表查询该科室该月份该维度的收费明细
    try:
        # 根据是否需要区分业务类型构建不同的SQL
        if business_type:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                AND business_type = :business_type
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes,
                "business_type": business_type
            })
        else:
            sql = text("""
                SELECT 
                    item_code,
                    item_name,
                    SUM(amount) as total_amount,
                    SUM(quantity) as total_quantity
                FROM charge_details
                WHERE prescribing_dept_code = :dept_code
                AND TO_CHAR(charge_time, 'YYYY-MM') = :period
                AND item_code = ANY(:item_codes)
                GROUP BY item_code, item_name
                ORDER BY total_amount DESC
            """)
            result = db.execute(sql, {
                "dept_code": dept_code,
                "period": period,
                "item_codes": item_codes
            })
        
        charge_details_data = result.fetchall()
        
        # 构建响应
        items = []
        total_amount = Decimal('0')
        total_quantity = Decimal('0')
        
        for row in charge_details_data:
            item_code = row[0]
            charge_item = item_info_map.get(item_code)
            item_name = row[1] or (charge_item.item_name if charge_item else item_code)
            item_category = charge_item.item_category if charge_item else None
            unit_price = charge_item.unit_price if charge_item else None
            amount = Decimal(str(row[2])) if row[2] else Decimal('0')
            quantity = Decimal(str(row[3])) if row[3] else Decimal('0')
            
            items.append(DimensionDrillDownItem(
                period=period,
                department_code=dept_code,
                department_name=dept_name,
                item_code=item_code,
                item_name=item_name,
                item_category=item_category,
                unit_price=unit_price,
                amount=amount,
                quantity=quantity
            ))
            
            total_amount += amount
            total_quantity += quantity
        
        if items:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=items,
                total_amount=total_amount,
                total_quantity=total_quantity,
                message=None
            )
        else:
            return DimensionDrillDownResponse(
                dimension_name=dimension_name,
                items=[],
                total_amount=Decimal('0'),
                total_quantity=Decimal('0'),
                message="未找到该科室该月份该维度的收费明细数据"
            )
            
    except Exception as e:
        print(f"查询 charge_details 失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询收费明细失败: {str(e)}"
        )
