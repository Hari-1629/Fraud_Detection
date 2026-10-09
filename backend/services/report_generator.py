import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

def generate_pdf_report(doc_data: Dict[str, Any], clauses: list, risk_info: Dict[str, Any]) -> bytes:
    """
    Generates a PDF report containing Executive Summary, Financial Metrics, Clauses, and Risk Analysis.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=14,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("FinWise AI - Intelligent Financial Report", title_style))
    elements.append(Paragraph(f"Document Analysis & Decision Support Summary | Document ID: {doc_data.get('doc_id', 'N/A')}", subtitle_style))
    elements.append(Spacer(1, 10))

    # 1. Executive Summary Table
    elements.append(Paragraph("1. Extracted Key Financial Parameters", section_style))
    metrics_table_data = [
        [Paragraph("<b>Parameter</b>", normal_style), Paragraph("<b>Extracted Value</b>", normal_style)],
        ["Borrower Name", str(doc_data.get("borrower_name", "N/A"))],
        ["Loan Principal Amount", f"₹ {float(doc_data.get('loan_amount', 0)):,.2f}"],
        ["Annual Interest Rate", f"{float(doc_data.get('interest_rate', 0)):.2f}% ({doc_data.get('interest_type', 'Fixed')})"],
        ["Loan Tenure", f"{int(doc_data.get('tenure', 0))} Months"],
        ["Calculated Monthly EMI", f"₹ {float(doc_data.get('emi', 0)):,.2f}"],
        ["Processing Charges", f"₹ {float(doc_data.get('processing_fee', 0)):,.2f}"],
        ["Total Interest Payable", f"₹ {float(doc_data.get('total_interest', 0)):,.2f}"],
        ["Total Repayment Amount", f"₹ {float(doc_data.get('total_repayment', 0)):,.2f}"],
    ]

    t1 = Table(metrics_table_data, colWidths=[200, 300])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 15))

    # 2. Risk Analysis
    elements.append(Paragraph("2. AI Risk Assessment & Recommendations", section_style))
    risk_score = risk_info.get("risk_score", 5.0)
    risk_cat = risk_info.get("risk_category", "MEDIUM_RISK")
    elements.append(Paragraph(f"<b>Overall Contract Risk Rating:</b> {risk_cat} ({risk_score} / 10.0)", normal_style))
    
    for rec in risk_info.get("recommendations", []):
        elements.append(Paragraph(f"• {rec}", normal_style))
    elements.append(Spacer(1, 15))

    # 3. Key Clauses
    elements.append(Paragraph("3. Classified Financial Clauses", section_style))
    for c in clauses:
        elements.append(Paragraph(f"<b>{c.get('title')}</b> [{c.get('risk_level')}]", normal_style))
        elements.append(Paragraph(f"<i>Explanation:</i> {c.get('simple_explanation')}", normal_style))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
