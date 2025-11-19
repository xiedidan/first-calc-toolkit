"""
数据模板批量上传服务
"""
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.data_template import DataTemplate
from app.services.data_template_file_service import DataTemplateFileService
from app.schemas.data_template import BatchUploadItem, BatchUploadPreview, BatchUploadResult


class DataTemplateBatchService:
    """数据模板批量上传服务"""
    
    @staticmethod
    def parse_definition_filename(filename: str) -> Optional[Tuple[str, str]]:
        """
        解析表定义文档文件名
        格式：中文名(表名).md 或 中文名（表名）.md
        例如：交接班记录(TB_CIS_JJBJL).md 或 交接班记录（TB_CIS_JJBJL）.md
        
        Args:
            filename: 文件名
        
        Returns:
            Optional[Tuple[str, str]]: (中文名, 表名) 或 None
        """
        # 移除文件扩展名
        name_without_ext = Path(filename).stem
        
        # 正则表达式匹配：中文名(表名) 或 中文名（表名）
        # 支持英文括号和中文括号
        pattern = r'^(.+?)[\(（]([A-Za-z0-9_]+)[\)）]$'
        match = re.match(pattern, name_without_ext)
        
        if match:
            table_name_cn = match.group(1).strip()
            table_name = match.group(2).strip()
            return table_name_cn, table_name
        
        return None
    
    @staticmethod
    def parse_sql_filename(filename: str) -> Optional[str]:
        """
        解析SQL文件名
        格式：表名.sql
        例如：TB_CIS_JJBJL.sql
        
        Args:
            filename: 文件名
        
        Returns:
            Optional[str]: 表名 或 None
        """
        # 移除文件扩展名
        name_without_ext = Path(filename).stem
        
        # 验证是否为有效的表名（字母、数字、下划线）
        if re.match(r'^[A-Za-z0-9_]+$', name_without_ext):
            return name_without_ext
        
        return None
    
    @classmethod
    def match_files(
        cls,
        definition_files: List[UploadFile],
        sql_files: List[UploadFile]
    ) -> Dict[str, Dict]:
        """
        根据表名匹配表定义文档和SQL文件
        
        Args:
            definition_files: 表定义文档列表
            sql_files: SQL文件列表
        
        Returns:
            Dict[str, Dict]: 匹配结果字典
                {
                    "表名": {
                        "table_name": "表名",
                        "table_name_cn": "中文名",
                        "definition_file": UploadFile对象,
                        "sql_file": UploadFile对象,
                        "status": "matched/partial/unmatched",
                        "message": "提示信息"
                    }
                }
        """
        matched_data = {}
        
        # 解析表定义文档
        for file in definition_files:
            result = cls.parse_definition_filename(file.filename)
            if result:
                table_name_cn, table_name = result
                if table_name not in matched_data:
                    matched_data[table_name] = {
                        "table_name": table_name,
                        "table_name_cn": table_name_cn,
                        "definition_file": file,
                        "sql_file": None,
                        "status": "partial",
                        "message": "仅有表定义文档"
                    }
                else:
                    matched_data[table_name]["table_name_cn"] = table_name_cn
                    matched_data[table_name]["definition_file"] = file
                    if matched_data[table_name]["sql_file"]:
                        matched_data[table_name]["status"] = "matched"
                        matched_data[table_name]["message"] = "完全匹配"
            else:
                # 文件名格式不正确
                print(f"警告：表定义文档文件名格式不正确: {file.filename}")
        
        # 解析SQL文件
        for file in sql_files:
            table_name = cls.parse_sql_filename(file.filename)
            if table_name:
                if table_name not in matched_data:
                    matched_data[table_name] = {
                        "table_name": table_name,
                        "table_name_cn": None,
                        "definition_file": None,
                        "sql_file": file,
                        "status": "partial",
                        "message": "仅有SQL建表代码"
                    }
                else:
                    matched_data[table_name]["sql_file"] = file
                    if matched_data[table_name]["definition_file"]:
                        matched_data[table_name]["status"] = "matched"
                        matched_data[table_name]["message"] = "完全匹配"
            else:
                # 文件名格式不正确
                print(f"警告：SQL文件名格式不正确: {file.filename}")
        
        return matched_data
    
    @classmethod
    async def create_or_update_templates(
        cls,
        db: Session,
        hospital_id: int,
        matched_data: Dict[str, Dict]
    ) -> BatchUploadResult:
        """
        批量创建或更新数据模板
        
        Args:
            db: 数据库会话
            hospital_id: 医疗机构ID
            matched_data: 匹配结果字典
        
        Returns:
            BatchUploadResult: 批量上传结果
        """
        success_count = 0
        failed_count = 0
        skipped_count = 0
        details = []
        
        # 获取当前最大排序序号
        max_sort_order = db.query(DataTemplate.sort_order).filter(
            DataTemplate.hospital_id == hospital_id
        ).order_by(DataTemplate.sort_order.desc()).first()
        
        current_sort_order = Decimal(max_sort_order[0] if max_sort_order else 0)
        
        for table_name, data in matched_data.items():
            try:
                # 查询是否已存在
                existing = db.query(DataTemplate).filter(
                    DataTemplate.hospital_id == hospital_id,
                    DataTemplate.table_name == table_name
                ).first()
                
                # 保存文件
                definition_file_path = None
                definition_file_name = None
                sql_file_path = None
                sql_file_name = None
                
                if data["definition_file"]:
                    definition_file_path, definition_file_name = await DataTemplateFileService.save_file(
                        data["definition_file"],
                        hospital_id,
                        "definition"
                    )
                
                if data["sql_file"]:
                    sql_file_path, sql_file_name = await DataTemplateFileService.save_file(
                        data["sql_file"],
                        hospital_id,
                        "sql"
                    )
                
                if existing:
                    # 更新现有记录
                    if data["table_name_cn"]:
                        existing.table_name_cn = data["table_name_cn"]
                    if definition_file_path:
                        # 删除旧文件
                        DataTemplateFileService.delete_file(existing.definition_file_path)
                        existing.definition_file_path = definition_file_path
                        existing.definition_file_name = definition_file_name
                    if sql_file_path:
                        # 删除旧文件
                        DataTemplateFileService.delete_file(existing.sql_file_path)
                        existing.sql_file_path = sql_file_path
                        existing.sql_file_name = sql_file_name
                    
                    db.commit()
                    success_count += 1
                    details.append({
                        "table_name": table_name,
                        "action": "updated",
                        "message": "更新成功"
                    })
                else:
                    # 创建新记录
                    current_sort_order += Decimal("1.0")
                    
                    template = DataTemplate(
                        hospital_id=hospital_id,
                        table_name=table_name,
                        table_name_cn=data["table_name_cn"] or table_name,
                        is_core=False,
                        sort_order=current_sort_order,
                        definition_file_path=definition_file_path,
                        definition_file_name=definition_file_name,
                        sql_file_path=sql_file_path,
                        sql_file_name=sql_file_name
                    )
                    db.add(template)
                    db.commit()
                    success_count += 1
                    details.append({
                        "table_name": table_name,
                        "action": "created",
                        "message": "创建成功"
                    })
            
            except Exception as e:
                failed_count += 1
                details.append({
                    "table_name": table_name,
                    "action": "failed",
                    "message": f"失败: {str(e)}"
                })
                db.rollback()
        
        return BatchUploadResult(
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            details=details
        )
    
    @classmethod
    def generate_preview(
        cls,
        matched_data: Dict[str, Dict]
    ) -> BatchUploadPreview:
        """
        生成批量上传预览
        
        Args:
            matched_data: 匹配结果字典
        
        Returns:
            BatchUploadPreview: 预览数据
        """
        items = []
        matched_count = 0
        partial_count = 0
        
        for table_name, data in matched_data.items():
            item = BatchUploadItem(
                table_name=data["table_name"],
                table_name_cn=data["table_name_cn"],
                definition_file_name=data["definition_file"].filename if data["definition_file"] else None,
                sql_file_name=data["sql_file"].filename if data["sql_file"] else None,
                status=data["status"],
                message=data["message"]
            )
            items.append(item)
            
            if data["status"] == "matched":
                matched_count += 1
            elif data["status"] == "partial":
                partial_count += 1
        
        return BatchUploadPreview(
            items=items,
            total=len(items),
            matched=matched_count,
            partial=partial_count,
            unmatched=0
        )
