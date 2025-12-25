"""
对话消息导出服务单元测试

需求 12.1: 当用户导出指标口径结果时，智能数据问答模块应生成带有格式化表格的Markdown文件
需求 12.2: 当用户将指标口径结果导出为PDF时，智能数据问答模块应生成格式正确的PDF文档
需求 12.3: 当用户将查询数据导出为Excel时，智能数据问答模块应生成包含数据和列标题的Excel文件
需求 12.4: 当用户将查询数据导出为CSV时，智能数据问答模块应生成UTF-8编码的CSV文件
"""
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.conversation_export_service import ConversationExportService


def run_tests():
    print('=' * 60)
    print('对话消息导出服务单元测试')
    print('=' * 60)

    # 测试数据
    table_metadata = {
        'columns': ['指标名称', '业务口径', '源表', '维度'],
        'rows': [
            ['门诊收入', '门诊挂号费+诊疗费+检查费', 'TB_MZ_SFMXB', '科室、时间'],
            ['住院收入', '住院床位费+护理费+治疗费', 'TB_ZY_SFMXB', '科室、时间'],
            ['药品收入', '门诊药品+住院药品', 'TB_YP_SFMXB', '科室、药品类型'],
        ],
        'total_rows': 3
    }

    text_content = '''这是一段测试文本内容。

包含多行文本和一些**粗体**内容。

以及一些`代码`片段。'''

    code_metadata = {
        'language': 'sql',
        'code': '''SELECT 
    dept_name,
    SUM(amount) as total_amount
FROM charge_details
WHERE year_month = '2025-01'
GROUP BY dept_name
ORDER BY total_amount DESC;'''
    }

    results = []

    # 测试1: Markdown导出 - 文本
    print('\n测试1: Markdown导出 - 文本')
    try:
        result = ConversationExportService.export_to_markdown(text_content, 'text', None, '文本测试')
        content = result.getvalue().decode('utf-8')
        assert '# 文本测试' in content
        assert '导出时间' in content
        assert '测试文本内容' in content
        print(f'  ✓ 通过 - 大小: {len(result.getvalue())} bytes')
        results.append(('Markdown-文本', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('Markdown-文本', False))

    # 测试2: Markdown导出 - 表格
    print('\n测试2: Markdown导出 - 表格')
    try:
        result = ConversationExportService.export_to_markdown('', 'table', table_metadata, '指标口径查询')
        content = result.getvalue().decode('utf-8')
        assert '| 指标名称 | 业务口径 | 源表 | 维度 |' in content
        assert '| --- | --- | --- | --- |' in content
        assert '门诊收入' in content
        assert '共 3 条记录' in content
        print(f'  ✓ 通过 - 大小: {len(result.getvalue())} bytes')
        results.append(('Markdown-表格', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('Markdown-表格', False))

    # 测试3: Markdown导出 - 代码
    print('\n测试3: Markdown导出 - 代码')
    try:
        result = ConversationExportService.export_to_markdown('', 'code', code_metadata, 'SQL代码')
        content = result.getvalue().decode('utf-8')
        assert '```sql' in content
        assert 'SELECT' in content
        assert '```' in content
        print(f'  ✓ 通过 - 大小: {len(result.getvalue())} bytes')
        results.append(('Markdown-代码', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('Markdown-代码', False))

    # 测试4: PDF导出 - 文本
    print('\n测试4: PDF导出 - 文本')
    try:
        result = ConversationExportService.export_to_pdf(text_content, 'text', None, '文本测试')
        content = result.getvalue()
        assert content[:4] == b'%PDF'  # PDF文件头
        print(f'  ✓ 通过 - 大小: {len(content)} bytes')
        results.append(('PDF-文本', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('PDF-文本', False))

    # 测试5: PDF导出 - 表格
    print('\n测试5: PDF导出 - 表格')
    try:
        result = ConversationExportService.export_to_pdf('', 'table', table_metadata, '指标口径查询')
        content = result.getvalue()
        assert content[:4] == b'%PDF'
        print(f'  ✓ 通过 - 大小: {len(content)} bytes')
        results.append(('PDF-表格', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('PDF-表格', False))

    # 测试6: Excel导出 - 表格
    print('\n测试6: Excel导出 - 表格')
    try:
        result = ConversationExportService.export_to_excel('', 'table', table_metadata, '指标口径查询')
        content = result.getvalue()
        # Excel文件以PK开头（ZIP格式）
        assert content[:2] == b'PK'
        print(f'  ✓ 通过 - 大小: {len(content)} bytes')
        results.append(('Excel-表格', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('Excel-表格', False))

    # 测试7: CSV导出 - 表格
    print('\n测试7: CSV导出 - 表格')
    try:
        result = ConversationExportService.export_to_csv('', 'table', table_metadata)
        content = result.getvalue().decode('utf-8')
        # 检查内容
        assert '指标名称' in content
        assert '门诊收入' in content
        assert '住院收入' in content
        print(f'  ✓ 通过 - 大小: {len(result.getvalue())} bytes')
        results.append(('CSV-表格', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('CSV-表格', False))

    # 测试8: export_message统一接口
    print('\n测试8: export_message统一接口')
    try:
        for fmt in ['markdown', 'pdf', 'excel', 'csv']:
            file_data, ext, mime = ConversationExportService.export_message(
                content='',
                content_type='table',
                export_format=fmt,
                metadata=table_metadata,
                title='测试'
            )
            assert file_data is not None
            assert ext in ['.md', '.pdf', '.xlsx', '.csv']
            assert mime is not None
        print(f'  ✓ 通过 - 所有格式导出正常')
        results.append(('统一接口', True))
    except Exception as e:
        print(f'  ✗ 失败: {e}')
        results.append(('统一接口', False))

    # 测试9: 无效格式处理
    print('\n测试9: 无效格式处理')
    try:
        ConversationExportService.export_message('', 'text', 'invalid', None, None)
        print(f'  ✗ 失败 - 应该抛出ValueError')
        results.append(('无效格式', False))
    except ValueError as e:
        print(f'  ✓ 通过 - 正确抛出ValueError: {e}')
        results.append(('无效格式', True))
    except Exception as e:
        print(f'  ✗ 失败 - 错误类型不对: {e}')
        results.append(('无效格式', False))

    # 汇总
    print('\n' + '=' * 60)
    print('测试结果汇总')
    print('=' * 60)
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    for name, result in results:
        status = '✓ 通过' if result else '✗ 失败'
        print(f'{name}: {status}')
    print(f'\n总计: {passed} 通过, {failed} 失败')

    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
