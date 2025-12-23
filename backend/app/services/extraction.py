import io
from pypdf import PdfReader

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    UploadFile'dan gelen bytes verisini alır,
    içindeki tüm metni string olarak döndürür.
    """
    try:
        # Bytes verisini bellekte dosya gibi açıyoruz
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            # Her sayfadaki metni alıp ekliyoruz
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                
        return text.strip()
    except Exception as e:
        print(f"PDF Okuma Hatası: {e}")
        return ""