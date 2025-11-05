"""
测试汇总表导出功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.export_service import ExportService
from decimal import Decimal


def test_export_summary():
    """测试导出汇总表"""
    
    # 模拟汇总数据
    summary_data = {
        'summary': {
            'department_id': 0,
            'department_name': '全院汇总',
            'doctor_value': Decimal('1500000.50'),
            'doctor_ratio': 45.50,
            'nurse_value': Decimal('1000000.30'),
            'nurse_ratio': 30.30,
            'tech_value': Decimal('800000.20'),
            'tech_ratio': 24.20,
            'total_value': Decimal('3300000.00')
        },
        'departments': [
            {
                'department_id': 1,
                'department_name': '内科',
                'doctor_value': Decimal('500000.00'),
                'doctor_ratio': 50.00,
                'nurse_value': Decimal('300000.00'),
                'nurse_ratio': 30.00,
                'tech_value': Decimal('200000.00'),
                'tech_ratio': 20.00,
                'total_value': Decimal('1000000.00')
            },
            {
                'department_id': 2,
                'department_name': '外科',
                'doctor_value': Decimal('600000.00'),
                'doctor_ratio': 48.00,
                'nurse_value': Decimal('400000.00'),
                'nurse_ratio': 32.00,
                'tech_value': Decimal('250000.00'),
                'tech_ratio': 20.00,
                'total_value': Decimal('1250000.00')
            },
            {
                'department_id': 3,
                'department_name': '儿科',
                'doctor_value': Decimal('400000.50'),
                'doctor_ratio': 38.10,
                'nurse_value': Decimal('300000.30'),
                'nurse_ratio': 28.57,
                'tech_value': Decimal('350000.20'),
                'tech_ratio': 33.33,
                'total_value': Decimal('1050000.00')
            }
        ]
    }
    
    period = "2025-10"
    
    print(f"开始生成汇总表Excel文件...")
    print(f"评估月份: {period}")
    print(f"科室数量: {len(summary_data['departments'])}")
    
    # 生成Excel
    excel_file = ExportService.export_summary_to_excel(summary_data, period)
    
    # 保存到文件
    output_path = f"科室业务价值汇总_{period}_测试.xlsx"
    with open(output_path, 'wb') as f:
        f.write(excel_file.getvalue())
    
    print(f"\n✅ Excel文件生成成功！")
    print(f"📁 文件路径: {os.path.abspath(output_path)}")
    print(f"📊 文件大小: {len(excel_file.getvalue())} 字节")
    
    print("\n请打开Excel文件检查以下内容：")
    print("1. 标题行：科室业务价值汇总（2025-10）")
    print("2. 表头：两层表头，序列分组正确")
    print("3. 全院汇总行：加粗高亮显示")
    print("4. 数据格式：")
    print("   - 价值列：千分位，2位小数")
    print("   - 占比列：百分比格式")
    print("5. 边框和对齐：所有单元格有边框，对齐正确")


if __name__ == "__main__":
    test_export_summary()
