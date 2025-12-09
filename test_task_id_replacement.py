import sys
sys.path.insert(0, 'backend')
from app.database import SessionLocal
from app.models import CalculationStep

db = SessionLocal()
try:
    step = db.query(CalculationStep).filter(CalculationStep.id == 67).first()
    if not step:
        print('未找到步骤67')
        exit(1)
    
    # 模拟参数替换
    task_id = "test-task-123"
    model_version_id = 1
    code = step.code_content
    
    print(f"原始SQL中task_id占位符数量: {code.count('{task_id}')}")
    
    # 执行替换
    code = code.replace("{task_id}", task_id)
    code = code.replace("{version_id}", str(model_version_id))
    
    print(f"替换后SQL中task_id占位符数量: {code.count('{task_id}')}")
    print(f"替换后SQL中test-task-123出现次数: {code.count('test-task-123')}")
    
    # 查找INSERT语句
    insert_pos = code.find('INSERT INTO calculation_results')
    if insert_pos >= 0:
        print(f"\nINSERT语句中的task_id:")
        snippet = code[insert_pos:insert_pos+600]
        # 查找task_id行
        for line in snippet.split('\n'):
            if 'task_id' in line.lower():
                print(f"  {line.strip()}")
    
finally:
    db.close()
