"""
Report generator for test results
"""
import os
from datetime import datetime
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from test_runner import TestResult
import config

class ReportGenerator:
    """Generate test execution reports"""
    
    def __init__(self, test_results: List[TestResult], output_dir: str = None):
        self.test_results = test_results
        self.output_dir = output_dir or config.REPORT_OUTPUT_DIR
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_html_report(self) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        # Calculate summary statistics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{config.REPORT_TITLE}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #8366f1;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #8366f1;
            margin: 0 0 10px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-box {{
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .summary-value {{
            font-size: 32px;
            font-weight: bold;
            color: #8366f1;
        }}
        .summary-label {{
            font-size: 14px;
            color: #64748b;
            margin-top: 5px;
        }}
        .test-result {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .test-result.passed {{
            border-left: 4px solid #10b981;
        }}
        .test-result.failed {{
            border-left: 4px solid #ef4444;
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .test-name {{
            font-size: 18px;
            font-weight: 600;
        }}
        .badge {{
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge.passed {{
            background: #d1fae5;
            color: #065f46;
        }}
        .badge.failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .test-details {{
            font-size: 14px;
            color: #64748b;
            margin-bottom: 15px;
        }}
        .test-info {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }}
        .info-item {{
            padding: 8px;
            background: #f8fafc;
            border-radius: 4px;
        }}
        .info-label {{
            font-weight: 600;
            color: #475569;
        }}
        .assertions {{
            margin-top: 15px;
        }}
        .assertion {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 14px;
        }}
        .assertion.passed {{
            background: #f0fdf4;
            color: #166534;
        }}
        .assertion.failed {{
            background: #fef2f2;
            color: #991b1b;
        }}
        .error-message {{
            padding: 10px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            color: #991b1b;
            border-radius: 4px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config.REPORT_TITLE}</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="summary">
        <div class="summary-box">
            <div class="summary-value">{total}</div>
            <div class="summary-label">Total Tests</div>
        </div>
        <div class="summary-box">
            <div class="summary-value" style="color: #10b981;">{passed}</div>
            <div class="summary-label">Passed</div>
        </div>
        <div class="summary-box">
            <div class="summary-value" style="color: #ef4444;">{failed}</div>
            <div class="summary-label">Failed</div>
        </div>
        <div class="summary-box">
            <div class="summary-value">{success_rate:.1f}%</div>
            <div class="summary-label">Success Rate</div>
        </div>
    </div>
    
    <h2>Detailed Test Results</h2>
"""
        
        for result in self.test_results:
            status = "passed" if result.passed else "failed"
            status_text = "PASSED" if result.passed else "FAILED"
            
            html_content += f"""
    <div class="test-result {status}">
        <div class="test-header">
            <div class="test-name">{result.test_case.test_id}: {result.test_case.test_name}</div>
            <span class="badge {status}">{status_text}</span>
        </div>
        <div class="test-details">{result.test_case.description}</div>
        
        <div class="test-info">
            <div class="info-item">
                <span class="info-label">Expected Host:</span> {result.test_case.expected_host}
            </div>
            <div class="info-item">
                <span class="info-label">Actual Host:</span> {result.actual_host or 'N/A'}
            </div>
            <div class="info-item">
                <span class="info-label">Expected Port:</span> {result.test_case.expected_port}
            </div>
            <div class="info-item">
                <span class="info-label">Actual Port:</span> {result.actual_port or 'N/A'}
            </div>
            <div class="info-item">
                <span class="info-label">Expected Status:</span> {result.test_case.expected_status}
            </div>
            <div class="info-item">
                <span class="info-label">Actual Status:</span> {result.actual_status or 'N/A'}
            </div>
            <div class="info-item">
                <span class="info-label">Execution Time:</span> {result.execution_time:.2f}s
            </div>
            <div class="info-item">
                <span class="info-label">ACK Received:</span> {'Yes' if result.ack_received else 'No'}
            </div>
        </div>
        
        <div class="assertions">
            <strong>Assertions:</strong>
"""
            
            for assertion in result.assertions:
                assertion_status = "passed" if assertion['passed'] else "failed"
                icon = "✓" if assertion['passed'] else "✗"
                html_content += f"""
            <div class="assertion {assertion_status}">
                {icon} <strong>{assertion['name']}:</strong> {assertion['message']}
            </div>
"""
            
            html_content += """
        </div>
"""
            
            if result.error_message:
                html_content += f"""
        <div class="error-message">
            <strong>Error:</strong> {result.error_message}
        </div>
"""
            
            html_content += """
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_pdf_report(self) -> str:
        """Generate PDF report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8366f1'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        story.append(Paragraph(config.REPORT_TITLE, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        summary_data = [
            ['Total Tests', 'Passed', 'Failed', 'Success Rate'],
            [str(total), str(passed), str(failed), f"{success_rate:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch]*4)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Detailed results
        story.append(Paragraph("Detailed Test Results", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        for result in self.test_results:
            # Test header
            status_color = colors.green if result.passed else colors.red
            status_text = "PASSED" if result.passed else "FAILED"
            
            story.append(Paragraph(
                f"<b>{result.test_case.test_id}: {result.test_case.test_name}</b> - "
                f"<font color='{status_color.hexval()}'>{status_text}</font>",
                styles['Heading3']
            ))
            
            story.append(Paragraph(result.test_case.description, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Test details
            details_data = [
                ['Expected Host', result.test_case.expected_host, 'Actual Host', result.actual_host or 'N/A'],
                ['Expected Port', result.test_case.expected_port, 'Actual Port', result.actual_port or 'N/A'],
                ['Expected Status', result.test_case.expected_status, 'Actual Status', result.actual_status or 'N/A'],
                ['Execution Time', f"{result.execution_time:.2f}s", 'ACK Received', 'Yes' if result.ack_received else 'No']
            ]
            
            details_table = Table(details_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Assertions
            story.append(Paragraph("<b>Assertions:</b>", styles['Normal']))
            for assertion in result.assertions:
                icon = "✓" if assertion['passed'] else "✗"
                color = 'green' if assertion['passed'] else 'red'
                story.append(Paragraph(
                    f"<font color='{color}'>{icon}</font> <b>{assertion['name']}:</b> {assertion['message']}",
                    styles['Normal']
                ))
            
            if result.error_message:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    f"<font color='red'><b>Error:</b> {result.error_message}</font>",
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 0.3*inch))
        
        doc.build(story)
        return filepath