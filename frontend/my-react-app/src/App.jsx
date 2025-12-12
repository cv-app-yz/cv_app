import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);

  const uploadFile = async () => {
    if (!file) return alert("Lütfen bir PDF dosyası seçin");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setResult("");
    setPdfUrl(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/optimize", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${response.status}`);
      }

      // Backend'den JSON ile AI feedback + PDF URL gelecek
      const data = await response.json();

      setResult(data.ai_feedback || "✅ CV başarıyla optimize edildi!");
      setPdfUrl(data.pdf_url || null);

    } catch (error) {
      setResult(`❌ Hata: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="upload-box">
        <h2>CV Yükleme</h2>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={uploadFile} disabled={loading}>
          {loading ? "İşleniyor..." : "Yükle ve Optimize Et"}
        </button>
      </div>

      <div className="result-box">
        <h2>AI Analiz Sonucu</h2>
        <div className="result-text">
          {loading ? "⏳ AI ile CV optimize ediliyor..." : result || "Burada AI analiz sonucu görünecek."}
        </div>

        {pdfUrl && (
          <div className="download-section">
            <a href={pdfUrl} download="optimized_cv.pdf" className="download-btn">
              📥 Optimize Edilmiş CV'yi İndir
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;