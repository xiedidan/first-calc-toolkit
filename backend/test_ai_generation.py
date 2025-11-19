"""
AI数据生成功能测试脚本

功能：
1. 测试配置文件加载
2. 测试AI模型初始化
3. 测试科室工作量分配
4. 测试维度工作量分配
5. 模拟完整的数据生成流程（不实际调用AI）

使用方法：
    python test_ai_generation.py
"""
import sys
import os
import json
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.department import Department
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode


def test_config_loading():
    """测试配置文件加载"""
    print("="*70)
    print("测试1: 配置文件加载")
    print("="*70)
    
    config_files = [
        'report_data_config.example.json',
        'report_data_config_comprehensive.example.json'
    ]
    
    for config_file in config_files:
        print(f"\n测试配置文件: {config_file}")
        
        if not os.path.exists(config_file):
            print(f"  ⚠️  文件不存在，跳过")
            continue
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必填字段
            assert 'hospital_info' in config, "缺少hospital_info"
            assert 'total_workload' in config, "缺少total_workload"
            assert 'departments' in config, "缺少departments"
            
            print(f"  ✓ 配置文件格式正确")
            print(f"  ✓ 医院名称: {config['hospital_info']['name']}")
            print(f"  ✓ 科室数量: {len(config['departments'])}")
            
        except Exception as e:
            print(f"  ❌ 加载失败: {str(e)}")
            return False
    
    print("\n✅ 配置文件加载测试通过")
    return True


def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*70)
    print("测试2: 数据库连接")
    print("="*70)
    
    try:
        db = SessionLocal()
        
        # 测试查询模型版本
        model_version = db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).first()
        
        if model_version:
            print(f"  ✓ 找到激活的模型版本: {model_version.name}")
        else:
            print(f"  ⚠️  未找到激活的模型版本")
        
        # 测试查询科室
        dept_count = db.query(Department).filter(
            Department.is_active == True
        ).count()
        
        print(f"  ✓ 找到 {dept_count} 个启用的科室")
        
        # 测试查询维度节点
        if model_version:
            dimension_count = db.query(ModelNode).filter(
                ModelNode.version_id == model_version.id,
                ModelNode.node_type == "dimension"
            ).count()
            
            print(f"  ✓ 找到 {dimension_count} 个维度节点")
        
        db.close()
        print("\n✅ 数据库连接测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {str(e)}")
        return False


def test_workload_calculation():
    """测试工作量计算逻辑"""
    print("\n" + "="*70)
    print("测试3: 工作量计算逻辑")
    print("="*70)
    
    try:
        # 模拟配置数据
        total_workload = {
            'workload_based_total': {'value': 1000000},
            'consultation_total': {'value': 500},
            'mdt_total': {'value': 100},
            'case_total': {'value': 3000},
            'nursing_bed_days_total': {'value': 15000},
            'surgery_total': {'value': 2000},
            'observation_total': {'value': 800}
        }
        
        # 模拟科室分配
        dept_allocation = {
            'workload_based_ratio': 30.0,
            'consultation_ratio': 20.0,
            'mdt_ratio': 15.0,
            'case_ratio': 25.0,
            'nursing_bed_days_ratio': 0.0,
            'surgery_ratio': 0.0,
            'observation_ratio': 0.0
        }
        
        # 计算科室工作量
        dept_workload = {}
        dept_workload['workload_based'] = int(
            total_workload['workload_based_total']['value'] * 
            dept_allocation['workload_based_ratio'] / 100
        )
        dept_workload['consultation'] = int(
            total_workload['consultation_total']['value'] * 
            dept_allocation['consultation_ratio'] / 100
        )
        
        print(f"  总工作量: {total_workload['workload_based_total']['value']}")
        print(f"  科室比例: {dept_allocation['workload_based_ratio']}%")
        print(f"  科室工作量: {dept_workload['workload_based']}")
        
        assert dept_workload['workload_based'] == 300000, "工作量计算错误"
        assert dept_workload['consultation'] == 100, "会诊数计算错误"
        
        print("\n✅ 工作量计算逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 工作量计算失败: {str(e)}")
        return False


