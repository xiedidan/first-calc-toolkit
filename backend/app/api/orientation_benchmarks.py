"""
导向基准管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc

from app.api import deps
from app.models.orientation_benchmark import OrientationBenchmark
from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.schemas.orientation_benchmark import (
    OrientationBenchmark as OrientationBenchmarkSchema,
    OrientationBenchmarkCreate,
    OrientationBenchmarkUpdate,
    OrientationBenchmarkList,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)

router = APIRouter()


@router.get("", response_model=OrientationBenchmarkList)
def get_orientation_benchmarks(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    rule_id: Optional[int] = Query(None, description="按导向规则ID筛选"),
):
    """获取导向基准列表"""
    query = db.query(OrientationBenchmark)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, OrientationBenchmark, required=True)
    
    # 按导向规则筛选
    if rule_id:
        query = query.filter(OrientationBenchmark.rule_id == rule_id)
    
    # 预加载导向规则信息
    query = query.options(joinedload(OrientationBenchmark.rule))
    
    # 按创建时间倒序排序
    query = query.order_by(desc(OrientationBenchmark.created_at))
    
    # 总数
    total = query.count()
    
    # 分页
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 预加载 rule_name 字段
    for item in items:
        item.rule_name = item.rule.name if item.rule else None
    
    return OrientationBenchmarkList(total=total, items=items)


@router.post("", response_model=OrientationBenchmarkSchema)
def create_orientation_benchmark(
    benchmark_in: OrientationBenchmarkCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建导向基准"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 验证导向规则存在且属于当前医疗机构
    rule_query = db.query(OrientationRule).filter(OrientationRule.id == benchmark_in.rule_id)
    rule_query = apply_hospital_filter(rule_query, OrientationRule, required=True)
    rule = rule_query.first()
    if not rule:
        raise HTTPException(status_code=404, detail="导向规则不存在")
    
    # 验证导向类别必须为"基准阶梯"
    if rule.category != OrientationCategory.benchmark_ladder:
        raise HTTPException(
            status_code=400,
            detail="只有'基准阶梯'类别的导向规则可以创建基准"
        )
    
    # 检查同一导向下同一科室是否已存在基准
    existing_query = db.query(OrientationBenchmark).filter(
        OrientationBenchmark.rule_id == benchmark_in.rule_id,
        OrientationBenchmark.department_code == benchmark_in.department_code
    )
    existing_query = apply_hospital_filter(existing_query, OrientationBenchmark, required=True)
    existing = existing_query.first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"该导向规则下科室'{benchmark_in.department_code}'的基准已存在"
        )
    
    # 自动设置hospital_id
    benchmark_data = benchmark_in.model_dump()
    benchmark_data = set_hospital_id_for_create(benchmark_data, hospital_id)
    
    # 创建导向基准
    benchmark = OrientationBenchmark(**benchmark_data)
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    
    # 预加载 rule_name
    benchmark.rule_name = rule.name
    
    return benchmark


@router.get("/{benchmark_id}", response_model=OrientationBenchmarkSchema)
def get_orientation_benchmark(
    benchmark_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取导向基准详情"""
    query = db.query(OrientationBenchmark).filter(OrientationBenchmark.id == benchmark_id)
    query = apply_hospital_filter(query, OrientationBenchmark, required=True)
    query = query.options(joinedload(OrientationBenchmark.rule))
    benchmark = query.first()
    if not benchmark:
        raise HTTPException(status_code=404, detail="导向基准不存在")
    
    # 预加载 rule_name
    benchmark.rule_name = benchmark.rule.name if benchmark.rule else None
    
    return benchmark


@router.put("/{benchmark_id}", response_model=OrientationBenchmarkSchema)
def update_orientation_benchmark(
    benchmark_id: int,
    benchmark_in: OrientationBenchmarkUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新导向基准"""
    query = db.query(OrientationBenchmark).filter(OrientationBenchmark.id == benchmark_id)
    query = apply_hospital_filter(query, OrientationBenchmark, required=True)
    benchmark = query.first()
    if not benchmark:
        raise HTTPException(status_code=404, detail="导向基准不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, benchmark)
    
    # 如果更新导向规则ID，验证新规则存在且类别正确
    if benchmark_in.rule_id and benchmark_in.rule_id != benchmark.rule_id:
        rule_query = db.query(OrientationRule).filter(OrientationRule.id == benchmark_in.rule_id)
        rule_query = apply_hospital_filter(rule_query, OrientationRule, required=True)
        rule = rule_query.first()
        if not rule:
            raise HTTPException(status_code=404, detail="导向规则不存在")
        
        if rule.category != OrientationCategory.benchmark_ladder:
            raise HTTPException(
                status_code=400,
                detail="只有'基准阶梯'类别的导向规则可以创建基准"
            )
    
    # 如果更新科室代码，检查是否与其他基准重复
    if benchmark_in.department_code and benchmark_in.department_code != benchmark.department_code:
        rule_id = benchmark_in.rule_id if benchmark_in.rule_id else benchmark.rule_id
        existing_query = db.query(OrientationBenchmark).filter(
            OrientationBenchmark.rule_id == rule_id,
            OrientationBenchmark.department_code == benchmark_in.department_code,
            OrientationBenchmark.id != benchmark_id
        )
        existing_query = apply_hospital_filter(existing_query, OrientationBenchmark, required=True)
        existing = existing_query.first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"该导向规则下科室'{benchmark_in.department_code}'的基准已存在"
            )
    
    # 更新字段
    update_data = benchmark_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(benchmark, field, value)
    
    db.commit()
    db.refresh(benchmark)
    
    # 预加载 rule_name
    db_rule = db.query(OrientationRule).filter(OrientationRule.id == benchmark.rule_id).first()
    benchmark.rule_name = db_rule.name if db_rule else None
    
    return benchmark


@router.delete("/{benchmark_id}")
def delete_orientation_benchmark(
    benchmark_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除导向基准"""
    query = db.query(OrientationBenchmark).filter(OrientationBenchmark.id == benchmark_id)
    query = apply_hospital_filter(query, OrientationBenchmark, required=True)
    benchmark = query.first()
    if not benchmark:
        raise HTTPException(status_code=404, detail="导向基准不存在")
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, benchmark)
    
    # 删除导向基准
    db.delete(benchmark)
    db.commit()
    
    return {"message": "导向基准删除成功"}
