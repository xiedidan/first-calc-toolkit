"""
插入测试结果数据的 Python 脚本
用于测试报表功能
"""
import sys
import random
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

# 添加项目路径
sys.path.append('.')

from app.database import SessionLocal
from app.models.calculation_task import CalculationResult, CalculationSummary
from app.models.department import Department
from app.models.model_node import ModelNode


def insert_test_results(task_id: str, period: str = "2025-10", limit_departments: int = 20):
    """
    插入测试结果数据
    
    Args:
        task_id: 计算任务ID
        period: 计算周期
        limit_departments: 限制科室数量
    """
    db = SessionLocal()
    
    try:
        print(f"开始插入测试数据...")
        print(f"任务ID: {task_id}")
        print(f"计算周期: {period}")
        print(f"科室数量限制: {limit_departments}")
        print("-" * 60)
        
        # 清理旧数据（可选）
        # db.query(CalculationResult).filter(CalculationResult.task_id == task_id).delete()
        # db.query(CalculationSummary).filter(CalculationSummary.task_id == task_id).delete()
        # db.commit()
        
        # 获取模型节点（如果存在）
        nodes = db.query(ModelNode).all()
        node_map = {node.code: node for node in nodes if node.code}
        
        # 定义节点结构（如果数据库中没有，使用虚拟ID）
        sequences = {
            'DOCTOR_SEQ': {'id': 1, 'name': '医生序列'},
            'NURSE_SEQ': {'id': 2, 'name': '护理序列'},
            'TECH_SEQ': {'id': 3, 'name': '医技序列'},
        }
        
        dimensions = {
            'OUTPATIENT': {'id': 11, 'name': '门诊诊察', 'parent': 'DOCTOR_SEQ'},
            'INPATIENT': {'id': 12, 'name': '住院诊察', 'parent': 'DOCTOR_SEQ'},
            'SURGERY': {'id': 13, 'name': '手术', 'parent': 'DOCTOR_SEQ'},
            'BED_NURSING': {'id': 21, 'name': '床日护理', 'parent': 'NURSE_SEQ'},
            'SPECIAL_NURSING': {'id': 22, 'name': '专科护理', 'parent': 'NURSE_SEQ'},
            'RADIOLOGY': {'id': 31, 'name': '放射检查', 'parent': 'TECH_SEQ'},
            'LAB': {'id': 32, 'name': '检验', 'parent': 'TECH_SEQ'},
        }
        
        # 如果数据库中有节点，使用实际的节点ID
        for code, info in sequences.items():
            if code in node_map:
                info['id'] = node_map[code].id
        
        for code, info in dimensions.items():
            if code in node_map:
                info['id'] = node_map[code].id
                info['parent_id'] = node_map[code].parent_id
            else:
                parent_code = info['parent']
                info['parent_id'] = sequences[parent_code]['id']
        
        # 获取启用的科室
        departments = db.query(Department).filter(
            Department.is_active == True
        ).order_by(Department.sort_order).limit(limit_departments).all()
        
        if not departments:
            print("错误：没有找到启用的科室")
            return
        
        print(f"找到 {len(departments)} 个科室")
        print("-" * 60)
        
        # 遍历科室插入数据
        for idx, dept in enumerate(departments, 1):
            print(f"[{idx}/{len(departments)}] 处理科室: {dept.his_code} - {dept.his_name}")
            
            # 随机因子（0.5 - 1.5）
            random_factor = 0.5 + random.random()
            
            # 插入医生序列数据
            doctor_value = Decimal(str((50000 + random.random() * 100000) * random_factor))
            insert_sequence_result(db, task_id, dept.id, sequences['DOCTOR_SEQ'], doctor_value)
            
            # 医生序列的维度
            insert_dimension_result(
                db, task_id, dept.id, dimensions['OUTPATIENT'],
                workload=Decimal(str((500 + random.random() * 1000) * random_factor)),
                weight=Decimal(str(30 + random.random() * 20)),
                value=Decimal(str((20000 + random.random() * 40000) * random_factor)),
                ratio=Decimal(str(25 + random.random() * 15))
            )
            
            insert_dimension_result(
                db, task_id, dept.id, dimensions['INPATIENT'],
                workload=Decimal(str((200 + random.random() * 400) * random_factor)),
                weight=Decimal(str(80 + random.random() * 40)),
                value=Decimal(str((15000 + random.random() * 35000) * random_factor)),
                ratio=Decimal(str(20 + random.random() * 15))
            )
            
            insert_dimension_result(
                db, task_id, dept.id, dimensions['SURGERY'],
                workload=Decimal(str((50 + random.random() * 150) * random_factor)),
                weight=Decimal(str(200 + random.random() * 300)),
                value=Decimal(str((15000 + random.random() * 40000) * random_factor)),
                ratio=Decimal(str(15 + random.random() * 20))
            )
            
            # 插入护理序列数据
            nurse_value = Decimal(str((30000 + random.random() * 60000) * random_factor))
            insert_sequence_result(db, task_id, dept.id, sequences['NURSE_SEQ'], nurse_value)
            
            # 护理序列的维度
            insert_dimension_result(
                db, task_id, dept.id, dimensions['BED_NURSING'],
                workload=Decimal(str((800 + random.random() * 1200) * random_factor)),
                weight=Decimal(str(25 + random.random() * 15)),
                value=Decimal(str((20000 + random.random() * 40000) * random_factor)),
                ratio=Decimal(str(40 + random.random() * 20))
            )
            
            insert_dimension_result(
                db, task_id, dept.id, dimensions['SPECIAL_NURSING'],
                workload=Decimal(str((100 + random.random() * 300) * random_factor)),
                weight=Decimal(str(50 + random.random() * 50)),
                value=Decimal(str((10000 + random.random() * 30000) * random_factor)),
                ratio=Decimal(str(20 + random.random() * 20))
            )
            
            # 插入医技序列数据
            tech_value = Decimal(str((20000 + random.random() * 40000) * random_factor))
            insert_sequence_result(db, task_id, dept.id, sequences['TECH_SEQ'], tech_value)
            
            # 医技序列的维度
            insert_dimension_result(
                db, task_id, dept.id, dimensions['RADIOLOGY'],
                workload=Decimal(str((200 + random.random() * 400) * random_factor)),
                weight=Decimal(str(40 + random.random() * 30)),
                value=Decimal(str((10000 + random.random() * 25000) * random_factor)),
                ratio=Decimal(str(40 + random.random() * 20))
            )
            
            insert_dimension_result(
                db, task_id, dept.id, dimensions['LAB'],
                workload=Decimal(str((300 + random.random() * 500) * random_factor)),
                weight=Decimal(str(20 + random.random() * 20)),
                value=Decimal(str((8000 + random.random() * 20000) * random_factor)),
                ratio=Decimal(str(30 + random.random() * 20))
            )
            
            # 插入汇总数据
            total_value = doctor_value + nurse_value + tech_value
            
            summary = CalculationSummary(
                task_id=task_id,
                department_id=dept.id,
                doctor_value=doctor_value,
                doctor_ratio=Decimal(str((doctor_value / total_value * 100) if total_value > 0 else 0)),
                nurse_value=nurse_value,
                nurse_ratio=Decimal(str((nurse_value / total_value * 100) if total_value > 0 else 0)),
                tech_value=tech_value,
                tech_ratio=Decimal(str((tech_value / total_value * 100) if total_value > 0 else 0)),
                total_value=total_value
            )
            db.add(summary)
        
        # 提交所有数据
        db.commit()
        
        print("-" * 60)
        print("✅ 测试数据插入完成！")
        print("-" * 60)
        
        # 统计信息
        result_count = db.query(CalculationResult).filter(
            CalculationResult.task_id == task_id
        ).count()
        
        summary_count = db.query(CalculationSummary).filter(
            CalculationSummary.task_id == task_id
        ).count()
        
        print(f"插入结果记录数: {result_count}")
        print(f"插入汇总记录数: {summary_count}")
        print(f"平均每科室记录数: {result_count / len(departments):.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误: {str(e)}")
        raise
    finally:
        db.close()


