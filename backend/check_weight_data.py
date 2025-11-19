"""
检查计算结果中的权重值是否与模型节点中的权重一致
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.calculation_task import CalculationResult
from app.models.model_node import ModelNode
from app.models.calculation_task import CalculationTask

# 数据库连接
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/hospital_performance"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_weight_values(task_id: str, dept_id: int):
    """检查权重值"""
    db = SessionLocal()
    
    try:
        # 获取任务信息
        task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
        if not task:
            print(f"任务 {task_id} 不存在")
            return
        
        print(f"任务ID: {task_id}")
        print(f"模型版本ID: {task.model_version_id}")
        print(f"科室ID: {dept_id}")
        print("=" * 100)
        
        # 查询计算结果
        results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == dept_id,
            CalculationResult.node_type == 'dimension'
        ).order_by(CalculationResult.node_id).all()
        
        print(f"\n找到 {len(results)} 条维度计算结果\n")
        
        # 查询模型节点
        node_ids = [r.node_id for r in results]
        model_nodes = db.query(ModelNode).filter(ModelNode.id.in_(node_ids)).all()
        node_map = {node.id: node for node in model_nodes}
        
        # 对比权重值
        inconsistent_count = 0
        for result in results:
            model_node = node_map.get(result.node_id)
            
            if not model_node:
                print(f"⚠️  节点 {result.node_id} ({result.node_name}) 在模型中不存在")
                inconsistent_count += 1
                continue
            
            result_weight = result.weight
            model_weight = model_node.weight
            
            # 判断是否一致
            if result_weight is None and model_weight is None:
                status = "✓ 都为空"
            elif result_weight is None or model_weight is None:
                status = "✗ 一个为空"
                inconsistent_count += 1
            elif abs(float(result_weight) - float(model_weight)) < 0.0001:
                status = "✓ 一致"
            else:
                status = "✗ 不一致"
                inconsistent_count += 1
            
            # 只显示不一致的或前10条
            if "✗" in status or results.index(result) < 10:
                print(f"节点ID: {result.node_id:4d} | {result.node_name:30s} | "
                      f"结果权重: {str(result_weight):15s} | "
                      f"模型权重: {str(model_weight):15s} | "
                      f"{status}")
        
        print("\n" + "=" * 100)
        print(f"总计: {len(results)} 条记录")
        print(f"不一致: {inconsistent_count} 条记录")
        
        if inconsistent_count > 0:
            print("\n⚠️  发现权重不一致的情况！")
            print("可能原因：")
            print("1. 计算任务执行时使用的模型版本与当前模型版本不同")
            print("2. 模型节点的权重在计算后被修改")
            print("3. 计算逻辑中没有正确读取模型节点的权重")
        else:
            print("\n✓ 所有权重值一致")
        
    finally:
        db.close()

if __name__ == "__main__":
    # 使用示例
    task_id = "report-2025-10-20251030151533"  # 替换为实际的task_id
    dept_id = 3  # 替换为实际的department_id
    
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
    if len(sys.argv) > 2:
        dept_id = int(sys.argv[2])
    
    check_weight_values(task_id, dept_id)
