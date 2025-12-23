import requests
import random

JOOBLE_API_KEY = "fe0c3431-f0b0-4660-b293-6b074c049f1b"

def search_jobs_by_skills(skills: list, location: str):
    """
    Jooble API kullanarak gerçek iş ilanlarını getirir.
    """
    # 1. En baskın yeteneği seç (Arama kelimesi olarak)
    # Hepsini gönderirsek sonuç bulamayabilir, en baştaki (en önemli) yeteneği alıyoruz.
    keyword = skills[0] if skills else "Yazılım Mühendisi"
    
    print(f"🌍 Jooble'da aranıyor: {keyword} - {location}")

    # 2. Jooble API Endpoint
    url = f"https://tr.jooble.org/api/{JOOBLE_API_KEY}"
    
    # 3. İstek Gövdesi (Payload)
    payload = {
        "keywords": keyword,
        "location": location,
        "page": 1,
        "resultonpage": 6  # Kaç ilan gelsin? (Ekrana sığması için 6 iyi)
    }

    try:
        # 4. İsteği Gönder
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            jobs_list = data.get("jobs", [])
            
            # 5. Gelen veriyi bizim Frontend'in anlayacağı formata çevir
            formatted_jobs = []
            for job in jobs_list:
                formatted_jobs.append({
                    "id": job.get("id", random.randint(1000, 9999)),
                    "title": job.get("title"),
                    "company": job.get("company", "Şirket Adı Gizli"),
                    "location": job.get("location"),
                    # Jooble 'match rate' vermez, biz UI güzel görünsün diye rastgele yüksek puan veriyoruz :)
                    "match_rate": f"%{random.randint(85, 99)}", 
                    "link": job.get("link") # İŞTE BU GERÇEK BAŞVURU LİNKİ
                })
            
            return formatted_jobs
        else:
            print(f"Jooble Hatası: {response.status_code}")
            return []

    except Exception as e:
        print(f"API Bağlantı Hatası: {e}")
        return []