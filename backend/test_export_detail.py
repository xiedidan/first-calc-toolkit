"""
测试明细表导出功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.export_service import ExportService
from decimal import Decimal


def test_export_detail():
    """测试导出明细表"""
    
    # 模拟明细数据（树形结构）
    detail_data = {
        'doctor': [
            {
                'id': 1,
                'dimension_name': '门诊诊疗',
                'workload': Decimal('500000'),
                'hospital_value': '-',
                'business_guide': '-',
                'dept_value': '-',
                'amount': Decimal('150000'),
                'ratio': Decimal('60.00'),
                'children': [
                    {
                        'id': 11,
                        'dimension_name': '普通门诊',
                        'workload': Decimal('300000'),
                        'hospital_value': '0.5',
                        'business_guide': '提高门诊量',
                        'dept_value': '0.5',
                        'amount': Decimal('90000'),
                        'ratio': Decimal('60.00')
                    },
                    {
                        'id': 12,
                        'dimension_name': '专家门诊',
                        'workload': Decimal('200000'),
                        'hospital_value': '0.3',
                        'business_guide': '提升专家服务',
                        'dept_value': '0.3',
                        'amount': Decimal('60000'),
                        'ratio': Decimal('40.00')
                    }
                ]
            },
            {
                'id': 2,
                'dimension_name': '住院诊疗',
                'workload': Decimal('800000'),
                'hospital_value': '-',
                'business_guide': '-',
                'dept_value': '-',
                'amount': Decimal('100000'),
                'ratio': Decimal('40.00'),
                'children': [
                    {
                        'id': 21,
                        'dimension_name': '床位使用',
                        'workload': Decimal('500000'),
                        'hospital_value': '0.15',
                        'business_guide': '提高床位周转',
                        'dept_value': '0.15',
                        'amount': Decimal('75000'),
                        'ratio': Decimal('75.00')
                    },
                    {
                        'id': 22,
                        'dimension_name': '手术治疗',
                        'workload': Decimal('300000'),
                        'hospital_value': '0.083',
                        'business_guide': '提升手术质量',
                        'dept_value': '0.083',
                        'amount': Decimal('25000'),
                        'ratio': Decimal('25.00')
                    }
                ]
            }
        ],
        'nurse': [
            {
                'id': 3,
                'dimension_name': '护理服务',
                'workload': Decimal('400000'),
                'hospital_value': '0.25',
                'business_guide': '提升护理质量',
                'dept_value': '0.25',
                'amount': Decimal('100000'),
                'ratio': Decimal('100.00')
            }
        ],
        'tech': [
            {
                'id': 4,
                'dimension_name': '检验检查',
                'workload': Decimal('600000'),
                'hospital_value': '0.167',
                'business_guide': '提高检验效率',
                'dept_value': '0.167',
                'amount': Decimal('100000'),
                'ratio': Decimal('100.00')
            }
        ]
    }
    
    period = "2025-10"
    dept_name = "内科"
    
    print(f"开始生成明细表Excel文件...")
    print(f"科室: {dept_name}")
    print(f"评估月份: {period}")
    print(f"序列数量: {len([k for k, v in detail_data.items() if v])}")
    
    # 生成单个科室的Excel
    excel_file = ExportService.export_detail_to_excel(dept_name, period, detail_data)
    
    # 保存到文件
    output_path = f"{dept_name}_业务价值明细_{period}_测试.xlsx"
    with open(output_path, 'wb') as f:
        f.write(excel_file.getvalue())
    
    print(f"\n✅ 单个科室Excel文件生成成功！")
    print(f"📁 文件路径: {os.path.abspath(output_path)}")
    print(f"📊 文件大小: {len(excel_file.getvalue())} 字节")
    
    # 测试ZIP打包
    print(f"\n开始生成ZIP打包文件...")
    
    departments_data = [
        {
            'dept_name': '内科',
            'doctor': detail_data['doctor'],
            'nurse': detail_data['nurse'],
            'tech': detail_data['tech']
        },
        {
            'dept_name': '外科',
            'doctor': detail_data['doctor'],
            'nurse': detail_data['nurse'],
            'tech': detail_data['tech']
        },
        {
            'dept_name': '儿科',
            'doctor': detail_data['doctor'],
            'nurse': [],
            'tech': detail_data['tech']
        }
    ]
    
    zip_file = ExportService.export_all_details_to_zip(period, departments_data)
    
    # 保存ZIP文件
    zip_path = f"业务价值明细表_{period}_测试.zip"
    with open(zip_path, 'wb') as f:
        f.write(zip_file.getvalue())
    
    print(f"\n✅ ZIP文件生成成功！")
    print(f"📁 文件路径: {os.path.abspath(zip_path)}")
    print(f"📊 文件大小: {len(zip_file.getvalue())} 字节")
    print(f"📦 包含文件: 3个科室的Excel文件")
    
    print("\n请检查以下内容：")
    print("1. 打开单个Excel文件：")
    print("   - 有3个Sheet（医生序列、护理序列、医技序列）")
    print("   - 标题行显示正确")
    print("   - 树形结构用缩进表示")
    print("   - 数据格式正确（千分位、百分比）")
    print("2. 解压ZIP文件：")
    print("   - 包含3个Excel文件")
    print("   - 文件名格式：科室名_业务价值明细_2025-10.xlsx")
    print("   - 每个文件都可以正常打开")


if __name__ == "__main__":
    test_export_detail()
