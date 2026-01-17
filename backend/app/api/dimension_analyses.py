"""
维度分析 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.utils.hospital_filter import get_current_hospital_id_or_raise
from app.models.user import User
from app.models.dimension_analysis import DimensionAnalysis
from app.models.department import Department
from app.models.model_node import ModelNode
from app.schemas.dimension_analysis import (
    DimensionAnalysisCreate,
    DimensionAnalysisUpdate,
    DimensionAnalysisResponse,
    DimensionAnalysisQuery,
    DimensionAnalysisBatchQuery,
    DimensionAnalysisBatchResponse,
)

router = APIRouter()


def get_analysis_response(analysis: DimensionAnalysis, db: Session) -> DimensionAnalysisResponse:
    """构建分析响应对象"""
    # 获取关联信息
    department = db.query(Department).filter(Department.id == analysis.department_id).first()
    node = db.query(ModelNode).filter(ModelNode.id == analysis.node_id).first()
    creator = db.query(User).filter(User.id == analysis.created_by).first() if analysis.created_by else None
    updater = db.query(User).filter(User.id == analysis.updated_by).first() if analysis.updated_by else None
    
    return DimensionAnalysisResponse(
        id=analysis.id,
        hospital_id=analysis.hospital_id,
        department_id=analysis.department_id,
        node_id=analysis.node_id,
        period=analysis.period,
        content=analysis.content,
        department_name=department.accounting_unit_name if department else None,
        node_name=node.name if node else None,
        created_by=analysis.created_by,
        created_by_name=creator.username if creator else None,
        updated_by=analysis.updated_by,
        updated_by_name=updater.username if updater else None,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


@router.get("", response_model=DimensionAnalysisResponse)
def get_dimension_analysis(
    department_id: int = Query(..., description="科室ID"),
    node_id: int = Query(..., description="维度节点ID"),
    period: Optional[str] = Query(None, description="统计月份(YYYY-MM)，不传表示查询长期分析"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """获取单个维度分析"""
    query = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.hospital_id == hospital_id,
        DimensionAnalysis.department_id == department_id,
        DimensionAnalysis.node_id == node_id,
    )
    
    if period:
        query = query.filter(DimensionAnalysis.period == period)
    else:
        query = query.filter(DimensionAnalysis.period.is_(None))
    
    analysis = query.first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="未找到该维度分析")
    
    return get_analysis_response(analysis, db)


@router.post("/batch-query", response_model=DimensionAnalysisBatchResponse)
def batch_query_dimension_analyses(
    query_params: DimensionAnalysisBatchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """批量查询维度分析（用于明细表展示）"""
    # 查询当期分析
    current_analyses = {}
    if query_params.period:
        analyses = db.query(DimensionAnalysis).filter(
            DimensionAnalysis.hospital_id == hospital_id,
            DimensionAnalysis.department_id == query_params.department_id,
            DimensionAnalysis.node_id.in_(query_params.node_ids),
            DimensionAnalysis.period == query_params.period,
        ).all()
        
        for analysis in analyses:
            current_analyses[str(analysis.node_id)] = get_analysis_response(analysis, db)
    
    # 查询长期分析
    long_term_analyses = {}
    analyses = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.hospital_id == hospital_id,
        DimensionAnalysis.department_id == query_params.department_id,
        DimensionAnalysis.node_id.in_(query_params.node_ids),
        DimensionAnalysis.period.is_(None),
    ).all()
    
    for analysis in analyses:
        long_term_analyses[str(analysis.node_id)] = get_analysis_response(analysis, db)
    
    return DimensionAnalysisBatchResponse(
        current_analyses=current_analyses,
        long_term_analyses=long_term_analyses,
    )


@router.post("", response_model=DimensionAnalysisResponse)
def create_or_update_dimension_analysis(
    data: DimensionAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """创建或更新维度分析（upsert）"""
    # 验证科室存在
    department = db.query(Department).filter(
        Department.id == data.department_id,
        Department.hospital_id == hospital_id,
    ).first()
    if not department:
        raise HTTPException(status_code=404, detail="科室不存在")
    
    # 验证维度节点存在
    node = db.query(ModelNode).filter(ModelNode.id == data.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="维度节点不存在")
    
    # 查找现有分析
    query = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.hospital_id == hospital_id,
        DimensionAnalysis.department_id == data.department_id,
        DimensionAnalysis.node_id == data.node_id,
    )
    
    if data.period:
        query = query.filter(DimensionAnalysis.period == data.period)
    else:
        query = query.filter(DimensionAnalysis.period.is_(None))
    
    analysis = query.first()
    
    if analysis:
        # 更新现有分析
        analysis.content = data.content
        analysis.updated_by = current_user.id
    else:
        # 创建新分析
        analysis = DimensionAnalysis(
            hospital_id=hospital_id,
            department_id=data.department_id,
            node_id=data.node_id,
            period=data.period,
            content=data.content,
            created_by=current_user.id,
            updated_by=current_user.id,
        )
        db.add(analysis)
    
    db.commit()
    db.refresh(analysis)
    
    return get_analysis_response(analysis, db)


@router.put("/{analysis_id}", response_model=DimensionAnalysisResponse)
def update_dimension_analysis(
    analysis_id: int,
    data: DimensionAnalysisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """更新维度分析"""
    analysis = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.id == analysis_id,
        DimensionAnalysis.hospital_id == hospital_id,
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="未找到该维度分析")
    
    analysis.content = data.content
    analysis.updated_by = current_user.id
    
    db.commit()
    db.refresh(analysis)
    
    return get_analysis_response(analysis, db)


@router.delete("/{analysis_id}")
def delete_dimension_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """删除维度分析"""
    analysis = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.id == analysis_id,
        DimensionAnalysis.hospital_id == hospital_id,
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="未找到该维度分析")
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "删除成功"}


@router.get("/list", response_model=list[DimensionAnalysisResponse])
def list_dimension_analyses(
    department_id: Optional[int] = Query(None, description="科室ID"),
    node_id: Optional[int] = Query(None, description="维度节点ID"),
    period: Optional[str] = Query(None, description="统计月份(YYYY-MM)"),
    analysis_type: Optional[str] = Query(None, description="分析类型: current/long_term"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """列出维度分析"""
    query = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.hospital_id == hospital_id,
    )
    
    if department_id:
        query = query.filter(DimensionAnalysis.department_id == department_id)
    
    if node_id:
        query = query.filter(DimensionAnalysis.node_id == node_id)
    
    if period:
        query = query.filter(DimensionAnalysis.period == period)
    
    if analysis_type == "current":
        query = query.filter(DimensionAnalysis.period.isnot(None))
    elif analysis_type == "long_term":
        query = query.filter(DimensionAnalysis.period.is_(None))
    
    query = query.order_by(DimensionAnalysis.updated_at.desc())
    
    analyses = query.offset((page - 1) * size).limit(size).all()
    
    return [get_analysis_response(a, db) for a in analyses]


@router.post("/batch-query-by-codes")
def batch_query_by_codes(
    department_codes: list[str] = Query(..., description="科室代码列表"),
    dimension_codes: list[str] = Query(..., description="维度代码列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    hospital_id: int = Depends(get_current_hospital_id_or_raise),
):
    """根据科室代码和维度代码批量查询维度分析（用于学科规则展示）
    
    返回格式: { "dept_code|dim_code": { long_term: content, current_periods: [...] } }
    
    注意：科室代码会同时匹配 his_code 和 accounting_unit_code，以支持不同来源的数据
    """
    import sqlalchemy as sa
    from app.models.model_node import ModelNode
    
    # 通过 department_code 查找 department_id
    # 同时匹配 his_code 和 accounting_unit_code，以支持不同来源的数据
    departments = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        sa.or_(
            Department.his_code.in_(department_codes),
            Department.accounting_unit_code.in_(department_codes),
        ),
    ).all()
    
    # 构建科室代码到ID的映射（优先使用 his_code，其次使用 accounting_unit_code）
    dept_code_to_id = {}
    for d in departments:
        if d.his_code in department_codes:
            dept_code_to_id[d.his_code] = d.id
        if d.accounting_unit_code and d.accounting_unit_code in department_codes:
            dept_code_to_id[d.accounting_unit_code] = d.id
    
    # 通过 dimension_code 查找 node_id
    nodes = db.query(ModelNode).filter(
        ModelNode.code.in_(dimension_codes),
    ).all()
    dim_code_to_id = {n.code: n.id for n in nodes}
    
    # 构建查询条件
    dept_ids = list(set(dept_code_to_id.values()))
    node_ids = list(dim_code_to_id.values())
    
    if not dept_ids or not node_ids:
        return {}
    
    # 查询所有相关的维度分析
    analyses = db.query(DimensionAnalysis).filter(
        DimensionAnalysis.hospital_id == hospital_id,
        DimensionAnalysis.department_id.in_(dept_ids),
        DimensionAnalysis.node_id.in_(node_ids),
    ).all()
    
    # 构建反向映射（ID到所有可能的代码）
    id_to_dept_codes = {}
    for code, dept_id in dept_code_to_id.items():
        if dept_id not in id_to_dept_codes:
            id_to_dept_codes[dept_id] = []
        id_to_dept_codes[dept_id].append(code)
    
    id_to_dim_code = {v: k for k, v in dim_code_to_id.items()}
    
    # 组织结果
    result = {}
    for analysis in analyses:
        dept_codes_for_id = id_to_dept_codes.get(analysis.department_id, [])
        dim_code = id_to_dim_code.get(analysis.node_id)
        
        if not dept_codes_for_id or not dim_code:
            continue
        
        # 为每个匹配的科室代码创建结果
        for dept_code in dept_codes_for_id:
            key = f"{dept_code}|{dim_code}"
            if key not in result:
                result[key] = {
                    "long_term_content": None,
                    "current_analyses": [],
                }
            
            if analysis.period is None:
                result[key]["long_term_content"] = analysis.content
            else:
                # 避免重复添加
                existing_periods = [a["period"] for a in result[key]["current_analyses"]]
                if analysis.period not in existing_periods:
                    result[key]["current_analyses"].append({
                        "period": analysis.period,
                        "content": analysis.content,
                    })
    
    return result
