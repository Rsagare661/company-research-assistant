"""
Generates a professional PDF research report using ReportLab.
Returns raw PDF bytes (caller decides whether to base64-encode, stream, etc).
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT

ACCENT = colors.HexColor("#E8912E")
DARK = colors.HexColor("#1A1A1F")
MUTED = colors.HexColor("#6B7280")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Eyebrow", fontName="Helvetica-Bold", fontSize=9,
        textColor=ACCENT, spaceAfter=2, tracking=1,
    ))
    styles.add(ParagraphStyle(
        name="CompanyTitle", fontName="Helvetica-Bold", fontSize=24,
        textColor=DARK, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader", fontName="Helvetica-Bold", fontSize=12,
        textColor=ACCENT, spaceBefore=16, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="BulletItem", fontName="Helvetica", fontSize=10, leading=14,
        textColor=DARK, leftIndent=14, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="Muted", fontName="Helvetica", fontSize=8.5, textColor=MUTED,
    ))
    return styles


def build_report_pdf(report: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=f"{report.get('company_name', 'Company')} Research Report",
    )
    styles = _styles()
    story = []

    story.append(Paragraph("RELU CONSULTANCY &middot; COMPANY RESEARCH REPORT", styles["Eyebrow"]))
    story.append(Paragraph(report.get("company_name", "Unknown Company"), styles["CompanyTitle"]))
    story.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceAfter=12))

    # Company info table
    info_rows = [
        ["Website", report.get("website") or "—"],
        ["Phone", report.get("phone") or "Not publicly listed"],
        ["Address", report.get("address") or "Not publicly listed"],
        ["Industry", report.get("industry") or "—"],
    ]
    table = Table(info_rows, colWidths=[1.3 * inch, 4.7 * inch])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)

    story.append(Paragraph("SUMMARY", styles["SectionHeader"]))
    story.append(Paragraph(report.get("summary", ""), styles["Body"]))

    if report.get("products_services"):
        story.append(Paragraph("PRODUCTS &amp; SERVICES", styles["SectionHeader"]))
        for item in report["products_services"]:
            story.append(Paragraph(f"&bull;&nbsp; {item}", styles["BulletItem"]))

    if report.get("pain_points"):
        story.append(Paragraph("AI-GENERATED PAIN POINTS", styles["SectionHeader"]))
        for item in report["pain_points"]:
            story.append(Paragraph(f"&bull;&nbsp; {item}", styles["BulletItem"]))

    if report.get("additional_insights"):
        story.append(Paragraph("ADDITIONAL INSIGHTS", styles["SectionHeader"]))
        for item in report["additional_insights"]:
            story.append(Paragraph(f"&bull;&nbsp; {item}", styles["BulletItem"]))

    if report.get("competitors"):
        story.append(Paragraph("COMPETITORS", styles["SectionHeader"]))
        comp_rows = [["Name", "Website"]]
        for c in report["competitors"]:
            comp_rows.append([c.get("name", ""), c.get("website") or "—"])
        comp_table = Table(comp_rows, colWidths=[2.2 * inch, 3.8 * inch])
        comp_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(comp_table)

    if report.get("sources"):
        story.append(Paragraph("SOURCES", styles["SectionHeader"]))
        for s in report["sources"][:12]:
            story.append(Paragraph(s.get("url", ""), styles["Muted"]))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by Company Research Assistant &middot; {datetime.utcnow().strftime('%B %d, %Y')} &middot; "
        f"AI model: {report.get('ai_model_used', '—')}",
        styles["Muted"],
    ))

    doc.build(story)
    return buf.getvalue()
