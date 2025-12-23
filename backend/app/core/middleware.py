from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    """
    CORS ayarlarını yapılandırır.
    Frontend'den gelen isteklere izin verir.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",  # React alternatif port
        ],
        allow_credentials=True,
        allow_methods=["*"],  # GET, POST, PUT, DELETE vb. tüm methodlar
        allow_headers=["*"],  # Tüm header'lara izin ver
    )
    
    return app