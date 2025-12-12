import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from app.schemas.cv_schema import CVData

def create_cv_pdf(cv_data: CVData) -> bytes:
    """
    Pydantic CVData modelini alır ve Türkçe karakter destekli PDF döndürür.
    """
    
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title=f"{cv_data.personal_info.get('ad', 'CV')} Resume"
    )
    
    # --- FONT AYARLARI (TÜRKÇE KARAKTER İÇİN) ---
    # Font dosyasının yolunu bul (main.py'nin olduğu yerde arar)
    font_path = "arial.ttf"
    
    try:
        # Fontu sisteme kaydet
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        main_font = 'Arial'
    except Exception as e:
        print(f"UYARI: 'arial.ttf' bulunamadı! Türkçe karakterler bozuk çıkabilir. ({e})")
        main_font = 'Helvetica' # Yedek font (Türkçe desteklemez)

    story = []
    styles = getSampleStyleSheet()
    
    # --- STİLLER (Artık Arial kullanıyor) ---
    styles.add(ParagraphStyle(
        name='NameHeader',
        parent=styles['Heading1'],
        fontName=main_font,  # Fontu buraya atadık
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='TitleHeader',
        parent=styles['Heading2'],
        fontName=main_font,
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading3'],
        fontName=main_font,
        fontSize=12,
        leading=14,
        textColor=colors.darkblue,
        spaceBefore=12,
        spaceAfter=6,
        borderPadding=2,
        borderBottomWidth=1,
        borderColor=colors.lightgrey
    ))
    
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=9,
        leading=12,
        textColor=colors.grey
    ))

    # --- İÇERİK ---

    # 1. KİŞİSEL BİLGİLER
    ad = cv_data.personal_info.get("ad", "")
    soyad = cv_data.personal_info.get("soyad", "")
    unvan = cv_data.personal_info.get("unvan", "")
    
    story.append(Paragraph(f"{ad} {soyad}", styles['NameHeader']))
    story.append(Paragraph(unvan, styles['TitleHeader']))
    
    # 2. İLETİŞİM
    contact_parts = [
        cv_data.contact.email,
        cv_data.contact.phone,
        cv_data.contact.linkedin,
        cv_data.contact.location
    ]
    contact_str = " | ".join([c for c in contact_parts if c])
    story.append(Paragraph(contact_str, styles['SmallText']))
    story.append(Spacer(1, 20)) 
    
    # 3. ÖZET
    story.append(Paragraph("HAKKINDA", styles['SectionHeader']))
    story.append(Paragraph(cv_data.summary, styles['NormalText']))
    
    # 4. DENEYİM
    if cv_data.experience:
        story.append(Paragraph("İŞ DENEYİMİ", styles['SectionHeader']))
        for exp in cv_data.experience:
            story.append(Paragraph(f"<b>{exp.company}</b> - {exp.position}", styles['NormalText']))
            story.append(Paragraph(f"<i>{exp.date}</i>", styles['SmallText']))
            story.append(Paragraph(exp.description, styles['NormalText']))
            story.append(Spacer(1, 10))

    # 5. EĞİTİM
    if cv_data.education:
        story.append(Paragraph("EĞİTİM", styles['SectionHeader']))
        for edu in cv_data.education:
            story.append(Paragraph(f"<b>{edu.school}</b>", styles['NormalText']))
            story.append(Paragraph(f"{edu.degree} | {edu.date}", styles['SmallText']))
            story.append(Spacer(1, 8))

    # 6. YETENEKLER
    if cv_data.skills:
        story.append(Paragraph("YETKİNLİKLER", styles['SectionHeader']))
        if cv_data.skills.technical:
            story.append(Paragraph(f"<b>Teknik:</b> {', '.join(cv_data.skills.technical)}", styles['NormalText']))
        if cv_data.skills.soft:
            story.append(Paragraph(f"<b>Kişisel:</b> {', '.join(cv_data.skills.soft)}", styles['NormalText']))

    # 7. AI NOTU
    if cv_data.ai_feedback:
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        story.append(Paragraph("AI ÖNERİSİ", styles['SectionHeader']))
        story.append(Paragraph(f"<i>{cv_data.ai_feedback}</i>", styles['SmallText']))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()