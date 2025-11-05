"""
配置文件验证脚本

功能：
1. 验证配置文件格式是否正确
2. 检查必填字段是否完整
3. 检查数据类型是否正确
4. 输出验证报告

使用方法：
    python validate_config.py report_data_config.json
"""
import sys
import json
from typing import Dict, List, Tuple


def validate_hospital_info(hospital_info: dict) -> Tuple[bool, List[str]]:
    """验证医院信息"""
    errors = []
    
    required_fields = ['name', 'type', 'specialty', 'description', 'characteristics']
    for field in required_fields:
        if field not in hospital_info:
            errors.append(f"医院信息缺少必填字段: {field}")
    
    if 'characteristics' in hospital_info:
        if not isinstance(hospital_info['characteristics'], list):
            errors.append("医院特点(characteristics)必须是数组")
        elif len(hospital_info['characteristics']) == 0:
            errors.append("医院特点(characteristics)不能为空")
    
    return len(errors) == 0, errors


def validate_total_workload(total_workload: dict) -> Tuple[bool, List[str]]:
    """验证总工作量"""
    errors = []
    
    required_items = [
        'workload_based_total',
        'consultation_total',
        'mdt_total',
        'case_total',
        'nursing_bed_days_total',
        'surgery_total',
        'observation_total'
    ]
    
    for item in required_items:
        if item not in total_workload:
            errors.append(f"总工作量缺少必填项: {item}")
        else:
            item_data = total_workload[item]
            if 'value' not in item_data:
                errors.append(f"{item}缺少value字段")
            elif not isinstance(item_data['value'], (int, float)):
                errors.append(f"{item}的value必须是数字")
            elif item_data['value'] < 0:
                errors.append(f"{item}的value不能为负数")
            
            if 'description' not in item_data:
                errors.append(f"{item}缺少description字段")
    
    return len(errors) == 0, errors


def validate_departments(departments: list) -> Tuple[bool, List[str]]:
    """验证科室信息"""
    errors = []
    warnings = []
    
    if not isinstance(departments, list):
        errors.append("科室信息(departments)必须是数组")
        return False, errors
    
    if len(departments) == 0:
        errors.append("科室信息(departments)不能为空")
        return False, errors
    
    his_codes = set()
    valid_categories = ['医生专科', '护理病区', '护理非病区', '医技科室', '行政后勤']
    
    for idx, dept in enumerate(departments):
        dept_name = dept.get('his_name', f'科室{idx+1}')
        
        # 检查必填字段
        required_fields = ['his_code', 'his_name', 'category', 'business_characteristics', 'constraints']
        for field in required_fields:
            if field not in dept:
                errors.append(f"科室 {dept_name} 缺少必填字段: {field}")
        
        # 检查科室代码唯一性
        if 'his_code' in dept:
            if dept['his_code'] in his_codes:
                errors.append(f"科室代码重复: {dept['his_code']}")
            his_codes.add(dept['his_code'])
        
        # 检查科室类别
        if 'category' in dept:
            if dept['category'] not in valid_categories:
                warnings.append(f"科室 {dept_name} 的类别 '{dept['category']}' 不在标准类别中")
        
        # 检查约束条件
        if 'constraints' in dept:
            if not isinstance(dept['constraints'], list):
                errors.append(f"科室 {dept_name} 的约束条件(constraints)必须是数组")
            elif len(dept['constraints']) == 0:
                warnings.append(f"科室 {dept_name} 没有设置约束条件")
    
    return len(errors) == 0, errors + warnings


def validate_ai_config(ai_config: dict) -> Tuple[bool, List[str]]:
    """验证AI配置"""
    errors = []
    warnings = []
    
    # API密钥检查
    if 'api_key' not in ai_config:
        errors.append("AI配置缺少api_key字段")
    elif not ai_config['api_key']:
        warnings.append("api_key为空，请确保已设置环境变量")
    elif ai_config['api_key'].startswith('${'):
        # 环境变量格式，检查是否能解析
        import re
        import os
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, ai_config['api_key'])
        if matches:
            var_name = matches[0]
            if not os.getenv(var_name):
                warnings.append(f"环境变量 {var_name} 未设置")
    
    # 模型检查
    if 'model' not in ai_config:
        warnings.append("AI配置缺少model字段，将使用默认值")
    
    # base_url检查
    if 'base_url' in ai_config:
        if not ai_config['base_url'].startswith('http'):
            errors.append("base_url必须以http或https开头")
    
    # 参数范围检查
    if 'temperature' in ai_config:
        temp = ai_config['temperature']
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            errors.append("temperature必须在0-2之间")
    
    if 'max_tokens' in ai_config:
        if not isinstance(ai_config['max_tokens'], int) or ai_config['max_tokens'] <= 0:
            errors.append("max_tokens必须是正整数")
    
    if 'timeout' in ai_config:
        if not isinstance(ai_config['timeout'], int) or ai_config['timeout'] <= 0:
            errors.append("timeout必须是正整数")
    
    return len(errors) == 0, errors + warnings


