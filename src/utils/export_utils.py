"""
Export utilities for charts and data
Supports PNG/PDF chart export, CSV/Excel data export, and PDF report generation
"""

import os
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import logging
from datetime import datetime
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed - PDF export will be limited")


def export_chart_png(fig, output_path: str, width: int = 1200, height: int = 600, scale: int = 2):
    """Export Plotly chart as PNG"""
    try:
        fig.write_image(output_path, width=width, height=height, scale=scale)
        logger.info(f"Exported chart to PNG: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting PNG: {e}")
        return False


def export_chart_pdf(fig, output_path: str, width: int = 1200, height: int = 600):
    """Export Plotly chart as PDF"""
    try:
        fig.write_image(output_path, format='pdf', width=width, height=height)
        logger.info(f"Exported chart to PDF: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        return False


def export_data_csv(df: pd.DataFrame, output_path: str):
    """Export DataFrame to CSV"""
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Exported data to CSV: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return False


def export_data_excel(df: pd.DataFrame, output_path: str, sheet_name: str = "Data"):
    """Export DataFrame to Excel"""
    try:
        df.to_excel(output_path, index=False, sheet_name=sheet_name)
        logger.info(f"Exported data to Excel: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        return False


def generate_pdf_report(
    title: str,
    charts: list,
    data_summary: dict,
    output_path: str,
    project_info: dict = None
):
    """Generate comprehensive PDF report with charts and analysis"""
    if not REPORTLAB_AVAILABLE:
        logger.error("reportlab not available - cannot generate PDF report")
        return False
    
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E88E5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Project info
        if project_info:
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            for key, value in project_info.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", info_style))
            story.append(Spacer(1, 0.3*inch))
        
        # Data summary
        if data_summary:
            story.append(Paragraph("<b>Data Summary</b>", styles['Heading2']))
            summary_data = [['Metric', 'Value']]
            for key, value in data_summary.items():
                summary_data.append([str(key), str(value)])
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Charts
        story.append(Paragraph("<b>Visualizations</b>", styles['Heading2']))
        for i, (chart_title, chart_fig) in enumerate(charts, 1):
            story.append(Paragraph(f"{i}. {chart_title}", styles['Heading3']))
            
            # Export chart to temporary image
            temp_img = BytesIO()
            try:
                chart_fig.write_image(temp_img, format='png', width=800, height=400)
                temp_img.seek(0)
                img = Image(temp_img, width=6*inch, height=3*inch)
                story.append(img)
            except Exception as e:
                story.append(Paragraph(f"Error rendering chart: {str(e)}", styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Generated PDF report: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def create_export_directory(base_path: Path = None):
    """Create export directory if it doesn't exist"""
    if base_path is None:
        base_path = Path(__file__).parent.parent.parent / "exports"
    else:
        base_path = Path(base_path)
    
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path

