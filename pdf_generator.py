import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


def generate_pdf(product_name: str, doc_type: str, content: str) -> str:

    os.makedirs('pdfs', exist_ok=True)
    filename = f'pdfs/{product_name}_{doc_type}.pdf'.replace(' ', '_')

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2.5*cm,
        rightMargin=2.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # ── Colours ──────────────────────────────────────────────
    DARK   = colors.HexColor('#0F172A')
    ACCENT = colors.HexColor('#6366F1')
    GRAY   = colors.HexColor('#64748B')
    LIGHT  = colors.HexColor('#F8FAFC')
    MID    = colors.HexColor('#E2E8F0')
    WHITE  = colors.white

    # ── Styles ────────────────────────────────────────────────
    sCompany = ParagraphStyle(
        'company',
        fontSize=9,
        textColor=WHITE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    sDocType = ParagraphStyle(
        'doctype',
        fontSize=9,
        textColor=colors.HexColor('#A5B4FC'),
        fontName='Helvetica',
        alignment=TA_RIGHT
    )
    sTitle = ParagraphStyle(
        'title',
        fontSize=22,
        leading=28,
        textColor=DARK,
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    sMeta = ParagraphStyle(
        'meta',
        fontSize=9,
        textColor=GRAY,
        fontName='Helvetica',
        spaceAfter=2
    )
    sHeading = ParagraphStyle(
        'heading',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=4
    )
    sBody = ParagraphStyle(
        'body',
        fontSize=10,
        leading=16,
        textColor=DARK,
        fontName='Helvetica',
        spaceAfter=4
    )
    sBullet = ParagraphStyle(
        'bullet',
        fontSize=10,
        leading=16,
        textColor=DARK,
        fontName='Helvetica',
        leftIndent=16,
        spaceAfter=3
    )
    sFooter = ParagraphStyle(
        'footer',
        fontSize=8,
        textColor=GRAY,
        fontName='Helvetica',
        alignment=TA_CENTER
    )

    story = []

    # ── TOP HEADER BAR ────────────────────────────────────────
    doc_type_label = doc_type.replace('_', ' ').upper()
    header = Table([[
        Paragraph('AI PM Assistant', sCompany),
        Paragraph(doc_type_label, sDocType),
    ]], colWidths=[8*cm, 8*cm])
    header.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), DARK),
        ('TOPPADDING',    (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header)
    story.append(Spacer(1, 20))

    # ── TITLE SECTION ─────────────────────────────────────────
    story.append(Paragraph(product_name, sTitle))
    story.append(Paragraph(doc_type_label, ParagraphStyle(
        'sub', fontSize=11, textColor=ACCENT,
        fontName='Helvetica-Bold', spaceAfter=6
    )))

    # Meta info row
    today = datetime.now().strftime('%B %d, %Y')
    meta = Table([[
        Paragraph(f'Generated: {today}', sMeta),
        Paragraph('Powered by Llama 3 via Groq', ParagraphStyle(
            'm2', fontSize=9, textColor=GRAY,
            fontName='Helvetica', alignment=TA_RIGHT
        )),
    ]], colWidths=[8*cm, 8*cm])
    meta.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(meta)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(
        width='100%', thickness=2,
        color=ACCENT, spaceAfter=16
    ))

    # ── MAIN CONTENT ──────────────────────────────────────────
    for line in content.split('\n'):
        stripped = line.strip()

        if stripped == '':
            story.append(Spacer(1, 6))

        # Headings — lines ending with : or starting with a number
        elif (stripped.endswith(':') and len(stripped) < 60) or \
             (len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.):'):
            story.append(Paragraph(stripped, sHeading))

        # Bullet points
        elif stripped.startswith('-') or stripped.startswith('*') or stripped.startswith('•'):
            bullet_text = stripped.lstrip('-*• ').strip()
            story.append(Paragraph(f'• {bullet_text}', sBullet))

        # Bold lines (markdown style **)
        elif stripped.startswith('**') and stripped.endswith('**'):
            clean = stripped.strip('*')
            story.append(Paragraph(f'<b>{clean}</b>', sBody))

        # Hash headings (markdown style)
        elif stripped.startswith('#'):
            clean = stripped.lstrip('#').strip()
            story.append(Paragraph(clean, sHeading))

        # Normal body text
        else:
            story.append(Paragraph(stripped, sBody))

    # ── FOOTER ────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(
        width='100%', thickness=0.5,
        color=MID, spaceAfter=8
    ))
    story.append(Paragraph(
        f'Generated by AI PM Assistant  •  {today}  •  Confidential',
        sFooter
    ))

    doc.build(story)
    return filename