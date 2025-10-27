"""
测试维度目录智能导入功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dimension_import_service import DimensionImportService
from app.database import SessionLocal
import openpyxl
from io import BytesIO


def create_test_excel():
    """创建测试Excel文件"""
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # 表头
    ws.append(["收费编码", "收费名称", "维度预案", "专家意见"])
    
    # 测试数据
    test_data = [
        ["CK001", "血常规", "检验项目", "4D"],
        ["CK002", "尿常规", "检验项目", ""],
        ["SS001", "阑尾切除术", "甲级手术D", "4D"],
        ["SS002", "胆囊切除术", "", "4D"],
        ["ZL001", "换药", "护理操作", ""],
    ]
    
    for row in test_data:
        ws.append(row)
    
    # 保存到BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def test_parse_excel():
    """测试第一步：解析Excel"""
    print("\n=== 测试第一步：解析Excel ===")
    
    file_content = create_test_excel()
    result = DimensionImportService.parse_excel(file_content)
    
    print(f"会话ID: {result['session_id']}")
    print(f"表头: {result['headers']}")
    print(f"总行数: {result['total_rows']}")
    print(f"建议映射: {result['suggested_mapping']}")
    print(f"预览数据（前3行）:")
    for i, row in enumerate(result['preview_data'][:3], 1):
        print(f"  {i}. {row}")
    
    return result['session_id']


def test_extract_values(session_id: str):
    """测试第二步：提取唯一值"""
    print("\n=== 测试第二步：提取唯一值 ===")
    
    db = SessionLocal()
    try:
        field_mapping = {
            "item_code": "收费编码",
            "dimension_plan": "维度预案",
            "expert_opinion": "专家意见"
        }
        
        result = DimensionImportService.extract_unique_values(
            session_id=session_id,
            field_mapping=field_mapping,
            model_version_id=1,  # 假设存在ID为1的模型版本
            db=db
        )
        
        print(f"唯一值数量: {len(result['unique_values'])}")
        print(f"系统维度数量: {len(result['system_dimensions'])}")
        
        print("\n唯一值列表:")
        for item in result['unique_values']:
            print(f"  - {item['value']} ({item['source']}, 出现{item['count']}次)")
            if item['suggested_dimensions']:
                print(f"    建议维度: {item['suggested_dimensions'][0]['full_path']}")
        
        return result
    finally:
        db.close()


def test_generate_preview(session_id: str, extract_result: dict):
    """测试第三步：生成预览"""
    print("\n=== 测试第三步：生成预览 ===")
    
    db = SessionLocal()
    try:
        # 构建值映射（使用第一个建议的维度）
        value_mapping = []
        for item in extract_result['unique_values']:
            if item['suggested_dimensions']:
                value_mapping.append({
                    "value": item['value'],
                    "source": item['source'],
                    "dimension_ids": [item['suggested_dimensions'][0]['id']]
                })
        
        result = DimensionImportService.generate_preview(
            session_id=session_id,
            value_mapping=value_mapping,
            db=db
        )
        
        stats = result['statistics']
        print(f"统计信息:")
        print(f"  总数: {stats['total']}")
        print(f"  正常: {stats['ok']}")
        print(f"  警告: {stats['warning']}")
        print(f"  错误: {stats['error']}")
        
        print(f"\n预览数据（前5条）:")
        for i, item in enumerate(result['preview_items'][:5], 1):
            print(f"  {i}. {item['item_code']} -> {item['dimension_path']} [{item['status']}]")
            if item['message']:
                print(f"     提示: {item['message']}")
        
        return result
    finally:
        db.close()


def test_execute_import(session_id: str):
    """测试第四步：执行导入"""
    print("\n=== 测试第四步：执行导入 ===")
    
    db = SessionLocal()
    try:
        result = DimensionImportService.execute_import(
            session_id=session_id,
            confirmed_items=None,  # 导入所有预览项
            db=db
        )
        
        report = result['report']
        print(f"导入结果:")
        print(f"  成功: {report['success_count']}")
        print(f"  跳过: {report['skipped_count']}")
        print(f"  错误: {report['error_count']}")
        
        if report['errors']:
            print(f"\n错误详情:")
            for error in report['errors'][:5]:
                print(f"  - {error['item_code']}: {error['reason']}")
        
        return result
    finally:
        db.close()


def main():
    """主测试流程"""
    print("开始测试维度目录智能导入功能")
    print("=" * 50)
    
    try:
        # 第一步：解析Excel
        session_id = test_parse_excel()
        
        # 第二步：提取唯一值
        extract_result = test_extract_values(session_id)
        
        # 第三步：生成预览
        preview_result = test_generate_preview(session_id, extract_result)
        
        # 第四步：执行导入（可选，取消注释以执行实际导入）
        # execute_result = test_execute_import(session_id)
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
