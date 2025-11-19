"""
数据模板管理API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from decimal import Decimal

from app.api import deps
from app.models.data_template import DataTemplate
from app.models.hospital import Hospital
from app.schemas.data_template import (
    DataTemplate as DataTemplateSchema,
    DataTemplateCreate,
    DataTemplateUpdate,
    DataTemplateList,
    FileUploadResponse,
    BatchUploadPreview,
    BatchUploadResult,
    CopyTemplateRequest,
    CopyResult,
    HospitalSimple,
    ExportTemplateRequest,
)
from app.services.data_template_file_service import DataTemplateFileService
from app.services.data_template_batch_service import DataTemplateBatchService

router = APIRouter()


@router.get("", response_model=DataTemplateList)
def get_data_templates(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（表名、中文名、说明）"),
    is_core: Optional[bool] = Query(None, description="是否核心表筛选"),
    has_definition: Optional[bool] = Query(None, description="是否已上传表定义文档"),
    has_sql: Optional[bool] = Query(None, description="是否已上传SQL建表代码"),
    sort_by: Optional[str] = Query("sort_order", description="排序字段"),
    sort_order: Optional[str] = Query("asc", description="排序方向"),
):
    """获取数据模板列表"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                DataTemplate.table_name.contains(keyword),
                DataTemplate.table_name_cn.contains(keyword),
                DataTemplate.description.contains(keyword),
            )
        )
    
    # 核心表筛选
    if is_core is not None:
        query = query.filter(DataTemplate.is_core == is_core)
    
    # 文档状态筛选
    if has_definition is not None:
        if has_definition:
            query = query.filter(DataTemplate.definition_file_path.isnot(None))
        else:
            query = query.filter(DataTemplate.definition_file_path.is_(None))
    
    if has_sql is not None:
        if has_sql:
            query = query.filter(DataTemplate.sql_file_path.isnot(None))
        else:
            query = query.filter(DataTemplate.sql_file_path.is_(None))
    
    # 排序
    sort_column = getattr(DataTemplate, sort_by, DataTemplate.sort_order)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    
    # 转换为Schema对象
    schema_items = [DataTemplateSchema.from_orm(item) for item in items]
    
    return DataTemplateList(total=total, items=schema_items)


@router.post("", response_model=DataTemplateSchema)
def create_data_template(
    template_in: DataTemplateCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """创建数据模板"""
    from app.utils.hospital_filter import get_user_hospital_id
    
    hospital_id = get_user_hospital_id(current_user)
    
    # 检查表名是否已存在（同一医疗机构内）
    existing = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == hospital_id,
        DataTemplate.table_name == template_in.table_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="表名已存在")
    
    # 如果未提供排序序号，自动设置为最大值+1
    if template_in.sort_order is None:
        max_sort_order = db.query(func.max(DataTemplate.sort_order)).filter(
            DataTemplate.hospital_id == hospital_id
        ).scalar()
        sort_order = Decimal(max_sort_order or 0) + Decimal("1.0")
    else:
        sort_order = template_in.sort_order
    
    # 创建数据模板
    template_data = template_in.model_dump(exclude={'sort_order'})
    template_data['hospital_id'] = hospital_id
    template_data['sort_order'] = sort_order
    template = DataTemplate(**template_data)
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return DataTemplateSchema.from_orm(template)


