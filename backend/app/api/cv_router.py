from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services import extraction, ai_agent, pdf_generation
import time
import base64

router = APIRouter()

@router.post("/optimize")
async def optimize_cv(file: UploadFile = File(...)):
    print(f"🚀 İSTEK GELDİ: {file.filename} dosyası işleniyor...")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lütfen sadece PDF dosyası yükleyin.")
    
    try:
        start_time = time.time()
        file_content = await file.read()
        print(f"✅ Dosya okundu ({len(file_content)} bytes).")
        
        print("⏳ ADIM 1: Metin çıkarılıyor...")
        raw_text = extraction.extract_text_from_pdf(file_content)
        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=400, detail="PDF'den metin okunamadı.")
        print(f"✅ Metin çıkarıldı. (Uzunluk: {len(raw_text)} karakter)")
        
        print("⏳ ADIM 2: Gemini AI'ya gönderiliyor...")
        optimized = ai_agent.optimize_cv_with_gemini(raw_text)
        
        ai_feedback = optimized.ai_feedback if hasattr(optimized, 'ai_feedback') else "CV başarıyla optimize edildi."
        
        # PDF'i ai_feedback olmadan oluştur
        optimized.ai_feedback = None 
        
        pdf_bytes = pdf_generation.create_cv_pdf(optimized)
        
        # PDF'i base64'e çevir (indirme linki için)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"
        
        print(f"✅ PDF oluşturuldu. Toplam süre: {time.time()-start_time:.2f}s")
        
        return JSONResponse(content={
            "ai_feedback": ai_feedback,
            "pdf_url": pdf_url,
            "status": "success"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 KRİTİK HATA OLUŞTU: {e}")
        raise HTTPException(status_code=500, detail=str(e))