import sys
sys.path.insert(0, 'backend')
from app.database import SessionLocal
from app.models import CalculationWorkflow, ModelVersion

db = SessionLocal()
try:
    # 查询版本7的所有工作流
    workflows = db.query(CalculationWorkflow).filter(
        CalculationWorkflow.version_id == 7
    ).all()
    
    print(f'版本7的工作流列表:')
    print('-' * 60)
    for wf in workflows:
        print(f'ID: {wf.id}')
        print(f'名称: {wf.name}')
        print(f'版本ID: {wf.version_id}')
        print(f'是否激活: {wf.is_active}')
        print('-' * 60)
    
    if not workflows:
        print('版本7没有关联的工作流')
        print('\n查询所有工作流:')
        all_workflows = db.query(CalculationWorkflow).all()
        for wf in all_workflows:
            version = db.query(ModelVersion).filter(ModelVersion.id == wf.version_id).first()
            version_name = version.name if version else "未知"
            print(f'ID: {wf.id}, 名称: {wf.name}, 版本ID: {wf.version_id}, 版本名: {version_name}')
finally:
    db.close()
