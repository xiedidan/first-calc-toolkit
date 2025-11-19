"""
批量测试所有科室的维度工作量分配

使用方法：
    python test_all_dimensions.py                    # 测试所有科室
    python test_all_dimensions.py --limit 3          # 只测试前3个科室
    python test_all_dimensions.py --dept YS01 BHL01  # 只测试指定科室
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from populate_report_data_ai import AIDataGenerator, load_config, load_ai_config_from_file


def test_all_dimensions(dept_codes: list = None, limit: int = None):
    """批量测试科室的维度工作量分配"""
    
    # 1. 加载配置
    config_file = "report_data_config_real.json"
    print("="*70)
    print("批量测试科室维度工作量分配")
    print("="*70)
    print(f"配置文件: {config_file}\n")
    
    config = load_config(config_file)
    
    # 2. 加载科室分配结果
    with open("department_allocation_result.json", 'r', encoding='utf-8') as f:
        dept_allocations = json.load(f)
    
    # 3. 确定要测试的科室
    if dept_codes:
        test_depts = dept_codes
    else:
        test_depts = list(dept_allocations.keys())
        if limit:
            test_depts = test_depts[:limit]
    
    print(f"将测试 {len(test_depts)} 个科室\n")
    
    # 4. 获取数据库中的维度信息
    db = SessionLocal()
    try:
        model_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if not model_version:
            print("❌ 错误: 未找到激活的模型版本")
            return
        
        dimension_nodes = db.query(ModelNode).filter(
            ModelNode.version_id == model_version.id,
            ModelNode.node_type == "dimension"
        ).order_by(ModelNode.sort_order).all()
        
        print(f"模型版本: {model_version.name}")
        print(f"维度数量: {len(dimension_nodes)}\n")
        
    finally:
        db.close()
    
    # 5. 初始化AI生成器
    ai_config = load_ai_config_from_file(config)
    ai_generator = AIDataGenerator(
        prompts_file="ai_prompts.json",
        **ai_config
    )
    
    # 6. 批量测试
    results = {}
    success_count = 0
    fail_count = 0
    
    for idx, dept_code in enumerate(test_depts, 1):
        print("\n" + "="*70)
        print(f"[{idx}/{len(test_depts)}] 测试科室: {dept_code}")
        print("="*70)
        
        if dept_code not in dept_allocations:
            print(f"❌ 跳过: 未找到科室分配数据")
            fail_count += 1
            continue
        
        dept_allocation = dept_allocations[dept_code]
        dept_config = next((d for d in config['departments'] if d['his_code'] == dept_code), None)
        
        if not dept_config:
            print(f"❌ 跳过: 配置文件中未找到科室")
            fail_count += 1
            continue
        
        print(f"科室名称: {dept_config['his_name']}")
        print(f"科室类别: {dept_config['category']}")
        print(f"工作量比例: {dept_allocation['workload_based_ratio']:.1f}%")
        
        try:
            # 调用AI分配维度工作量
            dim_allocations = ai_generator.allocate_dimensions(
                dept_config,
                dept_allocation,
                dimension_nodes,
                config['total_workload']
            )
            
            # 统计结果
            total_workload = sum(alloc['workload'] for alloc in dim_allocations.values())
            non_zero_count = sum(1 for alloc in dim_allocations.values() if alloc['workload'] > 0)
            
            results[dept_code] = {
                'dept_name': dept_config['his_name'],
                'category': dept_config['category'],
                'total_workload': total_workload,
                'dimension_count': len(dim_allocations),
                'non_zero_count': non_zero_count,
                'allocations': dim_allocations
            }
            
            print(f"\n✓ 成功")
            print(f"  总工作量: {total_workload}")
            print(f"  分配维度数: {len(dim_allocations)}")
            print(f"  非零维度数: {non_zero_count}")
            
            success_count += 1
            
            # 保存单个科室结果
            output_file = f"dimension_allocation_{dept_code}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dim_allocations, f, ensure_ascii=False, indent=2)
            print(f"  结果已保存: {output_file}")
            
        except Exception as e:
            print(f"\n❌ 失败: {str(e)}")
            fail_count += 1
            import traceback
            traceback.print_exc()
    
    # 7. 输出汇总
    print("\n" + "="*70)
    print("测试汇总")
    print("="*70)
    print(f"总科室数: {len(test_depts)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    
    if results:
        print("\n各科室工作量分配:")
        for dept_code, result in results.items():
            print(f"  {dept_code} - {result['dept_name']}: 工作量={result['total_workload']}, 非零维度={result['non_zero_count']}")
    
    # 保存汇总结果
    summary_file = "dimension_allocation_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 汇总结果已保存: {summary_file}")
    
    return success_count == len(test_depts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量测试科室维度工作量分配")
    parser.add_argument(
        "--dept",
        nargs="+",
        help="指定要测试的科室代码（多个用空格分隔）"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="限制测试的科室数量"
    )
    
    args = parser.parse_args()
    
    try:
        success = test_all_dimensions(
            dept_codes=args.dept,
            limit=args.limit
        )
        
        if success:
            print("\n✅ 所有测试完成!")
        else:
            print("\n⚠️  部分测试失败")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
