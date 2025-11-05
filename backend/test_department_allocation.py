"""
测试科室工作量分配

使用方法：
    python test_department_allocation.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from populate_report_data_ai import AIDataGenerator, load_config, resolve_env_variable, load_ai_config_from_file


def test_department_allocation():
    """测试科室工作量分配"""
    print("="*70)
    print("测试科室工作量分配")
    print("="*70)
    
    # 1. 加载配置
    config_file = "report_data_config_real.json"
    print(f"\n1. 加载配置文件: {config_file}")
    config = load_config(config_file)
    
    # 2. 初始化AI生成器
    print("\n2. 初始化AI生成器")
    ai_config = load_ai_config_from_file(config)
    ai_generator = AIDataGenerator(
        prompts_file="ai_prompts.json",
        **ai_config
    )
    
    # 3. 调用AI分配科室工作量
    print("\n3. 调用AI分配科室工作量")
    print("-"*70)
    dept_allocations = ai_generator.allocate_departments(config)
    
    # 4. 输出结果
    print("\n" + "="*70)
    print("分配结果汇总")
    print("="*70)
    
    # 统计各类型工作量的总和
    totals = {
        'workload_based_ratio': 0,
        'consultation_ratio': 0,
        'mdt_ratio': 0,
        'case_ratio': 0,
        'nursing_bed_days_ratio': 0,
        'surgery_ratio': 0,
        'observation_ratio': 0
    }
    
    # 按科室类别分组
    by_category = {}
    
    for his_code, alloc in dept_allocations.items():
        # 累加总和
        for key in totals.keys():
            totals[key] += alloc.get(key, 0)
        
        # 按类别分组
        dept_config = next((d for d in config['departments'] if d['his_code'] == his_code), None)
        if dept_config:
            category = dept_config['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(alloc)
    
    # 输出总和验证
    print("\n各项工作量比例总和（应该都是100%）：")
    print("-"*70)
    for key, value in totals.items():
        status = "✓" if abs(value - 100) < 0.1 else "❌"
        print(f"{status} {key}: {value:.2f}%")
    
    # 按类别输出
    print("\n" + "="*70)
    print("按科室类别分组")
    print("="*70)
    
    for category, allocs in sorted(by_category.items()):
        print(f"\n【{category}】（{len(allocs)}个科室）")
        print("-"*70)
        
        # 计算该类别的工作量总和
        category_totals = {
            'workload_based_ratio': 0,
            'consultation_ratio': 0,
            'mdt_ratio': 0,
            'case_ratio': 0,
            'nursing_bed_days_ratio': 0,
            'surgery_ratio': 0,
            'observation_ratio': 0
        }
        
        for alloc in allocs:
            print(f"\n{alloc['his_code']} - {alloc['his_name']}")
            print(f"  工作量: {alloc['workload_based_ratio']:.1f}%")
            print(f"  会诊: {alloc['consultation_ratio']:.1f}%")
            print(f"  MDT: {alloc['mdt_ratio']:.1f}%")
            print(f"  病案: {alloc['case_ratio']:.1f}%")
            print(f"  床日: {alloc['nursing_bed_days_ratio']:.1f}%")
            print(f"  手术: {alloc['surgery_ratio']:.1f}%")
            print(f"  留观: {alloc['observation_ratio']:.1f}%")
            print(f"  理由: {alloc['reasoning']}")
            
            for key in category_totals.keys():
                category_totals[key] += alloc.get(key, 0)
        
        print(f"\n{category} 小计:")
        print(f"  工作量: {category_totals['workload_based_ratio']:.1f}%")
        print(f"  会诊: {category_totals['consultation_ratio']:.1f}%")
        print(f"  MDT: {category_totals['mdt_ratio']:.1f}%")
        print(f"  病案: {category_totals['case_ratio']:.1f}%")
        print(f"  床日: {category_totals['nursing_bed_days_ratio']:.1f}%")
        print(f"  手术: {category_totals['surgery_ratio']:.1f}%")
        print(f"  留观: {category_totals['observation_ratio']:.1f}%")
    
    # 保存结果到文件
    output_file = "department_allocation_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dept_allocations, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*70)
    print(f"✓ 结果已保存到: {output_file}")
    print("="*70)
    
    return dept_allocations


if __name__ == "__main__":
    try:
        result = test_department_allocation()
        print("\n✅ 测试完成!")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
