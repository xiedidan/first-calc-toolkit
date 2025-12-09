"""
导向规则服务
"""
from typing import Optional
from datetime import datetime
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from app.models.orientation_rule import OrientationRule, OrientationCategory
from app.models.orientation_benchmark import OrientationBenchmark
from app.models.orientation_ladder import OrientationLadder
from app.utils.hospital_filter import (
    apply_hospital_filter,
    validate_hospital_access,
)


class OrientationRuleService:
    """导向规则服务"""
    
    @staticmethod
    def copy_rule(db: Session, rule_id: int, hospital_id: int) -> OrientationRule:
        """
        复制导向规则及其关联数据
        
        Args:
            db: 数据库会话
            rule_id: 要复制的导向规则ID
            hospital_id: 当前医疗机构ID
            
        Returns:
            新创建的导向规则对象
            
        Raises:
            HTTPException: 当规则不存在或复制失败时
        """
        # 查询原始导向规则
        query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
        query = apply_hospital_filter(query, OrientationRule, required=True)
        original_rule = query.first()
        
        if not original_rule:
            raise HTTPException(status_code=404, detail="导向规则不存在")
        
        # 验证数据所属医疗机构
        validate_hospital_access(db, original_rule)
        
        try:
            # 开始事务（使用 db.begin_nested() 创建保存点）
            # 创建新的导向规则（名称添加"（副本）"）
            new_rule = OrientationRule(
                hospital_id=hospital_id,
                name=f"{original_rule.name}（副本）",
                category=original_rule.category,
                description=original_rule.description,
            )
            db.add(new_rule)
            db.flush()  # 刷新以获取新规则的ID
            
            # 根据类别复制关联数据
            if original_rule.category == OrientationCategory.benchmark_ladder:
                # 复制导向基准
                for benchmark in original_rule.benchmarks:
                    new_benchmark = OrientationBenchmark(
                        hospital_id=hospital_id,
                        rule_id=new_rule.id,
                        department_code=benchmark.department_code,
                        department_name=benchmark.department_name,
                        benchmark_type=benchmark.benchmark_type,
                        control_intensity=benchmark.control_intensity,
                        stat_start_date=benchmark.stat_start_date,
                        stat_end_date=benchmark.stat_end_date,
                        benchmark_value=benchmark.benchmark_value,
                    )
                    db.add(new_benchmark)
                
                # 复制导向阶梯
                for ladder in original_rule.ladders:
                    new_ladder = OrientationLadder(
                        hospital_id=hospital_id,
                        rule_id=new_rule.id,
                        ladder_order=ladder.ladder_order,
                        upper_limit=ladder.upper_limit,
                        lower_limit=ladder.lower_limit,
                        adjustment_intensity=ladder.adjustment_intensity,
                    )
                    db.add(new_ladder)
            
            elif original_rule.category == OrientationCategory.direct_ladder:
                # 仅复制导向阶梯
                for ladder in original_rule.ladders:
                    new_ladder = OrientationLadder(
                        hospital_id=hospital_id,
                        rule_id=new_rule.id,
                        ladder_order=ladder.ladder_order,
                        upper_limit=ladder.upper_limit,
                        lower_limit=ladder.lower_limit,
                        adjustment_intensity=ladder.adjustment_intensity,
                    )
                    db.add(new_ladder)
            
            # 其他类别不需要复制关联数据
            
            # 提交事务
            db.commit()
            db.refresh(new_rule)
            
            return new_rule
            
        except SQLAlchemyError as e:
            # 回滚事务
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"复制导向规则失败: {str(e)}"
            )
        except Exception as e:
            # 回滚事务
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"复制导向规则时发生未知错误: {str(e)}"
            )
    
    @staticmethod
    def export_rule(db: Session, rule_id: int, hospital_id: int) -> tuple[BytesIO, str]:
        """
        导出导向规则为Markdown文件
        
        Args:
            db: 数据库会话
            rule_id: 要导出的导向规则ID
            hospital_id: 当前医疗机构ID
            
        Returns:
            (BytesIO对象, 文件名) 元组
            
        Raises:
            HTTPException: 当规则不存在时
        """
        from app.models.hospital import Hospital
        
        # 查询导向规则
        query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
        query = apply_hospital_filter(query, OrientationRule, required=True)
        rule = query.first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="导向规则不存在")
        
        # 验证数据所属医疗机构
        validate_hospital_access(db, rule)
        
        # 获取医院名称
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        hospital_name = hospital.name if hospital else "未知医院"
        
        # 生成Markdown内容
        markdown_content = OrientationRuleService._generate_markdown(rule)
        
        # 生成文件名（医院名称_导向名称_时间戳.md）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{hospital_name}_{rule.name}_{timestamp}.md"
        
        # 将内容写入BytesIO
        buffer = BytesIO()
        buffer.write(markdown_content.encode('utf-8'))
        buffer.seek(0)
        
        return buffer, filename
    
    @staticmethod
    def export_rule_pdf(db: Session, rule_id: int, hospital_id: int) -> tuple[BytesIO, str]:
        """
        导出导向规则为PDF文件
        
        Args:
            db: 数据库会话
            rule_id: 要导出的导向规则ID
            hospital_id: 当前医疗机构ID
            
        Returns:
            (BytesIO对象, 文件名) 元组
            
        Raises:
            HTTPException: 当规则不存在时
        """
        # 查询导向规则
        query = db.query(OrientationRule).filter(OrientationRule.id == rule_id)
        query = apply_hospital_filter(query, OrientationRule, required=True)
        rule = query.first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="导向规则不存在")
        
        # 验证数据所属医疗机构
        validate_hospital_access(db, rule)
        
        # 生成PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 注册中文字体（使用系统自带的宋体）
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            font_name = 'SimSun'
        except:
            # 如果宋体不可用，使用默认字体
            font_name = 'Helvetica'
        
        # 创建样式
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # 二级标题样式
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15
        )
        
        # 正文样式
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14
        )
        
        # 构建PDF内容
        story = []
        
        # 标题
        story.append(Paragraph(rule.name, title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # 基本信息
        story.append(Paragraph('基本信息', heading_style))
        
        # 导向类别中文映射
        category_map = {
            OrientationCategory.benchmark_ladder: "基准阶梯",
            OrientationCategory.direct_ladder: "直接阶梯",
            OrientationCategory.other: "其他",
        }
        
        info_data = [
            ['导向名称', rule.name],
            ['导向类别', category_map.get(rule.category, rule.category)],
        ]
        
        if rule.description:
            info_data.append(['导向规则描述', rule.description])
        
        info_data.extend([
            ['创建时间', rule.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['更新时间', rule.updated_at.strftime('%Y-%m-%d %H:%M:%S')]
        ])
        
        info_table = Table(info_data, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))
        
        # 根据类别包含关联数据
        if rule.category == OrientationCategory.benchmark_ladder and rule.benchmarks:
            story.append(Paragraph('导向基准', heading_style))
            
            # 基准类别中文映射
            benchmark_type_map = {
                "average": "平均值",
                "median": "中位数",
                "max": "最大值",
                "min": "最小值",
                "other": "其他",
            }
            
            benchmark_data = [['科室代码', '科室名称', '基准类别', '管控力度', '统计开始时间', '统计结束时间', '基准值']]
            
            for benchmark in rule.benchmarks:
                benchmark_data.append([
                    benchmark.department_code,
                    benchmark.department_name,
                    benchmark_type_map.get(benchmark.benchmark_type, benchmark.benchmark_type),
                    f"{float(benchmark.control_intensity):.4f}",
                    benchmark.stat_start_date.strftime('%Y-%m-%d'),
                    benchmark.stat_end_date.strftime('%Y-%m-%d'),
                    f"{float(benchmark.benchmark_value):.4f}"
                ])
            
            benchmark_table = Table(benchmark_data, colWidths=[2*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm, 2*cm])
            benchmark_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(benchmark_table)
            story.append(Spacer(1, 0.5*cm))
        
        # 导向阶梯
        if (rule.category in [OrientationCategory.benchmark_ladder, OrientationCategory.direct_ladder]) and rule.ladders:
            story.append(Paragraph('导向阶梯', heading_style))
            
            ladder_data = [['阶梯次序', '阶梯下限', '阶梯上限', '调整力度']]
            
            for ladder in sorted(rule.ladders, key=lambda x: x.ladder_order):
                lower = "-∞" if ladder.lower_limit is None else f"{float(ladder.lower_limit):.4f}"
                upper = "+∞" if ladder.upper_limit is None else f"{float(ladder.upper_limit):.4f}"
                ladder_data.append([
                    str(ladder.ladder_order),
                    lower,
                    upper,
                    f"{float(ladder.adjustment_intensity):.4f}"
                ])
            
            ladder_table = Table(ladder_data, colWidths=[3*cm, 4*cm, 4*cm, 4*cm])
            ladder_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(ladder_table)
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        # 获取医院名称
        from app.models.hospital import Hospital
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        hospital_name = hospital.name if hospital else "未知医院"
        
        # 生成文件名（医院名称_导向名称_时间戳.pdf）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{hospital_name}_{rule.name}_{timestamp}.pdf"
        
        return buffer, filename
    
    @staticmethod
    def _generate_markdown(rule: OrientationRule) -> str:
        """
        生成导向规则的Markdown内容
        
        Args:
            rule: 导向规则对象
            
        Returns:
            Markdown格式的字符串
        """
        lines = []
        
        # 标题
        lines.append(f"# {rule.name}")
        lines.append("")
        
        # 基本信息
        lines.append("## 基本信息")
        lines.append("")
        lines.append(f"- **导向名称**: {rule.name}")
        
        # 导向类别中文映射
        category_map = {
            OrientationCategory.benchmark_ladder: "基准阶梯",
            OrientationCategory.direct_ladder: "直接阶梯",
            OrientationCategory.other: "其他",
        }
        lines.append(f"- **导向类别**: {category_map.get(rule.category, rule.category)}")
        
        if rule.description:
            lines.append(f"- **导向规则描述**: {rule.description}")
        
        lines.append(f"- **创建时间**: {rule.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **更新时间**: {rule.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 根据类别包含关联数据
        if rule.category == OrientationCategory.benchmark_ladder:
            # 导向基准
            if rule.benchmarks:
                lines.append("## 导向基准")
                lines.append("")
                lines.append("| 科室代码 | 科室名称 | 基准类别 | 管控力度 | 统计开始时间 | 统计结束时间 | 基准值 |")
                lines.append("|---------|---------|---------|---------|-------------|-------------|--------|")
                
                # 基准类别中文映射
                benchmark_type_map = {
                    "average": "平均值",
                    "median": "中位数",
                    "max": "最大值",
                    "min": "最小值",
                    "other": "其他",
                }
                
                for benchmark in rule.benchmarks:
                    benchmark_type_cn = benchmark_type_map.get(benchmark.benchmark_type, benchmark.benchmark_type)
                    stat_start = benchmark.stat_start_date.strftime('%Y-%m-%d')
                    stat_end = benchmark.stat_end_date.strftime('%Y-%m-%d')
                    lines.append(
                        f"| {benchmark.department_code} | {benchmark.department_name} | "
                        f"{benchmark_type_cn} | {float(benchmark.control_intensity):.4f} | "
                        f"{stat_start} | {stat_end} | {float(benchmark.benchmark_value):.4f} |"
                    )
                lines.append("")
            
            # 导向阶梯
            if rule.ladders:
                lines.append("## 导向阶梯")
                lines.append("")
                lines.append("| 阶梯次序 | 阶梯下限 | 阶梯上限 | 调整力度 |")
                lines.append("|---------|---------|---------|---------|")
                
                for ladder in sorted(rule.ladders, key=lambda x: x.ladder_order):
                    lower = "-∞" if ladder.lower_limit is None else f"{float(ladder.lower_limit):.4f}"
                    upper = "+∞" if ladder.upper_limit is None else f"{float(ladder.upper_limit):.4f}"
                    lines.append(
                        f"| {ladder.ladder_order} | {lower} | {upper} | "
                        f"{float(ladder.adjustment_intensity):.4f} |"
                    )
                lines.append("")
        
        elif rule.category == OrientationCategory.direct_ladder:
            # 仅导向阶梯
            if rule.ladders:
                lines.append("## 导向阶梯")
                lines.append("")
                lines.append("| 阶梯次序 | 阶梯下限 | 阶梯上限 | 调整力度 |")
                lines.append("|---------|---------|---------|---------|")
                
                for ladder in sorted(rule.ladders, key=lambda x: x.ladder_order):
                    lower = "-∞" if ladder.lower_limit is None else f"{float(ladder.lower_limit):.4f}"
                    upper = "+∞" if ladder.upper_limit is None else f"{float(ladder.upper_limit):.4f}"
                    lines.append(
                        f"| {ladder.ladder_order} | {lower} | {upper} | "
                        f"{float(ladder.adjustment_intensity):.4f} |"
                    )
                lines.append("")
        
        # 其他类别不包含关联数据
        
        return "\n".join(lines)
