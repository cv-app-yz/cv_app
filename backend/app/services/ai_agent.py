import google.generativeai as genai
import json
import re
from app.core.config import settings

print("🔴 YENİ 'ai_agent.py' YÜKLENDİ: GEMINI-PRO VE PARAMETRESİZ MOD AKTİF!") 

try:
    from app.schemas.cv_schema import CVData
except ImportError:
    try:
        from app.schemas.cv_schema import CVData
    except ImportError:
        print("HATA: CVData şeması import edilemedi. Dosya adını kontrol et.")
        raise

# API Ayarı
genai.configure(api_key=settings.GEMINI_API_KEY)

def clean_json_string(json_str: str) -> str:
    """
    Markdown temizleyicisi.
    Gemini bazen cevabı ```json ... ``` blokları içinde verir, bunları temizler.
    """
    if "```" in json_str:
        json_str = json_str.replace("```json", "").replace("```", "")
    return json_str.strip()

def optimize_cv_with_gemini(raw_text: str = None, cv_data: CVData = None) -> CVData:
    """
    Ham metin VEYA CVData'yı alır, AI ile optimize eder ve optimize edilmiş CVData döndürür.
    - raw_text: PDF'den çıkarılmış ham metin (PDF yükleme için)
    - cv_data: Yapılandırılmış CV verisi (Form için)
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Eğer CVData verildiyse JSON'a çevir, yoksa ham metin kullan
    if cv_data:
        cv_json = cv_data.model_dump()
        input_data = json.dumps(cv_json, ensure_ascii=False, indent=2)
        is_structured = True
    elif raw_text:
        input_data = raw_text
        is_structured = False
    else:
        raise ValueError("Ya raw_text ya da cv_data parametresi verilmelidir.")
    
    if is_structured:
        prompt = f"""
    Sen uzman bir İnsan Kaynakları (HR) danışmanı ve CV yazarısın. 
    Aşağıdaki CV verisini profesyonel, etkili ve kapsamlı bir CV'ye dönüştür.
    
    GÖREVLERİN:
    1. Özet (Summary) kısmını mutlaka yaz - 3-4 cümlelik profesyonel bir kendini tanıtma paragrafı oluştur:
       - Kullanıcının unvanı, deneyimleri ve becerilerine dayanarak kapsamlı bir özet yaz
       - Kariyer hedefleri, güçlü yönleri ve değer önerisi içermeli
       - Eğer özet eksik veya boşsa, CV'deki bilgilere dayanarak tamamen yeni bir özet oluştur
    2. Deneyim (Experience) açıklamalarını genişlet:
       - Kısa veya eksik açıklamaları detaylandır
       - "Ben yaptım" dilinden "Yapıldı/Edildi" gibi profesyonel dile çevir
       - Her deneyim için 3-5 madde halinde somut başarılar ve sorumluluklar yaz
       - Teknolojiler, metodolojiler, metrikler ve sonuçlar ekle
    3. Projeler (Projects) açıklamalarını zenginleştir:
       - Kısa proje açıklamalarını genişlet
       - Kullanılan teknolojiler, çözülen problemler, elde edilen sonuçlar ekle
       - Her proje için 2-4 madde halinde detaylı açıklama yaz
    4. Eğitim (Education) bilgilerini koru - Değiştirme, sadece formatla
    5. Kişisel Bilgiler ve İletişim bilgilerini olduğu gibi koru
    6. Beceriler (Skills) listesini olduğu gibi koru
     7. Tüm metinleri profesyonel, akıcı ve etkili Türkçe ile yaz
     8. 'ai_feedback' alanına detaylı bir analiz metni yaz (3-5 cümle):
        - CV'de yaptığın değişiklikleri ve iyileştirmeleri açıkla
        - Örnek: "CV'nizde deneyim açıklamalarını profesyonel dile çevirdim ve somut başarılar ekledim. Özet kısmını kariyer hedeflerinize uygun şekilde genişlettim. Proje açıklamalarına kullanılan teknolojiler ve sonuçlar eklendi."
        - Hangi bölümlerde ne değişiklik yaptığını belirt (deneyim, projeler, özet vb.)
        - Pozitif ve yapıcı bir ton kullan
        - Gereksiz uyarılar veya tarih kontrolleri yapma
     
     ÖNEMLİ KURALLAR:
     - Eksik veya kısa alanları mantıklı ve profesyonel cümlelerle doldur
     - Var olan bilgilere dayanarak gerçekçi ve inandırıcı içerik üret
     - Her açıklama somut, ölçülebilir ve etkileyici olsun
     - Madde işaretleri (•) kullanarak düzenli bir format oluştur
     - CV'yi zenginleştir ama abartma - gerçekçi kal
     - Tarih ve bilgileri olduğu gibi koru, yorum yapma
    
    ÇIKTI FORMATI:
    Bana SADECE geçerli bir JSON verisi ver. Başka hiçbir açıklama yazma.
    
    JSON Şeması:
    {{
      "personal_info": {{ "ad": "...", "soyad": "...", "unvan": "..." }},
      "contact": {{ "email": "...", "phone": "...", "linkedin": "...", "github": "...", "location": "..." }},
      "summary": "3-4 cümlelik profesyonel kendini tanıtma paragrafı",
      "education": [ {{ "school": "...", "degree": "...", "date": "..." }} ],
      "experience": [ {{ "company": "...", "position": "...", "date": "...", "description": "Detaylı ve profesyonel açıklama (3-5 madde)" }} ],
      "projects": [ {{ "name": "...", "date": "...", "description": "Zenginleştirilmiş proje açıklaması (2-4 madde)" }} ],
      "skills": {{ "technical": ["..."], "soft": ["..."] }},
      "ai_feedback": "Kısa ve pozitif geri bildirim (1-2 cümle)"
    }}
    
    CV VERİSİ:
    {input_data}
    """
    else:
        prompt = f"""
    Sen uzman bir İnsan Kaynakları (HR) danışmanı ve CV düzenleyicisisin.
    Aşağıdaki ham metni analiz et ve profesyonel bir CV yapısına dönüştür.
    
    GÖREVLERİN:
    1. Ham metindeki bilgileri ayıkla.
    2. Deneyim (Experience) kısımlarındaki açıklamaları "Ben yaptım" dilinden "Yapıldı/Edildi" gibi profesyonel dile çevir.
    3. Eksik bilgileri boş bırak.
    4. Skills (Yetenekler) kısmını Technical ve Soft olarak ayır.
     5. 'ai_feedback' alanına detaylı bir analiz metni yaz (3-5 cümle):
        - CV'de yaptığın değişiklikleri ve iyileştirmeleri açıkla
        - Hangi bölümlerde ne değişiklik yaptığını belirt (deneyim, projeler, özet vb.)
        - Örnek: "CV'nizde deneyim açıklamalarını profesyonel dile çevirdim ve somut başarılar ekledim. Özet kısmını kariyer hedeflerinize uygun şekilde genişlettim."
        - Pozitif ve yapıcı bir ton kullan
        - Gereksiz uyarılar veya tarih kontrolleri yapma
    
    ÇIKTI FORMATI:
    Bana SADECE geçerli bir JSON verisi ver. Başka hiçbir açıklama yazma.
    
    JSON Şeması:
    {{
      "personal_info": {{ "ad": "...", "soyad": "...", "unvan": "..." }},
      "contact": {{ "email": "...", "phone": "...", "linkedin": "...", "github": "...", "location": "..." }},
      "summary": "...",
      "education": [ {{ "school": "...", "degree": "...", "date": "..." }} ],
      "experience": [ {{ "company": "...", "position": "...", "date": "...", "description": "..." }} ],
      "projects": [ {{ "name": "...", "date": "...", "description": "..." }} ],
      "skills": {{ "technical": ["..."], "soft": ["..."] }},
      "ai_feedback": "Detaylı analiz: CV'de yapılan değişiklikler ve iyileştirmeler (3-5 cümle)"
    }}
    
    ÖNEMLİ: Experience (İş Deneyimi) ve Projects (Projeler) ayrı şeylerdir. 
    - Experience: Şirkette çalışırken yapılan işler
    - Projects: Kişisel veya bağımsız projeler (örn: Discord Bot, web sitesi, mobil uygulama vb.)
    Bu iki alanı birbirinden ayırt et ve doğru yerlere yerleştir.

    HAM METİN:
    {input_data}
    """

    try:
        if is_structured:
            print(f"🤖 AI CV Optimizasyonu başlıyor...")
        else:
            print(f"🤖 AI Modeli Çalışıyor: gemini-2.5-flash...")
        
        response = model.generate_content(prompt)
        
        # Gelen metni temizle
        cleaned_text = clean_json_string(response.text)
        
        # JSON'a çevir
        json_data = json.loads(cleaned_text)
        
        # Pydantic modeline dök
        validated_data = CVData(**json_data)
        
        if is_structured:
            print("✅ CV başarıyla optimize edildi.")
        else:
            print("✅ AI Yanıtı başarıyla işlendi.")
        return validated_data
        
    except Exception as e:
        print(f"❌ AI İşleme Hatası: {e}")
        # Hata durumunda detay görebilmek için ham yanıtı yazdıralım
        try:
            print(f"AI Ham Yanıtı: {response.text}")
        except:
            pass
        
        # Eğer CVData verildiyse ve hata oluştuysa orijinalini döndür
        if is_structured and cv_data:
            print("⚠️ Hata nedeniyle orijinal CV döndürülüyor.")
            return cv_data
        
        raise e