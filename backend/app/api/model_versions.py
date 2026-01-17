"""
模型版本管理API
"""
from typing import Optional
from io import BytesIO
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.models.discipline_rule import DisciplineRule
from app.schemas.model_version import (
    ModelVersionCreate,
    ModelVersionUpdate,
    ModelVersionResponse,
    ModelVersionListResponse,
)
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)
from app.services.model_version_export_service import ModelVersionExportService

router = APIRouter()


# ==================== 模型版本导入相关API（必须在 /{version_id} 之前定义）====================

from app.models.hospital import Hospital
from app.models.calculation_workflow import CalculationWorkflow
from app.models.calculation_step import CalculationStep
from app.models.model_version_import import ModelVersionImport
from app.schemas.model_version import (
    ImportableVersionListResponse,
    ImportableVersionResponse,
    VersionPreviewResponse,
    ModelVersionImportRequest,
    ModelVersionImportResponse,
    ImportInfoResponse,
)
from app.services.model_version_import_service import ModelVersionImportService
from sqlalchemy import func, and_


@router.get("/importable", response_model=ImportableVersionListResponse)
def get_importable_versions(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取可导入的模型版本列表（所有医疗机构的版本，管理员可见）"""
    # 查询所有医疗机构的模型版本（管理员可以看到所有）
    query = db.query(
        ModelVersion,
        Hospital.name.label("hospital_name")
    ).join(
        Hospital, ModelVersion.hospital_id == Hospital.id
    )
    
    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ModelVersion.version.ilike(search_pattern)) |
            (ModelVersion.name.ilike(search_pattern)) |
            (Hospital.name.ilike(search_pattern))
        )
    
    # 按创建时间倒序排列
    query = query.order_by(ModelVersion.created_at.desc())
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    # 构造响应
    items = []
    for version, hospital_name in results:
        items.append(ImportableVersionResponse(
            id=version.id,
            version=version.version,
            name=version.name,
            description=version.description,
            hospital_id=version.hospital_id,
            hospital_name=hospital_name,
            created_at=version.created_at
        ))
    
    return {"total": total, "items": items}


@router.post("/import", response_model=ModelVersionImportResponse)
def import_version(
    request: ModelVersionImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导入模型版本"""
    # 获取当前医疗机构ID
    current_hospital_id = get_current_hospital_id_or_raise()
    
    # 验证导入类型
    if request.import_type not in ["structure_only", "with_workflows"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的导入类型"
        )
    
    # 创建导入服务并执行导入
    import_service = ModelVersionImportService(db)
    
    try:
        result = import_service.import_model_version(
            request=request,
            target_hospital_id=current_hospital_id,
            user_id=current_user.id
        )
        
        return ModelVersionImportResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


# ==================== 模型版本导出API ====================

@router.get("/export/{version_id}")
def export_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出模型版本结构到Excel"""
    # 验证版本是否存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 导出Excel
    export_service = ModelVersionExportService(db)
    excel_buffer = export_service.export_to_excel(version_id)
    
    # 构建文件名
    filename = f"评估模型_{version.name}_{version.version}.xlsx"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


# ==================== 基础模型版本管理API ====================

@router.get("", response_model=ModelVersionListResponse)
def get_model_versions(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型版本列表"""
    query = db.query(ModelVersion)
    
    # 应用医疗机构过滤
    query = apply_hospital_filter(query, ModelVersion, required=True)
    
    # 搜索过滤
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ModelVersion.version.ilike(search_pattern)) |
            (ModelVersion.name.ilike(search_pattern)) |
            (ModelVersion.description.ilike(search_pattern))
        )
    
    # 按创建时间倒序排列
    query = query.order_by(ModelVersion.created_at.desc())
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


