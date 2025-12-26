import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
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
    
    # --- STİLLER (Fotoğraftaki formata göre) ---
    # İsim başlığı - Sola hizalı, büyük
    styles.add(ParagraphStyle(
        name='NameHeader',
        parent=styles['Heading1'],
        fontName=main_font,
        fontSize=22,
        leading=26,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=8,
        fontStyle='bold'
    ))
    
    # Bölüm başlıkları - Sola hizalı, bold, alt çizgi yok
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontName=main_font,
        fontSize=14,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceBefore=16,
        spaceAfter=8,
        fontStyle='bold'
    ))
    
    # Normal metin
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.black
    ))
    
    # İletişim bilgileri için küçük metin
    styles.add(ParagraphStyle(
        name='ContactText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=3
    ))
    
    # Şirket/Pozisyon başlığı
    styles.add(ParagraphStyle(
        name='JobTitle',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=11,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.black,
        fontStyle='bold',
        spaceAfter=2
    ))
    
    # Tarih/Detay bilgisi
    styles.add(ParagraphStyle(
        name='MetaText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=6
    ))
    
    # Yetenek listesi
    styles.add(ParagraphStyle(
        name='SkillText',
        parent=styles['Normal'],
        fontName=main_font,
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=colors.black,
        spaceAfter=4
    ))

    # --- İÇERİK (Fotoğraftaki formata göre) ---

    # 1. HEADER: İsim ve İletişim Bilgileri
    ad = cv_data.personal_info.get("ad", "")
    soyad = cv_data.personal_info.get("soyad", "")
    
    # İsim - Sola hizalı, büyük ve kalın
    story.append(Paragraph(f"{ad} {soyad}", styles['NameHeader']))
    
    # İletişim bilgileri - Ayrı satırlar halinde (Location, Phone, Email)
    contact_info = []
    if cv_data.contact.location:
        contact_info.append(Paragraph(cv_data.contact.location, styles['ContactText']))
    if cv_data.contact.phone:
        contact_info.append(Paragraph(cv_data.contact.phone, styles['ContactText']))
    if cv_data.contact.email:
        contact_info.append(Paragraph(cv_data.contact.email, styles['ContactText']))
    
    # Online profiller (GitHub ve LinkedIn)
    online_profiles = []
    if cv_data.contact.github:
        # GitHub linkini temizle (sadece github.com/... kısmını al)
        github_clean = cv_data.contact.github.replace("https://", "").replace("http://", "")
        online_profiles.append(Paragraph(f"GitHub: {github_clean}", styles['ContactText']))
    if cv_data.contact.linkedin:
        # LinkedIn linkini temizle
        linkedin_clean = cv_data.contact.linkedin.replace("https://", "").replace("http://", "").replace("www.", "")
        online_profiles.append(Paragraph(f"LinkedIn: {linkedin_clean}", styles['ContactText']))
    
    # İletişim bilgilerini ekle
    story.extend(contact_info)
    if online_profiles:
        story.extend(online_profiles)
    
    story.append(Spacer(1, 15))
    
    # 2. EĞİTİM (İlk bölüm)
    if cv_data.education:
        story.append(Paragraph("EĞİTİM", styles['SectionHeader']))
        for edu in cv_data.education:
            # Okul adı - Bold
            story.append(Paragraph(f"<b>{edu.school}</b>", styles['JobTitle']))
            # Bölüm ve tarih
            meta_info = f"{edu.degree}"
            if edu.date:
                meta_info += f" | {edu.date}"
            story.append(Paragraph(meta_info, styles['MetaText']))
            story.append(Spacer(1, 8))
    
    # 3. ÖZET (İkinci bölüm - Eğitimden sonra)
    if cv_data.summary and cv_data.summary.strip():
        story.append(Paragraph("ÖZET", styles['SectionHeader']))
        story.append(Paragraph(cv_data.summary, styles['NormalText']))
        story.append(Spacer(1, 12))
    
    # 4. BECERİLER (Üçüncü bölüm)
    if cv_data.skills and (cv_data.skills.technical or cv_data.skills.soft):
        story.append(Paragraph("BECERİLER", styles['SectionHeader']))
        
        # Teknik Beceriler
        if cv_data.skills.technical:
            tech_skills = ", ".join(cv_data.skills.technical)
            story.append(Paragraph(f"<b>Bilgisayar:</b> {tech_skills}", styles['SkillText']))
        
        # Kişisel Beceriler (eğer varsa)
        if cv_data.skills.soft:
            soft_skills = ", ".join(cv_data.skills.soft)
            story.append(Paragraph(f"<b>Kişisel Beceriler:</b> {soft_skills}", styles['SkillText']))
        
        story.append(Spacer(1, 4))
    
    # 5. DENEYİM (Dördüncü bölüm)
    if cv_data.experience:
        story.append(Paragraph("DENEYİM", styles['SectionHeader']))
        for exp in cv_data.experience:
            # Pozisyon başlığı - Bold (Fotoğraftaki gibi pozisyon/proje adı başlık olarak)
            position_title = exp.position if exp.position else exp.company
            if not position_title and exp.company:
                position_title = exp.company
            
            story.append(Paragraph(f"<b>{position_title}</b>", styles['JobTitle']))
            
            # Şirket ve tarih bilgisi (eğer pozisyon başlık olduysa şirket burada, yoksa sadece tarih)
            meta_parts = []
            if exp.company and position_title != exp.company:
                meta_parts.append(exp.company)
            if exp.date:
                # Tarih formatını kontrol et (yıl formatında olabilir)
                meta_parts.append(exp.date)
            
            if meta_parts:
                story.append(Paragraph(" | ".join(meta_parts), styles['MetaText']))
            
            # Açıklama - Eğer madde işaretleri varsa koru, yoksa normal paragraf olarak göster
            if exp.description:
                # Description'ı satırlara böl ve her satırı bullet point olarak göster
                desc_lines = exp.description.split('\n')
                for line in desc_lines:
                    line = line.strip()
                    if line:
                        # Eğer zaten madde işareti yoksa ekle
                        if not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                            line = f"• {line}"
                        story.append(Paragraph(line, styles['NormalText']))
            
            story.append(Spacer(1, 10))
    
    # 6. PROJELER (Beşinci bölüm - DENEYİM'den sonra)
    if cv_data.projects:
        story.append(Paragraph("PROJELER", styles['SectionHeader']))
        for project in cv_data.projects:
            # Proje adı - Bold (tarih varsa yanında)
            project_title = f"<b>{project.name}</b>"
            if project.date:
                project_title += f", {project.date}"
            story.append(Paragraph(project_title, styles['JobTitle']))
            
            # Açıklama - Madde işaretli olarak göster
            if project.description:
                desc_lines = project.description.split('\n')
                for line in desc_lines:
                    line = line.strip()
                    if line:
                        # Eğer zaten madde işareti yoksa ekle
                        if not line.startswith('•') and not line.startswith('-') and not line.startswith('*'):
                            line = f"• {line}"
                        story.append(Paragraph(line, styles['NormalText']))
            
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()