def validate_config(config_file: str) -> bool:
    """验证配置文件"""
    print("="*70)
    print("配置文件验证")
    print("="*70)
    print(f"配置文件: {config_file}\n")
    
    # 1. 读取配置文件
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ 配置文件格式正确（有效的JSON）\n")
    except FileNotFoundError:
        print(f"❌ 错误: 配置文件不存在: {config_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ 错误: 配置文件格式错误: {str(e)}")
        return False
    
    all_valid = True
    all_errors = []
    all_warnings = []
    
    # 2. 验证AI配置（可选）
    if 'ai_config' in config:
        print("-"*70)
        print("验证AI配置...")
        print("-"*70)
        valid, messages = validate_ai_config(config['ai_config'])
        if valid:
            print("✓ AI配置验证通过")
            if 'model' in config['ai_config']:
                print(f"  模型: {config['ai_config']['model']}")
            if 'base_url' in config['ai_config']:
                print(f"  端点: {config['ai_config']['base_url']}")
            
            # 显示警告
            warnings = [m for m in messages if '警告' in m or '未设置' in m or '为空' in m]
            if warnings:
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
                    all_warnings.append(warning)
        else:
            print("❌ AI配置验证失败")
            all_valid = False
            all_errors.extend([m for m in messages if m not in all_warnings])
        print()
    else:
        print("⚠️  配置文件中未找到ai_config，将使用命令行参数或环境变量\n")
    
    # 3. 验证顶层结构
    required_sections = ['hospital_info', 'total_workload', 'departments']
    for section in required_sections:
        if section not in config:
            all_errors.append(f"配置文件缺少必填部分: {section}")
            all_valid = False
    
    if not all_valid and all_errors:
        print("❌ 配置文件结构不完整\n")
        for error in all_errors:
            print(f"  - {error}")
        return False
    
    # 3. 验证医院信息
    print("-"*70)
    print("验证医院信息...")
    print("-"*70)
    valid, messages = validate_hospital_info(config['hospital_info'])
    if valid:
        print("✓ 医院信息验证通过")
        print(f"  医院名称: {config['hospital_info']['name']}")
        print(f"  医院类型: {config['hospital_info']['type']}")
        print(f"  医院特色: {config['hospital_info']['specialty']}")
    else:
        print("❌ 医院信息验证失败")
        all_valid = False
        all_errors.extend(messages)
    print()
    
    # 4. 验证总工作量
    print("-"*70)
    print("验证总工作量...")
    print("-"*70)
    valid, messages = validate_total_workload(config['total_workload'])
    if valid:
        print("✓ 总工作量验证通过")
        for key, data in config['total_workload'].items():
            print(f"  {data['description']}: {data['value']}")
    else:
        print("❌ 总工作量验证失败")
        all_valid = False
        all_errors.extend(messages)
    print()
    
    # 5. 验证科室信息
    print("-"*70)
    print("验证科室信息...")
    print("-"*70)
    valid, messages = validate_departments(config['departments'])
    if valid:
        print(f"✓ 科室信息验证通过（共 {len(config['departments'])} 个科室）")
        
        # 统计科室类别
        category_count = {}
        for dept in config['departments']:
            category = dept.get('category', '未知')
            category_count[category] = category_count.get(category, 0) + 1
        
        print("\n科室类别统计:")
        for category, count in sorted(category_count.items()):
            print(f"  {category}: {count}个")
        
        # 显示警告
        warnings = [m for m in messages if '警告' in m or '不在标准类别' in m or '没有设置' in m]
        if warnings:
            print("\n⚠️  警告:")
            for warning in warnings:
                print(f"  - {warning}")
                all_warnings.append(warning)
    else:
        print("❌ 科室信息验证失败")
        all_valid = False
        all_errors.extend([m for m in messages if m not in all_warnings])
    print()
    
    # 6. 输出验证结果
    print("="*70)
    if all_valid:
        print("✅ 配置文件验证通过!")
        if all_warnings:
            print(f"\n⚠️  发现 {len(all_warnings)} 个警告（不影响使用）:")
            for warning in all_warnings:
                print(f"  - {warning}")
    else:
        print("❌ 配置文件验证失败!")
        print(f"\n发现 {len(all_errors)} 个错误:")
        for error in all_errors:
            print(f"  - {error}")
    print("="*70)
    
    return all_valid


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_config.py <配置文件路径>")
        print("\n示例:")
        print("  python validate_config.py report_data_config.json")
        print("  python validate_config.py report_data_config.example.json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        success = validate_config(config_file)
        
        if success:
            print("\n💡 下一步:")
            print("  使用此配置文件运行AI数据生成:")
            print(f"  python populate_report_data_ai.py --config {config_file} --period 2025-10")
        else:
            print("\n💡 请修复上述错误后重新验证")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