@router.get("/{id}", response_model=DataTemplateSchema)
def get_data_template(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取数据模板详情"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    return DataTemplateSchema.from_orm(template)


@router.put("/{id}", response_model=DataTemplateSchema)
def update_data_template(
    id: int,
    template_in: DataTemplateUpdate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """更新数据模板"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    # 更新字段
    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return DataTemplateSchema.from_orm(template)


@router.delete("/clear-all")
def clear_all_templates(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除当前医院的所有数据模板"""
    from app.utils.hospital_filter import get_user_hospital_id
    import shutil
    from pathlib import Path
    
    hospital_id = get_user_hospital_id(current_user)
    
    # 查询所有数据模板
    templates = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == hospital_id
    ).all()
    
    deleted_count = len(templates)
    
    # 删除所有数据库记录
    for template in templates:
        db.delete(template)
    
    db.commit()
    
    # 删除整个医院的文件目录
    hospital_dir = Path(DataTemplateFileService.BASE_UPLOAD_DIR) / str(hospital_id)
    if hospital_dir.exists():
        try:
            shutil.rmtree(hospital_dir)
        except Exception as e:
            print(f"删除文件目录失败: {hospital_dir}, 错误: {str(e)}")
    
    return {
        "message": "删除成功",
        "deleted_count": deleted_count
    }


@router.delete("/{id}")
def delete_data_template(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """删除数据模板"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    # 删除关联的文件
    DataTemplateFileService.delete_file(template.definition_file_path)
    DataTemplateFileService.delete_file(template.sql_file_path)
    
    # 删除数据库记录
    db.delete(template)
    db.commit()
    
    return {"message": "删除成功"}



@router.post("/{id}/upload-definition", response_model=FileUploadResponse)
async def upload_definition_file(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """上传表定义文档"""
    from app.utils.hospital_filter import apply_hospital_filter, get_user_hospital_id
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    hospital_id = get_user_hospital_id(current_user)
    
    # 删除旧文件
    if template.definition_file_path:
        DataTemplateFileService.delete_file(template.definition_file_path)
    
    # 保存新文件
    file_path, file_name = await DataTemplateFileService.save_file(
        file, hospital_id, "definition"
    )
    
    # 更新数据库记录
    template.definition_file_path = file_path
    template.definition_file_name = file_name
    db.commit()
    
    return FileUploadResponse(
        success=True,
        message="上传成功",
        file_name=file_name,
        file_path=file_path
    )


@router.post("/{id}/upload-sql", response_model=FileUploadResponse)
async def upload_sql_file(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """上传SQL建表代码"""
    from app.utils.hospital_filter import apply_hospital_filter, get_user_hospital_id
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    hospital_id = get_user_hospital_id(current_user)
    
    # 删除旧文件
    if template.sql_file_path:
        DataTemplateFileService.delete_file(template.sql_file_path)
    
    # 保存新文件
    file_path, file_name = await DataTemplateFileService.save_file(
        file, hospital_id, "sql"
    )
    
    # 更新数据库记录
    template.sql_file_path = file_path
    template.sql_file_name = file_name
    db.commit()
    
    return FileUploadResponse(
        success=True,
        message="上传成功",
        file_name=file_name,
        file_path=file_path
    )


@router.get("/{id}/definition-content")
def get_definition_content(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取表定义文档内容"""
    from app.utils.hospital_filter import apply_hospital_filter
    from fastapi.responses import PlainTextResponse
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    if not template.definition_file_path:
        raise HTTPException(status_code=404, detail="表定义文档不存在")
    
    file_path = DataTemplateFileService.get_file_path(template.definition_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return PlainTextResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.get("/{id}/download-definition")
def download_definition_file(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """下载表定义文档"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    if not template.definition_file_path:
        raise HTTPException(status_code=404, detail="表定义文档不存在")
    
    file_path = DataTemplateFileService.get_file_path(template.definition_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=template.definition_file_name,
        media_type="application/octet-stream"
    )


@router.get("/{id}/sql-content")
def get_sql_content(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取SQL文件内容"""
    from app.utils.hospital_filter import apply_hospital_filter
    from fastapi.responses import PlainTextResponse
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    if not template.sql_file_path:
        raise HTTPException(status_code=404, detail="SQL建表代码不存在")
    
    file_path = DataTemplateFileService.get_file_path(template.sql_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return PlainTextResponse(content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.get("/{id}/download-sql")
def download_sql_file(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """下载SQL建表代码"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    if not template.sql_file_path:
        raise HTTPException(status_code=404, detail="SQL建表代码不存在")
    
    file_path = DataTemplateFileService.get_file_path(template.sql_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=template.sql_file_name,
        media_type="application/octet-stream"
    )



@router.post("/batch-upload", response_model=BatchUploadResult)
async def batch_upload_files(
    definition_files: List[UploadFile] = File(default=[]),
    sql_files: List[UploadFile] = File(default=[]),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """批量上传文件"""
    from app.utils.hospital_filter import get_user_hospital_id
    
    hospital_id = get_user_hospital_id(current_user)
    
    # 匹配文件
    matched_data = DataTemplateBatchService.match_files(definition_files, sql_files)
    
    # 创建或更新数据模板
    result = await DataTemplateBatchService.create_or_update_templates(
        db, hospital_id, matched_data
    )
    
    return result


@router.post("/batch-upload/preview", response_model=BatchUploadPreview)
async def preview_batch_upload(
    definition_files: List[UploadFile] = File(default=[]),
    sql_files: List[UploadFile] = File(default=[]),
):
    """预览批量上传结果"""
    # 匹配文件
    matched_data = DataTemplateBatchService.match_files(definition_files, sql_files)
    
    # 生成预览
    preview = DataTemplateBatchService.generate_preview(matched_data)
    
    return preview


@router.post("/{id}/move-up")
def move_up(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """上移数据模板"""
    from app.utils.hospital_filter import apply_hospital_filter, get_user_hospital_id
    
    hospital_id = get_user_hospital_id(current_user)
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    # 查找上一条记录
    prev_template = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == hospital_id,
        DataTemplate.sort_order < template.sort_order
    ).order_by(desc(DataTemplate.sort_order)).first()
    
    if not prev_template:
        raise HTTPException(status_code=400, detail="已经是第一条")
    
    # 交换排序序号
    template.sort_order, prev_template.sort_order = prev_template.sort_order, template.sort_order
    db.commit()
    
    return {"message": "上移成功"}


@router.post("/{id}/move-down")
def move_down(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """下移数据模板"""
    from app.utils.hospital_filter import apply_hospital_filter, get_user_hospital_id
    
    hospital_id = get_user_hospital_id(current_user)
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    # 查找下一条记录
    next_template = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == hospital_id,
        DataTemplate.sort_order > template.sort_order
    ).order_by(asc(DataTemplate.sort_order)).first()
    
    if not next_template:
        raise HTTPException(status_code=400, detail="已经是最后一条")
    
    # 交换排序序号
    template.sort_order, next_template.sort_order = next_template.sort_order, template.sort_order
    db.commit()
    
    return {"message": "下移成功"}


@router.put("/{id}/toggle-core")
def toggle_core(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """切换核心标志"""
    from app.utils.hospital_filter import apply_hospital_filter
    
    query = db.query(DataTemplate).filter(DataTemplate.id == id)
    query = apply_hospital_filter(query, DataTemplate, current_user)
    template = query.first()
    
    if not template:
        raise HTTPException(status_code=404, detail="数据模板不存在")
    
    # 切换核心标志
    template.is_core = not template.is_core
    db.commit()
    
    return {"is_core": template.is_core, "message": "切换成功"}


@router.get("/hospitals/list", response_model=List[HospitalSimple])
def get_hospitals_for_copy(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取其他医疗机构列表（用于复制）"""
    from app.utils.hospital_filter import get_user_hospital_id
    
    current_hospital_id = get_user_hospital_id(current_user)
    
    # 查询其他医疗机构
    hospitals = db.query(Hospital).filter(
        Hospital.id != current_hospital_id,
        Hospital.is_active == True
    ).all()
    
    return hospitals


@router.get("/hospitals/{hospital_id}/templates", response_model=List[DataTemplateSchema])
def get_hospital_templates(
    hospital_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """获取指定医疗机构的数据模板列表（用于复制）"""
    # 验证医疗机构存在
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="医疗机构不存在")
    
    # 查询数据模板
    templates = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == hospital_id
    ).order_by(DataTemplate.sort_order).all()
    
    return [DataTemplateSchema.from_orm(t) for t in templates]


@router.post("/export")
async def export_templates(
    request: ExportTemplateRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """导出数据模板为Markdown文档"""
    from fastapi.responses import Response
    from app.utils.hospital_filter import apply_hospital_filter
    import os
    from datetime import datetime
    
    # 查询数据模板
    query = db.query(DataTemplate).filter(DataTemplate.id.in_(request.template_ids))
    query = apply_hospital_filter(query, DataTemplate, current_user)
    templates = query.order_by(DataTemplate.sort_order).all()
    
    if not templates:
        raise HTTPException(status_code=404, detail="未找到数据模板")
    
    # 生成Markdown文档
    md_content = f"# 数据模板文档\n\n"
    md_content += f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += f"**模板数量**: {len(templates)}\n\n"
    md_content += "---\n\n"
    
    for idx, template in enumerate(templates, 1):
        md_content += f"## {idx}. {template.table_name_cn} ({template.table_name})\n\n"
        
        # 基本信息
        md_content += "### 基本信息\n\n"
        md_content += f"- **表名**: `{template.table_name}`\n"
        md_content += f"- **中文名**: {template.table_name_cn}\n"
        md_content += f"- **核心表**: {'是' if template.is_core else '否'}\n"
        if template.description:
            md_content += f"- **说明**: {template.description}\n"
        md_content += "\n"
        
        # 表定义文档
        if template.definition_file_path:
            md_content += "### 表定义\n\n"
            file_path = DataTemplateFileService.get_file_path(template.definition_file_path)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        definition_content = f.read()
                    md_content += definition_content + "\n\n"
                except Exception as e:
                    md_content += f"*无法读取表定义文档: {str(e)}*\n\n"
            else:
                md_content += "*表定义文档文件不存在*\n\n"
        
        # SQL建表代码
        if template.sql_file_path:
            md_content += "### SQL建表代码\n\n"
            file_path = DataTemplateFileService.get_file_path(template.sql_file_path)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    md_content += "```sql\n"
                    md_content += sql_content + "\n"
                    md_content += "```\n\n"
                except Exception as e:
                    md_content += f"*无法读取SQL文件: {str(e)}*\n\n"
            else:
                md_content += "*SQL文件不存在*\n\n"
        
        md_content += "---\n\n"
    
    # 返回Markdown文件
    return Response(
        content=md_content.encode('utf-8'),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=data_templates_{datetime.now().strftime('%Y%m%d')}.md"
        }
    )


@router.post("/copy", response_model=CopyResult)
def copy_templates(
    request: CopyTemplateRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    """从其他医疗机构复制数据模板"""
    from app.utils.hospital_filter import get_user_hospital_id
    
    target_hospital_id = get_user_hospital_id(current_user)
    
    # 验证源医疗机构存在
    source_hospital = db.query(Hospital).filter(Hospital.id == request.source_hospital_id).first()
    if not source_hospital:
        raise HTTPException(status_code=404, detail="源医疗机构不存在")
    
    # 查询要复制的数据模板
    source_templates = db.query(DataTemplate).filter(
        DataTemplate.hospital_id == request.source_hospital_id,
        DataTemplate.id.in_(request.template_ids)
    ).all()
    
    if not source_templates:
        raise HTTPException(status_code=404, detail="未找到要复制的数据模板")
    
    # 获取当前最大排序序号
    max_sort_order = db.query(func.max(DataTemplate.sort_order)).filter(
        DataTemplate.hospital_id == target_hospital_id
    ).scalar()
    current_sort_order = Decimal(max_sort_order or 0)
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    details = []
    
    for source_template in source_templates:
        try:
            # 检查是否已存在
            existing = db.query(DataTemplate).filter(
                DataTemplate.hospital_id == target_hospital_id,
                DataTemplate.table_name == source_template.table_name
            ).first()
            
            if existing:
                if request.conflict_strategy == "skip":
                    skipped_count += 1
                    details.append({
                        "table_name": source_template.table_name,
                        "action": "skipped",
                        "message": "表名已存在，跳过"
                    })
                    continue
                else:  # overwrite
                    # 删除旧文件
                    DataTemplateFileService.delete_file(existing.definition_file_path)
                    DataTemplateFileService.delete_file(existing.sql_file_path)
                    
                    # 复制文件
                    definition_file_path = None
                    sql_file_path = None
                    
                    if source_template.definition_file_path:
                        definition_file_path = DataTemplateFileService.copy_file(
                            source_template.definition_file_path,
                            target_hospital_id,
                            "definition",
                            source_template.definition_file_name
                        )
                    
                    if source_template.sql_file_path:
                        sql_file_path = DataTemplateFileService.copy_file(
                            source_template.sql_file_path,
                            target_hospital_id,
                            "sql",
                            source_template.sql_file_name
                        )
                    
                    # 更新记录
                    existing.table_name_cn = source_template.table_name_cn
                    existing.description = source_template.description
                    existing.is_core = source_template.is_core
                    existing.definition_file_path = definition_file_path
                    existing.definition_file_name = source_template.definition_file_name
                    existing.sql_file_path = sql_file_path
                    existing.sql_file_name = source_template.sql_file_name
                    
                    db.commit()
                    success_count += 1
                    details.append({
                        "table_name": source_template.table_name,
                        "action": "overwritten",
                        "message": "覆盖成功"
                    })
            else:
                # 复制文件
                definition_file_path = None
                sql_file_path = None
                
                if source_template.definition_file_path:
                    definition_file_path = DataTemplateFileService.copy_file(
                        source_template.definition_file_path,
                        target_hospital_id,
                        "definition",
                        source_template.definition_file_name
                    )
                
                if source_template.sql_file_path:
                    sql_file_path = DataTemplateFileService.copy_file(
                        source_template.sql_file_path,
                        target_hospital_id,
                        "sql",
                        source_template.sql_file_name
                    )
                
                # 创建新记录
                current_sort_order += Decimal("1.0")
                
                new_template = DataTemplate(
                    hospital_id=target_hospital_id,
                    table_name=source_template.table_name,
                    table_name_cn=source_template.table_name_cn,
                    description=source_template.description,
                    is_core=source_template.is_core,
                    sort_order=current_sort_order,
                    definition_file_path=definition_file_path,
                    definition_file_name=source_template.definition_file_name,
                    sql_file_path=sql_file_path,
                    sql_file_name=source_template.sql_file_name
                )
                db.add(new_template)
                db.commit()
                success_count += 1
                details.append({
                    "table_name": source_template.table_name,
                    "action": "copied",
                    "message": "复制成功"
                })
        
        except Exception as e:
            failed_count += 1
            details.append({
                "table_name": source_template.table_name,
                "action": "failed",
                "message": f"失败: {str(e)}"
            })
            db.rollback()
    
    return CopyResult(
        success_count=success_count,
        skipped_count=skipped_count,
        failed_count=failed_count,
        details=details
    )
