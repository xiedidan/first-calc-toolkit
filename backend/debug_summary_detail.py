"""
详细调试科室汇总表计算
彻底排查问题所在
"""
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.calculation_task import CalculationResult, CalculationSummary, CalculationTask
from app.models.department import Department
from app.models.model_node import ModelNode


def debug_summary_calculation(db: Session, task_id: str = None, dept_id: int = None):
    """详细调试汇总计算"""
    
    print("="*100)
    print("科室汇总表计算详细调试")
    print("="*100)
    
    # 如果没有指定task_id，使用最新的
    if not task_id:
        task = db.query(CalculationTask).order_by(
            CalculationTask.created_at.desc()
        ).first()
        if not task:
            print("❌ 未找到任务")
            return
        task_id = task.task_id
        print(f"使用最新任务: {task_id} (周期: {task.period})")
    
    # 如果没有指定dept_id，使用第一个科室
    if not dept_id:
        summary = db.query(CalculationSummary).filter(
            CalculationSummary.task_id == task_id
        ).first()
        if not summary:
            print("❌ 未找到汇总数据")
            return
        dept_id = summary.department_id
    
    dept = db.query(Department).filter(Department.id == dept_id).first()
    dept_name = f"{dept.his_code} - {dept.his_name}" if dept else f"科室ID: {dept_id}"
    
    print(f"调试科室: {dept_name}")
    print("="*100)
    print()
    
    # 1. 查看所有计算结果
    print("1️⃣  查看该科室的所有计算结果")
    print("-"*100)
    
    all_results = db.query(CalculationResult).filter(
        CalculationResult.task_id == task_id,
        CalculationResult.department_id == dept_id
    ).order_by(CalculationResult.node_type, CalculationResult.node_id).all()
    
    print(f"总共 {len(all_results)} 条记录")
    print()
    
    sequences = [r for r in all_results if r.node_type == "sequence"]
    dimensions = [r for r in all_results if r.node_type == "dimension"]
    
    print(f"序列: {len(sequences)} 个")
    for seq in sequences:
        print(f"  [{seq.node_id}] {seq.node_name}: 价值={seq.value}")
    print()
    
    print(f"维度: {len(dimensions)} 个")
    for dim in dimensions:
        parent_info = f"parent={dim.parent_id}" if dim.parent_id else "root"
        print(f"  [{dim.node_id}] {dim.node_name} ({parent_info}): 工作量={dim.workload}, 权重={dim.weight}, 价值={dim.value}")
    print()
    
    # 2. 分析每个序列的维度结构
    print("2️⃣  分析每个序列的维度结构")
    print("-"*100)
    
    for seq in sequences:
        print(f"\n序列: {seq.node_name} (ID={seq.node_id})")
        print(f"序列价值: {seq.value}")
        print()
        
        # 找出该序列的直接子维度
        first_level = [d for d in dimensions if d.parent_id == seq.node_id]
        print(f"  一级维度 ({len(first_level)} 个):")
        
        if not first_level:
            print("    ⚠️  没有找到一级维度！")
            # 检查是否有维度的parent_id指向这个序列
            print(f"    检查所有维度的parent_id:")
            for dim in dimensions:
                print(f"      [{dim.node_id}] {dim.node_name}: parent_id={dim.parent_id}")
            continue
        
        # 构建节点映射
        result_map = {d.node_id: d for d in dimensions}
        
        # 递归函数：从子节点汇总价值
        def calculate_sum_from_children(node_id: int, indent: str = "    ") -> Decimal:
            """递归计算节点的价值（从子节点汇总）"""
            result = result_map.get(node_id)
            if not result:
                print(f"{indent}⚠️  节点 {node_id} 不存在")
                return Decimal("0")
            
            # 查找该节点的所有子节点
            children = [d for d in dimensions if d.parent_id == node_id]
            
            if not children:
                # 叶子节点，直接返回自己的价值
                value = result.value or Decimal("0")
                print(f"{indent}🍃 [{node_id}] {result.node_name}: 叶子节点价值={value}")
                return value
            
            # 非叶子节点，汇总子节点的价值
            print(f"{indent}📁 [{node_id}] {result.node_name}: 非叶子节点，有 {len(children)} 个子节点")
            total_value = Decimal("0")
            for child in children:
                child_value = calculate_sum_from_children(child.node_id, indent + "  ")
                total_value += child_value
            
            print(f"{indent}   → 汇总价值 = {total_value}")
            return total_value
        
        # 计算序列价值
        sequence_value_calc = Decimal("0")
        for dim in first_level:
            print(f"\n  处理一级维度: [{dim.node_id}] {dim.node_name}")
            dim_value = calculate_sum_from_children(dim.node_id, "    ")
            sequence_value_calc += dim_value
            print(f"    累计序列价值: {sequence_value_calc}")
        
        print(f"\n  ✅ 序列 {seq.node_name} 计算价值: {sequence_value_calc}")
        print(f"  📊 序列 {seq.node_name} 存储价值: {seq.value}")
        
        if abs(sequence_value_calc - (seq.value or Decimal("0"))) > Decimal("0.01"):
            print(f"  ❌ 不匹配！差异: {sequence_value_calc - (seq.value or Decimal('0'))}")
        else:
            print(f"  ✅ 匹配！")
    
    # 3. 检查汇总表数据
    print("\n" + "="*100)
    print("3️⃣  检查汇总表数据")
    print("-"*100)
    
    summary = db.query(CalculationSummary).filter(
        CalculationSummary.task_id == task_id,
        CalculationSummary.department_id == dept_id
    ).first()
    
    if not summary:
        print("❌ 未找到汇总数据")
        return
    
    print(f"医生价值: {summary.doctor_value} ({summary.doctor_ratio}%)")
    print(f"护理价值: {summary.nurse_value} ({summary.nurse_ratio}%)")
    print(f"医技价值: {summary.tech_value} ({summary.tech_ratio}%)")
    print(f"科室总价值: {summary.total_value}")
    print()
    
    # 根据序列名称分类
    doctor_value_calc = Decimal("0")
    nurse_value_calc = Decimal("0")
    tech_value_calc = Decimal("0")
    
    print("序列分类:")
    for seq in sequences:
        value = seq.value or Decimal("0")
        node_name_lower = seq.node_name.lower()
        
        if "医生" in seq.node_name or "医疗" in seq.node_name or "医师" in seq.node_name or \
           "doctor" in node_name_lower or "physician" in node_name_lower:
            doctor_value_calc += value
            print(f"  医生序列: {seq.node_name} = {value}")
        elif "护理" in seq.node_name or "护士" in seq.node_name or \
             "nurse" in node_name_lower or "nursing" in node_name_lower:
            nurse_value_calc += value
            print(f"  护理序列: {seq.node_name} = {value}")
        elif "医技" in seq.node_name or "技师" in seq.node_name or \
             "tech" in node_name_lower or "technician" in node_name_lower:
            tech_value_calc += value
            print(f"  医技序列: {seq.node_name} = {value}")
        else:
            print(f"  ⚠️  未识别: {seq.node_name} = {value}")
    
    total_calc = doctor_value_calc + nurse_value_calc + tech_value_calc
    
    print()
    print("计算结果对比:")
    print(f"  医生: 计算={doctor_value_calc}, 存储={summary.doctor_value}, 匹配={'✅' if abs(doctor_value_calc - summary.doctor_value) < Decimal('0.01') else '❌'}")
    print(f"  护理: 计算={nurse_value_calc}, 存储={summary.nurse_value}, 匹配={'✅' if abs(nurse_value_calc - summary.nurse_value) < Decimal('0.01') else '❌'}")
    print(f"  医技: 计算={tech_value_calc}, 存储={summary.tech_value}, 匹配={'✅' if abs(tech_value_calc - summary.tech_value) < Decimal('0.01') else '❌'}")
    print(f"  总计: 计算={total_calc}, 存储={summary.total_value}, 匹配={'✅' if abs(total_calc - summary.total_value) < Decimal('0.01') else '❌'}")
    
    # 4. 检查模型节点结构
    print("\n" + "="*100)
    print("4️⃣  检查模型节点结构")
    print("-"*100)
    
    # 获取任务的模型版本
    task = db.query(CalculationTask).filter(CalculationTask.task_id == task_id).first()
    if task:
        model_nodes = db.query(ModelNode).filter(
            ModelNode.version_id == task.model_version_id
        ).order_by(ModelNode.sort_order).all()
        
        print(f"模型版本 {task.model_version_id} 的节点结构:")
        print()
        
        seq_nodes = [n for n in model_nodes if n.node_type == "sequence"]
        dim_nodes = [n for n in model_nodes if n.node_type == "dimension"]
        
        print(f"序列节点 ({len(seq_nodes)} 个):")
        for node in seq_nodes:
            print(f"  [{node.id}] {node.name} (code={node.code}, parent={node.parent_id})")
        
        print()
        print(f"维度节点 ({len(dim_nodes)} 个):")
        for node in dim_nodes:
            print(f"  [{node.id}] {node.name} (code={node.code}, parent={node.parent_id}, weight={node.weight})")
        
        print()
        print("维度的父子关系:")
        for seq in seq_nodes:
            print(f"\n  序列 [{seq.id}] {seq.name}:")
            children = [n for n in dim_nodes if n.parent_id == seq.id]
            if children:
                for child in children:
                    print(f"    └─ [{child.id}] {child.name}")
                    # 递归显示子维度
                    def show_children(parent_id, indent="      "):
                        sub_children = [n for n in dim_nodes if n.parent_id == parent_id]
                        for sc in sub_children:
                            print(f"{indent}└─ [{sc.id}] {sc.name}")
                            show_children(sc.id, indent + "  ")
                    show_children(child.id)
            else:
                print(f"    ⚠️  没有子维度")
    
    print("\n" + "="*100)
    print("调试完成")
    print("="*100)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="详细调试科室汇总表计算")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--dept-id", type=int, help="科室ID")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        debug_summary_calculation(db, args.task_id, args.dept_id)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