@router.post("", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
def create_model_version(
    version_in: ModelVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建模型版本"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 检查版本号是否已存在（同一医疗机构内）
    query = db.query(ModelVersion).filter(ModelVersion.version == version_in.version)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    existing = query.first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="版本号已存在"
        )
    
    # 创建新版本
    db_version = ModelVersion(
        version=version_in.version,
        name=version_in.name,
        description=version_in.description,
        hospital_id=hospital_id,
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # 如果指定了基础版本，复制其结构
    if version_in.base_version_id:
        query = db.query(ModelVersion).filter(ModelVersion.id == version_in.base_version_id)
        query = apply_hospital_filter(query, ModelVersion, required=True)
        base_version = query.first()
        if not base_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="基础版本不存在"
            )
        
        # 验证基础版本属于当前医疗机构
        validate_hospital_access(db, base_version, hospital_id)
        
        # 复制节点结构
        _copy_nodes(db, base_version.id, db_version.id)
        
        # 复制学科规则
        _copy_discipline_rules(db, base_version.id, db_version.id, hospital_id)
    
    return db_version


@router.get("/{version_id}", response_model=ModelVersionResponse)
def get_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型版本详情"""
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    return version


@router.put("/{version_id}", response_model=ModelVersionResponse)
def update_model_version(
    version_id: int,
    version_in: ModelVersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型版本"""
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, version)
    
    # 更新字段
    if version_in.name is not None:
        version.name = version_in.name
    if version_in.description is not None:
        version.description = version_in.description
    
    db.commit()
    db.refresh(version)
    return version


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型版本"""
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, version)
    
    # 不允许删除激活的版本
    if version.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除激活的版本"
        )
    
    db.delete(version)
    db.commit()


@router.put("/{version_id}/activate", response_model=ModelVersionResponse)
def activate_model_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """激活模型版本"""
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 验证数据所属医疗机构
    validate_hospital_access(db, version)
    
    # 取消当前医疗机构其他版本的激活状态
    query = db.query(ModelVersion)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    query.update({"is_active": False}, synchronize_session=False)
    
    # 激活当前版本
    version.is_active = True
    db.commit()
    db.refresh(version)
    
    return version


def _copy_nodes(db: Session, source_version_id: int, target_version_id: int):
    """复制节点结构"""
    # 获取源版本的所有根节点
    source_nodes = db.query(ModelNode).filter(
        ModelNode.version_id == source_version_id,
        ModelNode.parent_id.is_(None)
    ).all()
    
    # 递归复制节点
    for node in source_nodes:
        _copy_node_recursive(db, node, target_version_id, None)
    
    db.commit()


def _copy_node_recursive(db: Session, source_node: ModelNode, target_version_id: int, target_parent_id: Optional[int]):
    """递归复制节点"""
    # 创建新节点
    new_node = ModelNode(
        version_id=target_version_id,
        parent_id=target_parent_id,
        sort_order=source_node.sort_order,
        name=source_node.name,
        code=source_node.code,
        node_type=source_node.node_type,
        is_leaf=source_node.is_leaf,
        calc_type=source_node.calc_type,
        weight=source_node.weight,
        unit=source_node.unit,
        business_guide=source_node.business_guide,
        script=source_node.script,
        rule=source_node.rule,
        orientation_rule_ids=source_node.orientation_rule_ids,  # 复制导向规则ID列表
    )
    db.add(new_node)
    db.flush()  # 获取新节点的ID
    
    # 递归复制子节点
    for child in source_node.children:
        _copy_node_recursive(db, child, target_version_id, new_node.id)


def _copy_discipline_rules(db: Session, source_version_id: int, target_version_id: int, hospital_id: int):
    """复制学科规则"""
    # 获取源版本的所有学科规则
    source_rules = db.query(DisciplineRule).filter(
        DisciplineRule.version_id == source_version_id,
        DisciplineRule.hospital_id == hospital_id
    ).all()
    
    # 复制每条规则
    for rule in source_rules:
        new_rule = DisciplineRule(
            hospital_id=hospital_id,
            version_id=target_version_id,
            department_code=rule.department_code,
            department_name=rule.department_name,
            dimension_code=rule.dimension_code,
            dimension_name=rule.dimension_name,
            rule_description=rule.rule_description,
            rule_coefficient=rule.rule_coefficient,
        )
        db.add(new_rule)
    
    db.commit()


# ==================== 版本详情相关API（带路径参数）====================

@router.get("/{version_id}/preview", response_model=VersionPreviewResponse)
def preview_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """预览模型版本详情（用于导入前查看）"""
    # 查询版本信息
    version_query = db.query(
        ModelVersion,
        Hospital.name.label("hospital_name")
    ).join(
        Hospital, ModelVersion.hospital_id == Hospital.id
    ).filter(
        ModelVersion.id == version_id
    )
    
    result = version_query.first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    version, hospital_name = result
    
    # 统计节点数量
    node_count = db.query(func.count(ModelNode.id)).filter(
        ModelNode.version_id == version_id
    ).scalar()
    
    # 统计计算流程数量
    workflow_count = db.query(func.count(CalculationWorkflow.id)).filter(
        CalculationWorkflow.version_id == version_id
    ).scalar()
    
    # 统计计算步骤数量
    step_count = db.query(func.count(CalculationStep.id)).join(
        CalculationWorkflow, CalculationStep.workflow_id == CalculationWorkflow.id
    ).filter(
        CalculationWorkflow.version_id == version_id
    ).scalar()
    
    return VersionPreviewResponse(
        id=version.id,
        version=version.version,
        name=version.name,
        description=version.description,
        hospital_name=hospital_name,
        node_count=node_count or 0,
        workflow_count=workflow_count or 0,
        step_count=step_count or 0,
        created_at=version.created_at
    )


@router.get("/{version_id}/import-info", response_model=ImportInfoResponse)
def get_import_info(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型版本的导入信息"""
    # 验证版本存在且属于当前医疗机构
    query = db.query(ModelVersion).filter(ModelVersion.id == version_id)
    query = apply_hospital_filter(query, ModelVersion, required=True)
    version = query.first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型版本不存在"
        )
    
    # 查询导入记录
    import_record = db.query(
        ModelVersionImport,
        ModelVersion.version.label("source_version"),
        Hospital.name.label("source_hospital_name"),
        User.username.label("importer_name")
    ).join(
        ModelVersion, ModelVersionImport.source_version_id == ModelVersion.id
    ).join(
        Hospital, ModelVersionImport.source_hospital_id == Hospital.id
    ).join(
        User, ModelVersionImport.imported_by == User.id
    ).filter(
        ModelVersionImport.target_version_id == version_id
    ).first()
    
    if not import_record:
        # 不是导入的版本
        return ImportInfoResponse(is_imported=False)
    
    record, source_version, source_hospital_name, importer_name = import_record
    
    return ImportInfoResponse(
        is_imported=True,
        source_version=source_version,
        source_hospital_name=source_hospital_name,
        import_type=record.import_type,
        import_time=record.import_time,
        importer_name=importer_name
    )
