"""
生成业务价值报表测试数据

此脚本用于生成汇总表和明细表的测试数据，支持快速验证报表功能。
数据可以填0或随机值，主要用于验证数据结构和展示逻辑。
"""
import sys
import os
from decimal import Decimal
from datetime import datetime
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_task import CalculationTask, CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode


def generate_test_data(
    db: Session,
    period: str = "2025-10",
    use_random_values: bool = False,
    model_version_id: int = None
):
    """生成测试数据
    
    Args:
        db: 数据库会话
        period: 计算周期
        use_random_values: 是否使用随机值（False则填0）
        model_version_id: 模型版本ID（如果不指定，使用激活版本）
    """
    print(f"开始生成测试数据...")
    print(f"计算周期: {period}")
    print(f"使用随机值: {use_random_values}")
    
    # 1. 获取模型版本
    if model_version_id:
        model_version = db.query(ModelVersion).filter(ModelVersion.id == model_version_id).first()
    else:
        model_version = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
    
    if not model_version:
        print("错误: 未找到模型版本")
        return False
    
    print(f"使用模型版本: {model_version.name} (ID: {model_version.id})")
    
    # 2. 获取参与评估的科室
    departments = db.query(Department).filter(
        Department.is_active == True
    ).all()
    
    if not departments:
        print("错误: 未找到参与评估的科室")
        return False
    
    print(f"找到 {len(departments)} 个参与评估的科室")
    
    # 3. 获取模型结构
    nodes = db.query(ModelNode).filter(
        ModelNode.version_id == model_version.id
    ).order_by(ModelNode.sort_order).all()
    
    if not nodes:
        print("错误: 模型版本没有节点")
        return False
    
    print(f"找到 {len(nodes)} 个模型节点")
    
    # 4. 创建计算任务
    task_id = f"test-{period}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task = CalculationTask(
        task_id=task_id,
        model_version_id=model_version.id,
        workflow_id=None,
        period=period,
        status="completed",
        progress=Decimal("100.00"),
        description="测试数据生成任务",
        created_at=datetime.now(),
        started_at=datetime.now(),
        completed_at=datetime.now()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    print(f"创建计算任务: {task_id}")
    
    # 5. 为每个科室生成计算结果
    for dept in departments:
        print(f"  生成科室 {dept.his_name} 的数据...")
        
        # 为每个节点生成结果
        for node in nodes:
            # 生成工作量和价值
            if use_random_values:
                workload = Decimal(str(random.randint(100, 10000)))
                weight = Decimal(str(random.uniform(0.01, 1.0)))
                value = workload * weight
            else:
                workload = Decimal("0")
                weight = Decimal("0")
                value = Decimal("0")
            
            # 计算占比（暂时设为0，后续会重新计算）
            ratio = Decimal("0")
            
            result = CalculationResult(
                task_id=task_id,
                department_id=dept.id,
                node_id=node.id,
                node_name=node.name,
                node_code=node.code,
                node_type=node.node_type,
                parent_id=node.parent_id,
                workload=workload,
                weight=weight,
                value=value,
                ratio=ratio,
                created_at=datetime.now()
            )
            db.add(result)
        
        db.commit()
    
    print("计算结果生成完成")
    
    # 6. 计算汇总数据
    print("开始计算汇总数据...")
    
    for dept in departments:
        # 查询该科室的所有序列结果
        sequence_results = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id,
            CalculationResult.department_id == dept.id,
            CalculationResult.node_type == "sequence"
        ).all()
        
        # 计算各序列的价值
        doctor_value = Decimal("0")
        nurse_value = Decimal("0")
        tech_value = Decimal("0")
        
        for result in sequence_results:
            if "医生" in result.node_name or "医疗" in result.node_name:
                doctor_value += result.value or Decimal("0")
            elif "护理" in result.node_name:
                nurse_value += result.value or Decimal("0")
            elif "医技" in result.node_name:
                tech_value += result.value or Decimal("0")
        
        total_value = doctor_value + nurse_value + tech_value
        
        # 计算占比
        if total_value > 0:
            doctor_ratio = doctor_value / total_value * 100
            nurse_ratio = nurse_value / total_value * 100
            tech_ratio = tech_value / total_value * 100
        else:
            doctor_ratio = Decimal("0")
            nurse_ratio = Decimal("0")
            tech_ratio = Decimal("0")
        
        # 创建汇总记录
        summary = CalculationSummary(
            task_id=task_id,
            department_id=dept.id,
            doctor_value=doctor_value,
            doctor_ratio=doctor_ratio,
            nurse_value=nurse_value,
            nurse_ratio=nurse_ratio,
            tech_value=tech_value,
            tech_ratio=tech_ratio,
            total_value=total_value,
            created_at=datetime.now()
        )
        db.add(summary)
    
    db.commit()
    print("汇总数据生成完成")
    
    # 7. 输出统计信息
    result_count = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id
    ).count()
    
    summary_count = db.query(CalculationSummary).filter(
        CalculationSummary.task_id == task_id
    ).count()
    
    print("\n" + "="*60)
    print("测试数据生成完成!")
    print("="*60)
    print(f"任务ID: {task_id}")
    print(f"计算周期: {period}")
    print(f"科室数量: {len(departments)}")
    print(f"节点数量: {len(nodes)}")
    print(f"计算结果记录数: {result_count}")
    print(f"汇总记录数: {summary_count}")
    print("="*60)
    
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成业务价值报表测试数据")
    parser.add_argument("--period", default="2025-10", help="计算周期 (YYYY-MM)")
    parser.add_argument("--random", action="store_true", help="使用随机值（默认填0）")
    parser.add_argument("--model-version-id", type=int, help="模型版本ID（默认使用激活版本）")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        success = generate_test_data(
            db=db,
            period=args.period,
            use_random_values=args.random,
            model_version_id=args.model_version_id
        )
        
        if success:
            print("\n✅ 测试数据生成成功!")
            print("\n下一步:")
            print("1. 启动后端服务: uvicorn app.main:app --reload")
            print("2. 启动前端服务: cd frontend && npm run dev")
            print("3. 访问 http://localhost:5173 查看报表")
        else:
            print("\n❌ 测试数据生成失败!")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
