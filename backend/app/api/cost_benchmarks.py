"""
成本基准管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc
from datetime import datetime
from urllib.parse import quote
import io

from app.utils.timezone import china_now

from app.api import deps
from app.models.cost_benchmark import CostBenchmark
from app.models.model_version import ModelVersion
from app.schemas.cost_benchmark import (
    CostBenchmark as CostBenchmarkSchema,
    CostBenchmarkCreate,
    CostBenchmarkUpdate,
    CostBenchmarkList,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)

router = APIRouter()


@router.get("/export")
def export_cost_benchmarks(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    version_id: Optional[int] = Query(None, description="按模型版本ID筛选"),
    department_code: Optional[str] = Query(None, description="按科室代码筛选"),
    dimension_code: Optional[str] = Query(None, description="按维度代码筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（科室名称或维度名称）"),
):
    """导出成本基准到Excel"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        
        query = db.query(CostBenchmark)
        
        # 应用医疗机构过滤
        query = apply_hospital_filter(query, CostBenchmark, required=True)
        
        # 应用筛选条件（与列表接口相同）
        if version_id:
            query = query.filter(CostBenchmark.version_id == version_id)
        
        if department_code:
            query = query.filter(CostBenchmark.department_code == department_code)
        
        if dimension_code:
            query = query.filter(CostBenchmark.dimension_code == dimension_code)
        
        if keyword:
            query = query.filter(
                or_(
                    CostBenchmark.department_name.contains(keyword),
                    CostBenchmark.dimension_name.contains(keyword)
                )
            )
        
        # 按创建时间倒序排序
        query = query.order_by(desc(CostBenchmark.created_at))
        
        # 获取所有数据
        benchmarks = query.all()
        
        # 检查是否有数据
        if not benchmarks:
            raise HTTPException(status_code=400, detail="没有可导出的数据，请先添加成本基准或调整筛选条件")
        
        # 为每个记录构建完整的维度路径显示
        from app.models.model_node import ModelNode
        for item in benchmarks:
            # 查询维度节点及其父节点和祖父节点
            dimension_node = db.query(
                ModelNode.name.label('dimension_name'),
                ModelNode.parent_id
            ).filter(
                ModelNode.code == item.dimension_code,
                ModelNode.version_id == item.version_id,
                ModelNode.node_type == 'dimension'
            ).first()
            
            if dimension_node and dimension_node.parent_id:
                # 获取父节点（成本）
                parent_node = db.query(
                    ModelNode.name.label('parent_name'),
                    ModelNode.parent_id
                ).filter(
                    ModelNode.id == dimension_node.parent_id
                ).first()
                
                if parent_node and parent_node.parent_id:
                    # 获取祖父节点（医生/护理/医技）
                    grandparent_node = db.query(
                        ModelNode.name.label('grandparent_name')
                    ).filter(
                        ModelNode.id == parent_node.parent_id
                    ).first()
                    
                    if grandparent_node:
                        # 构建完整路径：医生-成本-人员经费
                        item.dimension_name = f"{grandparent_node.grandparent_name}-{parent_node.parent_name}-{dimension_node.dimension_name}"
        
        # 创建Excel工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "成本基准"
        
        # 设置列标题
        headers = [
            "科室代码", "科室名称", "模型版本名称", "维度代码", 
            "维度名称", "基准值", "创建时间", "更新时间"
        ]
        ws.append(headers)
        
        # 设置标题行样式
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 写入数据
        for benchmark in benchmarks:
            ws.append([
                benchmark.department_code,
                benchmark.department_name,
                benchmark.version_name,
                benchmark.dimension_code,
                benchmark.dimension_name,
                float(benchmark.benchmark_value),  # Decimal转float
                benchmark.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                benchmark.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        # 设置列宽
        column_widths = [15, 20, 20, 15, 30, 12, 20, 20]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width
        
        # 保存到内存
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # 获取医院名称
        from app.models.hospital import Hospital
        from app.utils.hospital_filter import get_current_hospital_id_or_raise
        hospital_id = get_current_hospital_id_or_raise()
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        hospital_name = hospital.name if hospital else "未知医院"
        
        # 生成文件名（医院名称_成本基准_时间戳.xlsx）- 使用中国时间
        timestamp = china_now().strftime('%Y%m%d_%H%M%S')
        filename = f"{hospital_name}_成本基准_{timestamp}.xlsx"
        
        # 返回文件
        return Response(
            content=output.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出成本基准失败: {str(e)}")


@router.get("", response_model=CostBenchmarkList)
def get_cost_benchmarks(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=1000, description="每页数量"),
    version_id: Optional[int] = Query(None, description="按模型版本ID筛选"),
    department_code: Optional[str] = Query(None, description="按科室代码筛选"),
    dimension_code: Optional[str] = Query(None, description="按维度代码筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词（科室名称或维度名称）"),
):
    """获取成本基准列表"""
    try:
        query = db.query(CostBenchmark)
        
        # 应用医疗机构过滤
        query = apply_hospital_filter(query, CostBenchmark, required=True)
        
        # 按模型版本筛选
        if version_id:
            query = query.filter(CostBenchmark.version_id == version_id)
        
        # 按科室代码筛选
        if department_code:
            query = query.filter(CostBenchmark.department_code == department_code)
        
        # 按维度代码筛选
        if dimension_code:
            query = query.filter(CostBenchmark.dimension_code == dimension_code)
        
        # 关键词搜索（科室名称或维度名称）
        if keyword:
            query = query.filter(
                or_(
                    CostBenchmark.department_name.contains(keyword),
                    CostBenchmark.dimension_name.contains(keyword)
                )
            )
        
        # 预加载模型版本信息
        query = query.options(joinedload(CostBenchmark.version))
        
        # 按创建时间倒序排序
        query = query.order_by(desc(CostBenchmark.created_at))
        
        # 总数
        total = query.count()
        
        # 分页
        items = query.offset((page - 1) * size).limit(size).all()
        
        # 为每个记录构建完整的维度路径显示
        from app.models.model_node import ModelNode
        for item in items:
            # 查询维度节点及其父节点和祖父节点
            dimension_node = db.query(
                ModelNode.name.label('dimension_name'),
                ModelNode.parent_id
            ).filter(
                ModelNode.code == item.dimension_code,
                ModelNode.version_id == item.version_id,
                ModelNode.node_type == 'dimension'
            ).first()
            
            if dimension_node and dimension_node.parent_id:
                # 获取父节点（成本）
                parent_node = db.query(
                    ModelNode.name.label('parent_name'),
                    ModelNode.parent_id
                ).filter(
                    ModelNode.id == dimension_node.parent_id
                ).first()
                
                if parent_node and parent_node.parent_id:
                    # 获取祖父节点（医生/护理/医技）
                    grandparent_node = db.query(
                        ModelNode.name.label('grandparent_name')
                    ).filter(
                        ModelNode.id == parent_node.parent_id
                    ).first()
                    
                    if grandparent_node:
                        # 构建完整路径：医生-成本-人员经费
                        item.dimension_name = f"{grandparent_node.grandparent_name}-{parent_node.parent_name}-{dimension_node.dimension_name}"
        
        return CostBenchmarkList(total=total, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成本基准列表失败: {str(e)}")


@router.post("", response_model=CostBenchmarkSchema)
def create_cost_benchmark(
    benchmark_in: CostBenchmarkCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建成本基准"""
    try:
        # 获取当前医疗机构ID
        hospital_id = get_current_hospital_id_or_raise()
        
        # 验证必填字段
        if not benchmark_in.department_code:
            raise HTTPException(status_code=400, detail="科室代码不能为空")
        if not benchmark_in.department_name:
            raise HTTPException(status_code=400, detail="科室名称不能为空")
        if not benchmark_in.version_id:
            raise HTTPException(status_code=400, detail="模型版本不能为空")
        if not benchmark_in.version_name:
            raise HTTPException(status_code=400, detail="模型版本名称不能为空")
        if not benchmark_in.dimension_code:
            raise HTTPException(status_code=400, detail="维度代码不能为空")
        if not benchmark_in.dimension_name:
            raise HTTPException(status_code=400, detail="维度名称不能为空")
        if benchmark_in.benchmark_value is None:
            raise HTTPException(status_code=400, detail="基准值不能为空")
        
        # 验证基准值必须大于0
        if benchmark_in.benchmark_value <= 0:
            raise HTTPException(status_code=400, detail="基准值必须大于0")
        
        # 验证基准值范围
        if benchmark_in.benchmark_value > 999999999.99:
            raise HTTPException(status_code=400, detail="基准值不能超过999999999.99")
        
        # 验证模型版本存在且属于当前医疗机构
        version_query = db.query(ModelVersion).filter(ModelVersion.id == benchmark_in.version_id)
        version_query = apply_hospital_filter(version_query, ModelVersion, required=True)
        version = version_query.first()
        if not version:
            raise HTTPException(status_code=404, detail="模型版本不存在或不属于当前医疗机构")
        
        # 检查唯一性约束：同一医疗机构内，科室+版本+维度组合唯一
        existing_query = db.query(CostBenchmark).filter(
            CostBenchmark.department_code == benchmark_in.department_code,
            CostBenchmark.version_id == benchmark_in.version_id,
            CostBenchmark.dimension_code == benchmark_in.dimension_code
        )
        existing_query = apply_hospital_filter(existing_query, CostBenchmark, required=True)
        existing = existing_query.first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"该科室（{benchmark_in.department_name}）在模型版本（{benchmark_in.version_name}）下的维度（{benchmark_in.dimension_name}）成本基准已存在"
            )
        
        # 自动设置hospital_id
        benchmark_data = benchmark_in.model_dump()
        benchmark_data = set_hospital_id_for_create(benchmark_data, hospital_id)
        
        # 创建成本基准
        benchmark = CostBenchmark(**benchmark_data)
        db.add(benchmark)
        db.commit()
        db.refresh(benchmark)
        
        return benchmark
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建成本基准失败: {str(e)}")


@router.get("/{benchmark_id}", response_model=CostBenchmarkSchema)
def get_cost_benchmark(
    benchmark_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取成本基准详情"""
    try:
        query = db.query(CostBenchmark).filter(CostBenchmark.id == benchmark_id)
        query = apply_hospital_filter(query, CostBenchmark, required=True)
        query = query.options(joinedload(CostBenchmark.version))
        benchmark = query.first()
        if not benchmark:
            raise HTTPException(status_code=404, detail="成本基准不存在或不属于当前医疗机构")
        
        return benchmark
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取成本基准详情失败: {str(e)}")


@router.put("/{benchmark_id}", response_model=CostBenchmarkSchema)
def update_cost_benchmark(
    benchmark_id: int,
    benchmark_in: CostBenchmarkUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新成本基准"""
    try:
        query = db.query(CostBenchmark).filter(CostBenchmark.id == benchmark_id)
        query = apply_hospital_filter(query, CostBenchmark, required=True)
        benchmark = query.first()
        if not benchmark:
            raise HTTPException(status_code=404, detail="成本基准不存在或不属于当前医疗机构")
        
        # 验证数据所属医疗机构
        validate_hospital_access(db, benchmark)
        
        # 如果更新基准值，验证必须大于0
        if benchmark_in.benchmark_value is not None:
            if benchmark_in.benchmark_value <= 0:
                raise HTTPException(status_code=400, detail="基准值必须大于0")
            if benchmark_in.benchmark_value > 999999999.99:
                raise HTTPException(status_code=400, detail="基准值不能超过999999999.99")
        
        # 如果更新模型版本ID，验证新版本存在且属于当前医疗机构
        if benchmark_in.version_id and benchmark_in.version_id != benchmark.version_id:
            version_query = db.query(ModelVersion).filter(ModelVersion.id == benchmark_in.version_id)
            version_query = apply_hospital_filter(version_query, ModelVersion, required=True)
            version = version_query.first()
            if not version:
                raise HTTPException(status_code=404, detail="模型版本不存在或不属于当前医疗机构")
        
        # 检查更新后是否违反唯一性约束
        department_code = benchmark_in.department_code if benchmark_in.department_code else benchmark.department_code
        version_id = benchmark_in.version_id if benchmark_in.version_id else benchmark.version_id
        dimension_code = benchmark_in.dimension_code if benchmark_in.dimension_code else benchmark.dimension_code
        
        # 获取用于显示的名称
        department_name = benchmark_in.department_name if benchmark_in.department_name else benchmark.department_name
        version_name = benchmark_in.version_name if benchmark_in.version_name else benchmark.version_name
        dimension_name = benchmark_in.dimension_name if benchmark_in.dimension_name else benchmark.dimension_name
        
        existing_query = db.query(CostBenchmark).filter(
            CostBenchmark.department_code == department_code,
            CostBenchmark.version_id == version_id,
            CostBenchmark.dimension_code == dimension_code,
            CostBenchmark.id != benchmark_id
        )
        existing_query = apply_hospital_filter(existing_query, CostBenchmark, required=True)
        existing = existing_query.first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"该科室（{department_name}）在模型版本（{version_name}）下的维度（{dimension_name}）成本基准已存在"
            )
        
        # 更新字段
        update_data = benchmark_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(benchmark, field, value)
        
        db.commit()
        db.refresh(benchmark)
        
        return benchmark
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新成本基准失败: {str(e)}")


@router.delete("/{benchmark_id}")
def delete_cost_benchmark(
    benchmark_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除成本基准"""
    try:
        query = db.query(CostBenchmark).filter(CostBenchmark.id == benchmark_id)
        query = apply_hospital_filter(query, CostBenchmark, required=True)
        benchmark = query.first()
        if not benchmark:
            raise HTTPException(status_code=404, detail="成本基准不存在或不属于当前医疗机构")
        
        # 验证数据所属医疗机构
        validate_hospital_access(db, benchmark)
        
        # 删除成本基准
        db.delete(benchmark)
        db.commit()
        
        return {"message": "成本基准删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除成本基准失败: {str(e)}")
