# projenin temel ayarlarını yaptıgımız dosya 

import os 
from dotenv import load_dotenv
from pydantic import BaseSettings, SettingsConfigDict

load_dotenv()  # .env dosyasını yükle

class Settings(BaseSettings):

    GEMINI_API_KEY: str
    PROJECT_NAME : str 

    # 5 MB = 5 * 1024 * 1024 bytes
    MAX_FILE_SIZE_BYTES: int = 5_242_880
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()    
