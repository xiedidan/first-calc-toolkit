"""
维度目录管理API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.api import deps
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.charge_item import ChargeItem
from app.utils.hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
)
from app.schemas.dimension_item import (
    DimensionItemMapping as DimensionItemMappingSchema,
    DimensionItemMappingCreate,
    DimensionItemList,
    ChargeItem as ChargeItemSchema,
    SmartImportParseResponse,
    SmartImportFieldMapping,
    SmartImportExtractResponse,
    SmartImportPreviewRequest,
    SmartImportPreviewResponse,
    SmartImportExecuteRequest,
    SmartImportExecuteResponse,
)
from app.services.dimension_import_service import DimensionImportService

router = APIRouter()


@router.get("", response_model=DimensionItemList)
def get_dimension_items(
    dimension_code: Optional[str] = Query(None, description="维度节点编码（单个）"),
    dimension_codes: Optional[str] = Query(None, description="维度节点编码列表（逗号分隔）"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    orphans_only: bool = Query(False, description="仅显示无效记录（收费编码不在收费项目表中）"),
    no_dimension_only: bool = Query(False, description="仅显示无维度项目（维度记录不存在或找不到）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=10000, description="每页数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取维度的收费项目目录"""
    from app.models.model_node import ModelNode
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取当前激活的模型版本ID
    from app.models.model_version import ModelVersion
    active_version = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    ).first()
    
    query = db.query(
        DimensionItemMapping.id,
        DimensionItemMapping.dimension_code,
        DimensionItemMapping.item_code,
        DimensionItemMapping.created_at,
        ChargeItem.item_name,
        ChargeItem.item_category,
        ModelNode.name.label('dimension_name')
    ).filter(
        DimensionItemMapping.hospital_id == hospital_id  # 医院隔离
    ).outerjoin(  # 使用LEFT JOIN，即使收费项目不存在也显示
        ChargeItem,
        and_(
            DimensionItemMapping.item_code == ChargeItem.item_code,
            ChargeItem.hospital_id == hospital_id  # 收费项目也要医院隔离
        )
    ).outerjoin(  # LEFT JOIN维度节点表获取维度名称，限定为当前激活版本
        ModelNode,
        and_(
            DimensionItemMapping.dimension_code == ModelNode.code,
            ModelNode.version_id == active_version.id if active_version else None
        )
    )
    
    # 如果指定了维度编码，则过滤（支持单个或多个）
    if dimension_codes:
        # 多个维度编码（逗号分隔）
        code_list = [code.strip() for code in dimension_codes.split(',') if code.strip()]
        if code_list:
            query = query.filter(DimensionItemMapping.dimension_code.in_(code_list))
    elif dimension_code is not None:
        # 单个维度编码（向后兼容）
        query = query.filter(DimensionItemMapping.dimension_code == dimension_code)
    
    # 如果只显示无效记录（收费编码不在收费项目表中）
    if orphans_only:
        query = query.filter(ChargeItem.item_code.is_(None))
    
    # 如果只显示无维度项目（维度记录不存在或找不到）
    if no_dimension_only:
        query = query.filter(
            or_(
                DimensionItemMapping.dimension_code.is_(None),
                DimensionItemMapping.dimension_code == '',
                ModelNode.id.is_(None)  # 维度code存在但找不到对应的ModelNode记录
            )
        )
    
    # 关键词搜索 - 修复：支持搜索item_code，即使ChargeItem不存在
    # 使用coalesce处理NULL值，或者分别检查每个字段
    if keyword:
        query = query.filter(
            or_(
                DimensionItemMapping.item_code.contains(keyword),  # 使用DimensionItemMapping的item_code
                # 使用and_确保只在字段不为NULL时才搜索
                (ChargeItem.item_name.isnot(None)) & (ChargeItem.item_name.contains(keyword)),
                (ChargeItem.item_category.isnot(None)) & (ChargeItem.item_category.contains(keyword)),
            )
        )
    
    # 总数
    total = query.count()
    
    # 分页
    results = query.offset((page - 1) * size).limit(size).all()
    
    # 构建完整的维度路径
    def build_dimension_path(dimension_code: str) -> str:
        """通过code构建维度的完整路径"""
        if not dimension_code:
            return ""
        
        node = db.query(ModelNode).filter(ModelNode.code == dimension_code).first()
        if not node:
            return ""
        
        path_parts = [node.name]
        current = node
        
        while current.parent_id:
            parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
            if parent:
                path_parts.insert(0, parent.name)
                current = parent
            else:
                break
        
        return " - ".join(path_parts)
    
    # 转换为Schema
    items = [
        DimensionItemMappingSchema(
            dimension_code=r.dimension_code,
            item_code=r.item_code,
            id=r.id,
            item_name=r.item_name if r.item_name else None,
            item_category=r.item_category if r.item_category else None,
            dimension_name=build_dimension_path(r.dimension_code) if r.dimension_code else None,
            created_at=r.created_at
        )
        for r in results
    ]
    
    return DimensionItemList(total=total, items=items)