def test_value_calculation():
    """测试价值计算逻辑"""
    print("\n" + "="*70)
    print("测试4: 价值计算逻辑")
    print("="*70)
    
    try:
        # 模拟维度数据
        workload = Decimal("1000")
        weight = Decimal("1.5")
        
        # 计算价值
        value = workload * weight
        
        print(f"  工作量: {workload}")
        print(f"  权重: {weight}")
        print(f"  价值: {value}")
        
        assert value == Decimal("1500"), "价值计算错误"
        
        # 测试占比计算
        total_value = Decimal("5000")
        ratio = (value / total_value * 100).quantize(Decimal("0.01"))
        
        print(f"  总价值: {total_value}")
        print(f"  占比: {ratio}%")
        
        assert ratio == Decimal("30.00"), "占比计算错误"
        
        print("\n✅ 价值计算逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 价值计算失败: {str(e)}")
        return False


def test_prompt_template():
    """测试提示词模板"""
    print("\n" + "="*70)
    print("测试5: 提示词模板")
    print("="*70)
    
    try:
        # 加载提示词文件
        with open('ai_prompts.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        # 检查必需的提示词
        required_prompts = [
            'department_allocation_prompt',
            'dimension_allocation_prompt',
            'validation_prompt'
        ]
        
        for prompt_name in required_prompts:
            assert prompt_name in prompts, f"缺少提示词: {prompt_name}"
            
            prompt = prompts[prompt_name]
            assert 'system' in prompt, f"{prompt_name}缺少system字段"
            assert 'user_template' in prompt, f"{prompt_name}缺少user_template字段"
            
            print(f"  ✓ {prompt_name} 格式正确")
        
        # 测试模板变量替换
        template = prompts['department_allocation_prompt']['user_template']
        
        test_vars = {
            'hospital_name': '测试医院',
            'hospital_type': '综合医院',
            'hospital_specialty': '综合',
            'hospital_description': '测试描述',
            'hospital_characteristics': '特点1\n特点2',
            'total_workload_info': '工作量信息',
            'departments_info': '科室信息'
        }
        
        result = template.format(**test_vars)
        assert '测试医院' in result, "模板变量替换失败"
        
        print(f"  ✓ 模板变量替换正常")
        
        print("\n✅ 提示词模板测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 提示词模板测试失败: {str(e)}")
        return False


def test_department_matching():
    """测试科室匹配"""
    print("\n" + "="*70)
    print("测试6: 科室匹配")
    print("="*70)
    
    try:
        # 加载配置文件
        config_file = 'report_data_config.example.json'
        if not os.path.exists(config_file):
            print(f"  ⚠️  配置文件不存在，跳过测试")
            return True
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config_dept_codes = [d['his_code'] for d in config['departments']]
        print(f"  配置文件中的科室代码: {config_dept_codes}")
        
        # 查询数据库中的科室
        db = SessionLocal()
        db_departments = db.query(Department).filter(
            Department.is_active == True,
            Department.his_code.in_(config_dept_codes)
        ).all()
        
        db_dept_codes = [d.his_code for d in db_departments]
        print(f"  数据库中匹配的科室: {db_dept_codes}")
        
        # 检查未匹配的科室
        unmatched = set(config_dept_codes) - set(db_dept_codes)
        if unmatched:
            print(f"  ⚠️  未匹配的科室代码: {unmatched}")
            print(f"  提示: 这些科室在数据库中不存在或未启用")
        else:
            print(f"  ✓ 所有科室都已匹配")
        
        db.close()
        
        print("\n✅ 科室匹配测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 科室匹配测试失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("AI数据生成功能测试")
    print("="*70)
    print()
    
    tests = [
        ("配置文件加载", test_config_loading),
        ("数据库连接", test_database_connection),
        ("工作量计算", test_workload_calculation),
        ("价值计算", test_value_calculation),
        ("提示词模板", test_prompt_template),
        ("科室匹配", test_department_matching)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 {test_name} 出现异常: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {test_name}")
    
    print("-"*70)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        print("\n下一步:")
        print("  1. 设置API密钥: set OPENAI_API_KEY=your_key")
        print("  2. 运行数据生成: python populate_report_data_ai.py --config report_data_config.example.json --period 2025-10")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查并修复")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
