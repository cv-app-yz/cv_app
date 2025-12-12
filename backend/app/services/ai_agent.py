import google.generativeai as genai
import json
import re
from app.core.config import settings

# --- BU YAZIYI TERMİNALDE GÖRMELİYİZ (KODUN GÜNCELLENDİĞİNİN KANITI) ---
print("🔴 YENİ 'ai_agent.py' YÜKLENDİ: GEMINI-PRO VE PARAMETRESİZ MOD AKTİF!") 

# Şema Import (Güvenlikli: Dosya adın 'cv.py' de olsa 'cv_schema.py' de olsa çalışır)
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

def optimize_cv_with_gemini(raw_text: str) -> CVData:
    
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Sen uzman bir İnsan Kaynakları (HR) danışmanı ve CV düzenleyicisisin.
    Aşağıdaki ham metni analiz et ve profesyonel bir CV yapısına dönüştür.
    
    GÖREVLERİN:
    1. Ham metindeki bilgileri ayıkla.
    2. Deneyim (Experience) kısımlarındaki açıklamaları "Ben yaptım" dilinden "Yapıldı/Edildi" gibi profesyonel dile çevir.
    3. Eksik bilgileri boş bırak.
    4. Skills (Yetenekler) kısmını Technical ve Soft olarak ayır.
    5. 'ai_feedback' alanına Türkçe tavsiye yaz.
    
    ÇIKTI FORMATI:
    Bana SADECE geçerli bir JSON verisi ver. Başka hiçbir açıklama yazma.
    
    JSON Şeması:
    {{
      "personal_info": {{ "ad": "...", "soyad": "...", "unvan": "..." }},
      "contact": {{ "email": "...", "phone": "...", "linkedin": "...", "location": "..." }},
      "summary": "...",
      "education": [ {{ "school": "...", "degree": "...", "date": "..." }} ],
      "experience": [ {{ "company": "...", "position": "...", "date": "...", "description": "..." }} ],
      "skills": {{ "technical": ["..."], "soft": ["..."] }},
      "ai_feedback": "..."
    }}

    HAM METİN:
    {raw_text}
    """

    try:
        print(f"🤖 AI Modeli Çalışıyor: gemini-pro (Parametresiz)...")
        
        # --- KRİTİK DÜZELTME ---
        # Hata veren 'generation_config' parametresi TAMAMEN kaldırıldı.
        response = model.generate_content(prompt)
        
        # Gelen metni temizle
        cleaned_text = clean_json_string(response.text)
        
        # JSON'a çevir
        json_data = json.loads(cleaned_text)
        
        # Pydantic modeline dök
        validated_data = CVData(**json_data)
        
        print("✅ AI Yanıtı başarıyla işlendi.")
        return validated_data

    except Exception as e:
        print(f"❌ AI İşleme Hatası: {e}")
        # Hata durumunda detay görebilmek için ham yanıtı yazdıralım
        try:
            print(f"AI Ham Yanıtı: {response.text}")
        except:
            pass
        raise e