@router.post("", response_model=dict)
def create_dimension_items(
    mapping_in: DimensionItemMappingCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """为维度添加收费项目"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    added_count = 0
    skipped_count = 0
    
    for item_code in mapping_in.item_codes:
        # 检查收费项目是否存在（且属于当前医疗机构）
        charge_item = db.query(ChargeItem).filter(
            ChargeItem.item_code == item_code,
            ChargeItem.hospital_id == hospital_id
        ).first()
        if not charge_item:
            skipped_count += 1
            continue
        
        # 检查是否已经关联（在当前医疗机构内）
        existing = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.hospital_id == hospital_id,
            DimensionItemMapping.dimension_code == mapping_in.dimension_code,
            DimensionItemMapping.item_code == item_code
        ).first()
        if existing:
            skipped_count += 1
            continue
        
        # 创建映射（设置hospital_id）
        mapping = DimensionItemMapping(
            hospital_id=hospital_id,
            dimension_code=mapping_in.dimension_code,
            item_code=item_code
        )
        db.add(mapping)
        added_count += 1
    
    db.commit()
    
    return {
        "message": f"成功添加 {added_count} 个项目，跳过 {skipped_count} 个项目",
        "added_count": added_count,
        "skipped_count": skipped_count
    }


@router.delete("/dimension/{dimension_code}/clear-all")
def clear_all_dimension_items(
    dimension_code: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空指定维度的所有收费项目"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 只删除当前医疗机构的映射
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        DimensionItemMapping.dimension_code == dimension_code
    ).delete()
    
    db.commit()
    
    return {
        "message": f"已清空维度 {dimension_code} 的所有项目",
        "deleted_count": deleted_count
    }


@router.delete("/clear-all")
def clear_all_dimension_items_for_hospital(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清空当前医院的所有维度目录数据"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 删除当前医疗机构的所有维度目录映射
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id
    ).delete()
    
    db.commit()
    
    return {
        "message": f"已清空当前医院的所有维度目录数据",
        "deleted_count": deleted_count
    }


@router.delete("/orphans/clear-all")
def clear_all_orphan_items(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清除所有无效记录（收费编码不在收费项目表中的记录）"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询当前医疗机构的所有孤儿记录的ID
    orphan_ids = db.query(DimensionItemMapping.id).outerjoin(
        ChargeItem,
        and_(
            DimensionItemMapping.item_code == ChargeItem.item_code,
            ChargeItem.hospital_id == hospital_id
        )
    ).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        ChargeItem.item_code.is_(None)
    ).all()
    
    orphan_ids = [id[0] for id in orphan_ids]
    
    if not orphan_ids:
        return {
            "message": "没有找到无效记录",
            "deleted_count": 0
        }
    
    # 删除这些记录
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id.in_(orphan_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"已清除所有无效记录",
        "deleted_count": deleted_count
    }


@router.delete("/no-dimension/clear-all")
def clear_all_no_dimension_items(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清除所有无维度项目（维度记录不存在或找不到的记录）"""
    from app.models.model_node import ModelNode
    from app.models.model_version import ModelVersion
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取当前激活的模型版本ID
    active_version = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    ).first()
    
    # 查询当前医疗机构的所有无维度项目的ID
    no_dimension_ids = db.query(DimensionItemMapping.id).outerjoin(
        ModelNode,
        and_(
            DimensionItemMapping.dimension_code == ModelNode.code,
            ModelNode.version_id == active_version.id if active_version else None
        )
    ).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        or_(
            DimensionItemMapping.dimension_code.is_(None),
            DimensionItemMapping.dimension_code == '',
            ModelNode.id.is_(None)
        )
    ).all()
    
    no_dimension_ids = [id[0] for id in no_dimension_ids]
    
    if not no_dimension_ids:
        return {
            "message": "没有找到无维度项目",
            "deleted_count": 0
        }
    
    # 删除这些记录
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id.in_(no_dimension_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"已清除所有无维度项目",
        "deleted_count": deleted_count
    }


