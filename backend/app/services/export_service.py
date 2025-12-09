"""
报表导出服务
"""
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from io import BytesIO
from typing import List, Dict, Any
from decimal import Decimal
import zipfile


class ExportService:
    """报表导出服务"""
    
    @staticmethod
    def export_summary_to_excel(summary_data: dict, period: str, hospital_name: str = None) -> BytesIO:
        """
        导出汇总表到Excel
        
        Args:
            summary_data: 汇总数据，包含summary和departments
            period: 评估月份
            
        Returns:
            BytesIO: Excel文件的字节流
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "汇总表"
        
        # 设置列宽（增加10%）
        ws.column_dimensions['A'].width = 15  # 科室代码
        ws.column_dimensions['B'].width = 22  # 科室名称 (20 * 1.1)
        ws.column_dimensions['C'].width = 16.5  # 医生价值 (15 * 1.1)
        ws.column_dimensions['D'].width = 13  # 医生占比 (12 * 1.1)
        ws.column_dimensions['E'].width = 16.5  # 护理价值 (15 * 1.1)
        ws.column_dimensions['F'].width = 13  # 护理占比 (12 * 1.1)
        ws.column_dimensions['G'].width = 16.5  # 医技价值 (15 * 1.1)
        ws.column_dimensions['H'].width = 13  # 医技占比 (12 * 1.1)
        ws.column_dimensions['I'].width = 20  # 科室总价值 (18 * 1.1)
        
        # 标题行
        title_cell = ws.cell(row=1, column=1, value=f"科室业务价值汇总（{period}）")
        title_cell.font = Font(name='微软雅黑', size=14, bold=True)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.merge_cells('A1:I1')
        ws.row_dimensions[1].height = 30
        
        # 表头样式
        header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 第一层表头（序列分组）
        row = 2
        ws.merge_cells(f'A{row}:A{row+1}')  # 科室代码
        ws.cell(row=row, column=1, value='科室代码')
        
        ws.merge_cells(f'B{row}:B{row+1}')  # 科室名称
        ws.cell(row=row, column=2, value='科室名称')
        
        ws.merge_cells(f'C{row}:D{row}')  # 医生序列
        ws.cell(row=row, column=3, value='医生序列')
        
        ws.merge_cells(f'E{row}:F{row}')  # 护理序列
        ws.cell(row=row, column=5, value='护理序列')
        
        ws.merge_cells(f'G{row}:H{row}')  # 医技序列
        ws.cell(row=row, column=7, value='医技序列')
        
        ws.merge_cells(f'I{row}:I{row+1}')  # 科室总价值
        ws.cell(row=row, column=9, value='科室总价值')
        
        # 第二层表头（价值/占比）
        row = 3
        ws.cell(row=row, column=3, value='价值')
        ws.cell(row=row, column=4, value='占比')
        ws.cell(row=row, column=5, value='价值')
        ws.cell(row=row, column=6, value='占比')
        ws.cell(row=row, column=7, value='价值')
        ws.cell(row=row, column=8, value='占比')
        
        # 应用表头样式
        for r in [2, 3]:
            for c in range(1, 10):
                cell = ws.cell(row=r, column=c)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
        
        ws.row_dimensions[2].height = 25
        ws.row_dimensions[3].height = 25
        
        # 数据行样式
        data_alignment_left = Alignment(horizontal='left', vertical='center')
        data_alignment_right = Alignment(horizontal='right', vertical='center')
        data_alignment_center = Alignment(horizontal='center', vertical='center')
        
        # 全院汇总样式（高亮）
        summary_font = Font(name='微软雅黑', size=11, bold=True)
        summary_fill = PatternFill(start_color='E7E6E6', end_color='E7E6E6', fill_type='solid')
        
        # 普通数据样式
        normal_font = Font(name='微软雅黑', size=10)
        
        # 写入数据
        row = 4
        
        # 全院汇总行
        summary = summary_data['summary']
        ws.cell(row=row, column=1, value=summary.get('department_code') or '')
        ws.cell(row=row, column=2, value=summary['department_name'])
        ws.cell(row=row, column=3, value=float(summary['doctor_value']))
        ws.cell(row=row, column=4, value=float(summary['doctor_ratio']) / 100)
        ws.cell(row=row, column=5, value=float(summary['nurse_value']))
        ws.cell(row=row, column=6, value=float(summary['nurse_ratio']) / 100)
        ws.cell(row=row, column=7, value=float(summary['tech_value']))
        ws.cell(row=row, column=8, value=float(summary['tech_ratio']) / 100)
        ws.cell(row=row, column=9, value=float(summary['total_value']))
        
        # 应用全院汇总样式
        for c in range(1, 10):
            cell = ws.cell(row=row, column=c)
            cell.font = summary_font
            cell.fill = summary_fill
            cell.border = border
            
            if c in [1, 2]:
                cell.alignment = data_alignment_left
            elif c in [4, 6, 8]:  # 占比列
                cell.alignment = data_alignment_center
                cell.number_format = '0.00%'
            else:  # 价值列
                cell.alignment = data_alignment_right
                cell.number_format = '#,##0.00'
        
        ws.row_dimensions[row].height = 22
        row += 1
        
        # 各科室数据行
        for dept in summary_data['departments']:
            ws.cell(row=row, column=1, value=dept.get('department_code') or '')
            ws.cell(row=row, column=2, value=dept['department_name'])
            ws.cell(row=row, column=3, value=float(dept['doctor_value']))
            ws.cell(row=row, column=4, value=float(dept['doctor_ratio']) / 100)
            ws.cell(row=row, column=5, value=float(dept['nurse_value']))
            ws.cell(row=row, column=6, value=float(dept['nurse_ratio']) / 100)
            ws.cell(row=row, column=7, value=float(dept['tech_value']))
            ws.cell(row=row, column=8, value=float(dept['tech_ratio']) / 100)
            ws.cell(row=row, column=9, value=float(dept['total_value']))
            
            # 应用普通数据样式
            for c in range(1, 10):
                cell = ws.cell(row=row, column=c)
                cell.font = normal_font
                cell.border = border
                
                if c in [1, 2]:
                    cell.alignment = data_alignment_left
                elif c in [4, 6, 8]:  # 占比列
                    cell.alignment = data_alignment_center
                    cell.number_format = '0.00%'
                else:  # 价值列
                    cell.alignment = data_alignment_right
                    cell.number_format = '#,##0.00'
            
            ws.row_dimensions[row].height = 20
            row += 1
        
        # 保存到BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    @staticmethod
    def export_detail_to_excel(dept_name: str, period: str, detail_data: Dict[str, List[Dict]], hospital_name: str = None) -> BytesIO:
        """
        导出单个科室的明细表到Excel
        
        Args:
            dept_name: 科室名称
            period: 评估月份
            detail_data: 明细数据，包含doctor、nurse、tech三个序列的树形数据
            
        Returns:
            BytesIO: Excel文件的字节流
        """
        wb = Workbook()
        
        # 样式定义
        title_font = Font(name='微软雅黑', size=14, bold=True)
        title_alignment = Alignment(horizontal='center', vertical='center')
        
        header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        data_font = Font(name='微软雅黑', size=10)
        data_alignment_left = Alignment(horizontal='left', vertical='center')
        data_alignment_right = Alignment(horizontal='right', vertical='center')
        data_alignment_center = Alignment(horizontal='center', vertical='center')
        
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # 为每个序列创建一个Sheet
        sequence_names = {
            'doctor': '医生序列',
            'nurse': '护理序列',
            'tech': '医技序列'
        }
        
        first_sheet = True
        for seq_key, seq_name in sequence_names.items():
            if seq_key not in detail_data or not detail_data[seq_key]:
                continue
            
            if first_sheet:
                ws = wb.active
                ws.title = seq_name
                first_sheet = False
            else:
                ws = wb.create_sheet(title=seq_name)
            
            # 设置列宽
            ws.column_dimensions['A'].width = 33  # 维度名称
            ws.column_dimensions['B'].width = 13  # 工作量
            ws.column_dimensions['C'].width = 16  # 全院业务价值
            ws.column_dimensions['D'].width = 27  # 业务导向（增加50%：18 * 1.5）
            ws.column_dimensions['E'].width = 16  # 科室业务价值
            ws.column_dimensions['F'].width = 16  # 业务价值金额
            
            # 标题行
            title_text = f"{dept_name} - {seq_name}业务价值明细（{period}）"
            title_cell = ws.cell(row=1, column=1, value=title_text)
            title_cell.font = title_font
            title_cell.alignment = title_alignment
            ws.merge_cells('A1:F1')  # 改为F1（去掉占比列）
            ws.row_dimensions[1].height = 30
            
            # 表头（去掉占比列）
            headers = ['维度名称（业务价值占比）', '工作量', '全院业务价值', '业务导向', '科室业务价值', '业务价值金额']
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=2, column=col_idx, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border
            ws.row_dimensions[2].height = 25
            
            # 写入树形数据
            row = 3
            
            def write_tree_node(node: Dict, level: int, current_row: int) -> int:
                """递归写入树形节点"""
                # 计算缩进（每级缩进4个空格，让层级更明显）
                indent = '    ' * level
                
                # 维度名称（带占比）
                dim_name = indent + node['dimension_name']
                if node.get('ratio') is not None and node['ratio'] != 0:
                    dim_name += f"（{float(node['ratio']):.2f}%）"
                
                ws.cell(row=current_row, column=1, value=dim_name)
                ws.cell(row=current_row, column=2, value=float(node.get('workload', 0)) if node.get('workload') else None)
                ws.cell(row=current_row, column=3, value=node.get('hospital_value', '-'))
                ws.cell(row=current_row, column=4, value=node.get('business_guide', '-'))
                ws.cell(row=current_row, column=5, value=node.get('dept_value', '-'))
                ws.cell(row=current_row, column=6, value=float(node.get('amount', 0)) if node.get('amount') else None)
                
                # 应用样式（去掉占比列）
                for col in range(1, 7):
                    cell = ws.cell(row=current_row, column=col)
                    cell.font = data_font
                    cell.border = border
                    
                    if col == 1:  # 维度名称
                        cell.alignment = data_alignment_left
                    elif col in [2, 6]:  # 工作量、金额
                        cell.alignment = data_alignment_right
                        if cell.value and isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0.00'
                    else:  # 其他
                        cell.alignment = data_alignment_center
                
                ws.row_dimensions[current_row].height = 20
                current_row += 1
                
                # 递归处理子节点
                if 'children' in node and node['children']:
                    for child in node['children']:
                        current_row = write_tree_node(child, level + 1, current_row)
                
                return current_row
            
            # 写入所有一级维度
            for node in detail_data[seq_key]:
                row = write_tree_node(node, 0, row)
        
        # 如果没有任何数据，删除默认Sheet
        if first_sheet:
            ws = wb.active
            ws.title = "无数据"
            ws.cell(row=1, column=1, value="该科室暂无业务价值数据")
        
        # 保存到BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
    
    @staticmethod
    def export_all_details_to_zip(period: str, departments_data: List[Dict[str, Any]], hospital_name: str = None) -> BytesIO:
        """
        导出所有科室的明细表，打包成ZIP
        
        Args:
            period: 评估月份
            departments_data: 所有科室的明细数据列表
                每个元素包含：dept_name, doctor, nurse, tech
            hospital_name: 医院名称
            
        Returns:
            BytesIO: ZIP文件的字节流
        """
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for dept_data in departments_data:
                dept_name = dept_data['dept_name']
                
                # 生成该科室的Excel文件
                detail_data = {
                    'doctor': dept_data.get('doctor', []),
                    'nurse': dept_data.get('nurse', []),
                    'tech': dept_data.get('tech', [])
                }
                
                excel_file = ExportService.export_detail_to_excel(dept_name, period, detail_data, hospital_name)
                
                # 添加到ZIP（医院名称_科室名称_业务价值明细_期间.xlsx）
                if hospital_name:
                    filename = f"{hospital_name}_{dept_name}_业务价值明细_{period}.xlsx"
                else:
                    filename = f"{dept_name}_业务价值明细_{period}.xlsx"
                zip_file.writestr(filename, excel_file.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer
