from pydantic import BaseModel, Field
from typing import List, Optional


class Education(BaseModel):
    school: str = Field(..., description="Okul veya Üniversite adı")
    degree: str = Field(..., description="Bölüm veya Derece (Örn: Bilgisayar Mühendisliği)")
    date: str = Field(..., description="Başlangıç ve Bitiş yılı (Örn: 2020 - 2024)")

class Experience(BaseModel):
    company: str = Field(..., description="Şirket adı")
    position: str = Field(..., description="Çalışılan pozisyon/ünvan")
    date: str = Field(..., description="Çalışma tarih aralığı (Örn: 2022 - Devam)")
    # AI burayı "Ben yaptım" dilinden "Yapıldı/Edildi" diline çevirecek
    description: str = Field(..., description="Yapılan işlerin profesyonel ve maddeler halinde özeti")

class Project(BaseModel):
    name: str = Field(..., description="Proje adı")
    date: Optional[str] = Field(None, description="Proje tarihi (Örn: 2020-2024)")
    description: str = Field(..., description="Proje açıklaması veya yapılanların maddeler halinde özeti")

class ContactInfo(BaseModel):
    email: str = Field(..., description="E-posta adresi")
    phone: Optional[str] = Field(None, description="Telefon numarası")
    linkedin: Optional[str] = Field(None, description="LinkedIn profil linki")
    github: Optional[str] = Field(None, description="GitHub profil linki")
    location: Optional[str] = Field(None, description="Şehir / Ülke")

class Skills(BaseModel):
    technical: List[str] = Field(default=[], description="Programlama dilleri, frameworkler (Python, React vb.)")
    soft: List[str] = Field(default=[], description="Kişisel yetkinlikler (Liderlik, İletişim vb.)")

# Ana Şema (Bütün CV)

class CVData(BaseModel):
    personal_info: dict = Field(..., description="Ad, Soyad ve Unvan bilgileri")
    contact: ContactInfo
    summary: str = Field(..., description="Kişiyi anlatan kısa, vurucu profesyonel özet")
    education: List[Education] = Field(default=[])
    experience: List[Experience] = Field(default=[])
    projects: List[Project] = Field(default=[], description="Kişisel veya profesyonel projeler listesi")
    skills: Skills
    
    # AI'ın bize notu (Frontend'de kullanıcıya ipucu vermek için)
    ai_feedback: Optional[str] = Field(None, description="CV'nin genel durumu hakkında AI'ın kısa yorumu")