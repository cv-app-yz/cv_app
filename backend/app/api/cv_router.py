from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services import extraction, ai_agent, pdf_generation, job_service
import time
import base64

router = APIRouter()

@router.post("/analyze-and-match")
async def analyze_and_match(
    file: UploadFile = File(...),
    city: str = Form(default="Istanbul") # Frontend'den gelen şehir bilgisi
):
    print(f"🚀 İSTEK GELDİ: {file.filename} dosyası işleniyor... (Konum: {city})")
    
    # 1. Dosya Uzantı Kontrolü
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lütfen sadece PDF dosyası yükleyin.")
    
    try:
        start_time = time.time()
        
        # 2. Dosyayı Oku
        file_content = await file.read()
        print(f"✅ Dosya okundu ({len(file_content)} bytes).")
        
        # 3. Metin Çıkarma (Extraction)
        print("⏳ ADIM 1: Metin çıkarılıyor...")
        raw_text = extraction.extract_text_from_pdf(file_content)
        
        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=400, detail="PDF'den metin okunamadı.")
        print(f"✅ Metin çıkarıldı. (Uzunluk: {len(raw_text)} karakter)")
        
        # 4. Gemini AI Optimizasyonu
        print("⏳ ADIM 2: Gemini AI'ya gönderiliyor...")
        optimized_cv = ai_agent.optimize_cv_with_gemini(raw_text)
        print("✅ Gemini analizi tamamlandı.")

        # AI feedback'i sakla (PDF'de gösterilmiyor ama frontend'e döneceğiz)
        ai_feedback_text = optimized_cv.ai_feedback if optimized_cv.ai_feedback else "CV'niz başarıyla hazırlandı."
        
        # PDF oluştururken feedback alanını geçici olarak temizle (PDF'de gösterilmiyor)
        optimized_cv.ai_feedback = None 
        
        print("⏳ ADIM 3: Optimize edilmiş PDF oluşturuluyor...")
        pdf_bytes = pdf_generation.create_cv_pdf(optimized_cv)
        
        # Feedback'i geri yükle
        optimized_cv.ai_feedback = ai_feedback_text
        
        # PDF'i Base64 formatına çevir (İndirme linki için)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"
        print(f"✅ PDF oluşturuldu.")

        # --- YENİ ÖZELLİK: İŞ EŞLEŞTİRME ---
        print(f"⏳ ADIM 4: İş ilanları aranıyor ({city})...")
        
        # Yetenekleri topla (Technical + Soft)
        all_skills = []
        if optimized_cv.skills:
            # Pydantic modelinden güvenli veri çekme
            tech = getattr(optimized_cv.skills, 'technical', [])
            soft = getattr(optimized_cv.skills, 'soft', [])
            all_skills = tech + soft
            
        # Servise sor
        recommended_jobs = job_service.search_jobs_by_skills(skills=all_skills, location=city)
        print(f"✅ {len(recommended_jobs)} adet uygun iş bulundu.")

        total_duration = time.time() - start_time
        print(f"🎉 İŞLEM TAMAMLANDI! Toplam süre: {total_duration:.2f}s")

        # 5. Birleştirilmiş Yanıt Dön
        # optimized_cv bir Pydantic modeli olduğu için .model_dump() veya .dict() ile JSON'a çevrilebilir.
        # FastAPI JSONResponse bunu otomatik halleder ama model_dump() daha garantidir.
        return JSONResponse(content={
            "status": "success",
            "ai_feedback": ai_feedback_text,  # AI'dan gelen kısa ve pozitif geri bildirim
            "pdf_url": pdf_url,
            "optimized_cv": optimized_cv.model_dump(), # Frontend'de skill listelemek için gerekli
            "job_matches": recommended_jobs
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 KRİTİK HATA OLUŞTU: {e}")
        raise HTTPException(status_code=500, detail=str(e))