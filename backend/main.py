from fastapi import FastAPI
from app.api.cv_router import router as cv_router
from app.core.config import settings
from app.core.middleware import setup_cors

app = FastAPI(
    title="CV Optimizer API", 
    version="1.0.0", 
    description="Gemini destekli CV optimizasyon API'si"
)

# CORS middleware'i ekle
setup_cors(app)

# Router'ları ekliyoruz
app.include_router(cv_router, prefix="/api/v1", tags=["CV Operations"])

@app.get("/")
def root():
    return {"message": "CV Optimizasyon API'si Çalışıyor! /docs adresine giderek test edebilirsin."}
