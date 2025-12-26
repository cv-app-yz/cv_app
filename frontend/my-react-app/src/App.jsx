import { useState } from "react";
import axios from "axios"; // Fetch yerine Axios kullanıyoruz
import "./App.css";

function App() {
  // --- STATE TANIMLARI ---
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [city, setCity] = useState(""); // Şehir bilgisi
  const [aiFeedback, setAiFeedback] = useState(""); // AI geri bildirimi
  const [jobs, setJobs] = useState([]); // İş ilanları listesi

  // --- API İSTEĞİ FONKSİYONU ---
  const uploadFile = async () => {
    if (!file) return alert("Lütfen bir PDF dosyası seçin");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("city", city); // Şehir bilgisini de gönderiyoruz

    setLoading(true);
    setAiFeedback("");
    setPdfUrl(null);
    setJobs([]);

    try {
      // DOĞRUSU (/v1 ekledik):
      const response = await axios.post("http://127.0.0.1:8000/api/v1/analyze-and-match", formData);

      const data = response.data;

      // 1. AI Geri Bildirimi - Kısa ve pozitif mesaj
      const feedbackText = data.ai_feedback || data.optimized_cv?.ai_feedback || "✅ CV analizi tamamlandı.";
      setAiFeedback(feedbackText);

      // 2. İş İlanları
      setJobs(data.job_matches || []);

      // 3. PDF URL (Backend'den geliyorsa)
      // Not: Backend'deki return kısmına 'pdf_url' eklediğini varsayıyoruz.
      if (data.pdf_url) {
        setPdfUrl(data.pdf_url);
      } else if (data.optimized_cv) {
         // Eğer backend PDF url dönmüyorsa ama optimize data dönüyorsa
         // İleride buraya PDF oluşturma isteği eklenebilir.
         // Şimdilik eski akış bozulmasın diye null bırakıyoruz.
      }

    } catch (error) {
      console.error(error);
      setAiFeedback(`❌ Hata: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* --- YÜKLEME ALANI --- */}
      <div className="upload-box">
        <h2>CV Analiz & İş Bulma Platformu</h2>
        
        {/* Şehir Seçimi (YENİ) */}
        <div style={{ marginBottom: '10px' }}>
          <input 
            type="text" 
            placeholder="Şehir Girin (Örn: Ankara)" 
            value={city} 
            onChange={(e) => setCity(e.target.value)}
            style={{ padding: '8px', marginRight: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
        </div>

        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        
        <button onClick={uploadFile} disabled={loading} style={{ marginTop: '10px' }}>
          {loading ? "Analiz Ediliyor..." : "Yükle ve İş Bul"}
        </button>
      </div>

      {/* --- SONUÇ ALANI (Eski yapı korundu) --- */}
      <div className="result-box">
        <h2>AI Analiz Sonucu</h2>
        <div className="result-text">
          {loading ? "⏳ AI CV'nizi inceliyor ve uygun işleri arıyor..." : aiFeedback || "Henüz analiz yapılmadı."}
        </div>

        {/* PDF İndirme Butonu (Eski özellik) */}
        {pdfUrl && (
          <div className="download-section">
            <a href={pdfUrl} download="optimized_cv.pdf" className="download-btn">
              📥 Optimize Edilmiş CV'yi İndir
            </a>
          </div>
        )}
      </div>

      {/* --- İŞ İLANLARI LİSTESİ (YENİ ÖZELLİK) --- */}
      {jobs.length > 0 && (
        <div className="result-box" style={{ marginTop: '20px' }}>
          <h2>🎯 Sizin İçin Seçilen İlanlar</h2>
          <div style={{ display: 'grid', gap: '15px', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
            {jobs.map((job) => (
              <div key={job.id} style={{ 
                border: '1px solid #ddd', 
                borderRadius: '8px', 
                padding: '15px', 
                backgroundColor: '#fff',
                textAlign: 'left',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ margin: '0 0 5px 0', fontSize: '1.1rem', color: '#333' }}>{job.title}</h3>
                <p style={{ margin: '5px 0', color: '#666' }}>🏢 {job.company}</p>
                <p style={{ margin: '5px 0', color: '#666' }}>📍 {job.location}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                  <span style={{ color: '#2ecc71', fontWeight: 'bold' }}>Uyum: {job.match_rate}</span>
                  {/* --- MEVCUT KODUNUZUN İÇİNDEKİ İLGİLİ KISIM --- */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                    
                    {/* 👇 BURAYI DEĞİŞTİRİYORUZ 👇 */}
                    <a href={job.link} target="_blank" rel="noopener noreferrer">
                        <button style={{ padding: '5px 10px', fontSize: '0.9rem', cursor: 'pointer' }}>
                          Başvur
                        </button>
                    </a>
                    {/* 👆 DEĞİŞİKLİK BİTTİ 👆 */}
                    
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

export default App;