@router.delete("/filtered/clear-all")
def clear_filtered_items(
    dimension_codes: Optional[str] = Query(None, description="维度节点编码列表（逗号分隔）"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清除当前筛选条件下的所有项目"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 构建查询
    query = db.query(DimensionItemMapping.id).filter(
        DimensionItemMapping.hospital_id == hospital_id
    )
    
    # 如果指定了维度编码，则过滤
    if dimension_codes:
        code_list = [code.strip() for code in dimension_codes.split(',') if code.strip()]
        if code_list:
            query = query.filter(DimensionItemMapping.dimension_code.in_(code_list))
    
    # 关键词搜索
    if keyword:
        query = query.outerjoin(
            ChargeItem,
            and_(
                DimensionItemMapping.item_code == ChargeItem.item_code,
                ChargeItem.hospital_id == hospital_id
            )
        ).filter(
            or_(
                DimensionItemMapping.item_code.contains(keyword),
                (ChargeItem.item_name.isnot(None)) & (ChargeItem.item_name.contains(keyword)),
                (ChargeItem.item_category.isnot(None)) & (ChargeItem.item_category.contains(keyword)),
            )
        )
    
    # 获取要删除的ID列表
    ids_to_delete = [id[0] for id in query.all()]
    
    if not ids_to_delete:
        return {
            "message": "没有找到符合条件的记录",
            "deleted_count": 0
        }
    
    # 删除这些记录
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id.in_(ids_to_delete)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"已清除筛选项目",
        "deleted_count": deleted_count
    }


@router.get("/duplicates", response_model=DimensionItemList)
def get_duplicate_items(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=10000, description="每页数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取重复记录（同一项目在同一父级维度下出现多次）
    
    重复的定义：同一个收费项目(item_code)在同一个父级维度(parent_id)下的多个末级维度中出现
    例如：某手术项目在"医生-手术-门诊"和"医生-手术-住院"下都出现，则都是重复记录
    """
    from app.models.model_node import ModelNode
    from app.models.model_version import ModelVersion
    from sqlalchemy import func, text
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取当前激活的模型版本ID
    active_version = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    ).first()
    
    if not active_version:
        return DimensionItemList(total=0, items=[])
    
    # 使用原生SQL查询重复记录
    # 逻辑：找出同一个item_code在同一个parent_id下出现多次的记录
    duplicate_sql = text("""
        WITH item_parent AS (
            -- 获取每个映射记录对应的维度的父节点ID
            SELECT 
                dim.id,
                dim.dimension_code,
                dim.item_code,
                mn.parent_id
            FROM dimension_item_mappings dim
            JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = :version_id
            WHERE dim.hospital_id = :hospital_id
        ),
        duplicate_groups AS (
            -- 找出在同一父节点下出现多次的item_code
            SELECT item_code, parent_id
            FROM item_parent
            GROUP BY item_code, parent_id
            HAVING COUNT(*) > 1
        )
        -- 返回所有重复记录的ID
        SELECT ip.id
        FROM item_parent ip
        JOIN duplicate_groups dg ON ip.item_code = dg.item_code AND ip.parent_id = dg.parent_id
        ORDER BY ip.item_code, ip.parent_id
    """)
    
    result = db.execute(duplicate_sql, {
        "hospital_id": hospital_id,
        "version_id": active_version.id
    })
    duplicate_ids = [row[0] for row in result.fetchall()]
    
    if not duplicate_ids:
        return DimensionItemList(total=0, items=[])
    
    # 查询这些重复记录的详细信息
    query = db.query(
        DimensionItemMapping.id,
        DimensionItemMapping.dimension_code,
        DimensionItemMapping.item_code,
        DimensionItemMapping.created_at,
        ChargeItem.item_name,
        ChargeItem.item_category,
        ModelNode.name.label('dimension_name')
    ).filter(
        DimensionItemMapping.id.in_(duplicate_ids)
    ).outerjoin(
        ChargeItem,
        and_(
            DimensionItemMapping.item_code == ChargeItem.item_code,
            ChargeItem.hospital_id == hospital_id
        )
    ).outerjoin(
        ModelNode,
        and_(
            DimensionItemMapping.dimension_code == ModelNode.code,
            ModelNode.version_id == active_version.id
        )
    ).order_by(DimensionItemMapping.item_code, ModelNode.parent_id)
    
    # 总数
    total = len(duplicate_ids)
    
    # 分页
    results = query.offset((page - 1) * size).limit(size).all()
    
    # 构建完整的维度路径
    def build_dimension_path(dimension_code: str) -> str:
        if not dimension_code:
            return ""
        
        node = db.query(ModelNode).filter(
            ModelNode.code == dimension_code,
            ModelNode.version_id == active_version.id
        ).first()
        if not node:
            return ""
        
        path_parts = [node.name]
        current = node
        
        while current.parent_id:
            parent = db.query(ModelNode).filter(ModelNode.id == current.parent_id).first()
            if parent:
                path_parts.insert(0, parent.name)
                current = parent
            else:
                break
        
        return " - ".join(path_parts)
    
    # 转换为Schema
    items = [
        DimensionItemMappingSchema(
            dimension_code=r.dimension_code,
            item_code=r.item_code,
            id=r.id,
            item_name=r.item_name if r.item_name else None,
            item_category=r.item_category if r.item_category else None,
            dimension_name=build_dimension_path(r.dimension_code) if r.dimension_code else None,
            created_at=r.created_at
        )
        for r in results
    ]
    
    return DimensionItemList(total=total, items=items)


@router.delete("/duplicates/clear-all")
def clear_all_duplicate_items(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """清除所有重复记录"""
    from app.models.model_node import ModelNode
    from app.models.model_version import ModelVersion
    from sqlalchemy import text
    
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 获取当前激活的模型版本ID
    active_version = db.query(ModelVersion).filter(
        ModelVersion.hospital_id == hospital_id,
        ModelVersion.is_active == True
    ).first()
    
    if not active_version:
        return {
            "message": "没有找到激活的模型版本",
            "deleted_count": 0
        }
    
    # 查询重复记录的ID
    duplicate_sql = text("""
        WITH item_parent AS (
            SELECT 
                dim.id,
                dim.dimension_code,
                dim.item_code,
                mn.parent_id
            FROM dimension_item_mappings dim
            JOIN model_nodes mn ON dim.dimension_code = mn.code AND mn.version_id = :version_id
            WHERE dim.hospital_id = :hospital_id
        ),
        duplicate_groups AS (
            SELECT item_code, parent_id
            FROM item_parent
            GROUP BY item_code, parent_id
            HAVING COUNT(*) > 1
        )
        SELECT ip.id
        FROM item_parent ip
        JOIN duplicate_groups dg ON ip.item_code = dg.item_code AND ip.parent_id = dg.parent_id
    """)
    
    result = db.execute(duplicate_sql, {
        "hospital_id": hospital_id,
        "version_id": active_version.id
    })
    duplicate_ids = [row[0] for row in result.fetchall()]
    
    if not duplicate_ids:
        return {
            "message": "没有找到重复记录",
            "deleted_count": 0
        }
    
    # 删除这些记录
    deleted_count = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id.in_(duplicate_ids)
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"已清除所有重复记录",
        "deleted_count": deleted_count
    }


@router.get("/charge-items/search", response_model=list[ChargeItemSchema])
def search_charge_items(
    keyword: str = Query(..., description="搜索关键词"),
    dimension_code: Optional[str] = Query(None, description="排除已关联的维度编码"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """搜索收费项目（用于添加时搜索）"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 只搜索当前医疗机构的收费项目
    query = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == hospital_id,
        or_(
            ChargeItem.item_code.contains(keyword),
            ChargeItem.item_name.contains(keyword),
            ChargeItem.item_category.contains(keyword),
        )
    )
    
    # 如果指定了维度编码，排除已关联的项目（在当前医疗机构内）
    if dimension_code:
        linked_codes = db.query(DimensionItemMapping.item_code).filter(
            DimensionItemMapping.hospital_id == hospital_id,
            DimensionItemMapping.dimension_code == dimension_code
        ).all()
        linked_codes = [code[0] for code in linked_codes]
        if linked_codes:
            query = query.filter(~ChargeItem.item_code.in_(linked_codes))
    
    items = query.limit(limit).all()
    return items


# 通配路由必须放在具体路径之后

@router.put("/{mapping_id}")
def update_dimension_item(
    mapping_id: int,
    new_dimension_code: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新收费项目的维度"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询映射关系（必须属于当前医疗机构）
    mapping = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id == mapping_id,
        DimensionItemMapping.hospital_id == hospital_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="映射关系不存在")
    
    # 检查新维度是否存在
    from app.models.model_node import ModelNode
    new_dimension = db.query(ModelNode).filter(ModelNode.code == new_dimension_code).first()
    if not new_dimension:
        raise HTTPException(status_code=404, detail="目标维度不存在")
    
    # 检查新的映射关系是否已存在（在当前医疗机构内）
    existing = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id,
        DimensionItemMapping.dimension_code == new_dimension_code,
        DimensionItemMapping.item_code == mapping.item_code,
        DimensionItemMapping.id != mapping_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该收费项目已存在于目标维度中")
    
    # 更新维度
    mapping.dimension_code = new_dimension_code
    db.commit()
    
    return {"message": "更新成功"}


@router.delete("/{mapping_id}")
def delete_dimension_item(
    mapping_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除维度关联的收费项目"""
    # 获取当前医疗机构ID
    hospital_id = get_current_hospital_id_or_raise()
    
    # 查询映射关系（必须属于当前医疗机构）
    mapping = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.id == mapping_id,
        DimensionItemMapping.hospital_id == hospital_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="映射关系不存在")
    
    db.delete(mapping)
    db.commit()
    
    return {"message": "删除成功"}


# 智能导入相关接口

@router.post("/smart-import/parse", response_model=SmartImportParseResponse)
async def smart_import_parse(
    file: UploadFile = File(..., description="Excel文件"),
    sheet_name: Optional[str] = Query(None, description="工作表名称"),
    skip_rows: int = Query(0, ge=0, description="跳过前N行"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第一步：解析Excel文件，返回列名和预览数据"""
    # 读取文件内容
    file_content = await file.read()
    
    try:
        result = DimensionImportService.parse_excel(file_content, sheet_name, skip_rows)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文件失败: {str(e)}")


@router.post("/smart-import/extract-values", response_model=SmartImportExtractResponse)
def smart_import_extract_values(
    request: SmartImportFieldMapping,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第二步：提取维度预案和专家意见的唯一值，并提供智能匹配建议"""
    try:
        result = DimensionImportService.extract_unique_values(
            session_id=request.session_id,
            field_mapping=request.field_mapping,
            model_version_id=request.model_version_id,
            db=db,
            match_by=request.match_by
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取唯一值失败: {str(e)}")


@router.post("/smart-import/preview", response_model=SmartImportPreviewResponse)
def smart_import_preview(
    request: SmartImportPreviewRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """第三步：生成导入预览"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== Smart Import Preview Request ===")
    logger.info(f"Session ID: {request.session_id}")
    logger.info(f"Value mapping count: {len(request.value_mapping)}")
    
    # 获取当前医疗机构ID
    try:
        hospital_id = get_current_hospital_id_or_raise()
        logger.info(f"Hospital ID: {hospital_id}")
    except Exception as e:
        logger.error(f"Failed to get hospital ID: {e}")
        raise
    
    # 打印每个映射的详细信息
    for i, mapping in enumerate(request.value_mapping):
        logger.info(f"Mapping {i}: value='{mapping.value}', source='{mapping.source}', codes={mapping.dimension_codes}")
    
    try:
        result = DimensionImportService.generate_preview(
            session_id=request.session_id,
            value_mapping=request.value_mapping,
            db=db,
            hospital_id=hospital_id
        )
        logger.info(f"Preview generated successfully: {len(result['preview_items'])} items")
        return result
    except ValueError as e:
        logger.error(f"ValueError in generate_preview: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Exception in generate_preview: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"生成预览失败: {str(e)}")


@router.post("/smart-import/execute", response_model=SmartImportExecuteResponse)
def smart_import_execute(
    request: SmartImportExecuteRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """执行导入"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"=== Smart Import Execute Request ===")
    logger.info(f"Session ID: {request.session_id}")
    logger.info(f"Confirmed items: {len(request.confirmed_items) if request.confirmed_items else 'None (use all)'}")
    
    # 获取当前医疗机构ID
    try:
        hospital_id = get_current_hospital_id_or_raise()
        logger.info(f"Hospital ID: {hospital_id}")
    except Exception as e:
        logger.error(f"Failed to get hospital ID: {e}")
        raise
    
    try:
        result = DimensionImportService.execute_import(
            session_id=request.session_id,
            confirmed_items=request.confirmed_items,
            db=db,
            hospital_id=hospital_id
        )
        logger.info(f"Import executed successfully: {result['report']['success_count']} items")
        return result
    except ValueError as e:
        logger.error(f"ValueError in execute_import: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Exception in execute_import: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"执行导入失败: {str(e)}")
