"""
导入相关的 Celery 任务
"""
from celery import Task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.excel_import_service import ExcelImportService
from app.config.import_configs import CHARGE_ITEM_IMPORT_CONFIG
from app.models.charge_item import ChargeItem
from typing import Optional


class ImportTask(Task):
    """自定义任务基类，处理数据库会话"""
    
    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


@celery_app.task(bind=True, base=ImportTask, name="import_charge_items")
def import_charge_items_task(
    self,
    file_content: bytes,
    mapping: dict,
    hospital_id: int,
    db: Session = None
):
    """
    异步导入收费项目任务
    
    Args:
        file_content: Excel 文件内容（bytes）
        mapping: 字段映射关系
        hospital_id: 医疗机构ID
        db: 数据库会话（由 ImportTask 自动注入）
    """
    # 更新任务状态
    self.update_state(
        state='PROCESSING',
        meta={'current': 0, 'total': 0, 'status': '正在解析文件...'}
    )
    
    # 创建导入服务
    service = ExcelImportService(CHARGE_ITEM_IMPORT_CONFIG)
    
    # 自定义验证函数
    def validate_charge_item(row_data: dict, db: Session) -> Optional[str]:
        item_code = row_data.get("item_code", "")
        if item_code:
            existing = db.query(ChargeItem).filter(
                ChargeItem.hospital_id == hospital_id,
                ChargeItem.item_code == item_code
            ).first()
            if existing:
                return f"项目编码 {item_code} 已存在"
        return None
    
    # 数据预处理函数：添加hospital_id
    def preprocess_row(row_data: dict) -> dict:
        row_data['hospital_id'] = hospital_id
        return row_data
    
    # 自定义进度回调
    processed_count = [0]  # 使用列表以便在闭包中修改
    total_count = [0]
    
    def progress_callback(current: int, total: int):
        processed_count[0] = current
        total_count[0] = total
        self.update_state(
            state='PROCESSING',
            meta={
                'current': current,
                'total': total,
                'status': f'正在导入数据... ({current}/{total})'
            }
        )
    
    try:
        # 执行导入（带进度回调）
        result = service.import_data_with_progress(
            file_content,
            mapping,
            db,
            ChargeItem,
            validate_charge_item,
            progress_callback,
            preprocess_row
        )
        
        return {
            'status': 'completed',
            'success_count': result['success_count'],
            'failed_count': result['failed_count'],
            'failed_items': result['failed_items']
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