def insert_sequence_result(db: Session, task_id: str, dept_id: int, seq_info: dict, value: Decimal):
    """插入序列结果"""
    result = CalculationResult(
        task_id=task_id,
        department_id=dept_id,
        node_id=seq_info['id'],
        node_name=seq_info['name'],
        node_code=None,
        node_type='sequence',
        parent_id=None,
        workload=None,
        weight=None,
        value=value,
        ratio=None
    )
    db.add(result)


def insert_dimension_result(
    db: Session, task_id: str, dept_id: int, dim_info: dict,
    workload: Decimal, weight: Decimal, value: Decimal, ratio: Decimal
):
    """插入维度结果"""
    result = CalculationResult(
        task_id=task_id,
        department_id=dept_id,
        node_id=dim_info['id'],
        node_name=dim_info['name'],
        node_code=None,
        node_type='dimension',
        parent_id=dim_info['parent_id'],
        workload=workload,
        weight=weight,
        value=value,
        ratio=ratio
    )
    db.add(result)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='插入测试结果数据')
    parser.add_argument('task_id', help='计算任务ID')
    parser.add_argument('--period', default='2025-10', help='计算周期 (默认: 2025-10)')
    parser.add_argument('--limit', type=int, default=20, help='科室数量限制 (默认: 20)')
    
    args = parser.parse_args()
    
    insert_test_results(args.task_id, args.period, args.limit)
