"""
数据模板文件存储服务
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException


class DataTemplateFileService:
    """数据模板文件存储服务"""
    
    # 基础上传目录
    BASE_UPLOAD_DIR = "uploads/data-templates"
    
    # 文件类型子目录
    DEFINITION_SUBDIR = "definitions"
    SQL_SUBDIR = "sql"
    
    # 允许的文件扩展名
    ALLOWED_DEFINITION_EXTENSIONS = {".md"}
    ALLOWED_SQL_EXTENSIONS = {".sql"}
    
    # 最大文件大小（10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def ensure_directory(cls, hospital_id: int, file_type: str) -> Path:
        """
        确保目录存在
        
        Args:
            hospital_id: 医疗机构ID
            file_type: 文件类型（definition/sql）
        
        Returns:
            Path: 目录路径对象
        """
        if file_type == "definition":
            subdir = cls.DEFINITION_SUBDIR
        elif file_type == "sql":
            subdir = cls.SQL_SUBDIR
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        dir_path = Path(cls.BASE_UPLOAD_DIR) / str(hospital_id) / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @classmethod
    def generate_unique_filename(cls, original_filename: str) -> str:
        """
        生成唯一文件名
        
        Args:
            original_filename: 原始文件名
        
        Returns:
            str: 唯一文件名（UUID_原始文件名）
        """
        # 生成UUID前缀
        unique_id = str(uuid.uuid4())
        # 组合UUID和原始文件名
        return f"{unique_id}_{original_filename}"
    
    @classmethod
    def validate_file(cls, file: UploadFile, file_type: str) -> None:
        """
        验证文件
        
        Args:
            file: 上传的文件
            file_type: 文件类型（definition/sql）
        
        Raises:
            HTTPException: 验证失败时抛出异常
        """
        # 验证文件名
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 验证文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_type == "definition":
            if file_ext not in cls.ALLOWED_DEFINITION_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"表定义文档必须是 .md 格式，当前格式: {file_ext}"
                )
        elif file_type == "sql":
            if file_ext not in cls.ALLOWED_SQL_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"SQL建表代码必须是 .sql 格式，当前格式: {file_ext}"
                )
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    @classmethod
    async def save_file(
        cls,
        file: UploadFile,
        hospital_id: int,
        file_type: str
    ) -> Tuple[str, str]:
        """
        保存文件
        
        Args:
            file: 上传的文件
            hospital_id: 医疗机构ID
            file_type: 文件类型（definition/sql）
        
        Returns:
            Tuple[str, str]: (文件路径, 原始文件名)
        
        Raises:
            HTTPException: 保存失败时抛出异常
        """
        # 验证文件
        cls.validate_file(file, file_type)
        
        # 读取文件内容并验证大小
        content = await file.read()
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大 {cls.MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 确保目录存在
        dir_path = cls.ensure_directory(hospital_id, file_type)
        
        # 生成唯一文件名
        unique_filename = cls.generate_unique_filename(file.filename)
        file_path = dir_path / unique_filename
        
        # 保存文件
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件保存失败: {str(e)}"
            )
        
        # 返回相对路径和原始文件名（使用字符串拼接而不是 relative_to）
        if file_type == "definition":
            subdir = cls.DEFINITION_SUBDIR
        else:
            subdir = cls.SQL_SUBDIR
        
        relative_path = f"{cls.BASE_UPLOAD_DIR}/{hospital_id}/{subdir}/{unique_filename}"
        return relative_path, file.filename
    
    @classmethod
    def save_definition_file(
        cls,
        file: UploadFile,
        hospital_id: int
    ) -> Tuple[str, str]:
        """
        保存表定义文档
        
        Args:
            file: 上传的文件
            hospital_id: 医疗机构ID
        
        Returns:
            Tuple[str, str]: (文件路径, 原始文件名)
        """
        import asyncio
        return asyncio.run(cls.save_file(file, hospital_id, "definition"))
    
    @classmethod
    def save_sql_file(
        cls,
        file: UploadFile,
        hospital_id: int
    ) -> Tuple[str, str]:
        """
        保存SQL建表代码
        
        Args:
            file: 上传的文件
            hospital_id: 医疗机构ID
        
        Returns:
            Tuple[str, str]: (文件路径, 原始文件名)
        """
        import asyncio
        return asyncio.run(cls.save_file(file, hospital_id, "sql"))
    
    @classmethod
    def get_file_path(cls, relative_path: str) -> Path:
        """
        获取文件完整路径
        
        Args:
            relative_path: 相对路径
        
        Returns:
            Path: 完整路径对象
        """
        return Path(relative_path)
    
    @classmethod
    def delete_file(cls, file_path: Optional[str]) -> None:
        """
        删除文件
        
        Args:
            file_path: 文件路径
        """
        if not file_path:
            return
        
        try:
            path = cls.get_file_path(file_path)
            if path.exists():
                path.unlink()
        except Exception as e:
            # 记录错误但不抛出异常，避免影响主流程
            print(f"删除文件失败: {file_path}, 错误: {str(e)}")
    
    @classmethod
    def copy_file(
        cls,
        source_path: str,
        target_hospital_id: int,
        file_type: str,
        original_filename: str
    ) -> str:
        """
        复制文件到目标医疗机构目录
        
        Args:
            source_path: 源文件路径
            target_hospital_id: 目标医疗机构ID
            file_type: 文件类型（definition/sql）
            original_filename: 原始文件名
        
        Returns:
            str: 新文件的相对路径
        
        Raises:
            HTTPException: 复制失败时抛出异常
        """
        # 确保源文件存在
        source = cls.get_file_path(source_path)
        if not source.exists():
            raise HTTPException(status_code=404, detail=f"源文件不存在: {source_path}")
        
        # 确保目标目录存在
        target_dir = cls.ensure_directory(target_hospital_id, file_type)
        
        # 生成唯一文件名
        unique_filename = cls.generate_unique_filename(original_filename)
        target_path = target_dir / unique_filename
        
        # 复制文件
        try:
            shutil.copy2(source, target_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件复制失败: {str(e)}"
            )
        
        # 返回相对路径（使用字符串拼接而不是 relative_to）
        if file_type == "definition":
            subdir = cls.DEFINITION_SUBDIR
        else:
            subdir = cls.SQL_SUBDIR
        
        return f"{cls.BASE_UPLOAD_DIR}/{target_hospital_id}/{subdir}/{unique_filename}"
